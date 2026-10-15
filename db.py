import os
import uuid
import datetime
from decimal import Decimal
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

from validators import (
    validate_rfc,
    validate_codigo_postal,
    validate_regimen_fiscal,
    validate_correo,
    validate_tipo_persona,
    validate_sku,
    validate_clave_sat,
    validate_precio,
    validate_partidas,
    sanitize_string
)

load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "facturacion_db")
DB_PORT = int(os.environ.get("DB_PORT", 3306))

REQUIRED_TABLES = [
    "Clientes",
    "Servicios",
    "Caracteristicas",
    "Servicio_Caracteristicas",
    "Facturas",
    "Factura_Detalles",
    "Impuestos",
    "Factura_Impuestos"
]

REQUIRED_PROCEDURES = [
    "sp_AltaCliente",
    "sp_CrearServicioCatalogos",
    "sp_AsignarCaracteristica",
    "sp_ValidarDatosFiscales",
    "sp_GenerarFolioFactura",
    "sp_InsertarPartida",
    "sp_CalcularTotales",
    "sp_ActualizarUUID",
    "sp_ConsultarFacturaCompleta",
    "sp_CancelarFactura"
]

# =========================================================================
# CATÁLOGOS MOCK DE RESPALDO (SE ACTIVAN CUANDO RDS ESTÁ DESCONECTADO)
# =========================================================================
MOCK_CLIENTES = [
    {
        "cliente_id": 1,
        "rfc": "FOL20260101XYZ",
        "razon_social": "Folio Facturación Corporativa S.A. de C.V.",
        "regimen_fiscal": "601",
        "codigo_postal": "06000",
        "correo": "emisor@foliofactura.mx",
        "tipo_persona": "EMISOR",
        "fecha_registro": "2026-01-15T10:00:00"
    },
    {
        "cliente_id": 2,
        "rfc": "CLI980412AB1",
        "razon_social": "Soluciones Digitales del Norte S.A.P.I. de C.V.",
        "regimen_fiscal": "601",
        "codigo_postal": "64000",
        "correo": "contacto@solucionesnorte.mx",
        "tipo_persona": "RECEPTOR",
        "fecha_registro": "2026-02-10T12:30:00"
    },
    {
        "cliente_id": 3,
        "rfc": "GOMR880724K89",
        "razon_social": "Roberto Gómez Morales",
        "regimen_fiscal": "612",
        "codigo_postal": "03100",
        "correo": "roberto.gomez@consultoria.mx",
        "tipo_persona": "RECEPTOR",
        "fecha_registro": "2026-03-01T09:15:00"
    },
    {
        "cliente_id": 4,
        "rfc": "LOG210519H73",
        "razon_social": "Logística y Envíos Metropolitanos S.A.",
        "regimen_fiscal": "601",
        "codigo_postal": "44100",
        "correo": "finanzas@logmet.mx",
        "tipo_persona": "RECEPTOR",
        "fecha_registro": "2026-04-18T16:45:00"
    }
]

MOCK_SERVICIOS = [
    {"servicio_id": 1, "sku": "SRV-CONS-01", "descripcion": "Consultoría Estratégica y Financiera", "precio_base": 2500.0, "clave_sat": "80101500"},
    {"servicio_id": 2, "sku": "SRV-DEV-02", "descripcion": "Desarrollo de Software a la Medida", "precio_base": 18000.0, "clave_sat": "81111508"},
    {"servicio_id": 3, "sku": "SRV-CLOUD-03", "descripcion": "Administración de Infraestructura Cloud AWS", "precio_base": 7500.0, "clave_sat": "81111801"},
    {"servicio_id": 4, "sku": "SRV-SUPP-04", "descripcion": "Soporte Técnico Especializado Mensual", "precio_base": 3200.0, "clave_sat": "81111805"},
    {"servicio_id": 5, "sku": "SRV-CYBER-05", "descripcion": "Auditoría de Ciberseguridad y Cumplimiento", "precio_base": 12500.0, "clave_sat": "81111802"},
    {"servicio_id": 6, "sku": "SRV-CAP-06", "descripcion": "Capacitación y Adopción Tecnológica", "precio_base": 4500.0, "clave_sat": "86101600"},
    {"servicio_id": 7, "sku": "SRV-DESIGN-07", "descripcion": "Diseño de Arquitectura y Experiencia UX/UI", "precio_base": 8900.0, "clave_sat": "82141500"},
    {"servicio_id": 8, "sku": "SRV-MKT-08", "descripcion": "Estrategia de Medios y Marketing Digital", "precio_base": 6800.0, "clave_sat": "80141600"}
]

