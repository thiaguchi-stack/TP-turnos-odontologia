# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

See `_shared/skill-resolver.md` for the full resolution protocol.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| /active-orchestrator:init, :kb, :rules, :discovery, :openspec, :devops, :find-skill, :registry — start a new project with the SDD/OpenSpec foundation flow | active-orchestrator | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\active-orchestrator\SKILL.md |
| descubrir/explorar el problema y el mercado antes de armar la KB; orquestado por active-orchestrator (fase discovery) | discovery-research | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\discovery-research\SKILL.md |
| crear/base/generar KB, "armar base de conocimiento", "documentar proyecto"; desde docs o desde cero | kb-creator | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\kb-creator\SKILL.md |
| armar CHANGES.md / roadmap / mapa de changes / plan de implementación / índice de changes | roadmap-generator | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\roadmap-generator\SKILL.md |
| "find a skill for X", "is there a skill for X", "how do I do X" (extender capacidades con skills del ecosistema) | find-skills | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\find-skill\SKILL.md |
| crear/generar/actualizar AGENTS.md o CLAUDE.md, "armar las reglas del proyecto", "instrucciones para los agentes" | agents-md-generator | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\agent-instruction\SKILL.md |
| investigar/scrapear un competidor a partir de una URL (nota markdown de esquema fijo) — sub-skill de discovery-research | web-scraper | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\web-scraper\SKILL.md |
| crear una skill desde cero, editar/mejorar una skill existente, correr evals/benchmarks o optimizar el trigger de una skill | skill-creator | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.agents\skills\skill-creator\SKILL.md |
| openspec explore / opsx explore — pensar un problema antes o durante un change | openspec-explore | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.opencode\skills\openspec-explore\SKILL.md |
| openspec propose / opsx propose — proponer un change con todos los artifacts | openspec-propose | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.opencode\skills\openspec-propose\SKILL.md |
| openspec apply / opsx apply / openspec implement — implementar los tasks de un change | openspec-apply-change | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.opencode\skills\openspec-apply-change\SKILL.md |
| openspec archive / opsx archive — archivar un change completado | openspec-archive-change | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.opencode\skills\openspec-archive-change\SKILL.md |
| openspec sync / opsx sync — sincronizar delta specs a specs main sin archivar | openspec-sync-specs | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.opencode\skills\openspec-sync-specs\SKILL.md |
| openspec update change / opsx update — revisar artifacts de planificación de un change (nunca edita código) | openspec-update-change | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\.opencode\skills\openspec-update-change\SKILL.md |

## Compact Rules

Pre-digested rules per skill. Delegators copy matching blocks into sub-agent prompts as `## Project Standards (auto-resolved)`.

### active-orchestrator
- Thin orchestrator: NEVER reimplement phase logic — route to sub-skill (Skill para fases interactivas, Agent para mecánicas).
- NO preguntar preguntas de contenido estratégico (system_type, scale, stack, checklist discovery) — esas son de kb-creator/discovery-research. Solo preguntás "¿hacer Discovery?" (phase-selection) y checkpoints.
- OWNER exclusivo del state file `.active-orchestrator-state.json`: solo escribe `version`, `step`, `owner`. Sub-skills escriben sus secciones.
- Check sub-skill presence antes de dispatch; si falta → ofrecer install → degradar si declina.
- Resume: si state existe con `step != "done"`, preguntar continuar o desde cero.
- Checkpoint en cada frontera de fase: nunca avanzar `step` sin "Continuar" explícito del usuario; nunca correr fases back-to-back.
- Orden de fases (§4.2): openspec init → [discovery-research opcional] → kb-creator → roadmap-generator → find-skill → skill-registry → agent-instruction.
- NUNCA instalar skills autónomamente; find-skill solo recomienda, el usuario decide (install gate). Instalación SOLO a project scope (`.agents/skills/`, sin `-g`) — escribe archivos que se commitean (HIGH governance).
- Lazy-load check: `npx skills list | grep <skill>` (scope de proyecto).
- Standalone commands (`/active-orchestrator:kb`, `:rules`, etc.) corren UNA fase y paran — sin gate de avance.
- Voseo rioplatense cuando el usuario habla español.

### discovery-research
- Fase de gobernanza MEDIA: checkpoints; nunca escribir `discovery/discovery.md` ni `state.discovery` sin confirmación explícita del usuario.
- Si hay URLs de competidores → invocar web-scraper una vez por URL; no reimplementar scraping. Sin URLs, seguir con Q&A pura (no bloquear).
- Correr `scripts/collect_sources.py` tras el scraping para tabla comparativa.
- Q&A de 11 puntos guiada por `references/checklist.md`; si un punto ya está resuelto por scraping, mostrar como resumen y pedir confirmación, no repreguntar.
- Riesgos/preguntas abiertas: assumption-mapping — todo supuesto sin probar alimenta riesgos.
- Salida: `discovery/discovery.md` (prosa, patrón `assets/example-discovery.md`) + sección `discovery` del state (schema en `references/state-contract.md`); escribir SOLO esa sección.

