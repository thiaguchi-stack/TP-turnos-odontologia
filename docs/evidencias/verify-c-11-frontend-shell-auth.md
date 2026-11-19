# Verify — `c-11-frontend-shell-auth`

Verificación de las tareas **7.3** (smoke contra backend local) y **7.4** (verificación final de integración) del change `openspec/changes/c-11-frontend-shell-auth/`, conforme a `docs/evidencias/README.md`.

- **Fecha de la corrida:** 2026-11-19.
- **Entorno:** `backend\.venv` (Python 3.14.7, uvicorn 0.54.0), Node v24.21.0, npm 11.19.0, Vitest 2.1.9. Dev server de Vite ya activo en `localhost:5173` (verificado que sirve este repo: el módulo transformado cita `frontend/src/main.tsx`).
- **Datos:** solo credenciales ficticias del seed y una base SQLite temporal en `%TEMP%\opencode\c11-smoke.db`. No se transcriben contraseñas ni datos de pacientes en este documento. No se tocó `backend/clinica.db`.
- **Alcance:** 2 tareas de verificación. No se escribió código de producción; las 26 tareas previas quedaron intactas.

---

## 1. Smoke HTTP (tarea 7.3)

Se levantó `uvicorn` embebido en el mismo proceso del script de smoke (hilo daemon, puerto 8000) y se apagó al finalizar. El script tomó las credenciales ficticias directamente de `backend/app/db/seed.py`, sin imprimirlas. Contra el proxy de Vite (`/api` → backend con `rewrite`) se obtuvieron **15/15 pasos OK**:

| # | Paso verificado | Resultado |
|---|-----------------|-----------|
| 1 | `GET /api/health` directo al backend | 200 |
| 2 | Dev server sirve la SPA (`#root`) | 200 |
| 3 | `GET /api/health` vía proxy → `/health` (404 esperado por el `rewrite`, riesgo documentado en `design.md`) | 404 |
| 4 | `POST /api/auth/login` urlencoded vía proxy (usuario admin del seed) → `access_token` + `token_type: Bearer` | OK |
| 5 | `GET /api/auth/me` con token de admin → `rol=admin`, sin `profesional_id` | OK |
| 6 | `GET /api/profesionales` sin header → 200 (catálogo público, contrato C-04/C-05) | 200 |
| 7 | `GET /api/profesionales` con Bearer → 200 | 200 |
| 8 | `GET /api/prestaciones` sin header → 200 (catálogo público) | 200 |
| 9 | `GET /api/prestaciones` con Bearer → 200 | 200 |
| 10 | `POST /api/auth/login` vía proxy (usuario odontólogo del seed) → token Bearer | OK |
| 11 | `GET /api/auth/me` con token de odontólogo → `rol=odontologo` con `profesional_id` | OK |
| 12 | Odontólogo consulta `/api/profesionales` con Bearer → 200 | 200 |
| 13 | Dev sirve `Navegacion.tsx` con el texto «Administración» | OK |
| 14 | Dev sirve `SinAcceso.tsx` con el texto «Sin acceso» | OK |
| 15 | 401 forzado en `/api/auth/me` con token inválido → 401 con `detalle`/`detail` (contenido no impreso) | 401 |

**Corrección de expectativa del smoke (no un defecto):** en una primera pasada se esperó 401 sin Bearer en los GET de catálogos. Los routers `backend/app/routers/profesionales.py:24-29` y `prestaciones.py:20-23` son públicos para `GET` y solo exigen `require_role("admin")` en POST/PUT/DELETE (`profesionales.py:41-79`, `prestaciones.py:26-51`). La expectativa se ajustó a 200; no se modificó producción.

### Comportamientos de UI cubiertos por tests, no por navegador

Este entorno no tiene automatización de navegador (no hay Playwright/Selenium instalados y C-18 es el change de E2E). Por eso los pasos del smoke que requieren clics se verificaron con React Testing Library sobre el mismo código que sirve Vite, y se registran como **no ejecutados en navegador real**:

| Paso pedido en 7.3 | Evidencia real | Estado |
|--------------------|----------------|--------|
| Redirect por rol tras el ingreso | `frontend/src/pages/Login.test.tsx:135` (admin → `/admin`) y `:153` (odontólogo → `/agenda`) | Verificado en RTL; no en navegador |
| Sin enlaces de administración para el odontólogo | `frontend/src/components/ProtectedRoute.test.tsx:78` (oculta «Administración», muestra agenda) y `:50` («Sin acceso» en `/admin`) | Verificado en RTL; no en navegador |
| Header Bearer en peticiones | `frontend/src/services/api.test.ts:35` (Bearer en petición privada) y `:48` (sin header en pública); pasos HTTP 6-9 confirman que el backend acepta el Bearer | Verificado |
| Cierre de sesión ante 401 forzado | `frontend/src/pages/Login.test.tsx:257` y `frontend/src/services/api.test.ts:109` + paso HTTP 15 (401 real del backend) | Verificado |
| Nueva pestaña sin sesión | `frontend/src/store/SesionContext.test.tsx:66` (solo `sessionStorage`) y `:106` (limpieza al cerrar); `localStorage` aparece solo en tests/setup de limpieza | Verificado por contrato de almacenamiento; no en pestaña real |
| Fecha en zona del consultorio | `frontend/src/shared/utils/date.test.ts:23,32,40,47`; `Intl.DateTimeFormat`/`toLocale` solo en `shared/utils` | Verificado |