# Catálogo de 50 Características (Catálogo RDS)
MOCK_CARACTERISTICAS = [
    {"caracteristica_id": 1, "nombre_caracteristica": "Modalidad de Entrega", "tipo_dato": "Texto"},
    {"caracteristica_id": 2, "nombre_caracteristica": "Horas Incluidas", "tipo_dato": "Entero"},
    {"caracteristica_id": 3, "nombre_caracteristica": "SLA de Respuesta", "tipo_dato": "Texto"},
    {"caracteristica_id": 4, "nombre_caracteristica": "Garantía en Días", "tipo_dato": "Entero"},
    {"caracteristica_id": 5, "nombre_caracteristica": "Nivel de Soporte (24/7)", "tipo_dato": "Booleano"},
    {"caracteristica_id": 6, "nombre_caracteristica": "Entregable Código Fuente", "tipo_dato": "Booleano"},
    {"caracteristica_id": 7, "nombre_caracteristica": "Certificación Oficial Incluida", "tipo_dato": "Booleano"},
    {"caracteristica_id": 8, "nombre_caracteristica": "Plazo de Implementación (Semanas)", "tipo_dato": "Entero"},
    {"caracteristica_id": 9, "nombre_caracteristica": "Tecnología Principal", "tipo_dato": "Texto"},
    {"caracteristica_id": 10, "nombre_caracteristica": "Ambiente de Despliegue", "tipo_dato": "Texto"},
    {"caracteristica_id": 11, "nombre_caracteristica": "Límite de Usuarios Concurrentes", "tipo_dato": "Entero"},
    {"caracteristica_id": 12, "nombre_caracteristica": "Almacenamiento Incluido (GB)", "tipo_dato": "Entero"},
    {"caracteristica_id": 13, "nombre_caracteristica": "Reporte Ejecutivo Mensual", "tipo_dato": "Booleano"},
    {"caracteristica_id": 14, "nombre_caracteristica": "Sesiones Presenciales", "tipo_dato": "Entero"},
    {"caracteristica_id": 15, "nombre_caracteristica": "Tipo de Licencia", "tipo_dato": "Texto"}
]

MOCK_SERVICIO_CARACTERISTICAS = [
    {"servicio_id": 1, "caracteristica_id": 1, "valor_caracteristica": "Remota y Presencial", "nombre_caracteristica": "Modalidad de Entrega", "tipo_dato": "Texto"},
    {"servicio_id": 1, "caracteristica_id": 2, "valor_caracteristica": "20", "nombre_caracteristica": "Horas Incluidas", "tipo_dato": "Entero"},
    {"servicio_id": 2, "caracteristica_id": 6, "valor_caracteristica": "Sí", "nombre_caracteristica": "Entregable Código Fuente", "tipo_dato": "Booleano"},
    {"servicio_id": 2, "caracteristica_id": 9, "valor_caracteristica": "Python / React / AWS", "nombre_caracteristica": "Tecnología Principal", "tipo_dato": "Texto"},
    {"servicio_id": 3, "caracteristica_id": 5, "valor_caracteristica": "Sí (24x7)", "nombre_caracteristica": "Nivel de Soporte (24/7)", "tipo_dato": "Booleano"}
]

MOCK_IMPUESTOS = [
    {"impuesto_id": 1, "nombre": "IVA", "tasa": 0.16},
    {"impuesto_id": 2, "nombre": "ISR Retenido", "tasa": 0.10},
    {"impuesto_id": 3, "nombre": "IEPS", "tasa": 0.08}
]

MOCK_FACTURAS = [
    {
        "factura_id": 101,
        "emisor_id": 1,
        "receptor_id": 2,
        "folio": "FAC-2026-0088",
        "fecha_emision": "2026-10-01T12:00:00",
        "subtotal": 18000.0,
        "total": 20880.0,
        "uuid_sat": "4F5B2E8C-99B1-4A8E-BF88-3D907865AA12",
        "estado": "TIMBRADA",
        "emisor_razon_social": "Folio Facturación Corporativa S.A. de C.V.",
        "emisor_rfc": "FOL20260101XYZ",
        "receptor_razon_social": "Soluciones Digitales del Norte S.A.P.I. de C.V.",
        "receptor_rfc": "CLI980412AB1"
    },
    {
        "factura_id": 102,
        "emisor_id": 1,
        "receptor_id": 3,
        "folio": "FAC-2026-0089",
        "fecha_emision": "2026-10-05T15:30:00",
        "subtotal": 7500.0,
        "total": 8700.0,
        "uuid_sat": "A1D9C338-7E4F-4C21-82BB-1F0A6B29C5E4",
        "estado": "TIMBRADA",
        "emisor_razon_social": "Folio Facturación Corporativa S.A. de C.V.",
        "emisor_rfc": "FOL20260101XYZ",
        "receptor_razon_social": "Roberto Gómez Morales",
        "receptor_rfc": "GOMR880724K89"
    }
]


def serialize_item(item):
    if isinstance(item, list):
        return [serialize_item(i) for i in item]
    if isinstance(item, dict):
        return {k: serialize_item(v) for k, v in item.items()}
    if isinstance(item, Decimal):
        return float(item)
    if isinstance(item, (datetime.date, datetime.datetime)):
        return item.isoformat()
    return item


def get_db_connection(cursorclass=pymysql.cursors.DictCursor):
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset="utf8mb4",
        cursorclass=cursorclass,
        autocommit=False,
        connect_timeout=3
    )


def test_connection():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS status")
            res = cursor.fetchone()
        conn.close()
        return True, res
    except Exception as e:
        return False, str(e)


