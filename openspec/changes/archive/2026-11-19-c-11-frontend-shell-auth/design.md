# Design

## Context

Ver `proposal.md` para el motivo. Estado observado antes de este change:

- La SPA solo tiene `BrowserRouter` con `/` y `Home` (`frontend/src/App.tsx:5-13`), un encabezado (`frontend/src/components/Encabezado.tsx:5-11`) y `formatearFecha` en `frontend/src/shared/utils/date.ts:1-19`, que ya usa `America/Argentina/Buenos_Aires`.
- `frontend/src/services/api.ts:1-20` es un wrapper `fetch` sin token, con error genérico y sin `status` tipado.
- `frontend/package.json:6-34` no tiene runner de tests ni dependencias de testing; `tsconfig.json:10-19` es estricto y no admite `any`.
- `frontend/vite.config.ts:8-13` proxea `/api` sin `rewrite`, pero los routers del backend están montados sin prefijo (`backend/app/main.py:33-36`). La única excepción es `GET /api/health` (`backend/app/main.py:39`).
- Contrato ya implementado y verificado en C-03: `POST /auth/login` con `OAuth2PasswordRequestForm` (`backend/app/routers/auth.py:17-25`) → `{access_token, token_type}` (`backend/app/schemas/auth.py:6-8`); claims `sub`/`rol`/`profesional_id`/`exp` (`backend/app/services/auth_service.py:104-114`); identidad autoritativa en `GET /auth/me` → `{id, email, rol, profesional_id}` (`backend/app/schemas/auth.py:11-17`). Errores 401/403/429 con `{"detalle": ...}` (`backend/app/core/handlers.py:17-35`), OAuth2 nativo con `{"detail": ...}` y validación 400 con `{"detail": ...}` (`backend/app/main.py:44-48`).
- Restricciones: reglas duras de `AGENTS.md`, KB (`03_actores_y_roles.md`, `05_reglas_de_negocio.md` §RN-AU/RN-DATOS, `07_flujos_principales.md:33`, `08_arquitectura_propuesta.md` §Seguridad), strict TDD Mode (RED → GREEN → TRIANGULATE → REFACTOR), textos en español rioplatense y datos ficticios. Governance MEDIO; C-03 ya archivado.

## Goals / Non-Goals

**Goals:**

- Dejar una SPA demostrable donde se pueda ingresar con el seed del backend, navegar según el rol y ejercitar `/profesionales` y `/prestaciones` con el token inyectado.
- Hacer del wrapper HTTP el único punto que adjunta el JWT y traduce errores; ninguna página llama `fetch` directo.
- Que la sesión se hidrate desde `/auth/me` y se comporte igual ante recarga, token vencido y cierre explícito.
- Cubrir los escenarios de auth con tests unitarios test-first y dejar un smoke manual documentado.

**Non-Goals:**

- Implementar reserva, grilla, agenda, altas/ediciones de catálogos, vista de completar turnos ni seed demo (C-12 a C-16); las pantallas quedan como placeholders.
- Modificar el backend, su CORS, su rate limit o sus rutas (C-17); agregar E2E (C-18).
- Depurar el JWT en el cliente para decidir identidad o permisos; el backend sigue siendo autoridad (RN-AU-01/02/03).
- Persistir sesión entre pestañas o guardar contraseñas.
- Editar `README.md` o `CHANGES.md` en esta fase: las correcciones se dejan como tareas para apply.

## Decisions

