import os
import json
import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template, request, redirect, url_for

import db
import dynamo
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

BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)


# =========================================================================
# CABECERAS DE SEGURIDAD HTTP Y MANEJO CENTRALIZADO DE ERRORES
# =========================================================================

@app.after_request
def add_security_headers(response):
    """Agrega cabeceras de seguridad contra XSS, Clickjacking y Sniffing."""
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' https:; "
        "font-src 'self' https: data:; "
        "img-src 'self' data: https:;"
    )
    return response


@app.errorhandler(400)
def bad_request_handler(e):
    if request.path.startswith("/api/"):
        return jsonify(error=getattr(e, "description", "Petición no válida.")), 400
    return "<h3>400 Solicitud no válida</h3>", 400


@app.errorhandler(404)
def not_found_handler(e):
    if request.path.startswith("/api/"):
        return jsonify(error="Recurso solicitado no encontrado."), 404
    return redirect(url_for("view_inicio"))


@app.errorhandler(500)
def internal_error_handler(e):
    app.logger.exception("Error interno del servidor")
    if request.path.startswith("/api/"):
        # Prevenir fuga de trazas o estructura interna de MySQL/RDS
        return jsonify(error="Ocurrió un error en el servidor procesando la solicitud. Verifique los registros del sistema."), 500
    return "<h3>500 Error interno del servidor</h3>", 500


# =========================================================================
# RUTAS DE INTERFAZ MONOLÍTICA (JINJA2 SSR)
# =========================================================================

@app.get("/")
def view_inicio():
    """Resumen general de facturación y cobranza."""
    facturas = db.list_facturas()
    clientes = db.list_clientes()
    servicios = db.list_servicios()

    # Formatear fechas para la vista
    for f in facturas:
        fec = str(f.get("fecha_emision", ""))
        f["fecha_emision_formateada"] = fec.split("T")[0] if "T" in fec else fec

    # Métricas financieras
    facturas_activas = [f for f in facturas if f.get("estado") != "CANCELADA"]
    total_facturado_val = sum(float(f.get("total", 0)) for f in facturas_activas)
    
    pagadas = [f for f in facturas if f.get("estado") in ("TIMBRADA", "Pagada")]
    total_cobrado_val = sum(float(f.get("total", 0)) for f in pagadas)

    pendientes = [f for f in facturas if f.get("estado") in ("PENDIENTE", "BORRADOR", "Pendiente")]
    total_por_cobrar_val = sum(float(f.get("total", 0)) for f in pendientes)

    porcentaje_cobro = 0
    if facturas_activas:
        porcentaje_cobro = round((len(pagadas) / len(facturas_activas)) * 100)

    return render_template(
        "inicio.html",
        active_page="inicio",
        page_title="Resumen general",
        page_eyebrow="CADA NÚMERO CUENTA UNA HISTORIA",
        page_caption="Una vista clara de tu negocio en AWS RDS, para seguir creciendo.",
        facturas=facturas,
        clientes=clientes,
        servicios=servicios,
        facturas_count=len(facturas),
        total_facturado=f"${total_facturado_val:,.2f} MXN",
        total_cobrado=f"${total_cobrado_val:,.2f} MXN",
        total_por_cobrar=f"${total_por_cobrar_val:,.2f} MXN",
        facturas_pagadas_count=len(pagadas),
        facturas_pendientes_count=len(pendientes),
        porcentaje_cobro=porcentaje_cobro
    )


@app.get("/diagnostico")
def view_diagnostico():
    """Panel de Supervisión de AWS RDS (8 tablas, 10 SPs) y DynamoDB."""
    rds_info = db.get_diagnostico()
    dynamo_info = dynamo.test_dynamodb_status()
    facturas = db.list_facturas()

    return render_template(
        "diagnostico.html",
        active_page="diagnostico",
        page_title="Diagnóstico RDS",
        page_eyebrow="SUPERVISIÓN DE INFRAESTRUCTURA",
        page_caption="Estado en tiempo real de AWS RDS (MySQL/MariaDB), 8 tablas SQL, 10 Stored Procedures y DynamoDB.",
        rds=rds_info,
        dynamo=dynamo_info,
        facturas_count=len(facturas)
    )


@app.get("/clientes")
def view_clientes():
    """Directorio y gestión CRUD de Clientes (Emisores y Receptores)."""
    clientes = db.list_clientes()
    facturas = db.list_facturas()

    return render_template(
        "clientes.html",
        active_page="clientes",
        page_title="Clientes",
        page_eyebrow="PERSONAS DETRÁS DE CADA PROYECTO",
        page_caption="Emisores y Receptores fiscales registrados en AWS RDS.",
        clientes=clientes,
        filtro_tipo="TODOS",
        facturas_count=len(facturas)
    )


