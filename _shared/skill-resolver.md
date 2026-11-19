# Skill Resolver Protocol

Documento de fundación (**no es una skill**). Lo consume el agente que delega trabajo a sub-agentes. La fuente de verdad de las skills es `.atl/skill-registry.md`; acá se define cómo resolverla e inyectarla.

## Propósito

El registry se construye **una vez** (costo alto: leer todos los `SKILL.md` y digerir sus reglas) y se consume **barato** en cada delegación: el orquestador copia los bloques de reglas compactas al prompt del sub-agente. El sub-agente no vuelve a leer el registry ni los `SKILL.md` por iniciativa propia.

## Cuándo ejecutarlo

- Antes de cada llamada a `task` que pueda beneficiarse de una skill del proyecto.
- Después de instalar, quitar o modificar skills: regenerar `.atl/skill-registry.md` con la skill `skill-registry` y revisar los bloques de la skill propia.

## Procedimiento

1. Leer `.atl/skill-registry.md` **una vez por sesión**. Fallback: `.agents/SKILLS.md`, si existe. Si no hay ninguno de los dos, omitir la sección de reglas en el prompt y dejar constancia de la ausencia.
2. Comparar los triggers de `## User Skills` con las tareas concretas del change y seleccionar solo las skills que apliquen. No inyectar el registry completo.
3. Copiar **enteros** los bloques `### <skill-name>` de `## Compact Rules` que correspondan, dentro de un encabezado `## Project Standards (auto-resolved)` en el prompt del sub-agente. No resumirlos ni recortarlos: son reglas ya pre-digeridas.
4. Pasar la ruta del `SKILL.md` como **contexto** (no su contenido) para que el sub-agente sepa dónde profundizar si lo necesita.
5. `## Project Conventions` se usa para resolver rutas de convenciones del repo sin hops extra; preferir las rutas repo-relativas sobre las absolutas cuando ambas estén presentes.

## Reglas de resolución de rutas

- Primario: skills del proyecto (`.agents/skills/`, `.opencode/skills/`, `.claude/skills/`, etc.).
- Fallback legacy: skills de usuario (`~/.config/opencode/skills/`, `~/.claude/skills/`, etc.); **nunca instalar ahí**.
- Deduplicar por nombre: gana la versión del proyecto.
- Excluir del escaneo: `sdd-*`, `_shared` y `skill-registry`.

## Gotchas verificados (2026-11-18)

- Agregar un `SKILL.md` al repo **no** lo hace visible de inmediato para la herramienta `Skill` en la sesión en curso: al intentar `Skill "auth-contract-audit"` respondió `Skill "auth-contract-audit" not found`. El descubrimiento por `AGENTS.md`/registry sí funcionó y el procedimiento se ejecutó leyendo el `SKILL.md`. La invocación por herramienta queda para una sesión que cargue la skill.
- Un MCP no es una skill: se documenta como integración (config global `~/.config/opencode/opencode.json` + copia reproducible en el repo) y no entra en este registry.
- La base de conocimiento prevalece sobre documentación externa; el MCP es apoyo técnico de firmas y hashing, nunca fuente de reglas de negocio.
- Si se regenera el registry, volver a revisar los bloques de `auth-contract-audit`: se recalculan desde el `SKILL.md`.
