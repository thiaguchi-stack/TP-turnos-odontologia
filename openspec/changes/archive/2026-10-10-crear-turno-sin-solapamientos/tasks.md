# Tasks — crear-turno-sin-solapamientos

> Referencias: comportamiento en `specs/turnos/spec.md`; decisiones técnicas en
> `design.md`. Reglas duras de `AGENTS.md` aplican en cada tarea.

## 1. Scaffolding del backend

- [x] 1.1 Crear `backend/pyproject.toml` con `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2.0`, `pydantic>=2`, `pytest`, `httpx` y `ruff` (pins compatibles Python 3.11) y verificar que `uv`/`pip` instala el entorno sin errores.
- [x] 1.2 Crear la estructura `backend/app/{core,models,schemas,services,routers,db}` + `backend/tests/` conforme a `knowledge-base/08 §Estructura de directorios` y verificar el árbol de carpetas con `Get-ChildItem`.
- [x] 1.3 Crear `backend/app/main.py` con la app FastAPI (`title`, `GET /api/health` → `{"status": "ok"}`) y verificar con TestClient que `/api/health` responde 200.

## 2. Persistencia y modelos mínimos

- [x] 2.1 Crear `app/db/base.py`, `app/db/session.py` (`engine` desde `DATABASE_URL` default `sqlite:///./clinica.db`, `SessionLocal`, `get_db`) y `app/core/config.py` (Pydantic Settings con `database_url`) y verificar que el engine se instancia y que `get_db` cierra la sesión.
- [x] 2.2 Implementar los modelos SQLAlchemy 2.x (`Mapped`/`mapped_column`) `Profesional`, `Prestacion`, `Sillon`, `Paciente` (stub mínimo), `Turno` y `Bloqueo` con los atributos, FKs y defaults exactos de `knowledge-base/04 §Entidades` (incluyendo `Turno.sillon_id` NOT NULL, `Bloqueo.sillon_id` nullable y enum `estado` con default `reservado`) y verificar con `pytest` unit que cada modelo se crea con sus defaults (test `tests/test_models.py`).
- [x] 2.3 Configurar `main.py` para ejecutar `Base.metadata.create_all` al arrancar y verificar por integración que la app arranca y deja la tabla `turno` creada en SQLite en memoria.
- [x] 2.4 Escribir un fixture de pytest (`conftest.py`) que cree un engine SQLite en memoria (`StaticPool`), sete los datos ficticios mínimos (1 profesional activo, 1 inactivo, 2 sillones activos + 1 inactivo, 2 prestaciones activas + 1 inactiva, 1 paciente) y provea `db` de sesión y `client` de TestClient, y verificar que el fixture se usa en un test humo que entra a cada tabla.

## 3. Servicio crear_turno con unit tests

- [x] 3.1 Implementar excepciones de dominio (`TurnoRechazadoError(motivo)`, `TurnoSolapadoError(motivo)`) en `app/services/errores.py` y verificar con `pytest` que se levantan con `pytest.raises` y exponen `motivo` en español.
- [x] 3.2 Implementar `app/services/turno_service.py::crear_turno`turno(db, *, profesional_id, paciente_id, prestacion_id, sillon_id, fecha_hora_inicio)` con el orden de validación y la firma del design D2 (sin `estado` ni `fecha_hora_fin`), que derive `fecha_hora_fin = inicio + duracion_minutos` (RN-TU-02) y persista con `estado="reservado"`, y verificar con el test **unit feliz**: turno [09:00, 09:30) del 2026-11-05 con estado `reservado`.
- [x] 3.3 Implementar la consulta de solapamiento del design D3 (tres conjuntos: turnos del `profesional_id`, turnos del `sillon_id`, bloqueos con `sillon_id IS NULL OR = sillon_id`; condición `inicio_existente < fin_nuevo AND fin_existente > inicio_nuevo`; exclusión de `estado="cancelado"`) y verificar con **unit tests** todos los escenarios del spec: colisión por profesional (409 por `TurnoSolapadoError` con motivo "profesional"), colisión por sillón (motivo "sillón"), colisión con bloqueo (nulo y con sillón, motivo "bloqueo"), borde 09:30 permitido e inicio 09:29 rechazado (`[inicio, fin)`), turno cancelado no bloquea.
- [x] 3.4 Implementar las validaciones de elegibilidad: FKs existentes, profesional `activo` (RN-PR-01), sillón `activo` (RN-TU-09), prestación `activa` (RN-PR-02) y `fecha_hora_inicio` no pasada (RN-TU-06), todo lanzando `TurnoRechazadoError` sin tocar la DB, y verificar con **unit tests** cada caso: profesional inactivo, sillón inactivo, prestación inactiva y turno en el pasado (fecha fija anterior a `now`).

## 4. API POST /turnos con tests de integración

- [x] 4.1 Crear `app/schemas/turno.py` con `TurnoCreate` (solo `profesional_id`, `paciente_id`, `prestacion_id`, `sillon_id`, `fecha_hora_inicio`; `model_config = ConfigDict(extra="forbid")`) y `TurnoRead` (con `fecha_hora_fin` y `estado`), y verificar con `pytest` que `TurnoCreate` rechaza los campos `estado` y `fecha_hora_fin` (ValidationError).
- [x] 4.2 Crear `app/routers/turnos.py` con `POST /turnos` delgado (decodifica `TurnoCreate`, llama `crear_turno`, mapea `TurnoSolapadoError → 409`, `TurnoRechazadoError → 400`) y montarlo en `main.py`, y verificar con un **test de integración** que una creación feliz responde `201` y el body de `TurnoRead` trae `estado="reservado"` y `fecha_hora_fin` derivado (2026-11-05T09:30).
- [x] 4.3 Agregar handler global de `RequestValidationError → 400` (D4) en `main.py` y verificar con **test de integración** que enviar `estado` o `fecha_hora_fin` en el request responde `400` sin crear turno.
- [x] 4.4 Verificar con **tests de integración** el resto de los códigos del spec: `409` para colisión por profesional, por sillón y con bloqueo (cada uno con detalle en español), `400` para pasado, profesional inactivo, sillón inactivo y prestación inactiva, y `201` para el borde 09:30 y para la creación sobre un turno cancelado.

## 5. Calidad y trazabilidad

- [x] 5.1 Ejecutar `ruff check` + `ruff format --check` sobre `backend/` y corregir todo hallazgo hasta que pase sin errores.
- [x] 5.2 Ejecutar la suite completa (`pytest backend/tests -q`) y verificar que todos los tests unit e integración corresponen 1:1 con los escenarios de `specs/turnos/spec.md` (feliz, colisiones, bordes, estados inactivos, pasado, cancelado), sin tests pendientes ni `xfail`.
- [x] 5.3 Verificar la entrada de trazabilidad ya agregada en `CHANGES.md` (sección «Changes OPSX de la consigna (desvíos deliberados)»: fila `crear-turno-sin-solapamientos` alineada a C-07/C-08 con desvío declarado) y confirmar que no se modificó el resto del documento (`git diff` limitado a la adición).

## Workflow follow-up

- Presentar los artefactos de planning al orquestador para revisión antes de archivar.
- Al aprobar, ejecutar el flujo de apply (`/opsx:apply cambiar-turno-sin-solapamientos`) y luego archivar el change.
- Al ejecutarse `C-02 core-models` (governance CRITICO), absorber/mergear estos modelos con los canónicos de la KB y re-emitir esta capability como delta si el comportamiento cambia.