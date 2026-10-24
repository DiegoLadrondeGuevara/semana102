"""Crea un alumno sin sobrescribir otro con la misma clave."""

from botocore.exceptions import ClientError

from common import ApiError, required_data, required_string, response, run, table


def lambda_handler(event, context):
    def action(body):
        tenant_id = required_string(body, "tenant_id")
        alumno_id = required_string(body, "alumno_id")
        alumno_datos = required_data(body)
        alumno = {
            "tenant_id": tenant_id,
            "alumno_id": alumno_id,
            "alumno_datos": alumno_datos,
        }
        try:
            table().put_item(
                Item=alumno,
                ConditionExpression="attribute_not_exists(tenant_id) AND attribute_not_exists(alumno_id)",
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ApiError(409, "El alumno ya existe") from exc
            raise
        return response(201, alumno=alumno)

    return run(event, action)