### kb-creator
- 10 canónicos obligatorios con nombres exactos en `knowledge-base/` (raíz, NUNCA en docs/): 01_vision, 02_descripcion, 03_actores, 04_modelo_de_datos, 05_reglas_de_negocio, 06_funcionalidades, 07_flujos, 08_arquitectura, 09_decisiones, 10_preguntas_abiertas + README.md índice.
- Auto-detecta Mode A (docs/ con fuentes → silent, source "ingest") vs Mode B (desde cero → interactivo, source "interactive"); usar estructura de `assets/canonical-templates.md`.
- Mode A: no preguntar; ambigüedad → 10_preguntas_abiertas.md. Nunca inventar un valor de discovery con baja confianza.
- Mode B: socio estratégico — párrafo de entendimiento, 3-5 incertidumbres, 2-3 enfoques, 3-5 preguntas estratégicas, esperar respuesta antes de escribir archivos.
- Extras permitidos con prefijo `1X_`/`2X_` kebab-case; nunca reemplazan a los 10 canónicos.
- Hook de estado (solo si state existe): escribir `state.kb` (created_by, source, discovery, files) y nada más.

### roadmap-generator
- Pre-checks obligatorios antes de generar: knowledge-base/ existe + 10 canónicos + openspec/ existe. Si falla → NO generar, mensaje claro.
- Salida: UN archivo `CHANGES.md` en la raíz del proyecto (no dentro de openspec/).
- Input: si orquestado usar `state.kb.files` (autoritativo) + `state.kb.discovery` (hint); standalone leer `04_modelo_de_datos`, `06_funcionalidades`, `07_flujos`, `08_arquitectura` (+03, 05, 10 si existen).
- Estructura fija (contrato, no agregar/quitar secciones de 1er nivel): árbol de dependencias, gates, camino crítico, plan 3 agentes, fases con items `### [C-NN] kebab-case` → Estado/Scope/Dependencias/Governance/Leer antes.
- Códigos C-NN padding 2 dígitos; kebab-case sin prefijos us-NNN-. Scope con bullets operacionales (endpoints/migraciones/tests concretos), no descriptivos.
- Dependencias: infra (C-01) primero → modelos core → auth → entidad referenciada → backend antes que frontend → integraciones/pagos al final → admin después → refactors UI al último.
- Governance: BAJO (scaffolding/CRUD) | MEDIO (estado/flujos) | ALTO (notifs/roles/WS/observabilidad) | CRITICO (auth, pagos, datos sensibles, modelos core).
- Hook de estado: escribir `state.roadmap` (created_by, source "CHANGES.md", changes lista C-NN); no tocar `step`. Cerrar sugiriendo `/opsx:propose C-01`.

### find-skills
- Buscar skills del ecosistema (`npx skills find`, browse en skills.sh); líderboard primero para skills conocidas.
- Verificar calidad antes de recomendar: install count (preferir 1K+, cautela <100), reputación de la fuente (vercel-labs, anthropics, microsoft), stars del repo (<100 → escepticismo).
- Modo recomendar: presentar nombre, qué hace, install count, fuente, comando `npx skills add <owner/repo@skill>`.
- Instalar solo con permiso explícito y a project scope: `npx skills add <owner/repo@skill> -y` — SIN `-g` (cae en `.agents/skills/` del proyecto; por convención del proyecto las skills viven en el repo, nunca a user level).
- Si no hay skill relevante: ofrecer hacerlo manualmente o `npx skills init`.

### agents-md-generator
- Pre-checks: knowledge-base/ + 02_descripcion_general.md existen; sin CHANGES.md generar igual omitiendo sección Roadmap y avisando.
- Salida: `AGENTS.md` Y `CLAUDE.md` en la raíz, contenido idéntico (copia, no referencia).
- Leer el global `~/.claude/CLAUDE.md` para NO repetir sus reglas universales; referenciarlo con una línea, escribir solo reglas específicas del proyecto + universales ausentes del global.
- Skills: leer `.atl/skill-registry.md` como fuente de verdad (no re-escaneo) y mapear skill→rol con tabla; NO copiar compact rules (DRY: viven solo en el registry). Fallback si no existe: escanear `.agents/skills/` + `.claude/skills/` + `~/.claude/skills/`.
- Reglas duras: stack-aware (PascalCase/anys/tsconfig para React, snake_case/type hints para Python, etc.), NUNCA hardcodeadas.
- Única parte interactiva = confirmar reglas duras con el usuario (AskUserQuestion) → escribir solo lo confirmado.
- Secciones contrato: Stack | Base de Conocimiento | Skills Disponibles | Roadmap | Reglas Duras | Flujo de Trabajo (KB → CHANGES → /opsx:propose → archive).

