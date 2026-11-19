# Tasks

## 1. Setup de toolchain, proxy y entorno

- [x] 1.1 Agregar `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event` y `jsdom` como devDependencies en `frontend/package.json`, correr `npm install` y verificar que `package-lock.json` quedó actualizado sin `any` ni dependencias de producción nuevas.
- [x] 1.2 Configurar el runner: script `test` con `vitest run`, `test.environment = "jsdom"`, `setupFiles: ["./src/setupTests.ts"]` en `frontend/vite.config.ts`, tipados de Vitest en `tsconfig.json`/`vite-env.d.ts` y `src/setupTests.ts` con `jest-dom` + limpieza del DOM; verificar con un test trivial que `npm test` termina en verde y `npm run typecheck` pasa.
- [x] 1.3 Cerrar el gap del proxy: en `frontend/vite.config.ts` agregar `rewrite: (path) => path.replace(/^\/api/, "")` a la regla `/api` existente y dejar `VITE_API_URL=/api` en `frontend/.env.example`; verificar con `curl http://localhost:5173/api/health` contra el backend local que la petición llega al puerto 8000 y documentar en el smoke que `/api/health` se reescribe a `/health` (fuera del alcance de C-11, ver `design.md` Risks).
- [x] 1.4 Verificar que `npm run lint` y `npm run build` siguen pasando antes de tocar código de aplicación.

## 2. Wrapper HTTP tipado con JWT (TDD)

- [x] 2.1 [RED] Escribir `frontend/src/services/api.test.ts` con casos: petición privada adjunta `Authorization: Bearer <token>`, petición pública no adjunta header, error 401 con `{"detalle": ...}` y con `{"detail": ...}` expone `status` y mensaje, y errores 403/429/400 con `status` tipado; verificar que `npm test -- src/services/api.test.ts` falla por módulo/API inexistente.
- [x] 2.2 [GREEN] Implementar `frontend/src/types/auth.ts` (`Token`, `UsuarioSesion`, `Rol`) y `frontend/src/services/api.ts` con `ApiError` (`status`, `mensaje`), cuerpo JSON o `URLSearchParams`, lectura de `detalle ?? detail` y callback ante 401; verificar que `npm test -- src/services/api.test.ts` pasa y `npm run typecheck` no reporta `any`.
- [x] 2.3 [TRIANGULATE] Agregar casos de borde al test: token vacío no envía header, respuesta 401 sin cuerpo no rompe el wrapper, la contraseña nunca aparece en el error ni en `console`, y un 200 con cuerpo vacío no se parsea dos veces; verificar que los nuevos tests fallan antes del ajuste y pasan después.
- [x] 2.4 [REFACTOR] Extraer la normalización de mensajes y la construcción de headers a helpers internos sin cambiar el comportamiento cubierto; verificar `npm test -- src/services/api.test.ts` + `npm run lint`.

## 3. Store de sesión y persistencia (TDD)

- [x] 3.1 [RED] Escribir `frontend/src/store/SesionContext.test.tsx` con casos: guardar token en `sessionStorage`, no usarlo en `localStorage`, hidratar `id`/`email`/`rol`/`profesional_id` desde `GET /auth/me` (no desde el JWT), limpiar token e identidad al cerrar sesión y manejar 401 de hidratación como sesión expirada; verificar que el test falla antes de existir el store.
- [x] 3.2 [GREEN] Implementar `frontend/src/store/SesionContext.tsx` y `frontend/src/store/useSesion.ts` con estado `cargando`, `iniciarSesion`, `hidratar` y `cerrarSesion`, persistiendo solo el token en `sessionStorage`; verificar `npm test -- src/store/SesionContext.test.tsx` en verde y `npm run typecheck`.
- [x] 3.3 [TRIANGULATE] Agregar casos: dos hidrataciones concurrentes (StrictMode) no duplican `/auth/me`, un token de odontólogo conserva su `profesional_id`, y cerrar sesión vacía también el estado en memoria; verificar que fallan antes del ajuste y pasan después.
- [x] 3.4 [REFACTOR] Simplificar el reducer/contexto sin tocar la API pública del hook; verificar `npm test -- src/store/SesionContext.test.tsx` + `npm run lint`.

## 4. Router, guard de roles y navegación (TDD)

- [x] 4.1 [RED] Escribir `frontend/src/components/ProtectedRoute.test.tsx` y un test de navegación con casos: visitante sin sesión que navega a `/agenda` cae en `/login`, odontólogo que navega a `/admin` ve "Sin acceso", admin ve los enlaces de administración y el odontólogo no; verificar que fallan antes de implementar el router.
- [x] 4.2 [GREEN] Modificar `frontend/src/App.tsx` para definir zonas pública y protegida, crear `ProtectedRoute.tsx`, `Layout.tsx`, `Navegacion.tsx` y `SinAcceso.tsx` en `frontend/src/components/`, y pantallas placeholder `Login`, `DashboardAdmin` y `Agenda` en `frontend/src/pages/` con textos en español rioplatense; verificar `npm test -- src/components/ProtectedRoute.test.tsx` en verde y `npm run typecheck`.
- [x] 4.3 [TRIANGULATE] Agregar casos: ruta protegida directa sin pasar por la home no muestra datos, la home pública sin token no muestra datos clínicos ni de terceros, la navegación del odontólogo oculta acciones de administración pero muestra su agenda, y `/login` es alcanzable sin sesión; verificar que fallan antes del ajuste y pasan después.
- [x] 4.4 [REFACTOR] Unificar el layout público/privado sin duplicar encabezados; verificar `npm test -- src/components/ProtectedRoute.test.tsx` + `npm run lint`.

