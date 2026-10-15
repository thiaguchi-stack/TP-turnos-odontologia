# TP-turnos-odontologia

Sistema de gestión de turnos para un consultorio odontológico — trabajo práctico integrador de **Metodología I** (Thiago Oviedo, individual). Usa **Spec-Driven Development (OpenSpec) + Active Stack**.

## Estado del proyecto

- ✅ **Fundación**: `knowledge-base/` (dominio completo, 10 archivos + README), `CHANGES.md` (18 changes en 6 fases), `AGENTS.md`/`CLAUDE.md` (reglas duras del proyecto).
- ✅ **Discovery / investigación de mercado**: 34 sistemas relevados en `discovery/raw/` + verificación de fuentes en `discovery/verificacion-fuentes.md`.
- ✅ **Primer ciclo OPSX cerrado**: change `crear-turno-sin-solapamientos` (desvío deliberado → `C-07`/`C-08`), implementado y archivado con spec sincronizado.
- ✅ **Backend del ciclo archivado**: `backend/app/` (capas core/db/models/schemas/services/routers) + **72 tests passing**.
- ✅ **Fundación C-01**: `c-01-foundation-setup` implementado y archivado (CORS configurable, stub `core/security.py`, `.env.example` y scaffold `frontend/` Vite + React 18 + TS con build verificado).
- 🔲 **Roadmap OPSX**: continuar en el camino crítico `C-02 → C-03 → …` (ver `CHANGES.md`).

## Dónde está cada entregable

| Entregable | Ubicación | Estado |
|---|---|---|
| Informe de Discovery | [`discovery/informe-discovery.md`](discovery/informe-discovery.md) | ✅ |
| Informe de Discovery (PDF) | [`discovery/informe-discovery.pdf`](discovery/informe-discovery.pdf) | ✅ |
| Relevamiento raw (34 sistemas) | [`discovery/raw/`](discovery/raw/) | ✅ |
| Checklist de Discovery | [`discovery/checklist-discovery-research.md`](discovery/checklist-discovery-research.md) | ✅ |
| Verificación de fuentes + fichas | [`discovery/verificacion-fuentes.md`](discovery/verificacion-fuentes.md), [`discovery/sources/`](discovery/sources/) | ✅ |
| Matriz ponderada (33 productos) + script de verificación | [`discovery/matriz-ponderada.md`](discovery/matriz-ponderada.md), [`discovery/verificar_matriz.py`](discovery/verificar_matriz.py) | ✅ |
| Knowledge Base (10 archivos) | [`knowledge-base/`](knowledge-base/) (índice en [`knowledge-base/README.md`](knowledge-base/README.md)) | ✅ |
| Roadmap de changes (18, 6 fases) | [`CHANGES.md`](CHANGES.md) | ✅ |
| Instrucciones para agentes | [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md) | ✅ |
| Especificaciones OpenSpec vigentes | [`openspec/specs/turnos/`](openspec/specs/turnos/) | ✅ |
| Change archivado `crear-turno-sin-solapamientos` (proposal, design, tasks, spec delta) | [`openspec/changes/archive/2026-10-10-crear-turno-sin-solapamientos/`](openspec/changes/archive/2026-10-10-crear-turno-sin-solapamientos/) | ✅ archivado |
| Change archivado `c-01-foundation-setup` (proposal, design, tasks, spec delta) | [`openspec/changes/archive/2026-10-15-c-01-foundation-setup/`](openspec/changes/archive/2026-10-15-c-01-foundation-setup/) | ✅ archivado |
| Backend (implementación) | [`backend/app/`](backend/app/) → detalle en [`backend/README.md`](backend/README.md) | ✅ |
| Tests | [`backend/tests/`](backend/tests/) | ✅ 72 passing |
| Evidencias (verify + trazabilidad, pytest/ruff, explore, skills) | [`docs/evidencias/`](docs/evidencias/) | ✅ |
| Reflexión final | [`docs/reflexion.pdf`](docs/reflexion.pdf) (+ [`docs/reflexion.md`](docs/reflexion.md)) | ✅ |
| Frontend (React + Vite) | [`frontend/`](frontend/) (scaffold C-01: Vite + React 18 + TS) | ✅ scaffold |

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11+ · FastAPI · SQLAlchemy 2.x · Pydantic 2.x |
| Base de datos | SQLite (dev, en memoria para tests) / PostgreSQL opcional |
| Tests | pytest + httpx (`TestClient`) |
| Lint | Ruff + mypy (backend) · ESLint + Prettier (frontend) |
| Frontend | React 18 · Vite 5 · TypeScript (estricto) · react-router-dom |

## Estructura del repo

