# API de alumnos — Taller 2, semana 10

Cinco Lambdas Python 3.12 desplegadas en **un mismo API Gateway REST** mediante Serverless Framework.

## Antes de desplegar

1. En AWS Academy, inicia el laboratorio y configura las credenciales temporales de AWS en la MV. Comprueba el acceso con `aws sts get-caller-identity`.
2. Confirma que existe la tabla DynamoDB `t_alumnos` en la región de despliegue, con clave de partición **`tenant_id` (String)** y clave de ordenación **`alumno_id` (String)**. El `serverless.yml` **no crea la tabla**. Si tu tabla tiene otro nombre, define `ALUMNOS_TABLE` antes de desplegar. Si sus claves son distintas, tendrás que ajustar el código.
3. Confirma que la cuenta AWS `904208419583` tiene el rol IAM `LabRole` con permisos de ejecución para DynamoDB y CloudWatch Logs. Las credenciales temporales usadas por Serverless deben permitir crear Lambda y API Gateway. El YAML usa `arn:aws:iam::904208419583:role/LabRole` y la organización Serverless `diegoladrondeguevara`.
4. Usa Serverless Framework **v3**: compruébalo con `serverless --version` o instálalo con `sudo npm install -g serverless@3`. Si tu instalación requiere login, ejecuta `serverless login`.

## Despliegue en Ubuntu/MV

```bash
git clone https://github.com/DiegoLadrondeGuevara/semana102.git
cd semana102
serverless deploy
```

La configuración usa `us-east-1` y stage `dev`, como el ejemplo del profesor. Puedes cambiar la región con `serverless deploy --region <region>` y el stage con `--stage <stage>`. Para otro nombre de tabla: `export ALUMNOS_TABLE=nombre_real` antes del deploy. Después de desplegar, copia la URL base de los endpoints que imprime Serverless, hasta `/dev`, por ejemplo `https://abc123.execute-api.us-east-1.amazonaws.com/dev`.

## Postman

Importa `API Alumnos.postman_collection.json`. La variable `baseUrl` ya contiene la URL del despliegue `dev`: `https://zv2cnq3ai5.execute-api.us-east-1.amazonaws.com/dev`. Si vuelves a desplegar y cambia la URL, actualiza esa variable, sin `/alumnos/...` al final. Las cinco peticiones envían **Body → raw → JSON** y `Content-Type: application/json`. Ejecútalas en orden con el Collection Runner: Crear, Listar, Buscar, Modificar y Eliminar. Crear genera un `alumno_id` de prueba único (`TEST-...`), las peticiones siguientes reutilizan ese ID y Eliminar limpia el registro. Cada petición incluye pruebas de respuesta.

| Ruta POST | Body requerido | Resultado |
| --- | --- | --- |
| `/alumnos/crear` | `tenant_id`, `alumno_id`, `alumno_datos` | `201`, alumno creado |
| `/alumnos/listar` | `tenant_id` | `200`, `num_reg` y `alumnos` |
| `/alumnos/buscar` | `tenant_id`, `alumno_id` | `200`, alumno; `404` si no existe |
| `/alumnos/modificar` | `tenant_id`, `alumno_id`, `alumno_datos` | `200`, alumno actualizado; `404` si no existe |
| `/alumnos/eliminar` | `tenant_id`, `alumno_id` | `200`; `404` si no existe |

`ModificarAlumno` reemplaza **todo** el objeto `alumno_datos`; envía todos los campos que deseas conservar. La creación no sobrescribe un alumno existente. Listar consulta todas las páginas de DynamoDB para el `tenant_id` indicado.

Los ejemplos originales del docente no incluyen validación de tokens ni authorizer en API Gateway. Esta versión mantiene las rutas sin autenticación para reproducir el flujo de Postman del taller. Las credenciales AWS se usan para **desplegar** y el rol `LabRole` da permisos a las Lambdas; ninguna de esas credenciales se envía en Postman. Si el curso exige un token para estas rutas, hará falta especificar el emisor y el mecanismo de validación antes de habilitarlo.
