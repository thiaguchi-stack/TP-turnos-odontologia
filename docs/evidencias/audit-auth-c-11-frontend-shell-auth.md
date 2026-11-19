# Auditoría de contrato de auth — c-11-frontend-shell-auth

## Alcance

- Fecha: 2026-11-19. Auditoría **previa a la implementación** de un change de governance MEDIO; revisión, no aprobación de gobernanza ni escritura de código de producción.
- Artefactos leídos: `openspec/changes/c-11-frontend-shell-auth/proposal.md`,
  `design.md`, `specs/spa-auth-session/spec.md`, `tasks.md`.
- KB citada: `knowledge-base/03_actores_y_roles.md`,
  `knowledge-base/05_reglas_de_negocio.md`,
  `knowledge-base/07_flujos_principales.md`,
  `knowledge-base/08_arquitectura_propuesta.md`,
  `knowledge-base/09_decisiones_y_supuestos.md`, `AGENTS.md`.
- Contrato del backend verificado como contexto: `backend/app/routers/auth.py:14-30`,
  `backend/app/schemas/auth.py:6-17`, `backend/app/services/auth_service.py:89-114`,
  `backend/app/core/handlers.py:17-35`, `backend/app/core/deps.py:12-37`,
  `backend/app/main.py:33-48`.
- Estado previo del frontend: `frontend/src/App.tsx:5-13`,
  `frontend/src/services/api.ts:1-20`, `frontend/package.json:6-34`.
- La skill es de revisión: no escribe código de producción.

## Reglas transcriptas

Texto literal verificado contra los archivos reales:

- RN-AU-01 — "Las rutas de administración exigen JWT válido; el paciente reserva sin autenticarse (solo con datos de contacto + token de cancelación)." (`knowledge-base/05_reglas_de_negocio.md:9`)
- RN-AU-02 — "Un usuario `odontologo` solo ve y modifica turnos del profesional asociado (`usuario.profesional_id`)." (`knowledge-base/05_reglas_de_negocio.md:10`)
- RN-AU-03 — "Solo un usuario `admin` puede crear/editar profesionales, prestaciones, bloqueos, sillones y usuarios." (`knowledge-base/05_reglas_de_negocio.md:11`)
- RN-AU-04 — "Las contraseñas se guardan hasheadas (bcrypt/argon2); nunca en texto plano." (`knowledge-base/05_reglas_de_negocio.md:12`)
- DD-07 — "Capa de servicios + routers delgados en FastAPI | Testeabilidad y cumplimiento de reglas de negocio en un solo lugar (RN-TU) | Lógica en routers (menos testeable)" (`knowledge-base/09_decisiones_y_supuestos.md:13`)
- DD-08 — "Tratamiento de datos conforme a Ley 25.326 (consentimiento, acceso autorizado) | El sistema maneja datos personales de salud; responsabilidad desde el diseño, aunque sea un TP | Ignorar privacidad (inaceptable para datos de salud)" (`knowledge-base/09_decisiones_y_supuestos.md:14`)
- RN-DATOS-01 — "Los datos personales y de salud de los pacientes se tratan conforme a la Ley 25.326 (Argentina): finalidad determinada, consentimiento en la reserva, acceso solo a personal autorizado." (`knowledge-base/05_reglas_de_negocio.md:42`)
- RN-DATOS-02 — "No se expone información clínica en rutas públicas: la reserva online recibe únicamente datos de contacto; la ficha clínica es backlog v2." (`knowledge-base/05_reglas_de_negocio.md:43`)

## Mapa regla / escenario / evidencia