```
├── AGENTS.md / CLAUDE.md        Reglas duras + guía para agentes
├── CHANGES.md                   Roadmap de changes (18) + cambios OPSX de la consigna
├── knowledge-base/              Fuente de verdad del dominio (10 archivos + README)
├── discovery/                   Investigación de mercado
│   ├── informe-discovery.md     Informe consolidado
│   ├── informe-discovery.pdf    Informe en PDF
│   ├── checklist-discovery-research.md
│   ├── verificacion-fuentes.md  Verificación de las URLs citadas
│   ├── matriz-ponderada.md      Ranking ponderado (33 productos)
│   ├── verificar_matriz.py      Consistencia raw ↔ matriz
│   ├── raw/                     34 sistemas relevados (argentina, latam, internacional)
│   └── sources/                 Fichas por fuente
├── docs/
│   ├── bitacora-inspeccion.md
│   ├── evidencias/              Verify + trazabilidad, pytest/ruff, explore, skills
│   ├── reflexion.md/.html/.pdf  Reflexión final (PDF es el entregable)
│   └── explore/                 Relevamientos OPSX
├── openspec/
│   ├── specs/turnos/            Spec vigente (capability turnos)
│   └── changes/
│       ├── archive/
│       │   └── 2026-10-15-c-01-foundation-setup/   Change archivado
│       └── archive/2026-10-10-crear-turno-sin-solapamientos/
├── backend/
│   ├── app/                     API FastAPI (core, db, models, schemas, services, routers)
│   ├── tests/                   Suite pytest (72 tests)
│   └── pyproject.toml
├── frontend/
│   ├── src/                     SPA React (pages, components, services, shared)
│   ├── index.html
│   ├── vite.config.ts           Proxy /api → http://localhost:8000
│   ├── tsconfig.json            TypeScript estricto
│   └── package.json
├── .agents/skills/              Skills del proyecto
└── .atl/skill-registry.md       Registro de skills por agente
```

## Puesta en marcha

### Requisitos

- Python 3.11+ (desarrollado con 3.14).
- Node.js 20+ y npm (para el frontend).
- Git.
- Los comandos usan el Python del entorno virtual directamente: no hace falta activarlo.

### Backend (PowerShell en Windows)

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -e "backend[dev]"

backend\.venv\Scripts\python.exe -m pytest backend\tests -v

backend\.venv\Scripts\ruff.exe check backend
backend\.venv\Scripts\ruff.exe format --check backend

backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

### Backend (Git Bash en Windows)

```bash
python -m venv backend/.venv
backend/.venv/Scripts/python -m pip install -e "backend[dev]"

backend/.venv/Scripts/python -m pytest backend/tests -v

backend/.venv/Scripts/ruff check backend
backend/.venv/Scripts/ruff format --check backend

backend/.venv/Scripts/python -m uvicorn app.main:app --reload --app-dir backend
```

### Backend (Linux / macOS)

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -e "backend[dev]"

backend/.venv/bin/python -m pytest backend/tests -v

backend/.venv/bin/ruff check backend
backend/.venv/bin/ruff format --check backend

backend/.venv/bin/python -m uvicorn app.main:app --reload --app-dir backend
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev      # servidor de desarrollo en http://localhost:5173
```

Verificación de tipos y build de producción:

```bash
cd frontend
npx tsc --noEmit        # chequeo de tipos (modo estricto)
npm run build           # build de producción en frontend/dist
npm run lint            # ESLint
npm run format:check    # Prettier
```

Levantá backend y frontend en paralelo: el servidor de Vite proxea `/api` hacia
`http://localhost:8000` (ver `frontend/vite.config.ts`), así que podés abrir
`http://localhost:5173` y consumir la API sin tocar CORS en dev.

Notas:

- El extra `[dev]` (definido en `backend/pyproject.toml`) instala **ruff**; pytest y httpx ya vienen en las dependencias base.
- Los tests usan SQLite **en memoria** (`DATABASE_URL=sqlite://` lo fija `backend/tests/conftest.py`); no tocan la base local. Estado actual: **72 tests passing**.
- El frontend usa **TypeScript estricto** (`frontend/tsconfig.json`) y no admite `any`. Las rutas privadas y el interceptor JWT llegan en `C-03`/`C-19`; el `services/api.ts` actual es el wrapper base.
- Copiá `backend/.env.example` a `backend/.env` y `frontend/.env.example` a `frontend/.env` para configurar el entorno local.
- Para la estructura por capas del backend y un ejemplo de uso de la API, ver [`backend/README.md`](backend/README.md).

## Endpoints implementados (v1 del change archivado)

| Método | Ruta | Respuesta |
|--------|------|-----------|
| `GET` | `/api/health` | `200` `{"status":"ok"}` |
| `POST` | `/turnos` | `201` turno `reservado` con `fecha_hora_fin` derivada de la prestación · `409` solapamiento (profesional, sillón o bloqueo) · `400` datos inválidos / pasado / recurso inactivo |

Reglas de negocio aplicadas: `fecha_hora_fin = inicio + duracion_minutos(prestación)`, intervalos `[inicio, fin)`, sin solapamiento por profesional **ni** por sillón/box, sin turnos en el pasado ni con recursos inactivos, `estado`/`fecha_hora_fin` no se aceptan del request (Pydantic `extra="forbid"`).

## Documentación de referencia

- `knowledge-base/01_vision_y_objetivos.md` → `10_preguntas_abiertas.md` (leer el archivo relevante antes de tocar cada área).
- `CHANGES.md` → plan completo: dependencias, paralelismo, camino crítico y governance por change.
- `AGENTS.md` → reglas duras del proyecto (no romperlas).
- `openspec/` → specs vigentes (`specs/`) y changes en curso o archivados (`changes/`).

## Notas de entrega

- Todos los datos en seeds, tests y ejemplos son **ficticios** (Ley 25.326, RN-DATOS-03): ningún dato clínico real ni de terceros en el repo.
- Sin secretos en el repo: claves e integraciones van en `.env` (ignorado por git).