1. **Base URL y proxy con `rewrite` (decisión lockada).** `frontend/.env.example` pasa a `VITE_API_URL=/api` y `frontend/vite.config.ts` agrega `rewrite: (path) => path.replace(/^\/api/, "")` sobre el proxy existente. Así `/api/auth/login` llega a `/auth/login` en `localhost:8000` sin tocar el backend ni depender de CORS. Alternativa descartada: `VITE_API_URL=http://localhost:8000` (exige CORS y expone el puerto; el proxy ya existe y la KB lo prevé en `08_arquitectura_propuesta.md:35,56`).
2. **Tests con Vitest + React Testing Library + jsdom (decisión lockada).** Se agregan como devDependencies y un script `test`; `setupTests.ts` registra `jest-dom` y limpia el DOM. Alternativa descartada: solo smoke manual, que no cumple el strict TDD Mode ni deja regresión para los tres escenarios obligatorios (login OK, redirect por rol, 401 → logout). Si se usa `@testing-library/jest-dom`, se incluye su tipado en `tsconfig`/`vite-env.d.ts` sin `any`.
3. **Persistencia en `sessionStorage` (decisión lockada).** Guarda solo el token; la identidad vive en memoria y se rehidrata. Alternativa descartada: `localStorage` (sobrevive al cierre del navegador y aumenta exposición del token).
4. **Store de sesión con Context + hook propio.** `SesionContext.tsx` expone `{usuario, rol, profesional_id, estado, iniciarSesion, cerrarSesion, hidratar}`; `useSesion.ts` es el único acceso. Alternativa descartada: Zustand (nueva dependencia sin beneficio para una SPA de un solo tenant; el roadmap admite "context/Zustand"). El estado incluye `cargando` para evitar parpadeos durante la hidratación.
5. **Flujo de login en dos pasos.** La página envía `POST /auth/login` como `URLSearchParams` (`username`/`password`) a través del wrapper; con el `access_token` se guarda el token y se llama `GET /auth/me` para poblar la sesión. Alternativa descartada: decodificar el JWT en el cliente (no es fuente de verdad y expira distinto; `/auth/me` valida usuario activo en DB, `backend/app/services/auth_service.py:89-101`). La contraseña nunca se guarda ni se incluye en mensajes de error o logs.
6. **Wrapper tipado con callback de expiración.** `apiFetch<T>` acepta cuerpo JSON o `URLSearchParams`, calcula la URL con `VITE_API_URL`, adjunta Bearer solo si hay token, expone `ApiError` con `status` y `mensaje` leído de `detalle ?? detail`, y ante 401 invoca `cerrarSesion()` y navega a `/login`. Alternativa descartada: lanzar `Error` con texto del `statusText` (pierde el mensaje del backend y obliga a cada página a detectar 401).
7. **Guard de ruta y navegación por rol.** `ProtectedRoute` recibe los roles permitidos, espera a que termine la hidratación y redirige a `/login` sin sesión o a `/sin-acceso` con rol no autorizado. La navegación oculta administración al odontólogo. Destinos post-login: admin → `/admin` (placeholder), odontólogo → `/agenda` (placeholder). Alternativa descartada: mostrar u ocultar enlaces sin guard (un visitante podría navegar directo y ver la shell). El guard es UX: no reemplaza `require_role`/`require_odontologo_own` en el backend.
8. **Fecha/hora compartida.** Se reutiliza `frontend/src/shared/utils/date.ts` vía `shared/utils/index.ts`; si hace falta una variante, se agrega ahí. Alternativa descartada: `toLocaleString` en cada componente (rompe la regla dura y la consistencia `es-AR`/zona del consultorio).
9. **Correcciones documentales diferidas.** `README.md:183`, `CHANGES.md:342` y el proxy quedan como tareas explícitas del apply; este propose no toca esos archivos.

## Risks / Trade-offs

- [El `rewrite` de `/api` convierte `/api/health` en `/health`, que no existe en el backend (`backend/app/main.py:39`)] → C-11 no consume health desde la SPA; si se necesita, se agregará una regla de proxy específica o se alineará el backend en otro change, sin alterar esta decisión.
- [`/auth/me` rechaza tokens de usuarios inactivados después del login (`backend/app/services/auth_service.py:97-99`)] → la hidratación trata el 401 como sesión expirada: limpia token, identidad y redirige al ingreso con mensaje en español.
- [El token se pierde al cerrar la pestaña por diseño] → se documenta en el smoke que cada demo arranca con un login nuevo; es el comportamiento acordado.
- [Rate limit de 5 fallos por 60 s (`backend/app/core/handlers.py:31-35`) puede trabar la demo] → el smoke usa credenciales correctas y espacia los intentos negativos; los tests unitarios mockean la respuesta 429.
- [StrictMode dispara efectos dos veces en desarrollo] → la hidratación se implementa con guarda de "en curso"/cleanup para no duplicar `/auth/me`.
- [Agregar dependencias de test al locked `package-lock.json`] → la tarea de setup corre `npm install` y verifica `npm run typecheck` + `npm run lint` + `npm test` antes de seguir.
- [El guard de cliente puede dar falsa sensación de seguridad] → se documenta que la autoridad es el backend y se cubre con tests que una ruta protegida sin sesión no renderiza contenido.

## Migration Plan

No hay migración de base de datos ni cambios de backend. En la fase de apply: (1) setup de proxy/env/dependencias de test, (2) tipos + wrapper + store test-first, (3) router/guard/navegación y pantallas placeholder, (4) login e hidratación, (5) correcciones documentales y smoke. Verificación local: `npm test`, `npm run typecheck`, `npm run lint`, `npm run build` y smoke contra `uvicorn` + `npm run dev`. Rollback: revertir los archivos del frontend tocados y `package.json`/`package-lock.json`/`.env.example`; sin datos que migrar.

## Open Questions

Ninguna. Las decisiones que afectaban el alcance (base URL, runner de tests y persistencia) están resueltas y lockadas; los destinos post-login y el manejo del 401 están fijados arriba.