@app.get("/servicios")
def view_servicios():
    """Catálogo de Servicios (+100) y asignación N:M de Características (+50)."""
    servicios = db.list_servicios()
    caracteristicas = db.list_caracteristicas()
    facturas = db.list_facturas()

    return render_template(
        "servicios.html",
        active_page="servicios",
        page_title="Servicios",
        page_eyebrow="TODO LO QUE OFRECES, ORGANIZADO",
        page_caption="Catálogo en AWS RDS con SKU, clave SAT y características asignadas.",
        servicios=servicios,
        caracteristicas=caracteristicas,
        facturas_count=len(facturas)
    )


@app.get("/facturas")
def view_facturas():
    """Listado, consulta completa y cancelación de facturas."""
    facturas = db.list_facturas()
    for f in facturas:
        fec = str(f.get("fecha_emision", ""))
        f["fecha_emision_formateada"] = fec.split("T")[0] if "T" in fec else fec

    return render_template(
        "facturas.html",
        active_page="facturas",
        page_title="Facturas",
        page_eyebrow="CADA FACTURA EN SU LUGAR",
        page_caption="Consulta de documentos fiscales y cancelación directa en AWS RDS.",
        facturas=facturas,
        facturas_count=len(facturas)
    )


@app.get("/facturas/nueva")
def view_factura_nueva():
    """Formulario transaccional de emisión de factura."""
    clientes = db.list_clientes()
    emisores = [c for c in clientes if c.get("tipo_persona") == "EMISOR"]
    receptores = [c for c in clientes if c.get("tipo_persona") == "RECEPTOR"]

    # Si no hay emisores explícitos, usar los disponibles
    if not emisores:
        emisores = clientes
    if not receptores:
        receptores = clientes

    servicios = db.list_servicios()
    facturas = db.list_facturas()
    default_folio = f"FAC-{datetime.datetime.now().year}-{str(len(facturas) + 1).zfill(4)}"
    today_date = datetime.date.today().isoformat()

    selected_receptor = request.args.get("cliente_id", type=int)
    selected_emisor = emisores[0]["cliente_id"] if emisores else None

    return render_template(
        "factura_nueva.html",
        active_page="facturas",
        page_title="Nueva Factura",
        page_eyebrow="EMISIÓN TRANSACCIONAL SAT",
        page_caption="Validación fiscal, generación de partidas, cálculo de impuestos y timbrado en RDS.",
        emisores=emisores,
        receptores=receptores,
        servicios=servicios,
        facturas_count=len(facturas),
        default_folio=default_folio,
        today_date=today_date,
        selected_emisor=selected_emisor,
        selected_receptor=selected_receptor
    )


# =========================================================================
# ENDPOINTS REST (JSON API / AJAX)
# =========================================================================

@app.get("/api/diagnostico")
def api_diagnostico():
    rds_info = db.get_diagnostico()
    dynamo_info = dynamo.test_dynamodb_status()
    return jsonify({"rds": rds_info, "dynamodb": dynamo_info})


@app.get("/api/clientes")
def get_clientes():
    tipo = sanitize_string(request.args.get("tipo_persona"), max_length=50) or None
    try:
        data = db.list_clientes(tipo_persona=tipo)
        return jsonify(data)
    except Exception as e:
        app.logger.exception("Error al listar clientes")
        return jsonify(error=f"No se pudieron consultar los clientes: {str(e)}"), 500


@app.post("/api/clientes")
def post_cliente():
    payload = request.get_json(silent=True) or {}
    rfc = payload.get("rfc")
    razon_social = payload.get("razon_social")
    regimen_fiscal = payload.get("regimen_fiscal", "601")
    codigo_postal = payload.get("codigo_postal", "00000")
    correo = payload.get("correo", "")
    tipo_persona = payload.get("tipo_persona", "RECEPTOR")

    if not rfc or not razon_social:
        return jsonify(error="El RFC y la Razón Social son campos requeridos."), 400

    try:
        cliente_id = db.alta_cliente(
            rfc=rfc,
            razon_social=razon_social,
            regimen_fiscal=regimen_fiscal,
            codigo_postal=codigo_postal,
            correo=correo,
            tipo_persona=tipo_persona
        )
        return jsonify(
            ok=True,
            mensaje="Cliente registrado exitosamente mediante sp_AltaCliente",
            cliente_id=cliente_id
        ), 201
    except ValueError as ve:
        return jsonify(error=str(ve)), 400
    except Exception as e:
        app.logger.exception("Error al crear cliente")
        return jsonify(error=f"No se pudo registrar el cliente: {str(e)}"), 500


