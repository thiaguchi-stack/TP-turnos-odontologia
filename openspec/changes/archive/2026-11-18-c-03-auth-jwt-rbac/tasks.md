# Tasks

## 1. Gate de gobernanza, dependencias, modelos y schemas

- [x] 1.1 Obtener la aprobación humana del gate **CRITICO** de C-03 y resolver los supuestos `SU-HASH-LEGADO` y `SU-RATELIMIT` de `design.md` antes de cualquier implementación; verificación: existe un registro de aprobación/decisión en `docs/evidencias/` y las tareas 2.1 a 5.3 NO se ejecutan sin ese registro (`AGENTS.md:124`, `CHANGES.md:181`)
- [x] 1.2 Declarar las dependencias de hashing/JWT (`passlib`, `bcrypt` y la librería de JWT aprobada) en `backend/pyproject.toml`, respetando lo resuelto en 1.1; verificación: `backend\.venv\Scripts\python.exe -c "import passlib, bcrypt, jwt"` termina sin error y `pip check` no reporta conflictos
- [x] 1.3 Reutilizar el modelo `Usuario` de C-02 sin agregar tablas ni columnas nuevas; verificación: `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_usuario.py backend\tests\test_models.py -q` en verde y `git diff -- backend/app/models/` sin cambios de esquema
- [x] 1.4 Definir los schemas Pydantic de request/response de auth (`TokenRead`, `UsuarioRead`, creación de usuario) con campos explícitos; verificación: el test unitario `backend\tests\test_schemas_auth.py::test_usuario_read_no_expone_password_hash` pasa y asevera `"password_hash" not in UsuarioRead.model_fields` (RN-AU-04)
- [x] 1.5 Leer `SECRET_KEY` y `TOKEN_EXPIRE_MIN` desde `Settings`, alinear el default de expiración a 480 minutos según la KB (o registrar la aprobación del desvío en el gate) y mantener los secretos fuera del repo; verificación: test de configuración con `monkeypatch` que cambia ambas variables, comprueba que el módulo de seguridad toma los nuevos valores y asevera `Settings().token_expire_min == 480` salvo desvío aprobado (`08_arquitectura_propuesta.md:46,50-56`; código actual en `backend/app/core/config.py:12`)

## 2. Seguridad (core)

- [x] 2.1 Implementar el `CryptContext` con bcrypt como esquema activo y conservar la verificación del hash PBKDF2 versionado de C-02 según lo aprobado en 1.1; verificación: `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_security.py -q` en verde, más un test que verifica la contraseña del admin sembrado y comprueba que el hash nuevo NO contiene la contraseña en claro (RN-AU-04, `backend/app/core/security.py:7-9`)
- [x] 2.2 Crear y decodificar el JWT con `sub`, `rol`, `profesional_id` y `exp` usando `SECRET_KEY` y `TOKEN_EXPIRE_MIN`; verificación: test unitario `backend\tests\test_auth_service.py::test_token_claims_y_expiracion` decodifica el token y asevera los cuatro claims; un token con `exp` vencido produce error que el router mapea a 401 (escenario "Token expirado")
- [x] 2.3 Declarar `OAuth2PasswordBearer` y usar `OAuth2PasswordRequestForm` en el login; verificación: el esquema Bearer aparece en el OpenAPI generado y el test `backend\tests\test_auth_api.py::test_login_form_urlencoded` envía `username`/`password` como formulario y obtiene 200 (apoyo técnico: doc FastAPI 0.110.3 en `docs/evidencias/mcp-context-c03.md`)

## 3. Servicios de auth (DD-07: la decisión de negocio acá, no en routers)

- [x] 3.1 `auth_service.autenticar` busca el usuario, verifica el hash y rechaza credenciales inválidas con un único error genérico; verificación: `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_auth_service.py -k "credenciales" -q` con casos de contraseña incorrecta y usuario inexistente que devuelven el mismo mensaje y ningún token (escenario "Contraseña incorrecta", RN-AU-01/04)
- [x] 3.2 `get_current_user` resuelve el usuario desde la DB en cada request y rechaza usuarios inactivos; verificación: test unitario que desactiva un usuario y comprueba que la resolución falla con 401 vía `TestClient` (escenario "Acceso sin token" y "Token expirado")
- [x] 3.3 `require_role("admin")` y `require_odontologo_own` deciden el acceso por rol y por `profesional_id`; verificación: `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_auth_service.py -k "rbac" -q` con aserciones de admin permitido, odontólogo rechazado para usuarios y odontólogo rechazado para `profesional_id` ajeno (RN-AU-02/03)
- [x] 3.4 Limitar intentos fallidos de login a 5 por 60 s por IP + email según 1.1; verificación: `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_auth_service.py -k "rate_limit" -q` simula 5 fallos y un sexto intento (incluso con contraseña correcta) y asevera error 429 sin `access_token` (escenario "Sexto intento fallido", `CHANGES.md:177`)

