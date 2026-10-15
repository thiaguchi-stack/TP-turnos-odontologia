# backend — API de turnos

Implementación del backend en **FastAPI + SQLAlchemy 2.x + Pydantic 2.x**. Routers delgados: la lógica de negocio vive en `app/services/` (DD-07, regla dura del proyecto).

Las instrucciones de instalación multiplataforma (venv, dependencias, uvicorn) están en el [README de la raíz](../README.md). Este archivo explica la estructura por capas, un ejemplo real de uso y cómo correr tests y lint.

## Estructura por capas

| Carpeta / archivo | Propósito |
|---|---|
| `app/core/` | Configuración de la app (`config.py`): settings leídos del entorno (p. ej. `DATABASE_URL`). Reloj único (`clock.py`): `clock.now()` devuelve la hora actual **naive local** (sin tz, Argentina) y es el único punto donde la app "lee el tiempo", para que los tests puedan controlarlo con `unittest.mock.patch`. |
| `app/db/` | Base declarativa y sesión (`base.py`, `session.py`): engine, `SessionLocal` y la dependencia `get_db`. |
| `app/models/` | Entidades SQLAlchemy: `turno`, `profesional`, `paciente`, `prestacion`, `sillon`, `bloqueo`. |
| `app/schemas/` | Schemas Pydantic de request/response (`TurnoCreate`, `TurnoRead`). `TurnoCreate` usa `extra="forbid"`: `estado` y `fecha_hora_fin` no se aceptan desde afuera. |
| `app/services/` | Lógica de negocio testeable: `turno_service.crear_turno()` valida recursos, pasado, duración derivada y solapamiento; `errores.py` define `TurnoRechazadoError` (→ `400`) y `TurnoSolapadoError` (→ `409`). |
| `app/routers/` | Endpoints HTTP delgados (`turnos.py`): delegan en services y traducen las excepciones de dominio a códigos HTTP. |
| `app/main.py` | App FastAPI: `lifespan` que crea las tablas, incluye el router de turnos, expone `GET /api/health` y convierte errores de validación en `400` con `detail`. |

## Ejemplo de uso: `POST /turnos`

Tomado de `app/routers/turnos.py` y cubierto por `tests/test_turnos_api.py`. Los ids corresponden a registros existentes (en los tests los crea el fixture de `tests/conftest.py`; en dev, a los que cargues en la base).

### Request

```http
POST /turnos
Content-Type: application/json
```

```json
{
  "profesional_id": 1,
  "paciente_id": 1,
  "prestacion_id": 1,
  "sillon_id": 1,
  "fecha_hora_inicio": "2026-11-05T09:00:00"
}
```

### `201 Created`

La duración se deriva de la prestación (en el ejemplo del test, una limpieza de 30 minutos):

```json
{
  "id": 1,
  "profesional_id": 1,
  "paciente_id": 1,
  "prestacion_id": 1,
  "sillon_id": 1,
  "fecha_hora_inicio": "2026-11-05T09:00:00",
  "fecha_hora_fin": "2026-11-05T09:30:00",
  "estado": "reservado"
}
```

`estado` nace siempre en `"reservado"` y `fecha_hora_fin` siempre se calcula (`inicio + duracion_minutos`); ninguno de los dos se acepta en el request.

### `409 Conflict` (solapamiento)

Si el horario choca con otro turno del mismo profesional, del mismo sillón o con un bloqueo de agenda (intervalos `[inicio, fin)`, borde a borde permitido):

```json
{
  "detail": "Ya existe un turno del mismo profesional en ese horario."
}
```

Los otros mensajes de `409`: `"El sillón ya está ocupado por otro profesional en ese horario."` y `"El profesional tiene un bloqueo de agenda en ese horario."`.

### `400 Bad Request`

- Campos de más en el body (p. ej. `estado` o `fecha_hora_fin`) o tipos inválidos.
- `"No se puede crear un turno en el pasado."` — el "pasado" se juzga sobre
  `fecha_hora_inicio` (`inicio < ahora`, ver spec «Sin turnos en el pasado»):
  un turno ya iniciado, aunque su fin derivado siga en el futuro, también se
  rechaza; `inicio` igual a `ahora` está permitido.
- Recursos inexistentes o inactivos: `"El profesional está inactivo y no recibe turnos nuevos."`, `"El sillón está inactivo…"`, `"La prestación está inactiva…"`.

## Tests y lint (desde `backend/`)

Los comandos asumen el entorno virtual ya creado según el [README de la raíz](../README.md). Los tests corren sobre SQLite **en memoria** (`DATABASE_URL=sqlite://` lo fija `tests/conftest.py`): no tocan la base local. Estado actual: **72 tests passing**.

### PowerShell

```powershell
.venv\Scripts\python.exe -m pytest -v
.venv\Scripts\ruff.exe check .
.venv\Scripts\ruff.exe format --check .
.venv\Scripts\python.exe -m mypy app
```

### Git Bash (Windows)

```bash
.venv/Scripts/python -m pytest -v
.venv/Scripts/ruff check .
.venv/Scripts/ruff format --check .
.venv/Scripts/python -m mypy app
```

### Linux / macOS

```bash
.venv/bin/python -m pytest -v
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m mypy app
```

Para levantar la API en dev desde `backend/`:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Los tests cubren las reglas de negocio del change archivado (`RN-TU-*`) y los casos de error `400`/`409`: solapamiento por profesional, por sillón y por bloqueo; borde a borde; turnos sobre turnos cancelados; turno en el pasado; recursos inactivos; campos prohibidos. El reloj de la app está centralizado en `app/core/clock.py` y los tests lo parchean para que los escenarios de tiempo (pasado, en curso, borde `inicio == ahora`) sean deterministas. Ver `tests/test_clock.py`, `tests/test_turnos_api.py` y `tests/test_turno_service.py`.
