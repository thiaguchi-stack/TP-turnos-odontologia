# Tasks

## 1. Schemas y capa de servicio

- [x] 1.1 Crear `backend/app/schemas/profesional.py` con `ProfesionalCreate`, `ProfesionalUpdate` y `ProfesionalRead` (`from_attributes=True`, `extra="forbid"`, `activo` booleano estricto, `nombre`/`apellido` no vacíos ≤100, `especialidad` opcional ≤100 y update con al menos un campo); verificar con `backend/tests/test_schemas_profesional.py` que los campos de lectura son solo `id`, `nombre`, `apellido`, `especialidad`, `activo` y que `activo="si"`, el campo extra `id`, el nombre vacío y el body vacío fallan.
- [x] 1.2 Agregar `ProfesionalNoEncontradoError` y `ProfesionalRechazadoError` a `backend/app/services/errores.py` con mensajes en español rioplatense; verificar con un test en `backend/tests/test_errores.py` que ambos exponen `motivo` y son instancias de `Exception`.
- [x] 1.3 Implementar `listar_activos` y `obtener_activo` en `backend/app/services/profesional_service.py`, filtrando `activo=true` y lanzando `ProfesionalNoEncontradoError` para id inexistente o inactivo; verificar con `backend/tests/test_profesional_service.py` que el listado excluye al profesional inactivo de la fixture `datos` y que el detalle de inactivo/inexistente falla.
- [x] 1.4 Implementar `crear` en el servicio con default `activo=true` y persistencia del payload validado; verificar con test unitario que el profesional queda activo y con `nombre`/`apellido`/`especialidad` ficticios correctos.
- [x] 1.5 Implementar `actualizar` en el servicio para `nombre`, `apellido`, `especialidad` y `activo`, permitiendo activar y desactivar sin borrar; verificar con tests unitarios la edición con `activo=false`, la reactivación con `activo=true` y el rechazo de id inexistente.
- [x] 1.6 Implementar `desactivar` en el servicio como baja lógica idempotente, sin `db.delete` y sin tocar turnos ni usuarios; verificar con tests unitarios que un profesional con turnos sigue persistido con `activo=false`, que uno sin turnos también se desactiva, que una segunda llamada no duplica registros y que un id inexistente falla.

## 2. Routers delgados y cableado

- [x] 2.1 Crear `backend/app/routers/profesionales.py` con `GET /profesionales` y `GET /profesionales/{id}` públicos, sin más lógica que la delegación al servicio y el mapeo a 404; verificar con `backend/tests/test_profesionales_api.py` que el listado sin `Authorization` devuelve 200 y solo el activo, que el detalle activo devuelve 200, que inactivo/inexistente devuelven 404 y que las respuestas contienen únicamente los cinco campos permitidos y ningún dato de pacientes o credenciales.
- [x] 2.2 Agregar `POST /profesionales` (201), `PUT /profesionales/{id}` (200) y `DELETE /profesionales/{id}` (200) con `Depends(require_role(RolUsuario.ADMIN))`, traduciendo errores de dominio a 400/404; verificar con `TestClient` el CRUD admin completo: alta con `activo=true` por omisión, edición y reactivación, baja con turnos/sin turnos/idempotente, 400 por nombre vacío/`activo="si"`/campo extra/body vacío y 404 por id inexistente.
- [x] 2.3 Registrar el router en `backend/app/main.py` con `app.include_router(profesionales.router)`; verificar que `app.openapi()` incluye las cinco rutas y que `backend/tests/test_health.py` sigue pasando.

## 3. Auth, RBAC y privacidad

- [x] 3.1 Verificar con `TestClient` que `POST /profesionales`, `PUT /profesionales/{id}` y `DELETE /profesionales/{id}` sin header `Authorization` responden 401 y no mutan el catálogo; cubre el escenario RBAC "Sin token...".
- [x] 3.2 Verificar con `TestClient` que un JWT vencido y otro firmado con clave distinta responden 401 en una ruta de administración de profesionales, reutilizando el patrón de `backend/tests/test_auth_api.py`; cubre "Token vencido o firma inválida...".
- [x] 3.3 Verificar con `TestClient` que un odontólogo autenticado recibe 403 al crear, editar y bajar profesionales, y que la DB no registra cambios; cubre "Odontólogo no puede administrar el catálogo" (RN-AU-03).
- [x] 3.4 Verificar con `caplog` y `TestClient` que las respuestas de catálogo no contienen `password_hash`, contraseñas ni datos de pacientes, y que los logs de esas requests tampoco; cubre "Campos exactos...", "El catálogo público no filtra..." y RN-DATOS-01/02/03.

## 4. Verificación integral

- [x] 4.1 Ejecutar la suite completa (`pytest` en `backend/`, incluidos los tests nuevos de servicio y API) y verificar que todos los tests pasan sin regresiones en auth ni turnos.
- [x] 4.2 Revisar la cobertura de los 7 requirements / 22 escenarios del delta `specs/profesionales/spec.md` contra los tests anteriores y ejecutar `openspec validate c-04-profesionales-api --strict`, verificando salida sin observaciones.

## Workflow follow-up

- Marcar `[x]` C-04 en `CHANGES.md` y archivar el change con sync de specs recién después de la revisión y con pedido explícito del usuario.
