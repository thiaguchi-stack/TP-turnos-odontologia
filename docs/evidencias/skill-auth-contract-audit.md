# Evidencia — skill propia `auth-contract-audit`

Fecha: 2026-11-18. Repo: `C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia`.

**Actualización 2026-11-19:** esta evidencia registra la creación de la skill y el contexto del 2026-11-18, cuando C-03 era el próximo change. Hoy `auth-contract-audit` sí figura en la lista de skills disponibles de la sesión (`.agents/skills/auth-contract-audit/SKILL.md`; disponibilidad verificada, invocación completa no comprobada) y C-03 está archivado en `openspec/changes/archive/2026-11-18-c-03-auth-jwt-rbac/` (`CHANGES.md:172-173`).

## 1. Solicitud exacta a la skill creadora

Invocación literal a la herramienta Skill (la herramienta no acepta campos de mensaje adicionales):

```text
name: "opencode-skill-creator"
```

La entrevista de intención quedó respondida por el brief del usuario, según su instrucción explícita de no preguntarle. Transcripción literal del mensaje recibido:

> Tu tarea es crear la **skill propia** del TP de Metodología I usando OBLIGATORIAMENTE la skill creadora ya instalada `opencode-skill-creator` (v0.3.7).
>
> Repo: `C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia`.
>
> ## Paso 1 — Usar la skill creadora
> Invocá la herramienta Skill con `name: "opencode-skill-creator"` (está disponible; su SKILL.md está en `C:\Users\Usuario\.config\opencode\skills\opencode-skill-creator\SKILL.md`). Seguí su workflow para **crear** una skill nueva. La creadora pide una entrevista de intención de 3-5 preguntas: **no se la hagas al usuario**; considerá que ya está respondida con el brief de abajo (es el requerimiento explícito del usuario y del PDF de la cátedra). Usá su staging en `%TEMP%\opencode-skills\<skill-name>\` si el workflow lo indica, y después copiá el resultado final al repo.
>
> ## Brief de la skill (respuestas a la entrevista)
>
> - **Nombre**: `auth-contract-audit` (kebab-case, cumple `^[a-z0-9]+(-[a-z0-9]+)*$`).
> - **Propósito**: auditar el contrato de seguridad de autenticación/autorización de un change del proyecto odontológico ANTES de prepararlo o implementarlo, verificando que las reglas RN-AU-01..04, DD-07 y RN-DATOS-01/02 estén realmente cubiertas por escenarios verificables y por tareas con verificación explícita. Es una skill de **revisión**, no escribe código de producción.
> - **Cuándo se activa (trigger)**: cuando se vaya a explorar/proponer/implementar/revisar un change que toque JWT, OAuth2 password flow, login, tokens, RBAC, roles admin/odontólogo, `require_role`, `require_odontologo_own`, endpoints protegidos o hashing de contraseñas. También cuando se revisen specs o tasks de autenticación. Incluí frases de activación en español ("auditar auth", "revisar contrato de seguridad", "chequear RBAC", "change de login") y en inglés para que el trigger funcione.
> - **Entradas necesarias**: (a) nombre/ruta del change o de los artefactos a auditar, (b) reglas de la KB: `knowledge-base/03_actores_y_roles.md`, `knowledge-base/05_reglas_de_negocio.md` (§RN-AU), `knowledge-base/08_arquitectura_propuesta.md` (§Seguridad), `knowledge-base/09_decisiones_y_supuestos.md` (DD-07/DD-08), y (c) opcionalmente documentación versionada de FastAPI/passlib disponible vía el MCP `context`.
> - **Procedimiento** (numerado, ejecutable):
>   1. Leer las reglas de autenticación de la KB y transcribir RN-AU-01/02/03/04 + DD-07 + RN-DATOS-01/02 con su texto exacto.
>   2. Mapear cada endpoint/rol del change contra esas reglas; marcar cuáles aplican y cuáles no, con justificación.
>   3. Verificar que cada regla aplicable tenga **al menos un escenario verificable** en la spec: uno de funcionamiento esperado, uno de error de negocio (403/401) y uno de borde (p. ej. token expirado, odontólogo intentando acceder a otro `profesional_id`).
>   4. Verificar que `tasks.md` indique **cómo se verificará** cada escenario (comando pytest / TestClient esperado).
>   5. Chequear las reglas duras: NUNCA exponer ni loguear `password_hash`; NUNCA omitir `require_role("admin")` / `require_odontologo_own`; NUNCA aceptar `estado` desde la reserva pública; sin secretos en ejemplos; sin código de producción (C-03 es governance CRITICO).
>   6. Emitir un informe en `docs/evidencias/audit-auth-<change>.md` con: tabla `Regla | Aplica | Escenario(s) | Evidencia (archivo:línea) | Estado`, lista de gaps priorizados (Alto/Medio/Bajo), y conclusión "listo para implementar" / "requiere ajustes".
> - **Resultado esperado**: ese archivo de auditoría, con cada hallazgo citando la regla o archivo de KB que lo origina. Si no hay gaps, decirlo explícitamente sin inventarlos.
> - **Criterios para revisar el resultado**: toda RN-AU-01..04 aplicable aparece con escenario; ningún hallazgo sin cita de regla/KB/archivo; sin secretos ni datos reales en ejemplos; el informe no contiene código de producción; texto en español rioplatense; el informe distingue claramente "verificado" de "no verificado".
>
> ## Paso 2 — Ubicación y adaptación
> - Guardá el SKILL.md final en `C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\auth-contract-audit\SKILL.md` (creá el directorio). Respetá el frontmatter YAML de la convención del repo: `---`, `name: auth-contract-audit`, `description: ...` (la descripción en inglés, orientada a trigger con "Use when...", es la convención de las skills del repo; el contenido del cuerpo en español rioplatense), y opcional `metadata` con `author`/`version`.
> - Agregá un `README.md` corto dentro de esa carpeta solo si la creadora lo genera; si no, no lo inventes.
> - Validá la skill con el validador de la creadora si existe (por ejemplo `skill_validate` o el comando que indique su SKILL.md). Si no podés validarla, decilo.
> - **No** registres la skill en `.atl/skill-registry.md`, **no** toques `AGENTS.md`/`CLAUDE.md`, **no** toques `README.md`, **no** modifiques la config global. Eso lo hace otro agente después. **No** hagas commits.
>
> ## Paso 3 — Evidencia
> Creá `docs/evidencias/skill-auth-contract-audit.md` con: (1) la solicitud exacta que le hiciste a la skill creadora, (2) qué pasos ejecutaste y qué produjo (ruta del staging + ruta final), (3) el frontmatter final de la skill, (4) resultado de la validación, (5) una explicación de qué aporta al change C-03. Sin secretos.
>
> ## Requisitos de honestidad
> Si la skill creadora no se puede invocar, no la simules: reportalo. Si generó algo con errores (descripción demasiado larga, nombre inválido, contenido en inglés, falta de criterios de revisión), **corregilo y documentá el antes y el después** en el archivo de evidencia — eso sirve para la revisión crítica del TP.
>
> ## Entrega
> Devolveme: ruta del SKILL.md creado, frontmatter exacto, resultado de la validación, ruta del archivo de evidencia, y cualquier defecto detectado y corregido (antes/después). Guardá también un recuerdo en engram con `project: "tp-turnos-odontologia"` y `topic_key: "opsx/c-03/skills-mcp"`.

## 2. Pasos ejecutados y productos

| # | Paso | Resultado |
|---|------|-----------|
| 1 | Confirmar versión instalada de la creadora | `.opencode-skill-creator-version` = `0.3.7` |
| 2 | Invocar la skill creadora | Workflow cargado (intake → draft en staging → evals → validación → instalación) |
| 3 | Intake | Aviso único de que omitir la entrevista reduce el ajuste al workflow real; se procede con el brief como confirmación explícita, sin preguntas al usuario |
| 4 | Verificar reglas contra la KB real | RN-AU y RN-DATOS en `knowledge-base/05_reglas_de_negocio.md:9-12,42-43`; DD-07/DD-08 en `knowledge-base/09_decisiones_y_supuestos.md:13-14`; seguridad en `knowledge-base/08_arquitectura_propuesta.md:39-46`; actores/RBAC en `knowledge-base/03_actores_y_roles.md:11-29`; gobernanza de C-03 en `CHANGES.md:171-186` |
| 5 | Borrador en staging (convención de la creadora) | `C:\Users\Usuario\AppData\Local\Temp\opencode-skills\auth-contract-audit\SKILL.md` |
| 6 | Test prompts de la creadora (sin assertions) | `C:\Users\Usuario\AppData\Local\Temp\opencode-skills\auth-contract-audit\evals\evals.json` (3 prompts: auditoría C-03, fuga de `profesional_id`, exposición de `password_hash`) |
| 7 | Validación del borrador | `skill_validate` → `valid: true`, `Skill is valid!` |
| 8 | Copia final al repo | `C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\auth-contract-audit\SKILL.md` (directorio creado; mismo contenido) |
| 9 | Validación y parseo de la copia final | `skill_validate` → `valid: true`; `skill_parse` → `name: auth-contract-audit`, `contentLength: 8379` |
| 10 | Alcance respetado | No se creó `README.md` (la creadora no lo genera); no se tocó `.atl/skill-registry.md`, `AGENTS.md`, `CLAUDE.md`, `README.md` raíz ni config global; no hay commits |

No se ejecutó el ciclo completo de evals/benchmark ni el visor de la creadora: requiere lanzar corridas con herramienta `Task`/subagentes (no disponible en esta invocación) y revisión humana interactiva del output. Tampoco se corrió `skill_optimize_loop`, para no reemplazar la descripción de trigger acordada en el brief. Los prompts quedaron en staging como punto de partida.

## 3. Frontmatter final (exacto)

```yaml
---
name: auth-contract-audit
description: Audit the authentication and authorization security contract of an OpenSpec change in the dental clinic project BEFORE proposing or implementing it. Use when exploring, proposing, implementing or reviewing changes that touch JWT, OAuth2 password flow, login, tokens, RBAC, roles admin/odontologo, require_role, require_odontologo_own, protected endpoints or password hashing, and when reviewing auth specs or tasks. Trigger also on "auditar auth", "revisar contrato de seguridad", "chequear RBAC", "change de login", "auth contract audit", "review auth specs". Cross-checks RN-AU-01..04, DD-07 and RN-DATOS-01/02 against verifiable scenarios and explicit test verification; emits a cited report, never production code.
metadata:
  author: tp-turnos-odontologia
  version: "1.0"
