# Design

## Context

See proposal.md for motivation. Estado actual: backend ya tiene FastAPI con health, modelos, servicios/routers de turnos, config básica y tests (cambio archivado). Faltan app/core/security.py, CORS configurable desde CORS_ORIGINS, .env.example (backend/frontend), y scaffold frontend completo (Vite+React+TS, proxy, api.ts). 

## Goals / Non-Goals

**Goals:**
- Agregar stub de seguridad sin lógica (preparado para JWT en C-03).
- Habilitar CORS desde configuración (settings.cors_origins) en app/main.py sin romper endpoints existentes.
- Crear .env.example en backend y frontend con variables acordadas (KB/CHANGES).
- Generar scaffold mínimo de frontend conforme a estructura propuesta (src/{pages,components,services,shared}), con proxy /api y api.ts base.
- Actualizar README con scripts de arranque frontend.

**Non-Goals:**
- Implementar auth/JWT (eso es C-03). Solo stub.
- Agregar endpoints nuevos o modificar lógica de turnos.
- Crear componentes de UI completos (solo estructura y archivos mínimos funcionales para build/dev).
- Reescribir archivos backend ya existentes.

## Decisions

- **CORS**: usar fastapi.middleware.cors.CORSMiddleware con allow_origins=settings.cors_origins (lista). Parsear CORS_ORIGINS desde env (coma-separados) en Settings o aceptarlos como lista; dado que pydantic-settings puede parsear strings, usar field_validator o definir como str|list[str] → normalizar a list[str]. Alternativa: hardcode solo localhost (menos flexible) — descartada para alinearse con CORS_ORIGINS configurable.
- **Security stub**: app/core/security.py mínimo (docstrings o funciones vacías) para evitar import errors; sin dependencias nuevas innecesarias. Evita tocar lógica de auth.
- **Frontend scaffold**: Vite + React 18 + TypeScript. react-router-dom para futuras rutas. tsconfig.json estricta; evitar any. Estructura por capas (services, shared) siguiendo KB 08.
- **Proxy**: vite.config.ts con proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } } para dev.
- **api.ts base**: wrapper simple con fetch que acepte base URL desde import.meta.env.VITE_API_URL o relativo con proxy. No añadir interceptores JWT aún (eso corresponde a cuando haya auth).
- **.env.example**: valores ficticios, sin secretos reales (coherente con RN-DATOS-03).
- **Delta-only**: nunca sobreescribir archivos backend existentes. Verificar presencia antes de escribir (tasks marcadas para hacerlo idempotente).

## Risks / Trade-offs

- [Riesgo menor] Diferencia entre scaffold generado por npm create vite@latest y estructura mínima requerida: generar solo lo estrictamente necesario para cumplir spec (evitar archivos innecesarios) para mantener repo limpio.
- [Trade-off] No instalar dependencias en esta etapa (solo crear archivos). La verificación puede limitarse a existencia/estructura de archivos según criterio de terminación.
- [Mitigación] Tasks explícitas: crear security.py, modificar main.py solo añadiendo CORS, crear env examples, crear frontend mínimo.

## Migration Plan

N/A (cambios de scaffolding, sin migraciones de datos).

## Open Questions

Ninguna. Alcance acotado al delta.