### web-scraper
- Esquema de salida FIJO de 8 campos, siempre en el mismo orden (`references/output-schema.md`), aunque un campo quede `(no publicado)`.
- NUNCA inventar datos que la página no muestra; un campo vacío marcado vale más que uno inventado.
- Validar URLs http(s); si la página da 403/paywall/CAPTCHA/SPA vacío → reportar limitación, NO reintentar con evasión.
- No crawling ni scraping masivo: solo páginas puntuales explícitamente pasadas (JS pesado/anti-bot = fuera de v1).
- Escribir `discovery/sources/<slug>.md` (slug via `scripts/slugify.py`; repetir el mismo competidor pisa el mismo archivo).
- Procesar URLs una por una; reportar cuántas resolvieron/fallaron sin abortar el lote por una URL caída.

### skill-creator
- Loop: capturar intención → entrevista/borrador → test prompts → runs → evaluar → iterar; ubicar en qué etapa está el usuario y arrancar desde ahí (si dice "no evalúes, andá a lo simple", respetar).
- Frontmatter `name` + `description` obligatorios; la description es el mecanismo de trigger: decir QUÉ hace Y CUÁNDO usarla, un poco "pushy" (combate el undertrigger).
- Progressive disclosure: SKILL.md <500 líneas ideal; capas extra en archivos referenciados con indicación de cuándo leerlos; TOC en referencias >300 líneas; organizar por dominio en `references/`.
- Estilo: forma imperativa, explicar el porqué en lugar de MUSTs pesados; definir plantillas de salida exactas y ejemplos Input/Output.
- Test cases: 2-3 prompts realistas en `evals/evals.json` (solo prompts al inicio), confirmarlos con el usuario; spawnear TODOS los runs (with-skill Y baseline) en el mismo turno y redactar asserts mientras corren.
- Prohibido malware/exploits ni skills engañosas o de acceso no autorizado (principle of lack of surprise).
- Optimización de description al final (evals de triggers + loop) solo cuando la skill está estable; aplicar el resultado y re-testear.

### openspec-explore
- Modo pensar, NO implementar: read-only sin confirmación; nunca escribir código ni features.
- Antes de cualquier acción write-capable (incluye `openspec new change`): nombrar artifacts/archivos a cambiar, preguntar sí/no, esperar confirmación en mensaje separado.
- Auto-capture prohibido: solo ofrecer capturar insights; confirmación cubre solo el scope descrito.
- ASCII para diagramas, NO unicode (anchos de terminal).
- Arrancar con `openspec list --json` + `openspec list --specs` + leer `openspec/config.yaml` (context/rules = constraints, NO copiarlos al output).
- Nunca scaffoldear changes a mano: siempre `openspec new change "<name>"` (con `--store <id>` cuando aplique).

### openspec-propose
- Solo crea artifacts de planificación (proposal.md, specs/<capability-path>/spec.md, design.md, tasks.md) — NUNCA editar código; al terminar parar y esperar request nuevo para apply.
- Al autorizar con un request que pide implementar: autoriza SOLO planificación; no arrastrar implementación.
- Store selection: si hay store nombrado/registrado, `openspec store list --json`, luego `--store <id>` sticky en comandos de specs/changes.
- Project check: `openspec list --json` y leer `root` antes de escribir; `root: null` → NO crear como side effect; decidir según auto-selected (parar, responder normal) vs explícito (preguntar init/store).
- `openspec context --json` para root autoritativo; fallos → parar, no fallback al cwd.
- Build order: `openspec status --change "<name>" --json` → `applyRequires` + requisitos transitivos via `requires` edges (NO `status done`); `openspec instructions <artifact-id>` para template/rules.
- Releer dependencias desde disco (el usuario pudo editarlas); `context`/`rules` son constraints, NO contenido del artifact.

### openspec-apply-change
- Seleccionar change; ambiguo → `openspec list --json` + preguntar. Anunciar "Using change: <name>".
- `openspec status --change --json` para schema/planningHome/contexto; `openspec instructions apply --change --json` para contextFiles y tasks.
- Estado blocked: mostrar mensaje y pausar (missingArtifacts → completarlos antes).
- Leer TODOS los contextFiles antes de implementar (proposal/specs/design/tasks). No copiar `context`/`operationGuidance` al código.
- Loop por task: cambios mínimos; marcar checkbox en el `sourcePath`/`line` devuelto; re-correr apply instructions para confirmar progreso.
- Pausar si: task ambiguo, se revela issue de diseño (sugerir update de artifacts), scope extra necesario, error/blocker.
- Nunca marcar `- [x]` si el comportamiento especificado no está completo (no parcial, no diferido).

