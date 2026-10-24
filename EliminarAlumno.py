"""Elimina un alumno existente por su clave compuesta."""

from botocore.exceptions import ClientError

from common import ApiError, required_string, response, run, table


def lambda_handler(event, context):
    def action(body):
        tenant_id = required_string(body, "tenant_id")
        alumno_id = required_string(body, "alumno_id")
        try:
            table().delete_item(
                Key={"tenant_id": tenant_id, "alumno_id": alumno_id},
                ConditionExpression="attribute_exists(tenant_id) AND attribute_exists(alumno_id)",
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ApiError(404, "El alumno no existe") from exc
            raise
        return response(200, tenant_id=tenant_id, alumno_id=alumno_id, mensaje="Alumno eliminado")

    return run(event, action)
