# TP-turnos-odontologia

Sistema de gestión de turnos para un consultorio odontológico — trabajo práctico integrador de **Metodología I** (Thiago Oviedo, individual). Usa **Spec-Driven Development (OpenSpec) + Active Stack**.

## Estado del proyecto

- ✅ **Fundación**: `knowledge-base/` (dominio completo, 10 archivos + README), `CHANGES.md` (18 changes en 6 fases), `AGENTS.md`/`CLAUDE.md` (reglas duras del proyecto).
- ✅ **Discovery / investigación de mercado**: 34 sistemas relevados en `docs/discovery/raw/` + verificación de fuentes en `docs/discovery/verificacion-fuentes.md`.
- ✅ **Primer ciclo OPSX cerrado**: change `crear-turno-sin-solapamientos` (desvío deliberado → `C-07`/`C-08`), implementado y archivado con spec sincronizado.
- 🔲 **Roadmap OPSX**: continuar en el camino crítico `C-01 → C-02 → C-03 → …` (ver `CHANGES.md`).

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11+ · FastAPI · SQLAlchemy 2.x · Pydantic 2.x |
| Base de datos | SQLite (dev, en memoria para tests) / PostgreSQL opcional |
| Tests | pytest + httpx (`TestClient`) |
| Lint | Ruff |
| Frontend | Pendiente (React + Vite, según KB) |

## Estructura del repo

```
├── AGENTS.md / CLAUDE.md        Reglas duras + guía para agentes
├── CHANGES.md                   Roadmap de changes (18) + cambios OPSX de la consigna
├── knowledge-base/              Fuente de verdad del dominio (10 archivos)
├── docs/
│   ├── discovery/               Investigación de mercado (raw + verificación)
│   └── explore/                 Relevamientos OPSX
├── openspec/
│   ├── specs/turnos/            Specs vigentes (capability turnos)
│   └── changes/archive/         Changes archivados (ciclos cerrados)
└── backend/                     Implementación (app + tests)
```

## Backend

### Requisitos

- Python 3.11+ (desarrollado con 3.14).
- Virtualenv en `backend/.venv` (ya creado en el repo).

### Instalación (desde cero)

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -e backend
```

### Correr los tests

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -v
```

Los tests usan SQLite **en memoria** (`DATABASE_URL=sqlite://` lo fija `backend/tests/conftest.py`); no tocan la base local. Estado actual: **58 tests passing**.

### Lint

```powershell
backend\.venv\Scripts\ruff.exe check backend
backend\.venv\Scripts\ruff.exe format --check backend
```

### Correr la API (dev)

```powershell
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

### Endpoints implementados (v1 del change archivado)

| Método | Ruta | Respuesta |
|--------|------|-----------|
| `GET` | `/api/health` | `200` `{"status":"ok"}` |
| `POST` | `/turnos` | `201` turno `reservado` con `fecha_hora_fin` derivada de la prestación · `409` solapamiento (profesional, sillón o bloqueo) · `400` datos inválidos / pasado / recurso inactivo |

Reglas de negocio aplicadas: `fecha_hora_fin = inicio + duracion_minutos(prestación)`, intervalos `[inicio, fin)`, sin solapamiento por profesional **ni** por sillón/box, sin turnos en el pasado ni con recursos inactivos, `estado`/`fecha_hora_fin` no se aceptan del request (Pydantic `extra="forbid"`).

## Documentación de referencia

- `knowledge-base/01_vision_y_objetivos.md` → `10_preguntas_abiertas.md` (leer el archivo relevante antes de tocar cada área).
- `CHANGES.md` → plan completo: dependencias, paralelismo, camino crítico y governance por change.
- `AGENTS.md` → reglas duras del proyecto (no romperlas).

## Notas de entrega

- Todos los datos en seeds, tests y ejemplos son **ficticios** (Ley 25.326, RN-DATOS-03): ningún dato clínico real ni de terceros en el repo.
- Sin secretos en el repo: claves e integraciones van en `.env` (ignorado por git).