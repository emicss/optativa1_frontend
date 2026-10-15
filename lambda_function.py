import json
import os
import time
from datetime import datetime
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))
table_idemp = dynamodb.Table("facturacion_idempotencia")
table_logs = dynamodb.Table("log_eventos_facturacion")

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*"
}

def json_serial(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def respuesta(status, datos):
    return {
        "statusCode": status,
        "headers": HEADERS,
        "body": json.dumps(datos, default=json_serial)
    }

def lambda_handler(event, context):
    metodo = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "GET")
    ruta = event.get("path") or event.get("rawPath", "/")

    if metodo == "OPTIONS":
        return respuesta(200, {"ok": True})

    try:
        # 1. Health check
        if ruta.endswith("/status"):
            client = dynamodb.meta.client
            tablas = client.list_tables().get("TableNames", [])
            return respuesta(200, {
                "ok": True,
                "status": "connected",
                "tables": {
                    "facturacion_idempotencia": "facturacion_idempotencia" in tablas,
                    "log_eventos_facturacion": "log_eventos_facturacion" in tablas
                }
            })

        # 2. Consultar Idempotencia
        if metodo == "GET" and "/idempotencia" in ruta:
            key = ruta.split("/")[-1]
            if not key or key == "idempotencia":
                key = (event.get("queryStringParameters") or {}).get("key", "")
            if not key:
                return respuesta(400, {"error": "Falta key"})
            item = table_idemp.get_item(Key={"idempotency_key": str(key)}).get("Item")
            if not item:
                return respuesta(404, {"found": False})
            return respuesta(200, {"found": True, "item": item})

        # 3. Guardar Idempotencia
        if metodo == "POST" and ruta.endswith("/idempotencia"):
            body = json.loads(event.get("body") or "{}")
            key = body.get("idempotency_key")
            if not key:
                return respuesta(400, {"error": "Falta idempotency_key"})
            item = {
                "idempotency_key": str(key),
                "status": body.get("status", "COMPLETED"),
                "factura_id": str(body.get("factura_id", "")),
                "response_payload": json.dumps(body.get("response_payload", {})),
                "created_at": datetime.utcnow().isoformat(),
                "ttl": int(time.time()) + 86400
            }
            table_idemp.put_item(Item=item)
            return respuesta(201, {"ok": True, "mensaje": "Idempotencia guardada"})

        # 4. Registrar Evento de Auditoria
        if metodo == "POST" and ruta.endswith("/eventos"):
            body = json.loads(event.get("body") or "{}")
            fid = str(body.get("factura_id", "")).strip()
            if not fid:
                return respuesta(400, {"error": "Falta factura_id"})
            item = {
                "factura_id": fid,
                "timestamp": int(time.time() * 1000),
                "fecha_iso": datetime.utcnow().isoformat() + "Z",
                "tipo_evento": body.get("tipo_evento", "GENERAL"),
                "detalle": json.dumps(body.get("detalle", {})) if isinstance(body.get("detalle"), (dict, list)) else str(body.get("detalle", ""))
            }
            table_logs.put_item(Item=item)
            return respuesta(201, {"ok": True, "mensaje": "Evento registrado en DynamoDB"})

        # 5. Consultar Auditoria de Factura
        if metodo == "GET" and "/eventos" in ruta:
            fid = ruta.split("/")[-1]
            if not fid or fid == "eventos":
                fid = (event.get("queryStringParameters") or {}).get("factura_id", "")
            if not fid:
                return respuesta(400, {"error": "Falta factura_id"})
            items = table_logs.query(
                KeyConditionExpression=Key("factura_id").eq(str(fid))
            ).get("Items", [])
            return respuesta(200, {"factura_id": fid, "eventos": items})

        return respuesta(404, {"error": f"Ruta no encontrada: {metodo} {ruta}"})

    except Exception as e:
        return respuesta(500, {"error": str(e)})
