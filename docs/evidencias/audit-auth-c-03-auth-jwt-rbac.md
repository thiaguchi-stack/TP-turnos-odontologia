# Auditoría de contrato de auth — c-03-auth-jwt-rbac

## Alcance

- Fecha: 2026-11-18. Cambio preparado (NO implementado): `governance CRITICO`.
- Artefactos leídos: `openspec/changes/c-03-auth-jwt-rbac/proposal.md`,
  `design.md`, `specs/user-auth/spec.md`, `tasks.md`.
- KB citada: `knowledge-base/03_actores_y_roles.md`,
  `knowledge-base/05_reglas_de_negocio.md`,
  `knowledge-base/07_flujos_principales.md`,
  `knowledge-base/08_arquitectura_propuesta.md`,
  `knowledge-base/09_decisiones_y_supuestos.md`, `AGENTS.md`, `CHANGES.md`.
- Código existente leído solo como contexto (sin modificar):
  `backend/app/core/security.py`, `backend/app/core/config.py`,
  `backend/app/main.py`, `backend/tests/test_security.py`,
  `backend/pyproject.toml`.
- **Camino de ejecución de la skill**: se intentó invocar la Skill tool con
  `name: "auth-contract-audit"`; la herramienta respondió
  `Skill "auth-contract-audit" not found` (no figura entre las skills
  disponibles de esta sesión). No se simuló la invocación: se leyó
  `.agents/skills/auth-contract-audit/SKILL.md` y se ejecutó su procedimiento
  manualmente, paso a paso. Esta acotación queda registrada acá como evidencia.

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

## Mapa regla / escenario / evidencia (ANTES de las correcciones)

| Regla | Aplica | Escenario(s) | Evidencia (archivo:línea) | Estado |
|-------|--------|--------------|---------------------------|--------|
| RN-AU-01 | Sí — login, rutas privadas y rutas públicas | OK: `spec.md:20-30`; Error 401: `spec.md:38-42,50-60`; Borde público: `spec.md:130-140` | `tasks.md:26,27,30,35` | No verificado — `tasks.md:35` no dice cómo se comprueba |
| RN-AU-02 | Sí — odontólogo por `profesional_id` | OK: `spec.md:99-103`; Borde 403: `spec.md:105-109` | `tasks.md:21,29` | Verificado |
| RN-AU-03 | Sí — CRUD de usuarios | OK 201: `spec.md:80-84`; Error 403: `spec.md:86-90` | `tasks.md:28` | Verificado |
| RN-AU-04 | Sí — hash, claims y respuestas | OK: `spec.md:20-30,68-72,80-84`; Borde sin hash: `spec.md:24,30,72,84` | `tasks.md:8,13,26,27,36` | No verificado — falta escenario de "nunca loguear" y verificación concreta |
| DD-07 | Sí — auth_service + routers delgados | Escenarios de servicio: `spec.md:38-42,80-90,117-121` | `tasks.md:17-30` (p. ej. `tasks.md:26` "el router solo delega") | Verificado |
| DD-08 | Sí — privacidad desde el diseño | Borde público: `spec.md:130-140` | `design.md` §Decisions 7, `tasks.md:35,36` | No verificado — depende de la verificación débil de `tasks.md:35` |
| RN-DATOS-01 | Sí — consentimiento y acceso autorizado | Borde: `spec.md:136-140` | `tasks.md:35` | No verificado — verificación solo manual |
| RN-DATOS-02 | Sí — rutas públicas sin datos clínicos | Borde: `spec.md:130-134` | `tasks.md:35` | No verificado — verificación solo manual |

Estado: solo `Verificado`, `No verificado` o `No aplica`. Las siete reglas
aparecen en el mapa; ninguna se marcó "No aplica" porque el change toca
credenciales, RBAC y rutas públicas de reserva.

## Gaps priorizados (ANTES)

1. **[Alto]** `tasks.md:35` dice "Verificar manualmente" las rutas públicas, sin
   comando `pytest`, ni código HTTP esperado, ni aserción. Origina en RN-AU-01
   (`05_reglas_de_negocio.md:9`) y en la lista de rutas públicas
   (`03_actores_y_roles.md:22-28`). Impacto: los escenarios `spec.md:130-140`
   quedan sin prueba reproducible; además esos endpoints recién existen en C-09,
   así que C-03 debe verificar la NO protección con un mecanismo disponible ya.
2. **[Alto]** RN-AU-04 (`05_reglas_de_negocio.md:12`) y la regla dura de no
   loguear contraseñas/hashes (`AGENTS.md:99`, `08_arquitectura_propuesta.md:42`)
   no tienen escenario en la spec; `tasks.md:36` solo propone un grep de salidas.
   Impacto: una filtración por logging quedaría sin detectar.
3. **[Medio]** `TOKEN_EXPIRE_MIN` tiene default 60 en
   `backend/app/core/config.py:12`, pero la KB fija 480 en
   `08_arquitectura_propuesta.md:55`; `design.md` cita 480 y `tasks.md:9` no
   exige alinearlo. Impacto: expiración distinta a la decidida sin aprobación.
4. **[Bajo]** `tasks.md:14-15` usa palabras en inglés ("verification",
   "Produce") en artefactos del proyecto. Origina en la regla de lenguaje
   (`AGENTS.md:127-129`). Impacto: consistencia del texto del TP.