| Regla | Aplica | Escenario(s) | Evidencia (archivo:línea) | Estado |
|-------|--------|--------------|---------------------------|--------|
| RN-AU-01 | Sí — el change agrega rutas privadas en la SPA, exige JWT en el wrapper y mantiene la home pública sin token | OK 401 y redirect: spec.md:19-23; Error de login 401: spec.md:51-55; Borde petición pública sin Authorization: spec.md:105-109 | `tasks.md:12,26,28,33,35,49`; `design.md` Decisions 6-7; `backend/app/core/deps.py:12-19` | Verificado |
| RN-AU-02 | Sí, en el alcance cliente: la sesión conserva `profesional_id` de `/auth/me` y el odontólogo no ve administración; no hay pantallas de turnos en C-11 (son C-13) | OK: spec.md:35-39, 67-71; Borde 403/negación en cliente: spec.md:35-39 | `tasks.md:19-21,26,28`; `backend/app/services/auth_service.py:89-101` (autoridad en backend) | Verificado |
| RN-AU-03 | Sí — la navegación y el guard de administración distinguen admin de odontólogo | OK admin: spec.md:29-33; Error odontólogo: spec.md:35-39 | `tasks.md:26,28,49`; `backend/app/core/deps.py:22-37` (RBAC real en backend) | Verificado |
| RN-AU-04 | Sí — se manipula la contraseña en el login del cliente; el hasheo sigue siendo responsabilidad del backend ya implementado | OK: spec.md:43; Borde sin contraseña en DOM/logs/error: spec.md:51-55; `tasks.md:14,33` | `tasks.md:14,33,36`; `design.md` Decisions 5 y 6; `backend/app/schemas/auth.py:6-17` | Verificado |
| DD-07 | Sí — constraint arquitectónica: sesión y HTTP en capas de servicio/store, páginas delegadas; no se modifica el backend | Sin escenario de usuario (decisión de diseño) | `design.md` Decisions 4-6; `tasks.md:13,20,27,34` | Verificado |
| DD-08 | Sí — acceso autorizado a la zona privada y sin datos clínicos en la pública | OK: spec.md:25-39; Borde: spec.md:13-17, 105-109 | `tasks.md:26,28,33,49`; `knowledge-base/08_arquitectura_propuesta.md:39-46` | Verificado |
| RN-DATOS-01 | No — C-11 no recolecta datos de pacientes ni pide consentimiento; eso pertenece a la reserva de C-12 (`CHANGES.md:348-353`). Acá rige solo el acceso autorizado, cubierto por RN-AU-01/DD-08 | — | `knowledge-base/05_reglas_de_negocio.md:42`; `CHANGES.md:350` | No aplica |
| RN-DATOS-02 | Sí — la home y la navegación pública no exponen datos clínicos ni de terceros | OK: spec.md:13-17; Borde respuesta pública sin token: spec.md:105-109 | `tasks.md:12,28,49`; `knowledge-base/08_arquitectura_propuesta.md:45` | Verificado |

Estado usado solo como `Verificado`, `No verificado` o `No aplica`. "Verificado" significa que el escenario y su forma de comprobación figuran en los artefactos leídos; **no** significa que el código exista todavía (el change está en fase de propose).

## Chequeo de reglas duras

- NUNCA exponer ni loguear `password_hash`: verificado en el plan — la respuesta de login solo se usa para tomar `access_token` (`spec.md:43`), `UsuarioSesion` se hidrata con `/auth/me` (`spec.md:65`), y los tests aseveran que la contraseña no aparece en errores ni en `console` (`tasks.md:14,33`). El hash sigue sin salir del backend (`backend/app/schemas/auth.py:6-17`; `knowledge-base/08_arquitectura_propuesta.md:42`).
- NUNCA exponer rutas privadas sin JWT válido ni saltear RBAC: verificado — guard por rol en cliente (`spec.md:25-39`, `tasks.md:26,28`) con `admin`/`odontologo`; `require_role` y `require_odontologo_own` siguen en el backend (`backend/app/core/deps.py:22-37`). El guard es UX, no autoridad (DD-07, `design.md` Decisions 7).
- NUNCA aceptar `estado` desde la reserva pública: no aplica — C-11 no crea turnos ni expone formularios de reserva; la reserva es C-12. La UI pública es solo la home (`spec.md:11-17`).
- NUNCA incluir secretos ni datos reales de pacientes: verificado — el smoke usa credenciales ficticias del seed y prohíbe passwords en el informe (`tasks.md:49`), y los tests son de sesión/HTTP sin datos de pacientes (`tasks.md:12-22`). `VITE_API_URL=/api` no es secreto (`design.md` Decision 1).
- NUNCA escribir código de producción en esta revisión: verificado — el propose creó solo `proposal.md`, `design.md`, `specs/spa-auth-session/spec.md`, `tasks.md`; el informe es el único archivo nuevo fuera de `openspec/`. No se aprobó la implementación ni se ejecutó apply.
- NUNCA poner lógica de negocio en routers: verificado — no se toca el backend; en el cliente la lógica de sesión y HTTP se concentra en store/servicio y las páginas delegan (`design.md` Decisions 4-6, `tasks.md:13,20,34`).
- NUNCA texto de UI/API en inglés: verificado — pantalla "Sin acceso" y mensajes de error en español rioplatense (`spec.md:27,55`, `tasks.md:27,34`).
- NUNCA calcular fechas/horas fuera de `shared/utils`: verificado — se reutiliza `frontend/src/shared/utils/date.ts:1-19` y se prohíbe duplicar formateos (`spec.md:117-125`, `tasks.md:40-43`).

## Gaps priorizados

No se detectaron gaps: las reglas aplicables tienen escenario y verificación explícita citados, y las reglas no aplicables llevan motivo. Queda como seguimiento del gate humano, no como gap del contrato: el informe `docs/evidencias/verify-c-11-frontend-shell-auth.md` debe generarse durante el apply (`tasks.md:49`) para pasar de "verificado en el plan" a "verificado en la implementación".

## Conclusión

`Listo para implementar` — desde el contrato de auth, C-11 cubre RN-AU-01..04, DD-07/DD-08 y RN-DATOS-02 con escenarios y comprobaciones concretas, sin exponer contraseñas ni datos de pacientes y sin reemplazar la autoridad de RBAC del backend. Esta conclusión no reemplaza el gate humano de governance MEDIO ni autoriza arrancar apply sin un request nuevo del usuario.
