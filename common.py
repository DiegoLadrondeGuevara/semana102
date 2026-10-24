"""Entrada, salida y validaciones compartidas por las cinco Lambdas."""

import json
import logging
import os
from decimal import Decimal

import boto3


class ApiError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code


def table():
    return boto3.resource("dynamodb").Table(os.environ.get("ALUMNOS_TABLE", "t_alumnos"))


def request_body(event):
    body = event.get("body") if isinstance(event, dict) else None
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ApiError(400, "El body debe ser JSON valido") from exc
    if not isinstance(body, dict):
        raise ApiError(400, "El body debe ser un objeto JSON")
    return body


def required_string(body, name):
    value = body.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ApiError(400, f"{name} debe ser un texto no vacio")
    return value


def required_data(body):
    value = body.get("alumno_datos")
    if not isinstance(value, dict):
        raise ApiError(400, "alumno_datos debe ser un objeto JSON")
    return value


def _json_default(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError(f"No se puede serializar {type(value).__name__}")


def response(status_code, **fields):
    payload = {"statusCode": status_code, **fields}
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(payload, ensure_ascii=False, default=_json_default),
    }


def run(event, action):
    try:
        return action(request_body(event))
    except ApiError as exc:
        return response(exc.status_code, error=str(exc))
    except Exception:
        logging.exception("Error al procesar la solicitud de alumnos")
        return response(500, error="Error interno al procesar la solicitud")