## Conclusión (ANTES)

`Requiere ajustes` — hay cuatro gaps abiertos (dos altos) que impiden dar por
cubiertas RN-AU-01, RN-AU-04, RN-DATOS-01/02 y DD-08. Además, el gate de
governance CRITICO (`CHANGES.md:181`, `AGENTS.md:124`) sigue pendiente de
aprobación humana: esta auditoría no autoriza implementar ni archivar el change.

---

## Revisión crítica: correcciones aplicadas a los artefactos (DESPUÉS)

Los cuatro gaps se cerraron volviendo a `spec.md`, `tasks.md` y `design.md`.
Las líneas de la sección anterior son las del estado inicial; las de acá son las
definitivas.

| Gap | Antes | Después |
|-----|-------|---------|
| 1 [Alto] rutas públicas sin verificación | `tasks.md:35` ("Verificar manualmente"), sin comando ni códigos; escenarios en `spec.md:130-140` | `tasks.md:35` ahora exige un test de regresión con `TestClient`, aserción de que ninguna ruta `/turnos/online` lleva dependencia de auth, un router de prueba **solo en tests** con 200 y 400 (nunca 401) para el caso con `estado`, y el comando `pytest ... -k "publico" -q`; escenarios definitivos en `spec.md:136-146`. Los endpoints reales se revalidan en C-09. |
| 2 [Alto] hash nunca logueado sin escenario | Sin escenario; `tasks.md:36` solo proponía un grep | Nuevo escenario `spec.md:74-78` con `caplog`, login 401 + 200 y aserción de ausencia de contraseña y `password_hash`; `tasks.md:36` ejecuta `pytest ... -k "sin_filtracion" -q` con aserción sobre `caplog.text`; `tasks.md:26` lo referencia. |
| 3 [Medio] expiración 60 vs. 480 | `backend/app/core/config.py:12` = 60; sin tarea que lo alinee | `design.md:57-59` y `design.md:125-127` registran la divergencia; `tasks.md:9` exige alinear el default a 480 (KB `08_arquitectura_propuesta.md:55`) o dejar aprobado el desvío en el gate, con aserción `Settings().token_expire_min == 480`. |
| 4 [Bajo] texto en inglés | `tasks.md:14-15` ("verification", "Produce") | `tasks.md:14-15` en español; se mantuvo la regla de lenguaje (`AGENTS.md:127-129`). |

Además se reforzó la trazabilidad del hash legado: `design.md:70-73` cita
`backend/app/core/security.py:7-9,21-29,58-78` como evidencia de que el formato
está versionado y `verify_password` se conserva para migrar en C-03; la decisión
sigue marcada como supuesto a validar en el gate, no como regla inventada.

## Mapa regla / escenario / evidencia (DESPUÉS)

| Regla | Aplica | Escenario(s) | Evidencia (archivo:línea) | Estado |
|-------|--------|--------------|---------------------------|--------|
| RN-AU-01 | Sí — login, rutas privadas y públicas | OK: `spec.md:20-30`; Error 401: `spec.md:38-42,50-60`; Borde público: `spec.md:136-146` | `tasks.md:26,27,30,35` | Verificado |
| RN-AU-02 | Sí — odontólogo por `profesional_id` | OK: `spec.md:105-109`; Borde 403: `spec.md:111-115` | `tasks.md:21,29` | Verificado |
| RN-AU-03 | Sí — CRUD de usuarios | OK 201: `spec.md:86-90`; Error 403: `spec.md:92-96` | `tasks.md:28` | Verificado |
| RN-AU-04 | Sí — hash, claims, respuestas y logs | OK: `spec.md:20-30,68-72,86-90`; Borde sin hash: `spec.md:24,30,72,90`; Borde logs: `spec.md:74-78` | `tasks.md:8,9,13,26,27,36` | Verificado |
| DD-07 | Sí — servicios + routers delgados | Decisiones de servicio: `spec.md:38-42,86-96,123-127` | `tasks.md:17-30` (p. ej. `tasks.md:26`) | Verificado |
| DD-08 | Sí — privacidad desde el diseño | Borde público: `spec.md:136-146`; consentimiento: `spec.md:144` | `design.md` §Decisions 7-8, `tasks.md:35,36` | Verificado |
| RN-DATOS-01 | Sí — consentimiento y acceso autorizado | Borde: `spec.md:142-146` | `tasks.md:35` | Verificado |
| RN-DATOS-02 | Sí — rutas públicas sin datos clínicos | Borde: `spec.md:136-140` | `tasks.md:35` | Verificado |

## Conclusión (DESPUÉS)

`Requiere ajustes` — los ajustes de trazabilidad ya están cerrados: las ocho
reglas transcriptas tienen escenario y verificación citados, y no quedan gaps
de especificación. Se mantiene `Requiere ajustes` y **no** se emite
`Listo para implementar` porque falta una condición externa a la auditoría: la
aprobación humana del gate CRITICO (`CHANGES.md:181`, `AGENTS.md:124`) y la
respuesta a los supuestos `SU-HASH-LEGADO` / `SU-RATELIMIT` (`design.md:149-155`).
Esta auditoría revisó artefactos: no escribió código de producción, no corrió
tests de implementación, no ejecutó apply ni archivó el change.
