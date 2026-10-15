# Proposal

## Why

El scaffolding base (monorepo backend+frontend, config, tooling y scripts de arranque) aún no está completo en el repo. El change archivado crear-turno-sin-solapamientos dejó un backend funcional (health, modelos, servicios de turnos, validaciones y tests), pero faltan: app/core/security.py (stub), configuración CORS desde variables de entorno, archivos .env.example para backend y frontend, y la totalidad del scaffold frontend (Vite + React 18 + TypeScript), junto con el paquete/tooling base para el frontend y documentación de arranque.

Este cambio completa la fundación mínima para poder iniciar la siguiente fase (C-02: core-models) con la estructura acordada, sin reescribir lo ya existente.

## What Changes

- Backend: agregar app/core/security.py (stub) para tener la capa de seguridad preparada para JWT (C-03) sin implementar lógica aún.
- Backend: actualizar app/main.py para habilitar CORS usando CORS_ORIGINS desde configuración (Pydantic Settings). Mantener endpoints existentes (health, validation handler).
- Configuración: crear .env.example en backend/ (DATABASE_URL, SECRET_KEY, CORS_ORIGINS, TOKEN_EXPIRE_MIN). Crear .env.example en frontend/ (VITE_API_URL).
- Frontend: scaffolding inicial Vite + React 18 + TypeScript + react-router-dom con estructura src/{pages,components,services,shared}.
- Frontend: vite.config.ts con proxy /api hacia backend (http://localhost:8000), tsconfig.json estricto (sin any), package.json con scripts (dev/build/preview/lint/format).
- Frontend: src/services/api.ts wrapper base (fetch) preparado para inyectar JWT en futuras fases.
- Documentación: actualizar README con scripts de arranque frontend (npm run dev) manteniendo contenido en español rioplatense.

## Capabilities

### New Capabilities
- foundation-setup: Completa el scaffolding mínimo del monorepo (backend foundation + frontend scaffold) y archivos de configuración/arranque.

### Modified Capabilities
- *(ninguna)*

## Impact

- Archivos nuevos: backend/app/core/security.py, backend/.env.example, frontend/ completo, frontend/.env.example.
- Archivos modificados: backend/app/main.py (agregar CORS), README.md (scripts frontend) — cambios mínimos.
- Sin cambios en lógica de negocio, sin endpoints nuevos. Tooling frontend base añadido.