---

## 2. Verificación final de integración (tarea 7.4)

| Comando | Resultado real |
|---------|----------------|
| `npm test` (baseline, antes de cualquier cambio) | 7 archivos, **49/49 tests pasan**; sin fallas preexistentes |
| `npm test` (final) | 7 archivos, **49/49 tests pasan** (21.10 s) |
| `npm run typecheck` | `tsc --noEmit`, exit 0, sin errores |
| `npm run lint` | `eslint .`, exit 0, sin errores |
| `npm run build` | `tsc && vite build`, exit 0; 49 módulos, `dist/assets/index-BiSb3Sf1.js` 171.13 kB (gzip 55.88 kB), 3.63 s |
| `openspec validate c-11-frontend-shell-auth --strict` | `Change 'c-11-frontend-shell-auth' is valid` (exit 0) |

Advertencias no bloqueantes en la suite: los *future flags* de React Router v7 (`v7_startTransition`, `v7_relativeSplatPath`) aparecen en stderr de tres tests; no son fallas.

### Reglas duras confirmadas por búsqueda

- **`any` en TypeScript:** 0 coincidencias en `frontend/src` para `:\s*any`, `as any`, `<any>`, `any[]`.
- **`fetch` directo:** 1 sola coincidencia, `frontend/src/services/api.ts:135` (el wrapper). Ninguna página/componente llama `fetch` directo.
- **`localStorage`:** solo en `setupTests.ts` y archivos `*.test.*` para limpieza/aseveraciones. La persistencia de producción usa `sessionStorage` (decisión lockada).
- **Fecha/hora:** `Intl.DateTimeFormat` solo en `shared/utils/date.ts:4,11` y su test; ningún componente formatea por su cuenta.
- **Contraseñas en claro:** 0 coincidencias de las claves del seed en `frontend/` ni en `docs/`; los fixtures usan valores ficticios (`clave-ficticia-de-prueba`, `clave-secreta-123`) y se asevera que no quedan en DOM ni logs (`Login.test.tsx:201`, `api.test.ts:143`).
- **Datos reales de pacientes:** 0 en fixtures. El único dato con forma de DNI en el frontend está en `ProtectedRoute.test.tsx:110` dentro de una aseveración **negativa** (verifica que la home pública no lo muestra). El seed es ficticio y no se modificó.

---

## 3. Tabla de evidencia (Strict TDD Mode)

| Tarea | Archivo de test / comando | Capa | Safety net | RED | GREEN | TRIANGULATE | REFACTOR | Resultado |
|-------|---------------------------|------|------------|-----|-------|-------------|----------|-----------|
| 7.3 | Script HTTP temporal `smoke_c11.py` + `Login.test.tsx`, `ProtectedRoute.test.tsx`, `SesionContext.test.tsx`, `api.test.ts` | Integración HTTP (uvicorn + proxy Vite) y UI con RTL | 49/49 en verde antes de empezar | N/A: tarea de verificación, no nueva funcionalidad | N/A: el comportamiento ya estaba en verde desde las tareas 2-6 | N/A: no se agregaron casos nuevos ni se modificó producción | N/A: no hubo código que refactorizar | PASS: 15/15 pasos HTTP y escenarios UI en verde; sin navegador real |
| 7.4 | `npm test`, `npm run typecheck`, `npm run lint`, `npm run build`, `openspec validate --strict`, greps de reglas duras | Toolchain + estático | 49/49 baseline y 49/49 final | N/A: verificación, no ciclo TDD | N/A: no se escribió código de producción | N/A: no se agregaron aserciones | N/A: no se agregaron aserciones | PASS: 49/49, 4 comandos exit 0, 6 reglas duras confirmadas |

No se escribieron aserciones triviales: no se crearon ni modificaron tests en estas dos tareas.

---

## 4. Hallazgos y limitaciones

1. **Startup con `clinica.db` (preexistente, fuera de C-11):** `uvicorn app.main:app` con la DB por defecto se colgó en `Running upgrade -> 001`. Inspección de `backend/clinica.db`: las 9 tablas existen pero `alembic_version` está vacío, así que Alembic reintenta la baseline sobre un esquema ya presente. Con una DB temporal limpia el arranque tarda ~0.7 s y el smoke corre completo. **No se corrigió**: no es un defecto de C-11 y cualquier reparación de la DB local requiere decisión del orquestador.
2. **Sin E2E de navegador:** redirect por rol, menú por rol, cierre por 401 y pestaña nueva se cubren con RTL; la demostración en navegador real queda para C-18.
3. **`/api/health` vía proxy:** devuelve 404 por el `rewrite` de `/api` a `/health`; riesgo ya documentado en `design.md` Risks, fuera del alcance de este change.
4. **Sin cambios de producción:** no se reveló ningún defecto nuevo en C-11; no hizo falta avisar al orquestador para corregir código.

---

## 5. Estado final

- Tareas 7.3 y 7.4 verificadas y marcadas en `openspec/changes/c-11-frontend-shell-auth/tasks.md`.
- Progreso del change: **28/28 tareas completas**.
- Próxima acción recomendada: revisar el informe de auditoría de auth y el gate humano de governance MEDIO, y archivar con `/opsx-archive` (no se hizo commit ni deploy).