### openspec-archive-change
- Seleccionar change (solo activos); `openspec instructions archive` = advisory, nunca bloquea.
- Advertencias (no bloquean, solo confirmar): artifacts incompletos o tasks incompletos; contar tasks vía `openspec list --json` (solo marcadores x/X).
- Delta sync assessment ANTES de archivar: comparar deltas vs main specs; si hay cambio pendiente → opciones "Sync now / Archive without syncing / Cancel".
- Capability nueva solo se crea con ADDED; MODIFIED/RENAMED sin main spec = sync-blocked; REMOVED-only requiere `retire_capabilities: true`.
- Sync inline (nunca en background — movería changeRoot durante el sync); verificar estructura post-sync antes de archivar.
- Archivar: `mkdir -p <changesDir>/archive`, mover changeRoot a `archive/YYYY-MM-DD-<name>`; no doble fecha; error si destino existe.
- No archivar mientras un sync esté en vuelo; nunca copiar texto de context/operationGuidance/rules a archivos de salida.

### openspec-sync-specs
- Merge agent-driven: editar main specs directamente (inteligente), no copiar el delta tal cual.
- Delta specs SOLO desde `artifactPaths.specs.existingOutputPaths`; nunca inferir de otros artifacts; honrar subset del caller, no ensanchar.
- Main spec nuevo: solo ADDED requirements (MODIFIED/RENAMED sin main = parar y reportar); REMOVED-only requiere `retire_capabilities: true`.
- `## Purpose` main = autoritativo, dejar intacto. Un nuevo main copia el Purpose del delta verbatim; si falta, placeholder TBD breve + avisar.
- Main specs SIN headers de delta (`## ADDED/MODIFIED/REMOVED/RENAMED`); todo bajo `## Requirements`. Requerimientos `### Requirement:` con `#### Scenario:`.
- Requirement retire → borrar spec.md + dir solo si TODAS las condiciones (sin requirements restantes, Purpose presente, no vacío antes, `retire_capabilities: true`, path real, resto del archivo canónico).
- Validar con `openspec validate --specs`; si falla, no afirmar éxito.

### openspec-update-change
- Nunca edita código: solo planning artifacts existentes. Si el plan implica código, apuntar a /opsx-apply.
- Usar artifact ids/paths de `openspec status --json`; editar solo `artifactPaths.<id>.existingOutputPaths` (paths concretos), nunca `resolvedOutputPath` (glob).
- Reconciliar en AMBAS direcciones (editar artifact posterior puede requerir revisar uno anterior).
- Confirmar CADA edit con el usuario antes de escribir; escriba tras confirmación.
- Changes "skipped": no tocar. Glob artifact parcialmente poblado → crear path concreto solo tras confirmación, con create-que-falla-si-existe.
- Si el request cambia la INTENCIÓN del change (no lo refina) → sugerir `openspec new change` con nombre nuevo (heuristic Update vs Start Fresh).
- Complete + implementado → sugerir `/opsx-archive`.

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| AGENTS.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\AGENTS.md | Index — references files below (Stack, KB, Skills, Roadmap, Reglas Duras, Flujo de Trabajo) |
| CLAUDE.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\CLAUDE.md | Copia idéntica de AGENTS.md (hash igual) — también indexa los archivos de abajo |
| CHANGES.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\CHANGES.md | Referenced by AGENTS.md/CLAUDE.md — roadmap de 18 changes |
| knowledge-base/01_vision_y_objetivos.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\01_vision_y_objetivos.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/02_descripcion_general.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\02_descripcion_general.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/03_actores_y_roles.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\03_actores_y_roles.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/04_modelo_de_datos.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\04_modelo_de_datos.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/05_reglas_de_negocio.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\05_reglas_de_negocio.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/06_funcionalidades.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\06_funcionalidades.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/07_flujos_principales.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\07_flujos_principales.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/08_arquitectura_propuesta.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\08_arquitectura_propuesta.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/09_decisiones_y_supuestos.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\09_decisiones_y_supuestos.md | Referenced by AGENTS.md/CLAUDE.md |
| knowledge-base/10_preguntas_abiertas.md | C:\Facultad\3er Semestre\Metodologia I\TP-turnos-odontologia\knowledge-base\10_preguntas_abiertas.md | Referenced by AGENTS.md/CLAUDE.md |

Read the convention files listed above for project-specific patterns and rules. All referenced paths have been extracted — no need to read index files to discover more.
