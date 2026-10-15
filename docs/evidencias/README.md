# Evidencias del TP — turnos odontología

Carpeta de **evidencias verificables** de los cycles OPSX cerrados. El criterio
(estructura, nombres y nivel de detalle) se copió del proyecto aprobado de
referencia
(`…\Temp\opencode\turnos-odontologia-metodologia\docs\evidencias\`): por cada
change archivado hay un `verify-*.md` con la trazabilidad spec → tests y las
salidas crudas de los runners en `.txt` adjuntos. El contenido es 100 % de
**este** repo: los comandos se corrieron acá y las salidas son las reales.

Rutas relativas a la raíz del repo. Todo en español rioplatense.

## Archivos

| Archivo | Qué es | Estado |
|---------|--------|--------|
| [README.md](README.md) | Este índice. | ✅ |
| [verify-crear-turno-sin-solapamientos.md](verify-crear-turno-sin-solapamientos.md) | Pieza central del change archivado `openspec/changes/archive/2026-10-10-crear-turno-sin-solapamientos/`: comandos reales, **tabla de trazabilidad escenario de la spec → test (ruta:línea)**, huecos, lint y estado final. | ✅ |
| [pytest-crear-turno-sin-solapamientos.txt](pytest-crear-turno-sin-solapamientos.txt) | Salida completa del runner `pytest -v` (58 tests). | ✅ |
| [ruff-crear-turno-sin-solapamientos.txt](ruff-crear-turno-sin-solapamientos.txt) | Salida de `ruff check backend` + `ruff format --check backend`. | ✅ |
| [mypy-backend.txt](mypy-backend.txt) | Salida de `mypy app` (`strict = true`, plugin de pydantic) desde `backend/`. | ✅ |
| [explore-crear-turno-sin-solapamientos.md](explore-crear-turno-sin-solapamientos.md) | Resumen de la exploración previa al change (OPSX Explore), citando sus fuentes. | ✅ |
| [skills.md](skills.md) | Skills instaladas en el repo y en qué etapa del flujo se usó cada una. | ✅ |

## Pendientes (no inventados, no creados)

- **`capturas/` — capturas de pantalla de la UI: PENDIENTE.** El proyecto tiene el
  scaffold de React desde `C-01` (build y `tsc` en verde), pero todavía sin
  páginas de reserva ni zona protegida — las pantallas llegan con la Fase 4
  (`C-11` en adelante). Se crea la carpeta y los archivos cuando exista la SPA.
  No se sube ninguna imagen inventada.
- **`mypy-*.txt` — salida de type-check: ✅.** El repo ya adoptó mypy
  (`[tool.mypy]` con `strict = true` en `backend/pyproject.toml`); la salida
  completa quedó en `mypy-backend.txt`.
- **Cambios futuros**: cada change que se archive sumará su trío
  `verify-<change>.md` + `pytest-<change>.txt` + `ruff-<change>.txt`.
  (`c-01-foundation-setup` y `c-02-core-models` están archivados; su trío de
  evidencia aún no se generó.)

## Cómo regenerar la evidencia

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -v
backend\.venv\Scripts\ruff.exe check backend
backend\.venv\Scripts\ruff.exe format --check backend
# type-check: correr DESDE backend\ (la config vive en backend\pyproject.toml)
#   .venv\Scripts\python.exe -m mypy app
```

Los tests corren sobre SQLite **en memoria** (`backend/tests/conftest.py`): no
toca la base local. El entorno usado para esta corrida:
`backend\.venv` (Python 3.14.7, pytest 9.1.1).
