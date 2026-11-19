# Auditoría de contrato de auth — c-05-prestaciones-api

## Alcance

- Fecha: 2026-11-19. Auditoría ligera posterior a la implementación (governance BAJO); revisión, no aprobación de gobernanza.
- Artefactos leídos: `openspec/changes/c-05-prestaciones-api/proposal.md`,
  `design.md`, `specs/prestaciones-api/spec.md`, `tasks.md`.
- KB citada: `knowledge-base/03_actores_y_roles.md`,
  `knowledge-base/05_reglas_de_negocio.md`,
  `knowledge-base/08_arquitectura_propuesta.md`,
  `knowledge-base/09_decisiones_y_supuestos.md`, `AGENTS.md`.
- Código y tests leídos como contexto: `backend/app/routers/prestaciones.py`,
  `backend/app/schemas/prestacion.py`, `backend/app/services/prestacion_service.py`,
  `backend/tests/test_prestaciones_api.py`, `backend/tests/conftest.py`.
- Esta skill es de revisión: no escribe código de producción.

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
| RN-AU-01 | Sí — `GET /prestaciones` público; POST/PUT exigen JWT | OK: spec.md:52-56; Error 401: spec.md:78-88; Borde sin modificar: spec.md:83-88 | `tasks.md:11-13`; `test_prestaciones_api.py::test_alta_sin_token_401`, `::test_edicion_sin_token_401`, `::test_listado_publico_sin_token_devuelve_solo_activas`; `routers/prestaciones.py:20-21,30,44` | Verificado |
| RN-AU-02 | No — C-05 no expone turnos ni rutas con `profesional_id`; el odontólogo solo consulta el catálogo (`03_actores_y_roles.md:18`) | — | `knowledge-base/03_actores_y_roles.md:16-18`; `spec.md:90-100` (403 para odontólogo) | No aplica |
| RN-AU-03 | Sí — alta y edición de prestaciones reservadas a `admin` | OK 201/200: spec.md:20-24,110-114; Error 403: spec.md:90-100; Borde extra `estado`: spec.md:38-42 | `tasks.md:12-13`; `test_prestaciones_api.py::test_odontologo_no_puede_crear_403`, `::test_odontologo_no_puede_editar_403`, `::test_admin_crea_prestacion_valida`; `routers/prestaciones.py:30,44` | Verificado |
| RN-AU-04 | Sí — se manipulan usuarios con `password_hash` en los fixtures de admin/odontólogo | OK campos exactos: spec.md:64-68; Borde sin hash en la respuesta: spec.md:24,68 | `tasks.md:11`; `test_prestaciones_api.py::test_listado_publico_no_expone_campos_ajenos_al_catalogo`, `::test_admin_crea_prestacion_valida`; `schemas/prestacion.py` (`PrestacionRead` con cuatro campos) | Verificado |
| DD-07 | Sí — decisión arquitectónica, sin escenario de usuario | — (arquitectura) | `tasks.md:7`; `services/prestacion_service.py:9-51` (decisión y validación); `routers/prestaciones.py:20-52` (solo delega y mapea errores) | Verificado |
| DD-08 | Sí — catálogo público sin datos personales de salud | OK: spec.md:52-56; Borde: spec.md:64-68 | `tasks.md:11`; `knowledge-base/08_arquitectura_propuesta.md:39-45`; `test_prestaciones_api.py::test_listado_publico_no_expone_campos_ajenos_al_catalogo` | Verificado |
| RN-DATOS-01 | No — el consentimiento de la reserva pertenece a C-09/C-12; en C-05 rige el acceso autorizado al catálogo, cubierto por RN-AU-01/03 y DD-08 | — | `knowledge-base/05_reglas_de_negocio.md:42`; `tasks.md:24` | No aplica |
| RN-DATOS-02 | Sí — ruta pública del catálogo sin información clínica | OK: spec.md:64-68; Borde no exposición de id de paciente: spec.md:24 | `tasks.md:11`; `schemas/prestacion.py`; `conftest.py:30-35` (datos ficticios); `knowledge-base/08_arquitectura_propuesta.md:45` | Verificado |

## Chequeo de reglas duras

- NUNCA exponer ni loguear `password_hash`: verificado — `PrestacionRead` expone solo
  `id`, `nombre`, `duracion_minutos` y `activa`; los tests de listado y alta aseveran su ausencia;
  `knowledge-base/08_arquitectura_propuesta.md:42`.
- NUNCA exponer rutas privadas sin JWT ni saltear RBAC: verificado — `require_role(RolUsuario.ADMIN)`
  en POST y PUT (`routers/prestaciones.py:30,44`); `require_odontologo_own` no aplica (sin rutas de turnos).
- NUNCA aceptar `estado` desde la reserva pública: no aplica, C-05 no crea turnos; el campo `estado`
  se rechaza con `extra="forbid"` en los schemas de prestación (RN-TU-04 queda para C-09/C-12).
- NUNCA incluir secretos ni datos reales de pacientes en ejemplos, seeds ni fixtures: verificado —
  `backend/tests/conftest.py:17-76` usa nombres, DNI y teléfonos ficticios, y los helpers de token usan
  `CLAVE_FICTICIA` con emails `.local` (`knowledge-base/05_reglas_de_negocio.md:44`).
- NUNCA poner lógica de negocio en routers: verificado — duración, existencia, filtrado de activas y
  no retroactividad viven en `prestacion_service.py`; el router solo delega y traduce errores a HTTP.
- NUNCA cambiar duración ni desactivar con efecto retroactivo: verificado — el servicio nunca actualiza
  `Turno`; `test_cambio_duracion_no_modifica_turno_existente` registra y asevera cero `UPDATE TURNO`.

## Gaps priorizados

No se detectaron gaps: todas las reglas aplicables tienen escenario y verificación citados.

## Conclusión

`Listo` — la implementación ya está terminada y verificada (11/11 tareas, 237 tests en verde,
Ruff limpio); no faltan reglas RN-AU, DD-07/08 ni RN-DATOS-01/02 con escenario o verificación
ausentes para el alcance de C-05.
