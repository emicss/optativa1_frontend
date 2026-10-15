import os
import time
import json
import logging
from datetime import datetime
import requests
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN", "")
TABLE_IDEMPOTENCIA = os.environ.get("DYNAMODB_TABLE_IDEMPOTENCIA", "facturacion_idempotencia")
TABLE_LOGS = os.environ.get("DYNAMODB_TABLE_LOGS", "log_eventos_facturacion")
DYNAMODB_API_GATEWAY = os.environ.get("DYNAMODB_API_GATEWAY", "").rstrip("/")


def get_dynamodb_resource():
    """Obtiene el recurso DynamoDB soportando AWS Academy Learner Lab (Session Token)."""
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        return boto3.resource("dynamodb", region_name=AWS_REGION)

    kwargs = {
        "region_name": AWS_REGION,
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY
    }
    if AWS_SESSION_TOKEN:
        kwargs["aws_session_token"] = AWS_SESSION_TOKEN

    return boto3.resource("dynamodb", **kwargs)


def test_dynamodb_status():
    """
    Prueba la disponibilidad de DynamoDB:
    Prioriza la conexión serverless a través de API Gateway + Lambda.
    Fallback a Boto3 directo si no hay API Gateway configurado.
    """
    if DYNAMODB_API_GATEWAY:
        try:
            r = requests.get(f"{DYNAMODB_API_GATEWAY}/status", timeout=4)
            if r.status_code == 200:
                data = r.json()
                tables = data.get("tables", {})
                idemp_exists = tables.get(TABLE_IDEMPOTENCIA, True)
                logs_exists = tables.get(TABLE_LOGS, True)
                return {
                    "status": "ok" if (idemp_exists and logs_exists) else "parcial",
                    "connected": True,
                    "provider": "AWS API Gateway + Lambda",
                    "endpoint": DYNAMODB_API_GATEWAY,
                    "region": AWS_REGION,
                    "tablas_encontradas": list(tables.keys()),
                    "idempotencia_table": {"nombre": TABLE_IDEMPOTENCIA, "activa": idemp_exists},
                    "logs_table": {"nombre": TABLE_LOGS, "activa": logs_exists}
                }
            else:
                return {
                    "status": "error",
                    "connected": False,
                    "provider": "AWS API Gateway + Lambda",
                    "endpoint": DYNAMODB_API_GATEWAY,
                    "error": f"API Gateway HTTP {r.status_code}: {r.text}",
                    "idempotencia_table": {"nombre": TABLE_IDEMPOTENCIA, "activa": False},
                    "logs_table": {"nombre": TABLE_LOGS, "activa": False}
                }
        except Exception as e:
            return {
                "status": "desconectado",
                "connected": False,
                "provider": "AWS API Gateway + Lambda",
                "endpoint": DYNAMODB_API_GATEWAY,
                "error": str(e),
                "idempotencia_table": {"nombre": TABLE_IDEMPOTENCIA, "activa": False},
                "logs_table": {"nombre": TABLE_LOGS, "activa": False}
            }

    try:
        dynamo = get_dynamodb_resource()
        client = dynamo.meta.client
        tables = client.list_tables().get("TableNames", [])

        idemp_exists = TABLE_IDEMPOTENCIA in tables
        logs_exists = TABLE_LOGS in tables

        return {
            "status": "ok" if (idemp_exists and logs_exists) else "parcial",
            "connected": True,
            "provider": "AWS SDK Boto3 Directo",
            "region": AWS_REGION,
            "tablas_encontradas": tables,
            "idempotencia_table": {"nombre": TABLE_IDEMPOTENCIA, "activa": idemp_exists},
            "logs_table": {"nombre": TABLE_LOGS, "activa": logs_exists}
        }
    except (NoCredentialsError, ClientError) as e:
        return {
            "status": "desconectado",
            "connected": False,
            "provider": "AWS SDK Boto3 Directo",
            "region": AWS_REGION,
            "error": str(e),
            "idempotencia_table": {"nombre": TABLE_IDEMPOTENCIA, "activa": False},
            "logs_table": {"nombre": TABLE_LOGS, "activa": False}
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "provider": "AWS SDK Boto3 Directo",
            "region": AWS_REGION,
            "error": str(e),
            "idempotencia_table": {"nombre": TABLE_IDEMPOTENCIA, "activa": False},
            "logs_table": {"nombre": TABLE_LOGS, "activa": False}
        }


def check_idempotency(idempotency_key):
    """
    Busca si existe una clave de idempotencia procesada en DynamoDB.
    """
    if not idempotency_key:
        return None

    if DYNAMODB_API_GATEWAY:
        try:
            r = requests.get(f"{DYNAMODB_API_GATEWAY}/idempotencia/{idempotency_key}", timeout=3)
            if r.status_code == 200:
                data = r.json()
                return data.get("item")
            return None
        except Exception as e:
            logger.warning(f"API Gateway check idempotency bypassed: {e}")
            return None

    try:
        dynamo = get_dynamodb_resource()
        table = dynamo.Table(TABLE_IDEMPOTENCIA)
        response = table.get_item(Key={"idempotency_key": str(idempotency_key)})
        return response.get("Item")
    except Exception as e:
        logger.warning(f"DynamoDB idempotency check bypassed: {e}")
        return None


def save_idempotency(idempotency_key, factura_id, status="COMPLETED", response_payload=None, ttl_hours=24):
    """
    Guarda el registro de idempotencia.
    """
    if not idempotency_key:
        return

    if DYNAMODB_API_GATEWAY:
        try:
            payload = {
                "idempotency_key": str(idempotency_key),
                "factura_id": str(factura_id) if factura_id else "",
                "status": status,
                "response_payload": response_payload or {}
            }
            requests.post(f"{DYNAMODB_API_GATEWAY}/idempotencia", json=payload, timeout=3)
            return
        except Exception as e:
            logger.warning(f"API Gateway save idempotency bypassed: {e}")
            return

    try:
        dynamo = get_dynamodb_resource()
        table = dynamo.Table(TABLE_IDEMPOTENCIA)
        now = int(time.time())
        item = {
            "idempotency_key": str(idempotency_key),
            "status": status,
            "factura_id": str(factura_id) if factura_id else None,
            "response_payload": json.dumps(response_payload) if response_payload else "{}",
            "created_at": datetime.utcnow().isoformat(),
            "ttl": now + (ttl_hours * 3600)
        }
        table.put_item(Item=item)
    except Exception as e:
        logger.warning(f"DynamoDB save idempotency bypassed: {e}")


def log_evento_facturacion(factura_id, tipo_evento, detalle):
    """
    Registra eventos en la tabla log_eventos_facturacion.
    """
    if not factura_id:
        return

    if DYNAMODB_API_GATEWAY:
        try:
            payload = {
                "factura_id": str(factura_id),
                "tipo_evento": tipo_evento,
                "detalle": detalle
            }
            requests.post(f"{DYNAMODB_API_GATEWAY}/eventos", json=payload, timeout=3)
            return
        except Exception as e:
            logger.warning(f"API Gateway log bypassed: {e}")
            return

    try:
        dynamo = get_dynamodb_resource()
        table = dynamo.Table(TABLE_LOGS)
        timestamp = datetime.utcnow().isoformat()
        item = {
            "factura_id": str(factura_id),
            "timestamp": timestamp,
            "tipo_evento": tipo_evento,
            "detalle": json.dumps(detalle) if isinstance(detalle, (dict, list)) else str(detalle)
        }
        table.put_item(Item=item)
    except Exception as e:
        logger.warning(f"DynamoDB log bypassed: {e}")
