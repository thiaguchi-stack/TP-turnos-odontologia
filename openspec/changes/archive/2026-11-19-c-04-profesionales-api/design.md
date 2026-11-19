# Design

## Context

Ver `proposal.md` para la motivación. Estado observable del repo al preparar este change:

- El modelo `Profesional` ya existe con `id`, `nombre`, `apellido`, `especialidad` (opcional) y `activo` (default `True`), sin constraints de obligatoriedad en la BD más allá del tipo (`backend/app/models/profesional.py:7-14`); la KB lo describe en `knowledge-base/04_modelo_de_datos.md:50-57`.
- C-03 archivó auth: `oauth2_scheme`, `get_current_user`, `require_role` y `require_odontologo_own` en `backend/app/core/deps.py:12-37`, con mapeo global de errores 401/403/429 en `backend/app/core/handlers.py:14-45` y `registrar_manejadores_auth(app)` ya llamado en `backend/app/main.py:32`.
- El patrón de router delgado ya está en `backend/app/routers/turnos.py:12-26`: el servicio lanza errores de dominio y el router los traduce a `HTTPException` (400/409). Los schemas usan `ConfigDict(from_attributes=True)` y `extra="forbid"` (`backend/app/schemas/auth.py:11-25`).
- `RequestValidationError` ya se mapea a 400 en `backend/app/main.py:42-46`, así que los errores de Pydantic no necesitan manejo nuevo.
- La fixture `client` de `backend/tests/conftest.py:96-109` inyecta una DB SQLite en memoria; `datos` (`conftest.py:91-93`) ya provee un profesional activo y otro inactivo con datos ficticios, reutilizables para el listado público.
- Reglas citadas: RN-PR-01 (`knowledge-base/05_reglas_de_negocio.md:32`), RN-AU-01/03 (`knowledge-base/05_reglas_de_negocio.md:9,11`), matriz RBAC y rutas públicas (`knowledge-base/03_actores_y_roles.md:11-29`), seguridad y validación de entrada (`knowledge-base/08_arquitectura_propuesta.md:39-46`), US-006 (`knowledge-base/06_funcionalidades.md:55-63`) y DD-07 (routers delgados, `AGENTS.md` §Reglas Duras).

Gobernanza BAJO (`CHANGES.md:204`): no requiere aprobación CRITICA, pero este documento es planning; no autoriza apply ni código de producción.

## Goals / Non-Goals

**Goals:**

- Exponer el catálogo de profesionales con un contrato HTTP estable para el selector de reserva (C-09/C-12) y para el futuro admin frontend (C-14).
- Mantener la decisión de negocio en `app/services/profesional_service.py`, con routers que solo declaran dependencias, llaman al servicio y traducen errores (DD-07).
- Aplicar RBAC admin al CRUD y reutilizar la auth de C-03 sin duplicar lógica de tokens ni de roles.
- Preservar el histórico de turnos y la integridad referencial de `Usuario.profesional_id` mediante baja lógica.
- Dejar cada comportamiento con un escenario verificable y una tarea con verificación explícita (pytest + `TestClient`).

**Non-Goals:**

- Modificar el modelo `Profesional` o ejecutar migraciones: el esquema ya existe y no cambia.
- Agregar un listado administrativo de inactivos, búsqueda/filtros/paginación ni endpoints de profesionales por especialidad: no están en el scope de C-04 (`CHANGES.md:197-202`). La reactivación se hace por id conocido con `PUT`.
- Administrar prestaciones, sillones, bloqueos ni usuarios (C-05, C-06 y C-03 respectivamente).
- Exponer datos clínicos, de pacientes ni credenciales; `password_hash` nunca sale de la capa de auth (RN-AU-04, RN-DATOS-01/02).
- Login de pacientes, integraciones externas, multi-tenant ni ficha clínica (DD-02/03/06).

## Decisions

1. **Capability nueva `profesionales`, sin deltas en specs existentes.** `modelo-datos` cubre persistencia/seed y `user-auth` cubre identidad/RBAC; ninguno cambia su comportamiento observable. Crear `openspec/specs/profesionales/spec.md` al archivar evita mezclar reglas de API con persistencia y deja a C-05 crear `prestaciones` de forma simétrica.

2. **Endpoints de lectura públicos con filtro de `activo`.** `GET /profesionales` devuelve solo activos y `GET /profesionales/{id}` responde 404 si el profesional está inactivo o no existe. Apoyo: la matriz RBAC permite al público "Leer lista (para reservar)" y al odontólogo "Leer" (`knowledge-base/03_actores_y_roles.md:17`), y RN-PR-01 exige que los inactivos no reciban reservas (`knowledge-base/05_reglas_de_negocio.md:32`). Alternativa descartada: exigir JWT en el detalle — complicaría el selector público sin beneficio; también se descartó devolver inactivos por id — filtraría mal la baja en la zona pública. Supuesto registrado: el único consumidor del detalle es la reserva/consultor de catálogo; el admin reactiva por id con `PUT`.

3. **`DELETE` siempre es baja lógica.** Fija `activo=false` y conserva la fila. El caso crítico "si tiene turnos" se cubre explícitamente para no borrar históricos (RN-PR-01, `knowledge-base/04_modelo_de_datos.md:92-103`); además, un borrado físico rompería `Usuario.profesional_id` aunque no hubiera turnos (`knowledge-base/04_modelo_de_datos.md:47`). Alternativa descartada: borrar físicamente cuando no hay turnos — introduce dos semánticas para el mismo verbo y riesgo de reutilización de ids. La operación es idempotente (una segunda llamada devuelve 200).