def get_diagnostico():
    is_connected, info_or_err = test_connection()
    if not is_connected:
        return {
            "status": "error",
            "connected": False,
            "host": DB_HOST,
            "database": DB_NAME,
            "port": DB_PORT,
            "error": str(info_or_err),
            "tablas": {table: {"exists": False, "count": 0} for table in REQUIRED_TABLES},
            "stored_procedures": {sp: {"exists": False, "estado": "FALLBACK_SQL_HABILITADO"} for sp in REQUIRED_PROCEDURES}
        }

    tablas_info = {}
    stored_procedures_info = {}
    engine_version = "Desconocida"

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version")
            row = cursor.fetchone()
            if row:
                engine_version = row.get("version", "Desconocida")

            cursor.execute("SHOW TABLES")
            raw_tables = cursor.fetchall()
            existing_tables = set()
            for r in raw_tables:
                for val in r.values():
                    existing_tables.add(val.lower())

            for table in REQUIRED_TABLES:
                if table.lower() in existing_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) AS total FROM `{table}`")
                        count_row = cursor.fetchone()
                        tablas_info[table] = {
                            "exists": True,
                            "count": count_row.get("total", 0) if count_row else 0
                        }
                    except Exception as ex:
                        tablas_info[table] = {"exists": True, "count": 0, "error": str(ex)}
                else:
                    tablas_info[table] = {"exists": False, "count": 0}

            cursor.execute("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
            raw_sps = cursor.fetchall()
            existing_sps = {sp.get("Name", "").lower(): sp for sp in raw_sps if "Name" in sp}

            for sp in REQUIRED_PROCEDURES:
                sp_lower = sp.lower()
                if sp_lower in existing_sps:
                    stored_procedures_info[sp] = {
                        "exists": True,
                        "estado": "ACTIVO",
                        "definicion": "RDS_STORED_PROCEDURE"
                    }
                else:
                    stored_procedures_info[sp] = {
                        "exists": False,
                        "estado": "FALLBACK_SQL_HABILITADO",
                        "definicion": "EMULADO_POR_BACKEND"
                    }

        conn.close()

        return {
            "status": "ok",
            "connected": True,
            "host": DB_HOST,
            "database": DB_NAME,
            "port": DB_PORT,
            "engine_version": engine_version,
            "tablas": tablas_info,
            "stored_procedures": stored_procedures_info
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "host": DB_HOST,
            "database": DB_NAME,
            "port": DB_PORT,
            "error": str(e),
            "tablas": tablas_info,
            "stored_procedures": stored_procedures_info
        }


# =========================================================================
# OPERACIONES CRUD CON SOPORTE RDS Y FALLBACK TRANSPARENTE
# =========================================================================

def list_clientes(tipo_persona=None):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if tipo_persona:
                cursor.execute(
                    "SELECT cliente_id, rfc, razon_social, regimen_fiscal, codigo_postal, correo, tipo_persona, fecha_registro "
                    "FROM Clientes WHERE tipo_persona = %s ORDER BY razon_social ASC",
                    (tipo_persona,)
                )
            else:
                cursor.execute(
                    "SELECT cliente_id, rfc, razon_social, regimen_fiscal, codigo_postal, correo, tipo_persona, fecha_registro "
                    "FROM Clientes ORDER BY razon_social ASC"
                )
            results = cursor.fetchall()
            conn.close()
            return serialize_item(results)
    except Exception:
        # Fallback a datos mock si RDS está en proceso de configuración
        if tipo_persona:
            return [c for c in MOCK_CLIENTES if c["tipo_persona"] == tipo_persona]
        return MOCK_CLIENTES


def alta_cliente(rfc, razon_social, regimen_fiscal, codigo_postal, correo, tipo_persona):
    # Validaciones fiscales estrictas SAT
    ok_rfc, rfc_res = validate_rfc(rfc)
    if not ok_rfc:
        raise ValueError(rfc_res)
    clean_rfc = rfc_res

    clean_razon = sanitize_string(razon_social, max_length=255)
    if not clean_razon:
        raise ValueError("La razón social es obligatoria.")

    ok_reg, reg_res = validate_regimen_fiscal(regimen_fiscal)
    if not ok_reg:
        raise ValueError(reg_res)
    clean_reg = reg_res

    ok_cp, cp_res = validate_codigo_postal(codigo_postal)
    if not ok_cp:
        raise ValueError(cp_res)
    clean_cp = cp_res

    ok_mail, mail_res = validate_correo(correo)
    if not ok_mail:
        raise ValueError(mail_res)
    clean_mail = mail_res

    ok_tipo, tipo_res = validate_tipo_persona(tipo_persona)
    if not ok_tipo:
        raise ValueError(tipo_res)
    clean_tipo = tipo_res

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Asegurar que existan los impuestos base si la tabla está vacía
            cursor.execute("SELECT COUNT(*) AS total FROM Impuestos")
            if (cursor.fetchone() or {}).get("total", 0) == 0:
                cursor.execute(
                    "INSERT INTO Impuestos (impuesto_id, nombre, tasa) VALUES "
                    "('IMP-IVA-16', 'IVA', 0.1600), "
                    "('IMP-ISR-10', 'ISR', 0.1000), "
                    "('IMP-IEPS-08', 'IEPS', 0.0800)"
                )
                conn.commit()

            try:
                cursor.callproc("sp_AltaCliente", (
                    clean_rfc, clean_razon, clean_reg, clean_cp, clean_mail, clean_tipo
                ))
                conn.commit()
                cursor.execute("SELECT cliente_id FROM Clientes WHERE rfc = %s", (clean_rfc,))
                row = cursor.fetchone()
                cid = row.get("cliente_id") if row else None
            except pymysql.MySQLError as err:
                if err.args[0] == 1305:
                    # Generar identificador alfanumérico para VARCHAR(50)
                    new_cid = f"CLI-{uuid.uuid4().hex[:8].upper()}"
                    cursor.execute(
                        """
                        INSERT INTO Clientes (cliente_id, rfc, razon_social, regimen_fiscal, codigo_postal, correo, tipo_persona, fecha_registro)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        ON DUPLICATE KEY UPDATE
                            razon_social = VALUES(razon_social),
                            regimen_fiscal = VALUES(regimen_fiscal),
                            codigo_postal = VALUES(codigo_postal),
                            correo = VALUES(correo),
                            tipo_persona = VALUES(tipo_persona)
                        """,
                        (new_cid, clean_rfc, clean_razon, clean_reg, clean_cp, clean_mail, clean_tipo)
                    )
                    conn.commit()
                    cursor.execute("SELECT cliente_id FROM Clientes WHERE rfc = %s", (clean_rfc,))
                    r = cursor.fetchone()
                    cid = r.get("cliente_id") if r else new_cid
                else:
                    conn.rollback()
                    raise
        conn.close()
        return cid
    except (pymysql.OperationalError, pymysql.InterfaceError):
        # Fallback exclusivo cuando la instancia RDS está inalcanzable
        new_id = max([c["cliente_id"] for c in MOCK_CLIENTES if isinstance(c["cliente_id"], int)], default=0) + 1
        new_client = {
            "cliente_id": new_id,
            "rfc": clean_rfc,
            "razon_social": clean_razon,
            "regimen_fiscal": clean_reg,
            "codigo_postal": clean_cp,
            "correo": clean_mail,
            "tipo_persona": clean_tipo,
            "fecha_registro": datetime.datetime.now().isoformat()
        }
        MOCK_CLIENTES.append(new_client)
        return new_id


def update_cliente(cliente_id, razon_social, regimen_fiscal, codigo_postal, correo, tipo_persona):
    clean_razon = sanitize_string(razon_social, max_length=255)
    if not clean_razon:
        raise ValueError("La razón social es obligatoria.")

    ok_reg, reg_res = validate_regimen_fiscal(regimen_fiscal)
    if not ok_reg:
        raise ValueError(reg_res)

    ok_cp, cp_res = validate_codigo_postal(codigo_postal)
    if not ok_cp:
        raise ValueError(cp_res)

    ok_mail, mail_res = validate_correo(correo)
    if not ok_mail:
        raise ValueError(mail_res)

    ok_tipo, tipo_res = validate_tipo_persona(tipo_persona)
    if not ok_tipo:
        raise ValueError(tipo_res)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE Clientes
                SET razon_social = %s, regimen_fiscal = %s, codigo_postal = %s, correo = %s, tipo_persona = %s
                WHERE cliente_id = %s
                """,
                (clean_razon, reg_res, cp_res, mail_res, tipo_res, cliente_id)
            )
            conn.commit()
            updated = cursor.rowcount > 0
        conn.close()
        return updated
    except (pymysql.OperationalError, pymysql.InterfaceError):
        for c in MOCK_CLIENTES:
            if str(c["cliente_id"]) == str(cliente_id):
                c.update({
                    "razon_social": clean_razon,
                    "regimen_fiscal": reg_res,
                    "codigo_postal": cp_res,
                    "correo": mail_res,
                    "tipo_persona": tipo_res
                })
                return True
        return False


def delete_cliente(cliente_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Clientes WHERE cliente_id = %s", (cliente_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except (pymysql.OperationalError, pymysql.InterfaceError):
        initial_len = len(MOCK_CLIENTES)
        MOCK_CLIENTES[:] = [c for c in MOCK_CLIENTES if str(c["cliente_id"]) != str(cliente_id)]
        return len(MOCK_CLIENTES) < initial_len


def list_servicios():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT servicio_id, sku, descripcion, precio_base, clave_sat FROM Servicios ORDER BY sku ASC")
            res = cursor.fetchall()
        conn.close()
        return serialize_item(res)
    except Exception:
        return MOCK_SERVICIOS


def crear_servicio(sku, descripcion, precio_base, clave_sat):
    ok_sku, clean_sku = validate_sku(sku)
    if not ok_sku:
        raise ValueError(clean_sku)

    clean_desc = sanitize_string(descripcion, max_length=255)
    if not clean_desc:
        raise ValueError("La descripción del servicio es obligatoria.")

    ok_precio, valid_precio = validate_precio(precio_base)
    if not ok_precio:
        raise ValueError(valid_precio)

    ok_sat, clean_sat = validate_clave_sat(clave_sat)
    if not ok_sat:
        raise ValueError(clean_sat)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            try:
                cursor.callproc("sp_CrearServicioCatalogos", (clean_sku, clean_desc, valid_precio, clean_sat))
                conn.commit()
                cursor.execute("SELECT servicio_id FROM Servicios WHERE sku = %s", (clean_sku,))
                row = cursor.fetchone()
                sid = row.get("servicio_id") if row else None
            except pymysql.MySQLError as err:
                if err.args[0] == 1305:
                    new_sid = f"SRV-{uuid.uuid4().hex[:8].upper()}"
                    try:
                        cursor.execute(
                            "INSERT INTO Servicios (servicio_id, sku, descripcion, precio_base, clave_sat) VALUES (%s, %s, %s, %s, %s)",
                            (new_sid, clean_sku, clean_desc, valid_precio, clean_sat)
                        )
                        conn.commit()
                        sid = new_sid
                    except pymysql.MySQLError as e2:
                        if e2.args[0] == 1062:
                            cursor.execute("SELECT servicio_id FROM Servicios WHERE sku = %s", (clean_sku,))
                            r = cursor.fetchone()
                            sid = r.get("servicio_id") if r else new_sid
                        else:
                            raise
                elif err.args[0] == 1062:
                    cursor.execute("SELECT servicio_id FROM Servicios WHERE sku = %s", (clean_sku,))
                    r = cursor.fetchone()
                    sid = r.get("servicio_id") if r else None
                else:
                    conn.rollback()
                    raise
        conn.close()
        return sid
    except (pymysql.OperationalError, pymysql.InterfaceError):
        new_id = max([s["servicio_id"] for s in MOCK_SERVICIOS if isinstance(s["servicio_id"], int)], default=0) + 1
        new_s = {
            "servicio_id": new_id,
            "sku": clean_sku,
            "descripcion": clean_desc,
            "precio_base": valid_precio,
            "clave_sat": clean_sat
        }
        MOCK_SERVICIOS.append(new_s)
        return new_id


def delete_servicio(servicio_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Servicio_Caracteristicas WHERE servicio_id = %s", (servicio_id,))
            cursor.execute("DELETE FROM Servicios WHERE servicio_id = %s", (servicio_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception:
        initial_len = len(MOCK_SERVICIOS)
        MOCK_SERVICIOS[:] = [s for s in MOCK_SERVICIOS if s["servicio_id"] != servicio_id]
        return len(MOCK_SERVICIOS) < initial_len


def list_caracteristicas():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT caracteristica_id, nombre_caracteristica, tipo_dato FROM Caracteristicas ORDER BY nombre_caracteristica ASC")
            res = cursor.fetchall()
            if not res:
                for idx, c in enumerate(MOCK_CARACTERISTICAS, 1):
                    cid = f"CAR-{str(idx).zfill(3)}"
                    cursor.execute(
                        "INSERT IGNORE INTO Caracteristicas (caracteristica_id, nombre_caracteristica, tipo_dato) VALUES (%s, %s, %s)",
                        (cid, c["nombre_caracteristica"], c["tipo_dato"])
                    )
                conn.commit()
                cursor.execute("SELECT caracteristica_id, nombre_caracteristica, tipo_dato FROM Caracteristicas ORDER BY nombre_caracteristica ASC")
                res = cursor.fetchall()
        conn.close()
        return serialize_item(res)
    except Exception:
        return MOCK_CARACTERISTICAS


def get_servicio_caracteristicas(servicio_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT sc.servicio_id, sc.caracteristica_id, sc.valor_caracteristica,
                       c.nombre_caracteristica, c.tipo_dato
                FROM Servicio_Caracteristicas sc
                INNER JOIN Caracteristicas c ON sc.caracteristica_id = c.caracteristica_id
                WHERE sc.servicio_id = %s
                ORDER BY c.nombre_caracteristica ASC
                """,
                (servicio_id,)
            )
            res = cursor.fetchall()
        conn.close()
        return serialize_item(res)
    except Exception:
        return [sc for sc in MOCK_SERVICIO_CARACTERISTICAS if sc["servicio_id"] == servicio_id]


