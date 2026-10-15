# Tasks — C-02 `core-models`

> **Strict TDD**: cada grupo parte del safety net verde (RED → GREEN → TRIANGULATE → REFACTOR).
> **Governance CRITICO**: el grupo 0 es un gate; no se escribe código de producción hasta que las decisiones abiertas de `design.md` estén aprobadas.

## 0. Gate de aprobación (governance CRITICO)

- [x] 0.1 Registrar la línea base de calidad y verificar que el safety net esté verde: `pytest` con ~72 tests passed y `mypy app` sin errores (comando ejecutado en `backend/`, salida adjunta como evidencia)
- [x] 0.2 Obtener aprobación humana explícita de OQ-1 (Alembic sí/no), OQ-2 (forma de `HorarioAtencion` + convención de `dia_semana`), OQ-3 (alcance de 8 tablas y delegar la regla rol↔profesional a C-03) y OQ-4 (hash mínimo en `security.py`) — verificación: decisiones registradas en `design.md` con la opción aprobada marcada

## 1. Enums tipados y mixin de auditoría (sin romper compatibilidad)

- [x] 1.1 Escribir tests RED de `EstadoTurno` y `RolUsuario`: valores exactos del enum, default `reservado`, rechazo de `"reprogramado"` y `"superadmin"`; verificar que fallan antes de implementar
- [x] 1.2 Implementar `EstadoTurno`/`RolUsuario` como clases enum y conservar `ESTADOS_TURNO` como alias de compatibilidad; verificar que los tests del punto 1.1 pasan y que los imports existentes siguen resolviendo
- [x] 1.3 Escribir tests RED de auditoría (`creado_en` automático en `Usuario`, `Paciente` y `Turno` sin enviarlo) y TRIANGULATE con reloj controlado (`app/core/clock.py`)
- [x] 1.4 Implementar el mixin de auditoría en `app/db/base.py` y aplicarlo a `Usuario`, `Paciente` y `Turno`; verificar tests de 1.3 y suite completa verde
- [x] 1.5 REFACTOR: reemplazar los `creado_en` duplicados por el mixin y verificar `pytest` + `mypy app` + `ruff check`

## 2. Modelo `Usuario` y `Turno.creado_por`

- [x] 2.1 Escribir tests RED de `Usuario`: creación con rol `admin` y `profesional_id` nulo OK, unicidad de `email` (segundo insert falla), `profesional_id` inexistente rechazado por FK
- [x] 2.2 Implementar `app/models/usuario.py` (`email` unique, `password_hash`, `rol`, `profesional_id` FK nullable, `activo` default true) y exportarlo en `app/models/__init__.py`; verificar tests de 2.1

- [x] 2.3 Escribir tests RED de `Turno.creado_por`: por defecto nulo (reserva online) y acepta FK a un `Usuario` existente
- [x] 2.4 Agregar `Turno.creado_por` (FK → `usuario.id`, nullable) y verificar tests de 2.3 más suite existente verde

- [x] 2.5 TRIANGULATE: casos borde de unicidad (email distinto mismo rol, email repetido con distinto `profesional_id`) y verificar que los tests discriman


## 3. Unicidades e índices de agenda

- [x] 3.1 Escribir tests RED de `Paciente`: mismo `(dni, telefono)` rechazado, mismo `dni` con teléfono distinto permitido; y de `Turno.token_cancelacion` duplicado rechazado, token nulo permitido
- [x] 3.2 Implementar `UniqueConstraint("dni", "telefono")` en `Paciente` y verificar tests de 3.1 sin romper el seed de `conftest.py`
- [x] 3.3 Declarar índices `turno(profesional_id, fecha_hora_inicio)`, `turno(sillon_id, fecha_hora_inicio)` y `bloqueo(profesional_id, fecha_hora_inicio)` con nombres explícitos, y verificar vía `sqlalchemy.inspect` que existen con el nombre esperado
- [x] 3.4 REFACTOR: verificar que `turno_service` (queries de solapamiento) sigue verde y que `pytest` + `mypy app` pasan

## 4. Modelo `HorarioAtencion` (SU-03)

