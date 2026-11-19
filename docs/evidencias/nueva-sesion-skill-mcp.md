# Evidencia — sesión nueva: descubrimiento de skill propia e integración MCP

Fecha: 2026-11-18
Repo: `C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia`

Arranqué sin contexto previo, solo con las instrucciones que el repo expone. No
instalé nada, no corrí `npx`, no hice commits y no modifiqué ningún otro archivo.

## Lecturas y comprobaciones realizadas

Lecturas (todas con la herramienta de lectura de archivos):

1. `AGENTS.md` (143 líneas) y `CLAUDE.md` (143 líneas): copia idéntica; índice
   de reglas del proyecto.
2. `.atl/skill-registry.md` (184 líneas): registry de skills, compact rules y
   convenciones del proyecto.
3. `.agents/skills/auth-contract-audit/SKILL.md` (100 líneas): SKILL.md de la
   skill propia.
4. `README.md` (207 líneas) y `docs/skills-mcp/README.md` (92 líneas).
5. Comprobaciones de contexto: `list_mcp_resources` → `{"resources": []}`;
   `list_mcp_resource_templates` → `{"resourceTemplates": []}`; búsqueda de
   `_shared/skill-resolver.md` → "No files found"; grep por `Skill tool` en
   `*.md` del repo.
6. Lectura de evidencias previas para contrastar el intento de invocación:
   `docs/evidencias/audit-auth-c-03-auth-jwt-rbac.md` (líneas 17-22),
   `docs/evidencias/skill-auth-contract-audit.md` (líneas 1-20) y
   `docs/evidencias/skills.md` (líneas 1-75).
7. Verificación previa a la escritura: `docs/evidencias/` existe y
   `nueva-sesion-skill-mcp.md` no existía (glob sin resultados).

No se ejecutaron comandos de terminal que modifiquen el estado del sistema.

## 1. Cómo encontré la skill propia

Camino exacto, en dos pasos:

- **Primero**: `AGENTS.md` / `CLAUDE.md`, sección `## Skills Disponibles`
  (líneas 48-59). La fila de la línea 55, bajo la columna "Rol" con valor
  **"Skill propia / auditoría de auth"**, lista la skill
  `auth-contract-audit` y dice: *"Revisión previa del contrato de seguridad de
  changes de auth (JWT, RBAC, RN-AU), sin escribir código de producción"* y
  *"usar al preparar o revisar C-03 y cualquier change con login, tokens, roles
  o endpoints protegidos"*. La nota de la línea 57 refuerza: *"Sí hay una skill
  propia del proyecto, `auth-contract-audit`, de auditoría de auth (no de
  stack)"*. La línea 59 indica que los compact rules se resuelven desde
  `.atl/skill-registry.md` y que la tabla solo mapea skill→rol.
- **Después**: `.atl/skill-registry.md`, sección `## User Skills` (líneas
  7-25), fila de la **línea 19**. Trigger: *"auditar contrato de seguridad de
  auth, revisar RBAC/JWT en un change de login, chequear RN-AU antes de
  proponer un change"*; skill `auth-contract-audit`; path absoluto
  `C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\auth-contract-audit\SKILL.md`.
  El mismo registry la desarrolla en `## Compact Rules` → `### auth-contract-audit`
  (líneas 103-110) y la nombra en `## Project Conventions` (línea 182), donde
  además da la ruta repo-relativa portable
  `.agents/skills/auth-contract-audit/SKILL.md`.

Qué hace y cuándo usarla: audita el contrato de seguridad (autenticación /
autorización) de un change de OpenSpec **antes** de proponerlo o implementarlo;
se activa al explorar, proponer, implementar o revisar cambios que toquen JWT,
OAuth2 password flow, login, tokens, RBAC, roles admin/odontólogo,
`require_role`, `require_odontologo_own`, endpoints protegidos o hashing de
contraseñas. Caso principal: `C-03` (`governance CRITICO`). Es solo revisión:
no escribe código de producción ni reemplaza el gate humano.

## 2. Procedimiento y criterio de revisión de `SKILL.md`

Frontmatter: `name: auth-contract-audit`, descripción "pushy" (qué hace y
cuándo usarla, con triggers en inglés y español), `author: tp-turnos-odontologia`,
`version: "1.0"` (líneas 1-7).

Entradas (líneas 15-21): nombre/ruta del change o de sus artefactos
(`proposal.md`, `design.md`, `specs/**/spec.md`, `tasks.md`); reglas de la KB
(`03_actores_y_roles.md`, `05_reglas_de_negocio.md` §RN-AU,
`08_arquitectura_propuesta.md` §Seguridad, `09_decisiones_y_supuestos.md`
DD-07/DD-08); y, opcional, documentación versionada vía el MCP `context`. Si
falta un artefacto, se registra como "no verificado" con la ruta buscada; no se
inventa contenido.

Procedimiento (líneas 23-90), 6 pasos:

1. Transcribir las reglas con texto exacto y cita `archivo:línea`
   (RN-AU-01..04, DD-07, DD-08, RN-DATOS-01/02) y comprobar la transcripción
   contra los archivos reales; si la KB cambió, usar el texto vigente.
2. Mapear endpoints, dependencias y roles contra las reglas; las siete reglas
   deben aparecer; "no aplica" solo con motivo.
3. Exigir por regla aplicable un escenario de funcionamiento esperado, un error
   de negocio con código explícito (401/403) y un escenario de borde; citar
   cada uno con `archivo:línea`. Lo ambiguo o solo narrativo cuenta como "no
   verificado".
4. Verificar en `tasks.md` que cada escenario tenga verificación explícita:
   comando `pytest` concreto, caso de `TestClient` con código HTTP o aserción
   sobre la respuesta. "Probar auth" no alcanza.
5. Chequear reglas duras: nunca exponer ni loguear `password_hash`; no omitir
   `require_role("admin")` / `require_odontologo_own`; no aceptar `estado` desde
   la reserva pública; sin secretos ni datos reales; sin código de producción;
   lógica en servicios, no en routers (DD-07).
6. Emitir `docs/evidencias/audit-auth-<change>.md` con alcance, reglas
   transcriptas, tabla regla / escenario / evidencia / estado
   (`Verificado`, `No verificado` o `No aplica`), gaps priorizados y conclusión
   `Listo para implementar` o `Requiere ajustes`.

Criterio de revisión (líneas 92-100): toda regla aplicable con escenario y cita;
ningún hallazgo sin cita de regla/KB/`archivo:línea`; sin secretas, contraseñas
ni datos reales de pacientes; sin código de producción ni aprobación de un
change CRITICO; texto en español rioplatense (voseo) y distinción clara entre
"verificado" y "no verificado". La KB prevalece sobre el MCP y `AGENTS.md`
prevalece ante cualquier conflicto (líneas 11-13).

## 3. Integración MCP encontrada

Fuentes: `AGENTS.md` sección `## Integraciones MCP` (líneas 63-69), `README.md`
líneas 35 y 200-201, y `docs/skills-mcp/README.md` (todo el archivo).

- **Nombre**: `context`, paquete `@neuledge/context@1`, servidor local por
  stdio.
- **Propósito y capacidades**: documentación **versionada** local para decidir
  firmas y hashing sin depender de un índice mutable; comandos `install`,
  `add`, `list`, `query`; paquetes instalados `fastapi@0.110.3` (824 secciones)
  y `passlib@1.7.4` (152 secciones).
- **Momento de uso**: al preparar o revisar changes de auth o del stack (por
  ejemplo C-03); nunca como fuente de reglas de negocio. La skill
  `auth-contract-audit` lo usa solo como apoyo para confirmar firmas y hashes
  (`SKILL.md:19`, `SKILL.md:13`; registry `:108`).
- **Límites**: solo lectura de documentación; sin secretos, credenciales ni
  datos de pacientes; sin API key ni OAuth; la KB prevalece sobre la doc y
  `AGENTS.md` sobre herramientas externas. Es tooling de desarrollo, no una
  integración externa del producto: sigue vigente la regla "Ninguna integración
  externa en v1".
- **Dónde vive la configuración**: en `~/.config/opencode/opencode.json`,
  **fuera del repo** (formato V1 de OpenCode 1.19.3: `mcp.<nombre>` con
  `enabled: true`). El repo solo reproduce el fragmento sin secretos en
  `docs/skills-mcp/README.md:33-48`. Requiere Node.js con `npx` y fija la
  versión con `npx -y @neuledge/context@1 ... serve`. Comprobación documentada:
  `list`, `query fastapi "OAuth2PasswordRequestForm"` y
  `query passlib "CryptContext"` (`docs/skills-mcp/README.md:53-71`).

En esta sesión **no pude verificar la conexión efectiva** al servidor: las
herramientas de recursos MCP devolvieron listas vacías (`resources: []`,
`resourceTemplates: []`). Solo verifiqué la documentación del repo.

## 4. Intento real de invocar la Skill tool — resultado literal

**No se pudo emitir la invocación.** En esta sesión no figura ninguna
herramienta llamada `Skill` entre las herramientas expuestas; las disponibles
son de lectura/búsqueda de archivos, listings de recursos MCP y consulta web.
Por lo tanto **no hay un texto de respuesta literal de la herramienta que
pueda citar**: la llamada no llegó a ejecutarse y no la simulé. Resultado
literal que puedo reportar: *"herramienta Skill no disponible en esta sesión;
invocación no emitida"*.

Como referencia literal del repo, `docs/evidencias/audit-auth-c-03-auth-jwt-rbac.md:17-22`
registra que en otra sesión sí se intentó y la herramienta respondió:

> `Skill "auth-contract-audit" not found`

