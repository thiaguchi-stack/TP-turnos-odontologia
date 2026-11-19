---
name: auth-contract-audit
description: Audit the authentication and authorization security contract of an OpenSpec change in the dental clinic project BEFORE proposing or implementing it. Use when exploring, proposing, implementing or reviewing changes that touch JWT, OAuth2 password flow, login, tokens, RBAC, roles admin/odontologo, require_role, require_odontologo_own, protected endpoints or password hashing, and when reviewing auth specs or tasks. Trigger also on "auditar auth", "revisar contrato de seguridad", "chequear RBAC", "change de login", "auth contract audit", "review auth specs". Cross-checks RN-AU-01..04, DD-07 and RN-DATOS-01/02 against verifiable scenarios and explicit test verification; emits a cited report, never production code.
metadata:
  author: tp-turnos-odontologia
  version: "1.0"
---

# Auditoría del contrato de autenticación / autorización

Esta skill es de **revisión**. No escribe código de producción, no aprueba un change ni reemplaza el gate humano de gobernanza (C-03 es `governance CRITICO`). Su valor es dejar evidencia de que cada regla de seguridad de la KB quedó cubierta por escenarios verificables y por tareas con verificación explícita, antes de que el change avance.

La KB es la fuente de verdad. La documentación versionada de FastAPI / passlib disponible vía el MCP `context` es opcional y solo sirve para confirmar firmas o hashes; ante cualquier conflicto, prevalece la KB y `AGENTS.md`.

## Entradas

- (a) Nombre o ruta del change y/o de los artefactos a auditar (`proposal.md`, `design.md`, `specs/**/spec.md`, `tasks.md` bajo `openspec/changes/...`), o la ruta de los artefactos sueltos.
- (b) Reglas de la KB: `knowledge-base/03_actores_y_roles.md`, `knowledge-base/05_reglas_de_negocio.md` (§RN-AU), `knowledge-base/08_arquitectura_propuesta.md` (§Seguridad), `knowledge-base/09_decisiones_y_supuestos.md` (DD-07 / DD-08).
- (c) Opcional: documentación versionada consultada con el MCP `context` (por ejemplo FastAPI 0.110.x y passlib 1.7.4). Citarla solo como apoyo, nunca como origen de una regla de negocio.

Si falta un artefacto o no se puede leer, no se inventa su contenido: se registra como "no verificado" con la ruta buscada.

## Procedimiento

1. **Transcribir las reglas con texto exacto.** Leer los archivos de (b) y copiar literalmente, con su ID y su fuente `archivo:línea`:

   - `knowledge-base/05_reglas_de_negocio.md` §RN-AU:
     - RN-AU-01: "Las rutas de administración exigen JWT válido; el paciente reserva sin autenticarse (solo con datos de contacto + token de cancelación)."
     - RN-AU-02: "Un usuario `odontologo` solo ve y modifica turnos del profesional asociado (`usuario.profesional_id`)."
     - RN-AU-03: "Solo un usuario `admin` puede crear/editar profesionales, prestaciones, bloqueos, sillones y usuarios."
     - RN-AU-04: "Las contraseñas se guardan hasheadas (bcrypt/argon2); nunca en texto plano."
   - `knowledge-base/09_decisiones_y_supuestos.md` DD-07: "Capa de servicios + routers delgados en FastAPI | Testeabilidad y cumplimiento de reglas de negocio en un solo lugar (RN-TU) | Lógica en routers (menos testeable)".
   - DD-08: "Tratamiento de datos conforme a Ley 25.326 (consentimiento, acceso autorizado) | El sistema maneja datos personales de salud; responsabilidad desde el diseño, aunque sea un TP | Ignorar privacidad (inaceptable para datos de salud)".
   - `knowledge-base/05_reglas_de_negocio.md` §RN-DATOS:
     - RN-DATOS-01: "Los datos personales y de salud de los pacientes se tratan conforme a la Ley 25.326 (Argentina): finalidad determinada, consentimiento en la reserva, acceso solo a personal autorizado."
     - RN-DATOS-02: "No se expone información clínica en rutas públicas: la reserva online recibe únicamente datos de contacto; la ficha clínica es backlog v2."

   Comprobar que la transcripción coincide con el archivo real antes de seguir; si la KB cambió, usar el texto vigente y citar la línea nueva.

2. **Mapear endpoints y roles contra las reglas.** Para cada endpoint, dependencia y rol del change (incluidas las rutas públicas de `knowledge-base/03_actores_y_roles.md` §Rutas públicas), marcar qué reglas aplican y cuáles no, con una justificación breve. Las siete reglas transcriptas deben aparecer en el mapa; "no aplica" es válido solo con motivo (por ejemplo, RN-DATOS-02 no aplica a un change que no expone rutas de reserva, pero sí RN-AU-04 si hay credenciales).

