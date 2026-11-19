# Auditoría de contrato de auth — c-04-profesionales-api

## Alcance

- Fecha: 2026-11-19. Cambio ya implementado (governance BAJO); revisión previa al archivado.
- Artefactos leídos: `openspec/changes/c-04-profesionales-api/proposal.md`,
  `design.md`, `specs/profesionales/spec.md`, `tasks.md`.
- KB citada: `knowledge-base/03_actores_y_roles.md`,
  `knowledge-base/05_reglas_de_negocio.md`,
  `knowledge-base/08_arquitectura_propuesta.md`,
  `knowledge-base/09_decisiones_y_supuestos.md`, `AGENTS.md`, `CHANGES.md`.
- Código leído solo como contexto (sin modificar):
  `backend/app/routers/profesionales.py`, `backend/app/schemas/profesional.py`,
  `backend/app/services/profesional_service.py`, `backend/tests/test_profesionales_api.py`.
- Esta skill es de revisión: no escribe código de producción ni reemplaza el gate humano.

## Reglas transcriptas

Texto literal verificado contra los archivos reales:

- RN-AU-01 — "Las rutas de administración exigen JWT válido; el paciente reserva
  sin autenticarse (solo con datos de contacto + token de cancelación)."
  (`knowledge-base/05_reglas_de_negocio.md:9`)
- RN-AU-02 — "Un usuario `odontologo` solo ve y modifica turnos del profesional
  asociado (`usuario.profesional_id`)."
  (`knowledge-base/05_reglas_de_negocio.md:10`)
- RN-AU-03 — "Solo un usuario `admin` puede crear/editar profesionales,
  prestaciones, bloqueos, sillones y usuarios."
  (`knowledge-base/05_reglas_de_negocio.md:11`)
- RN-AU-04 — "Las contraseñas se guardan hasheadas (bcrypt/argon2); nunca en
  texto plano." (`knowledge-base/05_reglas_de_negocio.md:12`)
- DD-07 — "Capa de servicios + routers delgados en FastAPI | Testeabilidad y
  cumplimiento de reglas de negocio en un solo lugar (RN-TU) | Lógica en routers
  (menos testeable)" (`knowledge-base/09_decisiones_y_supuestos.md:13`)
- DD-08 — "Tratamiento de datos conforme a Ley 25.326 (consentimiento, acceso
  autorizado) | El sistema maneja datos personales de salud; responsabilidad
  desde el diseño, aunque sea un TP | Ignorar privacidad (inaceptable para datos
  de salud)" (`knowledge-base/09_decisiones_y_supuestos.md:14`)
- RN-DATOS-01 — "Los datos personales y de salud de los pacientes se tratan
  conforme a la Ley 25.326 (Argentina): finalidad determinada, consentimiento en
  la reserva, acceso solo a personal autorizado."
  (`knowledge-base/05_reglas_de_negocio.md:42`)
- RN-DATOS-02 — "No se expone información clínica en rutas públicas: la reserva
  online recibe únicamente datos de contacto; la ficha clínica es backlog v2."
  (`knowledge-base/05_reglas_de_negocio.md:43`)

## Mapa regla / escenario / evidencia

| Regla | Aplica | Escenario(s) | Evidencia (archivo:línea) | Estado |
|-------|--------|--------------|---------------------------|--------|
| RN-AU-01 | Sí — GET público sin JWT y tres rutas de admin con JWT | OK: `spec.md:19-23`; Error 401: `spec.md:151-161`; Borde sin modificar: `spec.md:151-155` | `tasks.md:14,20,21`; `routers/profesionales.py:24,32,45,56,71` | Verificado |
| RN-AU-02 | No — C-04 no expone turnos ni filtra por `usuario.profesional_id`; el odontólogo solo lee el catálogo (`03_actores_y_roles.md:17`) | — | `knowledge-base/03_actores_y_roles.md:16-17`; `spec.md:163-167` | No aplica |
| RN-AU-03 | Sí — CRUD de profesionales reservado a `admin` | OK 201/200: `spec.md:67-71,95-105,123-139`; Error 403: `spec.md:163-167`; Borde token inválido: `spec.md:157-161` | `tasks.md:15,21,22`; `routers/profesionales.py:45,56,71` | Verificado |
| RN-AU-04 | Sí — se leen modelos con `password_hash`, aunque el change no gestiona contraseñas | OK campos exactos: `spec.md:51-55`; Borde sin credenciales en respuesta ni logs: `spec.md:57-61` | `tasks.md:5,14,23`; `schemas/profesional.py`; `routers/profesionales.py:24,32,41,51,67` | Verificado |
| DD-07 | Sí — decisión arquitectónica, sin escenario de usuario | — (arquitectura) | `tasks.md:5,7-10,14-15`; `routers/profesionales.py:21-79` (solo delega y mapea 400/404) | Verificado |
| DD-08 | Sí — catálogo público sin datos personales de salud | OK: `spec.md:19-23`; Borde: `spec.md:51-61` | `tasks.md:14,23`; `knowledge-base/08_arquitectura_propuesta.md:41-45` | Verificado |
| RN-DATOS-01 | No — el consentimiento en la reserva pertenece a C-09/C-12; en C-04 solo rige el acceso autorizado al catálogo, cubierto por DD-08 y RN-DATOS-02 | — | `knowledge-base/05_reglas_de_negocio.md:42`; `CHANGES.md:195-209` | No aplica |
| RN-DATOS-02 | Sí — rutas públicas de catálogo sin información clínica | OK: `spec.md:19-23`; Borde: `spec.md:51-61` | `tasks.md:14,23`; `knowledge-base/08_arquitectura_propuesta.md:45` | Verificado |

## Chequeo de reglas duras

- NUNCA exponer ni loguear `password_hash`: verificado — `ProfesionalRead` solo lista cinco campos y
  `tasks.md:23` usa `caplog`; `knowledge-base/08_arquitectura_propuesta.md:42`.
- NUNCA omitir `require_role("admin")`: verificado en las tres rutas de administración
  (`routers/profesionales.py:45,56,71`); `require_odontologo_own` no aplica porque no hay rutas de turnos.
- NUNCA aceptar `estado` desde la reserva pública: no aplica, C-04 no crea turnos;
  `knowledge-base/05_reglas_de_negocio.md` RN-TU-04 queda para C-09/C-12.
- NUNCA incluir secretos ni datos reales de pacientes en tests/fixtures: verificado — los tests usan
  nombres ficticios (`Valeria Sosa`, `Marta Gómez`), emails `.local` y `CLAVE_FICTICIA`;
  `knowledge-base/05_reglas_de_negocio.md:44`.
- NUNCA escribir código de producción en esta revisión: verificado — este informe es el único artefacto
  nuevo de la auditoría.
- NUNCA poner lógica de negocio en routers: verificado — baja lógica, validación de dominio y filtrado
  viven en `profesional_service.py`; el router solo delega y traduce errores a HTTP.

## Gaps priorizados

No se detectaron gaps: todas las reglas aplicables tienen escenario y verificación citados.

## Conclusión

`Listo para implementar` — con la aclaración de que la implementación ya está terminada y verificada
(15/15 tareas, 197 tests en verde, Ruff limpio); no faltan reglas RN-AU, DD-07/08 ni RN-DATOS-01/02
con escenario o verificación ausentes para el alcance de C-04.