@app.put("/api/clientes/<cliente_id>")
def put_cliente(cliente_id):
    payload = request.get_json(silent=True) or {}
    razon_social = payload.get("razon_social")
    regimen_fiscal = payload.get("regimen_fiscal")
    codigo_postal = payload.get("codigo_postal")
    correo = payload.get("correo")
    tipo_persona = payload.get("tipo_persona")

    if not razon_social or not tipo_persona:
        return jsonify(error="Completa la razón social y el tipo de persona."), 400

    try:
        updated = db.update_cliente(cliente_id, razon_social, regimen_fiscal, codigo_postal, correo, tipo_persona)
        if not updated:
            return jsonify(error="Cliente no encontrado."), 404
        return jsonify(ok=True, mensaje="Cliente actualizado correctamente.")
    except ValueError as ve:
        return jsonify(error=str(ve)), 400
    except Exception as e:
        app.logger.exception("Error al actualizar cliente")
        return jsonify(error=f"Error al actualizar cliente: {str(e)}"), 500


@app.delete("/api/clientes/<cliente_id>")
def del_cliente(cliente_id):
    try:
        deleted = db.delete_cliente(cliente_id)
        if not deleted:
            return jsonify(error="Cliente no encontrado o no se pudo eliminar."), 404
        return jsonify(ok=True, mensaje="Cliente eliminado.")
    except Exception as e:
        app.logger.exception("Error al eliminar cliente")
        return jsonify(error=f"No se pudo eliminar el cliente: {str(e)}"), 500


@app.get("/api/servicios")
def get_servicios():
    try:
        data = db.list_servicios()
        return jsonify(data)
    except Exception as e:
        app.logger.exception("Error al listar servicios")
        return jsonify(error=f"No se pudo consultar el catálogo de servicios: {str(e)}"), 500


@app.post("/api/servicios")
def post_servicio():
    payload = request.get_json(silent=True) or {}
    sku = payload.get("sku")
    descripcion = payload.get("descripcion")
    precio_base = payload.get("precio_base")
    clave_sat = payload.get("clave_sat")

    if not sku or not descripcion or precio_base is None:
        return jsonify(error="SKU, descripción y precio base son obligatorios."), 400

    try:
        s_id = db.crear_servicio(sku, descripcion, precio_base, clave_sat)
        return jsonify(
            ok=True,
            mensaje="Servicio registrado exitosamente mediante sp_CrearServicioCatalogos",
            servicio_id=s_id
        ), 201
    except ValueError as ve:
        return jsonify(error=str(ve)), 400
    except Exception as e:
        app.logger.exception("Error al crear servicio")
        return jsonify(error=f"No se pudo registrar el servicio: {str(e)}"), 500



@app.delete("/api/servicios/<servicio_id>")
def del_servicio(servicio_id):
    try:
        deleted = db.delete_servicio(servicio_id)
        if not deleted:
            return jsonify(error="Servicio no encontrado."), 404
        return jsonify(ok=True, mensaje="Servicio eliminado correctamente.")
    except Exception as e:
        app.logger.exception("Error al eliminar servicio")
        return jsonify(error=f"No se pudo eliminar el servicio: {str(e)}"), 500


@app.get("/api/caracteristicas")
def get_caracteristicas():
    try:
        data = db.list_caracteristicas()
        return jsonify(data)
    except Exception as e:
        app.logger.exception("Error al listar características")
        return jsonify(error=f"No se pudieron consultar las características: {str(e)}"), 500


@app.get("/api/servicios/<servicio_id>/caracteristicas")
def get_servicio_caracteristicas(servicio_id):
    try:
        data = db.get_servicio_caracteristicas(servicio_id)
        return jsonify(data)
    except Exception as e:
        app.logger.exception("Error al consultar características del servicio")
        return jsonify(error=f"Error al obtener características: {str(e)}"), 500


@app.post("/api/servicios/<servicio_id>/caracteristicas")
def post_asignar_caracteristica(servicio_id):
    payload = request.get_json(silent=True) or {}
    caracteristica_id = payload.get("caracteristica_id")
    valor_caracteristica = payload.get("valor_caracteristica", "")

    if not caracteristica_id:
        return jsonify(error="Debes seleccionar una característica a vincular."), 400

    try:
        db.asignar_caracteristica(servicio_id, caracteristica_id, valor_caracteristica)
        return jsonify(
            ok=True,
            mensaje="Característica asignada al servicio mediante sp_AsignarCaracteristica"
        ), 201
    except Exception as e:
        app.logger.exception("Error al asignar característica")
        return jsonify(error=f"No se pudo asignar la característica: {str(e)}"), 500


@app.delete("/api/servicios/<servicio_id>/caracteristicas/<caracteristica_id>")
def del_desasignar_caracteristica(servicio_id, caracteristica_id):
    try:
        deleted = db.desasignar_caracteristica(servicio_id, caracteristica_id)
        return jsonify(ok=True, mensaje="Característica desvinculada.")
    except Exception as e:
        app.logger.exception("Error al desvincular característica")
        return jsonify(error=f"No se pudo desvincular la característica: {str(e)}"), 500