4. **Schemas con validación estricta en Pydantic 2.** `ProfesionalCreate` exige `nombre` y `apellido` no vacíos tras `strip()` y con máximo 100 caracteres (alineado con `String(100)` del modelo), `especialidad` opcional con máximo 100, `activo: bool = True`; `ProfesionalUpdate` reúne los mismos campos como opcionales y exige al menos uno; todos con `extra="forbid"` y `bool` estricto para rechazar `"si"`/1 como `activo`. `ProfesionalRead` usa `from_attributes=True` y solo los cinco campos públicos. `RequestValidationError` ya produce 400 (`backend/app/main.py:42-46`). Alternativa descartada: validar a mano en el router — rompe DD-07 y deja la validación fuera del contrato del schema.

5. **Servicio con errores de dominio y router delgado.** `profesional_service.py` expone `listar_activos`, `obtener_activo`, `crear`, `actualizar` y `desactivar`; los errores `ProfesionalNoEncontradoError` y `ProfesionalRechazadoError` se agregan a `backend/app/services/errores.py` y el router los traduce a 404/400 siguiendo `backend/app/routers/turnos.py:21-26`. Alternativa descartada: registrar handlers globales nuevos — innecesario para errores de un solo recurso y mezclaría capas de auth con catálogo.

6. **RBAC reutilizado, sin lógica propia de tokens.** Las tres rutas de administración declaran `_admin: Usuario = Depends(require_role(RolUsuario.ADMIN))`, igual que `backend/app/routers/auth.py:33-40`. Los 401 (sin token, expirado, firma inválida) y 403 (odontólogo) ya los produce C-03 (`backend/app/core/handlers.py:17-45`); no se agrega middleware ni se guarda rol en la sesión. Alternativa descartada: comprobar `rol` dentro del servicio — acoplaría el servicio a la capa HTTP.

7. **Cableado y tests.** Registrar `profesionales.router` en `backend/app/main.py` junto a `auth` y `turnos`. Tests unitarios del servicio (`backend/tests/test_profesional_service.py`) y de integración (`backend/tests/test_profesionales_api.py`) con `client` y `datos` de `conftest.py`; los usuarios admin/odontólogo se crean con `security.hash_password` y se autentican por `POST /auth/login`, con contraseñas ficticias de test. Alternativa descartada: testear el servicio vía HTTP — las reglas puras se validan primero en unit.

### Contrato de auth verificado (auditoría ligera)

| Regla (fuente) | Cómo se cumple | Escenario spec | Verificación en tasks |
|---|---|---|---|
| RN-AU-01: JWT en ruta privada (`05_reglas_de_negocio.md:9`) | `require_role` en POST/PUT/DELETE; GET público | RBAC, escenario "Sin token..." | 3.1, 3.2 |
| RN-AU-03: solo admin gestiona catálogo (`05_reglas_de_negocio.md:11`) | `require_role(RolUsuario.ADMIN)` reutilizado | RBAC, escenario "Odontólogo..." | 3.3 |
| JWT expirado/firma inválida → 401 (`08_arquitectura_propuesta.md:41`) | Validación existente de C-03, sin código nuevo | RBAC, escenario "Token vencido..." | 3.2 |
| Sin `password_hash` ni datos de terceros (`08_arquitectura_propuesta.md:42-45`) | `ProfesionalRead` con whitelist de campos | "Campos exactos..." y "El catálogo público no filtra..." | 1.1, 3.4 |
| RBAC público/odontólogo/admin (`03_actores_y_roles.md:13-20`) | Lectura pública; escritura solo admin | Listado, detalle y RBAC | 2.1, 3.3 |
| Datos ficticios (RN-DATOS-03, `05_reglas_de_negocio.md:44`) | Fixtures de `conftest.py` y valores de test inventados | Todos | 1.1, 2.1, 3.4 |

## Risks / Trade-offs

- **[Riesgo] El detalle público devuelve 404 para inactivos y el admin no tiene listado de inactivos** → Mitigación: el admin conoce el id por el histórico/turnos y puede reactivarlo con `PUT`; este límite está registrado en Non-Goals y en la spec de baja lógica.
- **[Riesgo] La baja lógica acumula profesionales inactivos** → Mitigación: el filtro `activo=true` vive en el servicio y todas las lecturas públicas lo usan; no se expone un listado que mezcle estados.
- **[Riesgo] `bool` estricto y `extra="forbid"` rechacen clientes que envíen `1`/`0` o campos extra** → Mitigación: es deliberado y forma parte del contrato 400; el frontend C-14 enviará JSON booleano.
- **[Riesgo] El mapeo de 404/400 quede olvidado en una ruta nueva** → Mitigación: la tarea 2.2 cubre las tres rutas de administración con `TestClient` y la tarea 3.1 verifica los errores de negocio.
- **[Trade-off] Sin paginación ni filtros** → Aceptado: el consultorio es single-tenant y el catálogo es chico (DD-02, `knowledge-base/09_decisiones_y_supuestos.md`); se agregaría como change futuro si hiciera falta.

## Migration Plan

1. No hay cambio de esquema: el modelo `Profesional` y la tabla ya existen, no se ejecuta Alembic ni `create_all` nuevo.
2. Agregar los archivos de schemas, servicio, errores y router, y registrar el router en `app/main.py`.
3. Verificar con `openspec validate c-04-profesionales-api --strict` (planning) y con la suite pytest completa (apply).
4. Rollback: quitar `app.include_router(profesionales.router)` y los archivos nuevos; como no hay mutación de BD, no hay datos que revertir. Si ya se ejecutó apply con altas de prueba, eliminar solo esos registros ficticios.
