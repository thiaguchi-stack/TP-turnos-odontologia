# Skills del proyecto

Fuente: listado real de directorios (`Get-ChildItem .opencode\skills`,
`Get-ChildItem .agents\skills`) + `.atl/skill-registry.md` (registry generado
por `skill-registry`), `.active-orchestrator-state.json`, `docs/bitacora-inspeccion.md`
y `git log`. Sin inventar usos: si algo está instalado pero no hay registro de
que se haya usado, se dice.

A diferencia del proyecto de referencia (que instaló skills de stack — `tdd`,
`fastapi`, `python-pro`…), **acá todavía no hay skills de stack instaladas**;
`AGENTS.md` lo declara explícitamente ("hoy no hay skills de stack instaladas…
usar `find-skills` para buscar/recomendar e instalar solo con permiso
explícito"). Todo lo instalado corresponde a **orquestación/fundación** y al
**workflow OPSX**.

## Inventario (2 dirs versionados en el repo)

### `.opencode/skills/` — workflow OpenSpec (6)

```
openspec-apply-change    openspec-archive-change   openspec-explore
openspec-propose         openspec-sync-specs       openspec-update-change
```

(+ los wrappers de comando `.opencode/commands/opsx-{explore,propose,apply,archive,sync,update}.md`).

### `.agents/skills/` — orquestación y fundación (9)

```
active-orchestrator   agent-instruction   discovery-research
find-skill            kb-creator          roadmap-generator
skill-creator         skill-registry      web-scraper
```

- No existe `.claude/skills/` (verificado con `Test-Path`).
- `.agents/skills/` entró al repo en el commit `bcc289a` *"chore(skills): migrar
  skills a .agents/skills del proyecto"* (2026-10-15), siguiendo la convención
  de `AGENTS.md` (skills a nivel proyecto, viajan con el repo, nunca `-g`).

## Uso por etapa del flujo

El flujo completo fue `openspec init → discovery → KB → rules → roadmap →
propose → apply → verify → archive`. Orden y dueño de cada etapa:
`.active-orchestrator-state.json` (`step`, `created_by` de cada sección).

| Etapa | Fecha (commits/bitácora) | Skill usada | Por qué / evidencia |
|---|---|---|---|
| Arranque + `openspec init` | 2026-10-09 · commit `29d4b79` *"/active-orchestrator y openspec init"* | `active-orchestrator` | Orquestador del flujo de fundación; es el dueño exclusivo del state file (`.active-orchestrator-state.json`, `owner: "active-orchestrator"`). |
| **Discovery** (investigación de mercado) | 2026-10-09 → 2026-10-11 · commits `8a6b45d`, `95eee82` | `discovery-research` + `web-scraper` | `state.discovery.created_by = "discovery-research"`; `sources` = 3 URLs (dentaltotal.com.ar, doctoraliar.com.ar, tmdental.com.ar) → esas 3 las scrapearía `web-scraper` (sub-skill, 1 nota por URL, esquema fijo en `discovery/sources/`). Resultado: 34 sistemas en `discovery/raw/`; inspecciones **I-01/I-02** de `docs/bitacora-inspeccion.md`. |
| **Knowledge Base** | 2026-10-10 · commit `3f42b6c` | `kb-creator` | `state.kb.created_by = "kb-creator"`, `source: "interactive"`; generó los 10 canónicos + README en `knowledge-base/`. |
| **Rules** (reglas del proyecto) | step actual del state file: `"rules"` | `agent-instruction` (`agents-md-generator`) | Generó `AGENTS.md` + `CLAUDE.md` (idénticos) a partir de la KB, `CHANGES.md` y el mapeo skill→rol del registry. |
| **Roadmap** | 2026-10-11 · `CHANGES.md` | `roadmap-generator` | `state.roadmap.created_by = "roadmap-generator"`, `source: "CHANGES.md"`, lista `C-01…C-18`. Inspección **I-03**. |
| **Find skills + registry** | fase §4.2 del orquestador | `find-skill` → `skill-registry` | `.atl/skill-registry.md` (versiónado) con triggers + compact rules por skill; es la fuente que `AGENTS.md` referencia para la tabla "Skills Disponibles". |
| **OPSX Explore** | 2026-10-10 · `docs/explore/relevamiento-crear-turno-sin-solapamientos.md` | `openspec-explore` | Relevamiento read-only previo a la propuesta (inspección **I-04**): definió alcance Opción B y el desvío autónomo. |
| **OPSX Propose** | 2026-10-10 · carpeta del change | `openspec-propose` | Generó `proposal.md`, `design.md`, `specs/turnos/spec.md` (delta) y `tasks.md` (18 tasks) — solo planificación, sin código. |
| **OPSX Apply** | 2026-10-10 · commit `3f42b6c` *"etapa 5 6 y 7"* | `openspec-apply-change` | Implementó las 18 tasks (hoy 18/18 `[x]`); inspección **I-07**: cierre "solo con tests verdes" (58 passed). |
| **OPSX Sync + Archive** | 2026-10-10 · `openspec/specs/turnos/spec.md` + `openspec/changes/archive/2026-10-10-…/` | `openspec-sync-specs` → `openspec-archive-change` | El delta se sincronizó a la spec main (hoy solo difiere en el encabezado: `## ADDED Requirements` → `## Requirements`) y el change quedó en `archive/2026-10-10-…`. Registrado en `CHANGES.md`: *"Ciclo completo cerrado … explore → propose → apply → verify → archive el 2026-10-10"* y en `state.opsx.done = true`. |
| **Verify** (esta carpeta) | 2026-10-15 · `docs/evidencias/` | *(sin skill propia)* | OPSX no tiene comando de verify: se corrieron `pytest`/`ruff` a mano y se dejó la trazabilidad en `verify-crear-turno-sin-solapamientos.md`. |
| `skill-creator` | — | `skill-creator` | **Instalada, sin uso registrado** en el repo (no hay `evals/` ni skills propias creadas). Se dejó disponible para cuando se necesite crear/editar una skill. |

## Regla de precedencia

Si una skill contradice una regla de `AGENTS.md`, **manda `AGENTS.md`** (así
está escrito en el propio `AGENTS.md` §Reglas Duras: *"Ante conflicto entre la KB
y este archivo, las reglas duras prevalecen"*, y en la cabecera de
`.atl/skill-registry.md`: los compact rules se resuelven desde el registry y no
se copian a los prompts).

## Cómo se actualiza este archivo

1. `Get-ChildItem .opencode\skills` y `Get-ChildItem .agents\skills` (inventario).
2. `.atl/skill-registry.md` (triggers y compact rules — regenerar con
   `skill-registry` si cambió algo).
3. `.active-orchestrator-state.json` + `git log` + `docs/bitacora-inspeccion.md`
   (qué se usó y cuándo).
