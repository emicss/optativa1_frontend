# Folio · Sistema de Facturación Monolítico (Flask + Jinja2 + AWS RDS & DynamoDB)

Aplicación monolítica de facturación desarrollada en **Python (Flask) y Jinja2**, conservando al 100% el diseño visual y conectada a una base de datos relacional en **AWS RDS (MySQL/MariaDB)** y **AWS DynamoDB**.

---

## 1. Arquitectura del Proyecto

* **Backend y Vistas:** Python 3 + Flask 3 + Jinja2 (Renderizado en Servidor - SSR).
* **Base de Datos Principal (AWS RDS):** 8 Tablas SQL relacionales y 10 Stored Procedures para transacciones fiscales.
* **Base de Datos NoSQL (AWS DynamoDB):** Idempotencia de emisión (`facturacion_idempotencia`) y registro de auditoría (`log_eventos_facturacion`).
* **Estilos:** CSS puro en `static/css/` basado en la identidad visual del proyecto (tonos *sage, sand, lilac*).
* **Interactividad:** JavaScript vanilla en `static/js/app.js` (modales nativos `<dialog>`, adición dinámica de partidas, cálculo de IVA y llamadas asíncronas).

---

## 2. Puesta en Marcha

### Requisitos
* Python 3.10+ (probado en Python 3.14).

### Instalación de Dependencias

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Variables de Entorno (`.env`)

Copia el archivo de ejemplo y configura tus credenciales de AWS:

```sh
cp .env.example .env
```

Configura en `.env`:
* `DB_HOST`: Endpoint de la instancia AWS RDS (o `localhost` si se usa túnel SSH/local).
* `DB_USER`: Usuario maestro de la base de datos.
* `DB_PASSWORD`: Contraseña de la base de datos.
* `DB_NAME`: Nombre de la base de datos (por defecto `facturacion_db`).
* `DB_PORT`: Puerto MySQL (3306).
* `AWS_REGION`: Región de DynamoDB (por defecto `us-east-1`).
* `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`: Credenciales con permisos para DynamoDB.

### Ejecución del Monolito

```sh
python app.py
```

Abre en tu navegador: **http://127.0.0.1:5000**

---

## 3. Módulos y Rutas de la Aplicación

| Ruta | Descripción |
| :--- | :--- |
| `/` | **Resumen General:** Métricas financieras de cobro, total facturado y documentos recientes. |
| `/diagnostico` | **Panel de Diagnóstico RDS:** Supervisión de conexión, conteo de las 8 tablas SQL, estado de los 10 Stored Procedures y DynamoDB. |
| `/clientes` | **Directorio de Clientes:** Filtro de Emisores y Receptores, detalle fiscal y alta mediante `sp_AltaCliente`. |
| `/servicios` | **Catálogo de Servicios:** Catálogo con SKU, Clave SAT y asignación de características N:M mediante `sp_AsignarCaracteristica`. |
| `/facturas` | **Facturas:** Consulta de facturas completas (`sp_ConsultarFacturaCompleta`) y cancelación fiscal (`sp_CancelarFactura`). |
| `/facturas/nueva` | **Emisión de Factura:** Selección de Emisor, Receptor, partidas dinámicas, cálculo de impuestos y timbrado con UUID SAT. |

---

## 4. Endpoints de la API REST (`/api/*`)

* `GET /api/diagnostico`: Inspección en tiempo real de RDS y DynamoDB.
* `GET, POST, PUT, DELETE /api/clientes`: CRUD de clientes (prioriza `sp_AltaCliente`).
* `GET, POST, DELETE /api/servicios`: Catálogo de servicios (prioriza `sp_CrearServicioCatalogos`).
* `GET /api/caracteristicas`: Catálogo de 50 características.
* `GET, POST, DELETE /api/servicios/<id>/caracteristicas`: Relación N:M (prioriza `sp_AsignarCaracteristica`).
* `GET /api/impuestos`: Catálogo de impuestos (IVA, ISR, IEPS).
* `GET, POST /api/facturas`: Emisión transaccional completa con idempotencia DynamoDB.
* `GET /api/facturas/<id>`: Detalle completo de factura (`sp_ConsultarFacturaCompleta`).
* `PUT /api/facturas/<id>/cancelar`: Cancelación de factura (`sp_CancelarFactura`).

---

## 5. Verificación y Pruebas

Para verificar las pruebas de cálculo de facturación:

```sh
npm test
```