3. **Verificar escenarios en la spec.** Para cada regla aplicable exigir, como mínimo:
   - un escenario de **funcionamiento esperado** (por ejemplo login correcto devuelve JWT con `sub`/`rol`, o el odontólogo ve solo sus turnos);
   - un escenario de **error de negocio** con código explícito (401 no autenticado / 403 rol insuficiente);
   - un escenario de **borde** (token expirado, odontólogo intentando acceder a otro `profesional_id`, `password_hash` ausente en la respuesta, o reserva pública sin estado elegido por el paciente).

   Citar cada escenario con `archivo:línea`. Un escenario ambiguo o solo narrativo cuenta como "no verificado".

4. **Verificar la verificación en `tasks.md`.** Cada escenario debe tener una tarea que indique **cómo se comprobará**: comando `pytest` concreto, caso de `TestClient` esperado con código HTTP, o aserción sobre la respuesta. Anotar la tarea con `archivo:línea`. Una tarea que diga solo "probar auth" no es verificación explícita.

5. **Chequear las reglas duras.** Marcar cada ítem como verificado / no verificado, con cita:
   - NUNCA exponer ni loguear `password_hash` (RN-AU-04; `knowledge-base/08_arquitectura_propuesta.md` §Seguridad).
   - NUNCA omitir `require_role("admin")` ni `require_odontologo_own` donde corresponda (RN-AU-02/03).
   - NUNCA aceptar `estado` desde la reserva pública (RN-TU-04 + §Seguridad de la arquitectura).
   - NUNCA incluir secretos ni datos reales de pacientes en ejemplos, seeds ni fixtures (RN-DATOS-01/02/03; §Seguridad "Secretos").
   - NUNCA escribir código de producción en esta revisión: C-03 es `governance CRITICO` y requiere análisis y aprobación previa (`AGENTS.md`, `CHANGES.md` §C-03).
   - NUNCA poner lógica de negocio en routers: validación y decisión en servicios (DD-07).

6. **Emitir el informe.** Escribir `docs/evidencias/audit-auth-<change>.md` (donde `<change>` es el slug del change, por ejemplo `c-03-auth-jwt-rbac`). Usar este formato:

   ```markdown
   # Auditoría de contrato de auth — <change>

   ## Alcance
   <artefactos leídos con rutas y fecha; KB citada>

   ## Reglas transcriptas
   <texto exacto de RN-AU-01..04, DD-07, DD-08, RN-DATOS-01/02 con archivo:línea>

   ## Mapa regla / escenario / evidencia

   | Regla | Aplica | Escenario(s) | Evidencia (archivo:línea) | Estado |
   |-------|--------|--------------|---------------------------|--------|
   | RN-AU-01 | Sí — <motivo> | OK: ...; Error: ...; Borde: ... | spec.md:12, tasks.md:8 | Verificado |
   | RN-AU-02 | No — <motivo> | — | 03_actores_y_roles.md:13 | No aplica |

   Estado solo puede ser `Verificado`, `No verificado` o `No aplica`. No mezclar "parcial" con "verificado".

   ## Gaps priorizados
   1. [Alto] <hallazgo> — origina en <regla o KB archivo:línea> — impacto: <qué queda sin probar>
   2. [Medio] ...
   3. [Bajo] ...

   Si no hay gaps: "No se detectaron gaps: todas las reglas aplicables tienen escenario y verificación citados."

   ## Conclusión
   `Listo para implementar` o `Requiere ajustes` + una frase de justificación con las reglas que faltan.
   ```

   Todo hallazgo debe citar la regla, el archivo de KB o el `archivo:línea` que lo origina. Distinguir siempre "verificado" (evidencia leída) de "no verificado" (sin evidencia o artefacto ausente). Si no hay gaps, decirlo explícitamente: no inventar hallazgos para rellenar la plantilla.

## Criterios para revisar el resultado

Antes de entregar, chequear que:

- Toda RN-AU-01..04 aplicable aparece con al menos un escenario y su cita; DD-07, DD-08 y RN-DATOS-01/02 también están representados según apliquen.
- Ningún hallazgo carece de cita de regla, KB o archivo con línea.
- No hay secretos, contraseñas ni datos reales de pacientes en ejemplos ni en el informe.
- El informe no contiene código de producción ni aprueba la implementación de un change CRITICO.
- El texto está en español rioplatense (voseo) y la conclusión distingue con claridad "verificado" de "no verificado".