## 5. Login e hidratación en el arranque (TDD)

- [x] 5.1 [RED] Escribir `frontend/src/pages/Login.test.tsx` con casos: envío `urlencoded` a `/api/auth/login` con `username`/`password`, estado de carga visible, guardado del token y redirect según rol, error 401 con mensaje legible, error 429 y que la contraseña no queda en el DOM ni en logs; verificar que falla antes de conectar la página.
- [x] 5.2 [GREEN] Implementar `frontend/src/pages/Login.tsx` usando `useSesion()` y el wrapper, con loading y errores en español rioplatense, y cablear la hidratación desde `/auth/me` en el arranque de `frontend/src/main.tsx`/`App.tsx` sin decodificar el JWT; verificar `npm test -- src/pages/Login.test.tsx` en verde y `npm run typecheck`.
- [x] 5.3 [TRIANGULATE] Agregar casos: recarga con token vigente restaura la sesión, token vencido al hidratar redirige a `/login`, y un 401 en una petición posterior cierra la sesión y redirige (escenario de expiración de `specs/spa-auth-session/spec.md`); verificar que fallan antes del ajuste y pasan después.
- [x] 5.4 [REFACTOR] Extraer el mensaje de error de login al mismo normalizador del wrapper y revisar que no queden `fetch` directos fuera de `services/api.ts`; verificar `npm test` completo + `npm run lint` + `npm run build`.

## 6. Fecha/hora compartida (TDD)

- [x] 6.1 [RED] Escribir `frontend/src/shared/utils/date.test.ts`, con un render del placeholder que muestra la fecha, y aseverar formato `es-AR` en `America/Argentina/Buenos_Aires` aunque el entorno del test use otra zona; verificar que falla si se formatea con la zona del navegador.
- [x] 6.2 [GREEN] Reutilizar `frontend/src/shared/utils/date.ts` y, si falta algún formato, agregarlo solo ahí y exportarlo desde `frontend/src/shared/utils/index.ts` sin duplicar la utilidad; verificar `npm test -- src/shared/utils/date.test.ts` en verde y `npm run typecheck`.
- [x] 6.3 [TRIANGULATE] Agregar caso de cruce de día/mes por zona horaria y verificar que ningún componente calcula fechas por su cuenta (`grep` de `toLocale`/`Intl.DateTimeFormat` fuera de `shared/utils`); documentar el resultado en el informe del smoke.
- [x] 6.4 [REFACTOR] Ajustar nombres y exports de la utilidad sin cambiar la salida; verificar `npm test` completo + `npm run lint`.

## 7. Correcciones documentales y verificación de integración

- [x] 7.1 Corregir `README.md:183`: reemplazar la referencia a `C-03/C-19` (inexistente) por `C-11` como responsable de las rutas privadas y el interceptor JWT, sin tocar el resto del README; verificar con `grep -n "C-03/C-19" README.md` que no quedan ocurrencias y que la nueva línea nombra C-11.
- [x] 7.2 Corregir `CHANGES.md:342`: reemplazar "§Flujo 2 (Login)" por el puntero correcto al paso de login inline en `knowledge-base/07_flujos_principales.md:33` dentro del Flujo 2 (Gestión de agenda); verificar que `CHANGES.md` no queda con esa referencia errónea y que la línea apunta al archivo y número reales.
- [x] 7.3 Ejecutar el smoke contra el backend local siguiendo `docs/evidencias/README.md`: levantar `uvicorn` y `npm run dev`, entrar con las credenciales ficticias del seed, verificar redirect por rol, navegación sin enlaces de administración para el odontólogo, header Bearer en `/api/profesionales` y `/api/prestaciones`, cierre de sesión ante 401 forzado y nueva pestaña sin sesión; registrar pasos y resultados (sin passwords ni datos reales de pacientes) en `docs/evidencias/verify-c-11-frontend-shell-auth.md`.
- [x] 7.4 Verificación final de integración: correr `npm test`, `npm run typecheck`, `npm run lint`, `npm run build` y `openspec validate c-11-frontend-shell-auth --strict`, y confirmar que no hay `any`, `fetch` directo fuera del wrapper, contraseñas en claro ni datos reales en los fixtures.

## Workflow follow-up

- Revisar el informe `docs/evidencias/audit-auth-c-11-frontend-shell-auth.md` y pasar el gate humano de governance MEDIO antes de archivar.
- Archivar el change con `/opsx-archive` cuando las tareas y la revisión estén completas.