## 4. Routers delgados (solo exponen dependencias y llaman al servicio)

- [x] 4.1 `POST /auth/login`: el router solo delega en `auth_service`; verificación con `TestClient`: credenciales válidas → 200 con `access_token` y JWT decodificado con los cuatro claims y sin `password_hash` (escenarios "Login de admin" y "Login de odontólogo"), contraseña incorrecta → 401 sin token, sexto intento → 429; la no filtración en logs se comprueba en 5.3
- [x] 4.2 `GET /auth/me`: verificación con `TestClient`: token vigente → 200 con `id`, `email`, `rol`, `profesional_id` y aserción explícita `"password_hash" not in respuesta.json()`; sin token → 401; token expirado → 401 (escenarios "Consulta del usuario autenticado", "Acceso sin token", "Token expirado")
- [x] 4.3 CRUD de usuarios del sistema solo admin: verificación con `TestClient`: admin → 201 con usuario persistido y sin `password_hash` en la respuesta; odontólogo → 403 y ningún usuario creado (escenarios "Admin crea un usuario" y "Odontólogo intenta crear un usuario", RN-AU-03)
- [x] 4.4 Aplicar `require_odontologo_own` al acceso a turnos sin implementar el CRUD de C-08: verificación con `TestClient` sobre un endpoint de prueba definido en la suite: odontólogo sobre su `profesional_id` → 200 solo con sus turnos; sobre otro `profesional_id` → 403 sin filas (escenarios "Odontólogo consulta sus propios turnos" y "Odontólogo intenta consultar turnos de otro profesional", RN-AU-02)
- [x] 4.5 Montar el router de auth en `app/main.py` sin middleware global de autenticación; verificación: `GET /api/health` sigue respondiendo 200 sin token y el OpenAPI expone `/auth/login` y `/auth/me` (`03_actores_y_roles.md:22-29`)

## 5. Tests de integración y regresión

- [x] 5.1 Ejecutar la suite completa: `backend\.venv\Scripts\python.exe -m pytest backend\tests -q`; verificación: todos los tests pasan, incluidos los ya existentes de C-01/C-02 y del change archivado de turnos, sin regresiones de 401/403/429
- [x] 5.2 Verificar la no protección de las rutas públicas con un test de regresión en `backend/tests/test_auth_api.py`: (a) recrear un `TestClient` sobre la app y aseverar que ninguna ruta registrada bajo `/turnos/online` lleva dependencia de autenticación; (b) montar un router de prueba **solo en la suite** con `GET /turnos/online/disponibles` y `POST /turnos/online` sin JWT, y aseverar 200 y 400 respectivamente — nunca 401 — para el caso con `estado` inyectado; verificación: `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_auth_api.py -k "publico" -q` (escenarios "Consulta pública de franjas sin token" y "Reserva pública no permite elegir estado", RN-AU-01/RN-DATOS-02/RN-TU-04; los endpoints reales se revalidan en C-09)
- [x] 5.3 Usar solo datos ficticios en seeds y fixtures de auth y verificar que ningún log filtra contraseñas ni hashes; verificación: `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_auth_api.py -k "sin_filtracion" -q` usa `caplog` en un login fallido (401) y uno válido (200) y asevera que ni la contraseña de prueba ni `password_hash` aparecen en `caplog.text`, más revisión de `backend/tests/conftest.py` sin credenciales reales (RN-DATOS-03, RN-AU-04, `AGENTS.md:99`)

## Workflow follow-up

- La implementación de este change recién puede arrancar tras la aprobación del gate de governance CRITICO; los artefactos preparados NO habilitan el apply.
- Archivar el change y marcar el checkbox de `CHANGES.md` solo después de completar y verificar todas las tareas.