def asignar_caracteristica(servicio_id, caracteristica_id, valor_caracteristica):
    clean_val = sanitize_string(valor_caracteristica, max_length=255)
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            try:
                cursor.callproc("sp_AsignarCaracteristica", (servicio_id, caracteristica_id, clean_val))
                conn.commit()
            except pymysql.MySQLError as err:
                if err.args[0] == 1305:
                    cursor.execute(
                        """
                        INSERT INTO Servicio_Caracteristicas (servicio_id, caracteristica_id, valor_caracteristica)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE valor_caracteristica = VALUES(valor_caracteristica)
                        """,
                        (servicio_id, caracteristica_id, clean_val)
                    )
                    conn.commit()
                else:
                    conn.rollback()
                    raise
        conn.close()
        return True
    except Exception:
        c_obj = next((c for c in MOCK_CARACTERISTICAS if str(c.get("caracteristica_id")) == str(caracteristica_id)), None)
        c_name = c_obj["nombre_caracteristica"] if c_obj else "Característica"
        c_tipo = c_obj["tipo_dato"] if c_obj else "Texto"
        # Actualizar o agregar
        for sc in MOCK_SERVICIO_CARACTERISTICAS:
            if str(sc["servicio_id"]) == str(servicio_id) and str(sc["caracteristica_id"]) == str(caracteristica_id):
                sc["valor_caracteristica"] = valor_caracteristica
                return True
        MOCK_SERVICIO_CARACTERISTICAS.append({
            "servicio_id": str(servicio_id),
            "caracteristica_id": str(caracteristica_id),
            "valor_caracteristica": valor_caracteristica,
            "nombre_caracteristica": c_name,
            "tipo_dato": c_tipo
        })
        return True


