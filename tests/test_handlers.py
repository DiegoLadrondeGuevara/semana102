"""Pruebas locales del contrato HTTP sin conexión a AWS."""

import importlib
import json
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ClientError(Exception):
    def __init__(self, code):
        self.response = {"Error": {"Code": code}}


class Key:
    def __init__(self, name):
        self.name = name

    def eq(self, value):
        return self.name, value


class FakeTable:
    def __init__(self):
        self.items = {}

    def put_item(self, Item, **kwargs):
        key = Item["tenant_id"], Item["alumno_id"]
        if key in self.items:
            raise ClientError("ConditionalCheckFailedException")
        self.items[key] = Item.copy()

    def get_item(self, Key):
        item = self.items.get((Key["tenant_id"], Key["alumno_id"]))
        return {"Item": item} if item else {}

    def update_item(self, Key, ExpressionAttributeValues, **kwargs):
        key = Key["tenant_id"], Key["alumno_id"]
        if key not in self.items:
            raise ClientError("ConditionalCheckFailedException")
        self.items[key]["alumno_datos"] = ExpressionAttributeValues[":datos"]
        return {"Attributes": self.items[key].copy()}

    def delete_item(self, Key, **kwargs):
        key = Key["tenant_id"], Key["alumno_id"]
        if key not in self.items:
            raise ClientError("ConditionalCheckFailedException")
        del self.items[key]

    def query(self, KeyConditionExpression, **kwargs):
        _, tenant_id = KeyConditionExpression
        found = [item for key, item in self.items.items() if key[0] == tenant_id]
        if "ExclusiveStartKey" in kwargs:
            return {"Items": found[1:]}
        if len(found) > 1:
            return {"Items": found[:1], "LastEvaluatedKey": {"alumno_id": found[0]["alumno_id"]}}
        return {"Items": found}


fake_table = FakeTable()
boto3 = types.ModuleType("boto3")
boto3.resource = lambda name: types.SimpleNamespace(Table=lambda table_name: fake_table)
boto3_dynamodb = types.ModuleType("boto3.dynamodb")
boto3_conditions = types.ModuleType("boto3.dynamodb.conditions")
boto3_conditions.Key = Key
botocore = types.ModuleType("botocore")
botocore_exceptions = types.ModuleType("botocore.exceptions")
botocore_exceptions.ClientError = ClientError
sys.modules.update({
    "boto3": boto3,
    "boto3.dynamodb": boto3_dynamodb,
    "boto3.dynamodb.conditions": boto3_conditions,
    "botocore": botocore,
    "botocore.exceptions": botocore_exceptions,
})


handlers = {name: importlib.import_module(name).lambda_handler for name in (
    "CrearAlumno", "ListarAlumnos", "BuscarAlumno", "ModificarAlumno", "EliminarAlumno"
)}


def call(name, body, as_string=True):
    event = {"body": json.dumps(body) if as_string else body}
    result = handlers[name](event, None)
    payload = json.loads(result["body"])
    assert result["statusCode"] == payload["statusCode"]
    return result["statusCode"], payload


class HandlerTests(unittest.TestCase):
    def setUp(self):
        fake_table.items.clear()
        self.key = {"tenant_id": "UTEC", "alumno_id": "2021077990"}

    def test_crud_and_list_pagination(self):
        self.assertEqual(call("CrearAlumno", {**self.key, "alumno_datos": {"nombre": "Juana"}})[0], 201)
        self.assertEqual(call("CrearAlumno", {**self.key, "alumno_datos": {"nombre": "Otra"}})[0], 409)
        call("CrearAlumno", {"tenant_id": "UTEC", "alumno_id": "2", "alumno_datos": {"nombre": "Ana"}}, False)
        status, listed = call("ListarAlumnos", {"tenant_id": "UTEC"})
        self.assertEqual((status, listed["num_reg"]), (200, 2))
        self.assertEqual(call("BuscarAlumno", self.key)[1]["alumno"]["alumno_datos"]["nombre"], "Juana")
        status, changed = call("ModificarAlumno", {**self.key, "alumno_datos": {"nombre": "Juana 2"}})
        self.assertEqual((status, changed["alumno"]["alumno_datos"]["nombre"]), (200, "Juana 2"))
        self.assertEqual(call("EliminarAlumno", self.key)[0], 200)
        self.assertEqual(call("BuscarAlumno", self.key)[0], 404)

    def test_validation_and_missing_records(self):
        self.assertEqual(call("CrearAlumno", {"tenant_id": "UTEC"})[0], 400)
        self.assertEqual(call("ModificarAlumno", {**self.key, "alumno_datos": {}})[0], 404)
        self.assertEqual(call("EliminarAlumno", self.key)[0], 404)
        result = handlers["ListarAlumnos"]({"body": "{broken"}, None)
        self.assertEqual(result["statusCode"], 400)

    def test_numeric_json_data(self):
        status, payload = call("CrearAlumno", {**self.key, "alumno_datos": {"promedio": 17.5}})
        self.assertEqual((status, payload["alumno"]["alumno_datos"]["promedio"]), (201, 17.5))


if __name__ == "__main__":
    unittest.main()
