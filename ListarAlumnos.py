"""Lista todos los alumnos de un tenant, incluyendo páginas adicionales."""

from boto3.dynamodb.conditions import Key

from common import required_string, response, run, table


def lambda_handler(event, context):
    def action(body):
        tenant_id = required_string(body, "tenant_id")
        db_table = table()
        alumnos = []
        kwargs = {"KeyConditionExpression": Key("tenant_id").eq(tenant_id)}
        while True:
            result = db_table.query(**kwargs)
            alumnos.extend(result.get("Items", []))
            if "LastEvaluatedKey" not in result:
                break
            kwargs["ExclusiveStartKey"] = result["LastEvaluatedKey"]
        return response(200, tenant_id=tenant_id, num_reg=len(alumnos), alumnos=alumnos)

    return run(event, action)