- [x] 4.1 Escribir tests RED: franja válida (lunes 09:00–13:00) persistida y asociada al profesional; `hora_fin <= hora_inicio` rechazada; FK a profesional inexistente rechazada; dos franjas del mismo día para el mismo profesional conviven
- [x] 4.2 Implementar `app/models/horario_atencion.py` según la opción aprobada en OQ-2 (con `CheckConstraint(hora_fin > hora_inicio)` y unique por franja) y exportarlo en `app/models/__init__.py`; verificar tests de 4.1
- [x] 4.3 TRIANGULATE: franjas superpuestas del mismo día (documentar explícitamente si el modelo las permite y dejar constancia para `C-07`) y verificar el comportamiento con un test que capture la decisión

## 5. Seed mínimo idempotente

- [x] 5.1 Escribir tests RED de `seed_minimo`: en base vacía quedan 1 admin + 1 profesional activo + 1 usuario odontólogo vinculado; ejecutarlo dos veces no duplica registros ni altera los existentes
- [x] 5.2 Implementar `app/db/seed.py` (`seed_minimo(db)` idempotente con lookup por email/dni+teléfono y datos ficticios que cumplen RN-DATOS-03); verificar tests de 5.1 y `mypy app`
- [x] 5.3 Según OQ-4: implementar hash mínimo (`hash_password`/`verify_password` con `pbkdf2_hmac`) y test RED→GREEN de que `password_hash` del admin difiere de la contraseña en claro y `verify_password` la valida; verificar que el valor no aparece en logs ni en `__repr__`
- [x] 5.4 Invocar `seed_minimo` desde el `lifespan` de `app/main.py` y verificar con un test de startup que `/api/health` responde 200 y que la base quedó sembrada sin duplicar

## 6. Esquema versionado con Alembic — **condicional a OQ-1**

> Si OQ-1 se rechaza, eliminar este grupo y agregar en su lugar una tarea en el grupo 7 para documentar en `README` el borrado/recreación de `clinica.db` al cambiar el modelo.

- [x] 6.1 Agregar `alembic` a `pyproject.toml` y crear `alembic.ini` + `alembic/env.py` con `target_metadata = Base.metadata`; verificar que `alembic upgrade head` corre sin error sobre un archivo SQLite temporal
- [x] 6.2 Generar la revisión baseline `001` con las 8 tablas, FKs, unicidades e índices; verificar `alembic upgrade head` seguido de `alembic downgrade base` sobre archivo temporal sin errores
- [x] 6.3 Verificar que el esquema migrado coincide con `Base.metadata` (comparar tablas/columnas/índices con `sqlalchemy.inspect` en un test de consistencia)
- [x] 6.4 Definir y verificar el arranque: si el `lifespan` pasa a `alembic upgrade head`, confirmar que los tests in-memory siguen usando `create_all` y que la suite completa queda verde; documentar el flujo de migración en `README.md` (español rioplatense)

## 7. Verificación de integración y documentación

- [x] 7.1 Correr la suite completa (`pytest`) y verificar que el safety net original sigue verde y que todos los tests nuevos pasan
- [x] 7.2 Correr `mypy app` (strict) y `ruff check` y verificar salida sin errores
- [x] 7.3 Levantar la app (`uvicorn app.main:app`) contra un `DATABASE_URL` SQLite temporal y verificar arranque limpio, seed aplicado y `GET /api/health` = 200
- [x] 7.4 Verificar que no se expone ni loguea `password_hash` (grep de `password_hash` en `app/` + revisión de `__repr__`/logs) y que ningún test/fixture/seed contiene datos reales de pacientes (RN-DATOS-03)
- [x] 7.5 Documentar en `README.md` (español rioplatense): modelos incorporados, seed mínimo, flujo de esquema aprobado en OQ-1 y cómo correr los tests

## Workflow follow-up

- Presentar el resultado al usuario para **aprobación explícita** (governance CRITICO) antes de la implementación real.
- Al implementar y archivar: actualizar el scope de `[C-02]` en `CHANGES.md` (8 tablas + `HorarioAtencion` + Alembic) y marcar el change.
- Archivar el change y re-emitir delta de la capability `turnos` solo si algún comportamiento observable cambió respecto de lo especificado.