Ese mismo archivo indica que, ante la negative, se leyó
`.agents/skills/auth-contract-audit/SKILL.md` y se ejecutó el procedimiento en
forma manual. Es lo que hice acá para el punto 2: el descubrimiento por
instrucciones del repo funciona, pero la **carga de la Skill tool requiere que
la sesión la tenga registrada**. El repo lo describe así:

- `AGENTS.md:59` / `CLAUDE.md:59`: *"Los compact rules de cada skill los
  resuelve el orquestador desde `.atl/skill-registry.md` ... Esta tabla solo
  mapea skill→rol."* O sea: el indexado asume un orquestador que inyecta las
  reglas; un agente suelto no recibe la skill cargada.
- `.atl/skill-registry.md:3`: *"Delegator use only. Any agent that launches
  sub-agents reads this registry to resolve compact rules, then injects them
  directly into sub-agent prompts. Sub-agents do NOT read this registry or
  individual SKILL.md files."*
- `.agents/skills/active-orchestrator/SKILL.md:248` y `:275`: instrucciones
  del tipo *"Use the Skill tool to invoke `<skill-name>` for this project"* y
  `Skill("discovery-research")`: presuponen la herramienta.

Conclusión sobre este punto: el descubrimiento funciona; la invocación real de
la Skill tool **no** quedó comprobada en esta sesión.

## 5. Ambigüedades, omisiones y fricciones reales encontradas

1. **La Skill tool no está expuesta en esta sesión** y el repo la da por
   existente (`active-orchestrator/SKILL.md:248,275`), con un precedente de
   `Skill "auth-contract-audit" not found` en otra sesión
   (`docs/evidencias/audit-auth-c-03-auth-jwt-rbac.md:17-22`). El `AGENTS.md`
   no explica cómo pedirla ni qué hacer si no está.
2. **Registry "delegator only" vs. agente nuevo**: `.atl/skill-registry.md:3`
   dice que los sub-agentes NO leen el registry ni los `SKILL.md`, mientras
   `AGENTS.md:59` dice que los compact rules los resuelve el orquestador. Sin
   orquestador, tuve que leer igual registry y `SKILL.md` a mano para poder
   responder; no hay un camino documentado para ese caso.
3. **Configuración MCP fuera del repo**: `~/.config/opencode/opencode.json`
   (`AGENTS.md:69`, `docs/skills-mcp/README.md:4-5,35-48`). Leyendo solo el
   repo no se puede verificar el estado real del servidor; acá además los
   recursos MCP aparecieron vacíos.
4. **Protocolo de resolución referenciado pero ausente**: el registry dice
   *"See `_shared/skill-resolver.md` for the full resolution protocol"*
   (`.atl/skill-registry.md:5`) y la skill `skill-registry/SKILL.md:16,107`
   lo vuelve a citar, pero la búsqueda `_shared/skill-resolver.md` no devolvió
   archivos en el repo.
5. **Paths mezclados**: la tabla `User Skills` del registry usa rutas
   absolutas de esta máquina (líneas 11-25), mientras `Project Conventions`
   línea 182 aclara la ruta repo-relativa "para portabilidad". Un agente nuevo
   no sabe cuya usar.
6. **Nombres que no coinciden**: `AGENTS.md:53,57` y el registry `:15` hablan
   de `find-skills` (plural), pero el path apunta a
   `.agents\skills\find-skill\SKILL.md` (singular). Paso parecido con
   `agents-md-generator` (`AGENTS.md:52`) cuyo `SKILL.md` vive en
   `.agents\skills\agent-instruction\SKILL.md` (registry `:16`).
7. **Trigger en español vs. nombre en inglés**: el trigger del registry
   línea 19 es *"auditar contrato de seguridad de auth…"* y el rol en
   `AGENTS.md:55` dice "Skill propia / auditoría de auth", pero el
   `name:` del frontmatter es `auth-contract-audit` y su descripción está en
   inglés (`SKILL.md:2-3`). Buscar por el nombre en español no lleva
   directamente al archivo.
8. **"No hay skills de stack"**: la nota de `AGENTS.md:57` puede leerse como
   "no hay skills instaladas" cuando en realidad sí hay una propia de auditoría
   de auth; el paréntesis "(no de stack)" es fácil de pasar por alto.

## Conclusión general

La comprobación se cumple **en forma parcial**. Se cumple el descubrimiento en
sesión nueva: siguiendo solo `AGENTS.md`/`CLAUDE.md` → `.atl/skill-registry.md`
→ `SKILL.md` → READMEs, un agente encuentra la skill propia
`auth-contract-audit`, entiende su procedimiento y localiza el MCP `context`
con su propósito, límites y config. No se cumple la verificación de carga
efectiva: la Skill tool no está disponible en esta sesión (invocación no
emitida, sin respuesta literal propia) y los recursos del MCP aparecen vacíos.
La evidencia queda registrada acá sin simular resultados ni secretos.
