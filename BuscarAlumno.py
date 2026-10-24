"""Busca un alumno por tenant_id y alumno_id."""

from common import required_string, response, run, table


def lambda_handler(event, context):
    def action(body):
        tenant_id = required_string(body, "tenant_id")
        alumno_id = required_string(body, "alumno_id")
        result = table().get_item(Key={"tenant_id": tenant_id, "alumno_id": alumno_id})
        alumno = result.get("Item")
        if alumno is None:
            return response(404, error="El alumno no existe")
        return response(200, alumno=alumno)

    return run(event, action)