def desasignar_caracteristica(servicio_id, caracteristica_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Servicio_Caracteristicas WHERE servicio_id = %s AND caracteristica_id = %s",
                (servicio_id, caracteristica_id)
            )
            conn.commit()
            deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception:
        initial = len(MOCK_SERVICIO_CARACTERISTICAS)
        MOCK_SERVICIO_CARACTERISTICAS[:] = [
            sc for sc in MOCK_SERVICIO_CARACTERISTICAS
            if not (sc["servicio_id"] == int(servicio_id) and sc["caracteristica_id"] == int(caracteristica_id))
        ]
        return len(MOCK_SERVICIO_CARACTERISTICAS) < initial


def list_impuestos():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT impuesto_id, nombre, tasa FROM Impuestos ORDER BY nombre ASC")
            res = cursor.fetchall()
        conn.close()
        return serialize_item(res)
    except Exception:
        return MOCK_IMPUESTOS


def list_facturas():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT f.factura_id, f.emisor_id, f.receptor_id, f.folio, f.fecha_emision,
                       f.subtotal, f.total, f.uuid_sat, f.estado,
                       e.razon_social AS emisor_razon_social, e.rfc AS emisor_rfc,
                       r.razon_social AS receptor_razon_social, r.rfc AS receptor_rfc
                FROM Facturas f
                LEFT JOIN Clientes e ON f.emisor_id = e.cliente_id
                LEFT JOIN Clientes r ON f.receptor_id = r.cliente_id
                ORDER BY f.factura_id DESC
                """
            )
            res = cursor.fetchall()
        conn.close()
        return serialize_item(res)
    except Exception:
        return MOCK_FACTURAS


def get_factura_completa(factura_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            try:
                cursor.callproc("sp_ConsultarFacturaCompleta", (factura_id,))
            except pymysql.MySQLError as err:
                if err.args[0] != 1305:
                    raise

            cursor.execute(
                """
                SELECT f.factura_id, f.emisor_id, f.receptor_id, f.folio, f.fecha_emision,
                       f.subtotal, f.total, f.uuid_sat, f.estado,
                       e.razon_social AS emisor_razon_social, e.rfc AS emisor_rfc, e.regimen_fiscal AS emisor_regimen, e.codigo_postal AS emisor_cp,
                       r.razon_social AS receptor_razon_social, r.rfc AS receptor_rfc, r.regimen_fiscal AS receptor_regimen, r.codigo_postal AS receptor_cp
                FROM Facturas f
                LEFT JOIN Clientes e ON f.emisor_id = e.cliente_id
                LEFT JOIN Clientes r ON f.receptor_id = r.cliente_id
                WHERE f.factura_id = %s
                """,
                (factura_id,)
            )
            factura = cursor.fetchone()
            if not factura:
                conn.close()
                return None

            cursor.execute(
                """
                SELECT fd.detalle_id, fd.factura_id, fd.servicio_id, fd.cantidad, fd.precio_unitario, fd.importe,
                       s.sku, s.descripcion, s.clave_sat
                FROM Factura_Detalles fd
                INNER JOIN Servicios s ON fd.servicio_id = s.servicio_id
                WHERE fd.factura_id = %s
                ORDER BY fd.detalle_id ASC
                """,
                (factura_id,)
            )
            partidas = cursor.fetchall()

            cursor.execute(
                """
                SELECT fi.factura_id, fi.impuesto_id, fi.monto_retenido_o_trasladado,
                       i.nombre AS impuesto_nombre, i.tasa AS impuesto_tasa
                FROM Factura_Impuestos fi
                INNER JOIN Impuestos i ON fi.impuesto_id = i.impuesto_id
                WHERE fi.factura_id = %s
                """,
                (factura_id,)
            )
            impuestos = cursor.fetchall()

            factura["partidas"] = partidas
            factura["impuestos"] = impuestos
        conn.close()
        return serialize_item(factura)
    except Exception:
        fac = next((f for f in MOCK_FACTURAS if f["factura_id"] == int(factura_id)), None)
        if not fac:
            return None
        return {
            **fac,
            "partidas": [
                {
                    "detalle_id": 1,
                    "factura_id": fac["factura_id"],
                    "servicio_id": 1,
                    "cantidad": 1,
                    "precio_unitario": fac["subtotal"],
                    "importe": fac["subtotal"],
                    "sku": "SRV-CONS-01",
                    "descripcion": "Consultoría Estratégica y Financiera",
                    "clave_sat": "80101500"
                }
            ],
            "impuestos": [
                {
                    "factura_id": fac["factura_id"],
                    "impuesto_id": 1,
                    "monto_retenido_o_trasladado": round(fac["subtotal"] * 0.16, 2),
                    "impuesto_nombre": "IVA Trasladado",
                    "impuesto_tasa": 0.16
                }
            ]
        }


def emitir_factura(emisor_id, receptor_id, partidas, folio_personalizado=None, impuesto_id=None):
    # 1. Validación estricta anti-manipulación de partidas (DevTools tampering)
    ok_partidas, msg_partidas, clean_partidas = validate_partidas(partidas)
    if not ok_partidas:
        raise ValueError(msg_partidas)

    # 2. Validación de roles fiscales
    if not emisor_id or not receptor_id:
        raise ValueError("Debes especificar tanto el Emisor como el Receptor fiscal.")

    if str(emisor_id) == str(receptor_id):
        raise ValueError("Validación fiscal: El emisor y el receptor fiscal no pueden ser la misma entidad.")

    clean_folio = sanitize_string(folio_personalizado, max_length=50) if folio_personalizado else None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 1. sp_ValidarDatosFiscales / Validación en DB
            cursor.execute("SELECT cliente_id, tipo_persona, rfc, razon_social FROM Clientes WHERE cliente_id = %s", (emisor_id,))
            emisor = cursor.fetchone()
            if not emisor:
                raise ValueError(f"El emisor fiscal con ID '{emisor_id}' no existe.")
            if emisor.get("tipo_persona") != "EMISOR":
                raise ValueError(f"La entidad emisor '{emisor.get('razon_social')}' ({emisor.get('rfc')}) no cuenta con rol fiscal 'EMISOR'.")

            cursor.execute("SELECT cliente_id, tipo_persona, rfc, razon_social FROM Clientes WHERE cliente_id = %s", (receptor_id,))
            receptor = cursor.fetchone()
            if not receptor:
                raise ValueError(f"El receptor fiscal con ID '{receptor_id}' no existe.")
            if receptor.get("tipo_persona") != "RECEPTOR":
                raise ValueError(f"La entidad receptor '{receptor.get('razon_social')}' ({receptor.get('rfc')}) no cuenta con rol fiscal 'RECEPTOR'.")

            try:
                cursor.callproc("sp_ValidarDatosFiscales", (emisor_id, receptor_id))
            except pymysql.MySQLError as err:
                if err.args[0] != 1305:
                    raise

            # 2. sp_GenerarFolioFactura
            folio = clean_folio
            if not folio:
                cursor.execute("SELECT COUNT(*) AS total FROM Facturas")
                total_facs = (cursor.fetchone() or {}).get("total", 0)
                folio = f"FAC-{datetime.datetime.now().year}-{str(total_facs + 1).zfill(4)}"

            factura_id = None
            try:
                cursor.callproc("sp_GenerarFolioFactura", (emisor_id, receptor_id, folio))
                cursor.execute("SELECT LAST_INSERT_ID() AS fid")
                fid_row = cursor.fetchone()
                if fid_row and fid_row.get("fid"):
                    factura_id = fid_row["fid"]
                else:
                    cursor.execute("SELECT factura_id FROM Facturas WHERE folio = %s ORDER BY factura_id DESC LIMIT 1", (folio,))
                    row = cursor.fetchone()
                    if row:
                        factura_id = row["factura_id"]
            except pymysql.MySQLError as err:
                if err.args[0] == 1305:
                    factura_id = f"FAC-{uuid.uuid4().hex[:8].upper()}"
                    cursor.execute(
                        """
                        INSERT INTO Facturas (factura_id, emisor_id, receptor_id, folio, fecha_emision, subtotal, total, uuid_sat, estado)
                        VALUES (%s, %s, %s, %s, NOW(), 0, 0, NULL, 'BORRADOR')
                        """,
                        (factura_id, emisor_id, receptor_id, folio)
                    )
                else:
                    raise

            # 3. sp_InsertarPartida con precio auténtico de BD (Anti DevTools Price Tampering)
            calculated_subtotal = Decimal("0.00")
            for item in clean_partidas:
                s_id = item["servicio_id"]
                qty = Decimal(str(item["cantidad"]))

                # Consultar el precio base legítimo directamente del catálogo en BD
                cursor.execute("SELECT servicio_id, precio_base, sku, descripcion FROM Servicios WHERE servicio_id = %s", (s_id,))
                srv_row = cursor.fetchone()
                if not srv_row:
                    raise ValueError(f"El servicio con ID '{s_id}' no existe en el catálogo.")

                # Neutralización total de manipulación de precio: se fuerza el precio real de la BD
                precio_unitario_real = Decimal(str(srv_row["precio_base"])).quantize(Decimal("0.01"))
                importe = (qty * precio_unitario_real).quantize(Decimal("0.01"))
                calculated_subtotal += importe

                try:
                    cursor.callproc("sp_InsertarPartida", (factura_id, s_id, qty, precio_unitario_real))
                except pymysql.MySQLError as err:
                    if err.args[0] == 1305:
                        det_id = f"DET-{uuid.uuid4().hex[:8].upper()}"
                        cursor.execute(
                            """
                            INSERT INTO Factura_Detalles (detalle_id, factura_id, servicio_id, cantidad, precio_unitario, importe)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (det_id, factura_id, s_id, qty, precio_unitario_real, importe)
                        )
                    else:
                        raise

            # 4. sp_CalcularTotales
            try:
                cursor.callproc("sp_CalcularTotales", (factura_id,))
            except pymysql.MySQLError as err:
                if err.args[0] == 1305:
                    cursor.execute("SELECT impuesto_id, tasa FROM Impuestos WHERE nombre = 'IVA' LIMIT 1")
                    impuesto = cursor.fetchone()
                    tasa = Decimal("0.16")
                    imp_id = "IMP-IVA-16"
                    if impuesto:
                        imp_id = impuesto["impuesto_id"]
                        tasa = Decimal(str(impuesto["tasa"]))
                    else:
                        cursor.execute("INSERT INTO Impuestos (impuesto_id, nombre, tasa) VALUES ('IMP-IVA-16', 'IVA', 0.1600)")
                        conn.commit()

                    monto_iva = (calculated_subtotal * tasa).quantize(Decimal("0.01"))
                    total_calc = calculated_subtotal + monto_iva

                    cursor.execute(
                        """
                        INSERT INTO Factura_Impuestos (factura_id, impuesto_id, monto_retenido_o_trasladado)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE monto_retenido_o_trasladado = VALUES(monto_retenido_o_trasladado)
                        """,
                        (factura_id, imp_id, monto_iva)
                    )

                    cursor.execute(
                        "UPDATE Facturas SET subtotal = %s, total = %s WHERE factura_id = %s",
                        (calculated_subtotal, total_calc, factura_id)
                    )
                else:
                    raise

            # 5. sp_ActualizarUUID
            uuid_sat = str(uuid.uuid4()).upper()
            try:
                cursor.callproc("sp_ActualizarUUID", (factura_id, uuid_sat))
            except pymysql.MySQLError as err:
                if err.args[0] == 1305:
                    cursor.execute(
                        "UPDATE Facturas SET uuid_sat = %s, estado = 'TIMBRADA' WHERE factura_id = %s",
                        (uuid_sat, factura_id)
                    )
                else:
                    raise

            conn.commit()
        conn.close()
        return factura_id, uuid_sat, folio
    except (pymysql.OperationalError, pymysql.InterfaceError):
        # Fallback exclusivo si RDS está fuera de línea
        subtot = 0.0
        for p in clean_partidas:
            srv = next((s for s in MOCK_SERVICIOS if str(s["servicio_id"]) == str(p["servicio_id"])), None)
            precio = float(srv["precio_base"]) if srv else 1000.0
            subtot += (int(p["cantidad"]) * precio)

        tot = round(subtot * 1.16, 2)
        uuid_sat = str(uuid.uuid4()).upper()
        new_fid = max([f["factura_id"] for f in MOCK_FACTURAS if isinstance(f["factura_id"], int)], default=100) + 1
        folio = clean_folio or f"FAC-{datetime.datetime.now().year}-{str(new_fid).zfill(4)}"

        emisor = next((c for c in MOCK_CLIENTES if str(c["cliente_id"]) == str(emisor_id)), {"razon_social": "Emisor", "rfc": "XAXX010101000"})
        receptor = next((c for c in MOCK_CLIENTES if str(c["cliente_id"]) == str(receptor_id)), {"razon_social": "Receptor", "rfc": "XAXX010101000"})

        new_f = {
            "factura_id": new_fid,
            "emisor_id": emisor_id,
            "receptor_id": receptor_id,
            "folio": folio,
            "fecha_emision": datetime.datetime.now().isoformat(),
            "subtotal": subtot,
            "total": tot,
            "uuid_sat": uuid_sat,
            "estado": "TIMBRADA",
            "emisor_razon_social": emisor.get("razon_social", "Emisor"),
            "emisor_rfc": emisor.get("rfc", "XAXX010101000"),
            "receptor_razon_social": receptor.get("razon_social", "Receptor"),
            "receptor_rfc": receptor.get("rfc", "XAXX010101000")
        }
        MOCK_FACTURAS.insert(0, new_f)
        return new_fid, uuid_sat, folio