@app.get("/api/impuestos")
def get_impuestos():
    try:
        data = db.list_impuestos()
        return jsonify(data)
    except Exception as e:
        app.logger.exception("Error al listar impuestos")
        return jsonify(error=f"No se pudo consultar el catálogo de impuestos: {str(e)}"), 500


@app.get("/api/facturas")
def get_facturas():
    try:
        data = db.list_facturas()
        return jsonify(data)
    except Exception as e:
        app.logger.exception("Error al listar facturas")
        return jsonify(error=f"No se pudieron consultar las facturas: {str(e)}"), 500


@app.get("/api/facturas/<factura_id>")
def get_factura(factura_id):
    try:
        factura = db.get_factura_completa(factura_id)
        if not factura:
            return jsonify(error="Factura no encontrada."), 404
        return jsonify(factura)
    except Exception as e:
        app.logger.exception("Error al consultar detalle de factura")
        return jsonify(error=f"No se pudo obtener la factura: {str(e)}"), 500


@app.post("/api/facturas")
def post_factura():
    """
    Flujo transaccional de emisión de factura:
    1. Idempotencia en DynamoDB (si se incluye encabezado Idempotency-Key)
    2. Validar emisor y receptor (sp_ValidarDatosFiscales)
    3. Crear folio y encabezado (sp_GenerarFolioFactura)
    4. Insertar cada partida (sp_InsertarPartida)
    5. Calcular totales e impuestos (sp_CalcularTotales)
    6. Timbrar y guardar UUID (sp_ActualizarUUID)
    7. Registrar evento en log de auditoría NoSQL (log_eventos_facturacion)
    """
    payload = request.get_json(silent=True) or {}
    idempotency_key = request.headers.get("Idempotency-Key") or payload.get("idempotency_key")

    if idempotency_key:
        cached = dynamo.check_idempotency(idempotency_key)
        if cached:
            cached_resp = json.loads(cached.get("response_payload", "{}"))
            return jsonify({
                "ok": True,
                "idempotente": True,
                "mensaje": "Factura recuperada de caché de idempotencia DynamoDB",
                **cached_resp
            }), 200

    emisor_id = payload.get("emisor_id")
    receptor_id = payload.get("receptor_id")
    partidas = payload.get("partidas") or []
    folio_personalizado = payload.get("folio")

    if not emisor_id or not receptor_id:
        return jsonify(error="Debes seleccionar tanto un Emisor como un Receptor válidos."), 400

    if not partidas:
        return jsonify(error="La factura debe tener al menos una partida de servicio."), 400

    try:
        factura_id, uuid_sat, folio = db.emitir_factura(
            emisor_id=emisor_id,
            receptor_id=receptor_id,
            partidas=partidas,
            folio_personalizado=folio_personalizado
        )

        response_data = {
            "factura_id": factura_id,
            "folio": folio,
            "uuid_sat": uuid_sat,
            "estado": "TIMBRADA"
        }

        if idempotency_key:
            dynamo.save_idempotency(idempotency_key, factura_id, status="COMPLETED", response_payload=response_data)

        dynamo.log_evento_facturacion(
            factura_id=factura_id,
            tipo_evento="EMISION_FACTURA",
            detalle={
                "folio": folio,
                "emisor_id": emisor_id,
                "receptor_id": receptor_id,
                "uuid_sat": uuid_sat,
                "partidas_count": len(partidas)
            }
        )

        return jsonify({
            "ok": True,
            "mensaje": "Factura emitida y timbrada exitosamente",
            **response_data
        }), 201

    except ValueError as ve:
        return jsonify(error=str(ve)), 400
    except Exception as e:
        app.logger.exception("Error durante la emisión de factura")
        return jsonify(error=f"Error en la transacción de emisión: {str(e)}"), 500


@app.put("/api/facturas/<factura_id>/cancelar")
def cancelar_factura_route(factura_id):
    """Cancela la factura llamando a sp_CancelarFactura y registra en DynamoDB."""
    try:
        ok = db.cancelar_factura(factura_id)
        if not ok:
            return jsonify(error="Factura no encontrada para cancelar."), 404

        dynamo.log_evento_facturacion(
            factura_id=factura_id,
            tipo_evento="CANCELACION_FACTURA",
            detalle={"motivo": "Cancelación solicitada por el usuario"}
        )

        return jsonify(ok=True, mensaje="Factura cancelada correctamente mediante sp_CancelarFactura.")
    except ValueError as ve:
        return jsonify(error=str(ve)), 400
    except Exception as e:
        app.logger.exception("Error al cancelar factura")
        return jsonify(error=f"No se pudo cancelar la factura: {str(e)}"), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Iniciando Folio Monolítico en http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