---
```

## 4. Resultado de la validación

Comando: `skill_validate` sobre la ruta de staging y sobre la ruta final. Salida idéntica en ambas:

```json
{
  "valid": true,
  "message": "Skill is valid!"
}
```

`skill_parse` sobre la copia final confirmó `name: auth-contract-audit` y la descripción completa, sin truncamiento.

## 5. Qué aporta al change C-03

`C-03 auth-jwt-rbac` es el próximo change del camino crítico y tiene `Governance: CRITICO` (`CHANGES.md:171-186`): exige análisis y aprobación previa, sin código. La skill convierte esa puerta en un chequeo repetible y con evidencia:

- obliga a transcribir RN-AU-01..04, DD-07, DD-08 y RN-DATOS-01/02 desde la KB, evitando que el delta de specs "invente" reglas;
- exige escenarios de éxito, 401/403 y borde (token expirado, acceso a otro `profesional_id`), que son justamente los tests listados en `CHANGES.md:179`;
- exige que `tasks.md` diga cómo se verificará cada escenario con pytest/TestClient, y marca como "no verificado" lo que solo está narrado;
- controla las reglas duras de `AGENTS.md` (sin `password_hash` en respuestas/logs, sin saltear `require_role`/`require_odontologo_own`, sin secretos ni datos reales, sin código de producción antes de la aprobación);
- deja un artefacto auditoriable en `docs/evidencias/audit-auth-c-03-auth-jwt-rbac.md` con tabla citada, gaps priorizados y conclusión explícita.

Es apoyo de governance, no reemplaza la aprobación humana ni habilita la implementación.

## 6. Honestidad: defectos detectados y corregidos

- La creadora **sí se pudo invocar**; no se simuló su uso. No produjo errores de nombre, descripción, idioma del cuerpo ni de criterios de revisión: el validador pasó correctamente.
- Se corrigieron dos erratas del borrador redactado en staging, antes de la validación (no eran fallas del validador):
  - antes: `Citarla solo como apoyo, nunca como origende una regla de negocio.` → después: `Citarla solo como apoyo, nunca como origen de una regla de negocio.`
  - antes: `un escenario de **error de negocio** con código explicito (...)` → después: `un escenario de **error de negocio** con código explícito (...)`.
- La entrevista obligatoria de la creadora se omitió por instrucción explícita del usuario; se emitió el aviso correspondiente una sola vez.
- No hay gaps inventados en esta evidencia: el informe de auditoría de C-03 es Output de la skill y no se generó en esta tarea.
