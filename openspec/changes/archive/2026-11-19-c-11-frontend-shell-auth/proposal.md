# Proposal

## Why

Los cambios C-01 a C-05 dejaron un backend funcional (health, auth JWT/RBAC, profesionales y prestaciones) pero la SPA hoy solo tiene una home estática con un wrapper `fetch` sin token (`frontend/src/App.tsx:5-13`, `frontend/src/services/api.ts:3-20`). Sin cascarón ni sesión en el cliente, no se puede demostrar el flujo de login, la navegación por rol ni el acceso a las rutas privadas desde una UI real.

## What Changes

- Incorporar un router con zona pública y zona protegida, con `ProtectedRoute` que exige sesión vigente y rol (`admin` u `odontologo`) antes de renderizar; acceso denegado muestra una pantalla de "Sin acceso" en español rioplatense.
- Agregar layout y navegación que cambia según el rol: el odontólogo no ve enlaces de administración; las pantallas de reserva/agenda quedan como placeholders (C-12 a C-15 las implementan).
- Convertir `services/api.ts` en un wrapper tipado con interceptor JWT: inyecta `Authorization: Bearer`, propaga `status`, tolera cuerpos de error `detalle` y `detail`, y ante 401 cierra la sesión y redirige al login.
- Crear el store de sesión con `usuario`, `rol`, `profesional_id` y token persistido en `sessionStorage` (la sesión muere al cerrar la pestaña), con hidratación desde `GET /auth/me` al arrancar.
- Conectar la página `Login` a `POST /auth/login` con `application/x-www-form-urlencoded` (`username`/`password`), estados de carga y error (401, 403, 429), sin guardar contraseñas y sin decodificar el JWT en el cliente como fuente de verdad.
- Reutilizar `frontend/src/shared/utils/date.ts` para todo formateo de fecha/hora en zona `America/Argentina/Buenos_Aires`; no duplicar utilidades.
- Fijar el proxy de Vite con `rewrite` de `/api` al backend y el default `VITE_API_URL=/api`, para no depender de CORS en desarrollo.
- Incorporar Vitest + React Testing Library + jsdom y tests unitarios de login correcto, redirección por rol y expiración de sesión (401 → logout), más un smoke documentado contra el backend local.
- Registrar como tareas (sin editarlos en este change) las correcciones de documentación: `README.md:183` (atribuye el interceptor a `C-03/C-19` inexistente → `C-11`), `CHANGES.md:342` ("Flujo 2 (Login)" → flujo de login en `knowledge-base/07_flujos_principales.md:33`) y el proxy de `frontend/vite.config.ts:8-13`.

**BREAKING**: ninguno. El backend y su contrato no se modifican.

## Capabilities

### New Capabilities

- `spa-auth-session`: sesión del personal en la SPA, zonas pública y protegida con control de acceso por rol, wrapper HTTP con JWT, login e hidratación de identidad contra la API.

### Modified Capabilities

- Ninguna. `user-auth` describe el contrato del backend y no cambia: C-11 solo lo consume desde el cliente.

## Impact

- Frontend: `frontend/src/App.tsx`, `main.tsx`, `services/api.ts`, `components/`, `pages/`, `store/`, `types/`, `shared/utils/`, nuevos tests y `setupTests.ts`.
- Configuración: `frontend/vite.config.ts`, `frontend/package.json` y `frontend/.env.example` (devDependency de tests, proxy con `rewrite`, `VITE_API_URL=/api`).
- Documentación: correcciones pendientes en `README.md` y `CHANGES.md`, registradas en `tasks.md` para la fase de apply.
- Backend: sin cambios; se consumen `/auth/login`, `/auth/me`, `/profesionales` y `/prestaciones` tal como están montados.
- Dependencias: C-03 (archivado). Desbloquea C-12, C-13, C-14 y C-15. Governance: MEDIO.