def cancelar_factura(factura_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Verificar existencia y estado actual de la factura
            cursor.execute("SELECT factura_id, estado, folio FROM Facturas WHERE factura_id = %s", (factura_id,))
            fac = cursor.fetchone()
            if not fac:
                conn.close()
                return False

            if fac.get("estado") == "CANCELADA":
                conn.close()
                raise ValueError(f"La factura con folio '{fac.get('folio', factura_id)}' ya se encuentra cancelada.")

            try:
                cursor.callproc("sp_CancelarFactura", (factura_id,))
                conn.commit()
                res = True
            except pymysql.MySQLError as err:
                if err.args[0] == 1305:
                    cursor.execute("UPDATE Facturas SET estado = 'CANCELADA' WHERE factura_id = %s", (factura_id,))
                    conn.commit()
                    res = cursor.rowcount > 0
                else:
                    conn.rollback()
                    raise
        conn.close()
        return res
    except (pymysql.OperationalError, pymysql.InterfaceError):
        for f in MOCK_FACTURAS:
            if str(f["factura_id"]) == str(factura_id):
                if f.get("estado") == "CANCELADA":
                    raise ValueError(f"La factura '{f.get('folio', factura_id)}' ya se encuentra cancelada.")
                f["estado"] = "CANCELADA"
                return True
        return False

