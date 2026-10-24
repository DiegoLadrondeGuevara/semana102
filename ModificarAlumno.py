"""Reemplaza alumno_datos en un alumno existente."""

from botocore.exceptions import ClientError

from common import ApiError, required_data, required_string, response, run, table


def lambda_handler(event, context):
    def action(body):
        tenant_id = required_string(body, "tenant_id")
        alumno_id = required_string(body, "alumno_id")
        alumno_datos = required_data(body)
        try:
            result = table().update_item(
                Key={"tenant_id": tenant_id, "alumno_id": alumno_id},
                UpdateExpression="SET alumno_datos = :datos",
                ConditionExpression="attribute_exists(tenant_id) AND attribute_exists(alumno_id)",
                ExpressionAttributeValues={":datos": alumno_datos},
                ReturnValues="ALL_NEW",
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ApiError(404, "El alumno no existe") from exc
            raise
        return response(200, alumno=result["Attributes"])

    return run(event, action)
