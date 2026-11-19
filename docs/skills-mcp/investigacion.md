# Ficha de investigación — Skill propia y MCP para C-03

Fecha de consulta de las fuentes externas: 2026-11-18. Alcance: Parte 1 del TP de Metodología I (consigna `mcp-skills.pdf`).

**Actualización 2026-11-19:** esta ficha conserva el contexto de la investigación del 2026-11-18, cuando `C-03` era el próximo change y su implementación estaba fuera de alcance. Hoy `C-03` está archivado en `openspec/changes/archive/2026-11-18-c-03-auth-jwt-rbac/` (`CHANGES.md:172-173`) y la skill `auth-contract-audit` figura disponible en la lista de skills de la sesión actual (sin invocación nueva verificada).

## 1. Necesidad detectada y change elegido

Se eligió `C-03-auth-jwt-rbac` (JWT OAuth2 password flow + RBAC admin/odontólogo): es el próximo del camino crítico, tiene governance **CRITICO** y depende de `C-02 core-models`, archivado el 2026-10-15. No requiere funcionalidades inexistentes —el seed ficticio y el stub de `security.py` ya llegaron con C-02—, así que se pueden preparar análisis, specs y tasks; la implementación queda **fuera de alcance** hasta el gate humano de `AGENTS.md`. La tarea repetible es revisar a mano el contrato de seguridad al preparar artefactos de auth: RN-AU-01/02/03/04, DD-07 (routers delgados, regla en servicios) y RN-DATOS-01/02. Hoy esa revisión vive en la KB y en la memoria del equipo, sin checklist ni evidencia; el riesgo es perder una regla en el delta o escribir tasks no verificables. La necesidad MCP es complementaria: consultar documentación **versionada** de FastAPI 0.110.x y passlib 1.7.4 sin depender de un índice remoto mutable que responda con la API de otra release. La KB sigue mandando; el MCP solo reduce el riesgo de errar firmas, hashing y OAuth2.

## 2. Skill creadora y diseño de la skill propia

Creadora: `opencode-skill-creator` **v0.3.7**, instalada y habilitada como plugin en `~/.config/opencode/opencode.json` (clave `plugin`). El manifiesto local `.opencode-skill-creator-manifest.json` declara `schema: 1` y `packageVersion: 0.3.7`. Fuente oficial: repo `antongulin/opencode-skill-creator`, de Anton Gulin, Apache-2.0, adaptación de Anthropic skill-creator; release v0.3.7 del 2026-11-15. Declara soporte V2 y V1 ≥ 1.18.29; `opencode --version` dio **1.19.3**, dentro de V1 (de ahí la clave `plugin`, no `plugins`). Su flujo exige entrevista de 3–5 preguntas, borrador en staging, 2–3 evals con corridas pareadas (con/sin skill), grader, benchmark, revisión visual y, opcional, `skill_optimize_loop`; recién después se instala lo validado, en project scope (`.agents/skills/`, fuente de compatibilidad de OpenCode).

La skill propia `auth-contract-audit` la genera otro agente: acá solo se documenta el diseño. Audita el contrato de seguridad de un change de auth antes de prepararlo o implementarlo; se activa al proponer, implementar o revisar changes con JWT, login, RBAC, roles o endpoints protegidos (descripción "pushy" contra la subactivación conocida). Entradas: ruta al change y sus artefactos, más `knowledge-base/03_actores_y_roles.md`, `05_reglas_de_negocio.md`, `08_arquitectura_propuesta.md` y `09_decisiones_y_supuestos.md`. Procedimiento: (1) leer las reglas de la KB; (2) mapear cada endpoint/rol a RN-AU; (3) verificar que cada regla tenga escenario verificable (éxito, error de negocio, borde); (4) chequear que las tasks digan cómo se verificará cada escenario; (5) revisar que no se exponga `password_hash` ni falte `require_role`/`require_odontologo_own`; (6) emitir `docs/evidencias/audit-auth-<change>.md` con tabla regla→cobertura→evidencia y gaps priorizados. Criterios: RN-AU-01..04 con escenario, ningún hallazgo sin cita de regla/KB, sin secretos en ejemplos, sin código de producción (governance CRITICO) y español rioplatense. Ubicación final: `.agents/skills/auth-contract-audit/SKILL.md`.

## 3. Servidores MCP comparados y elección

| Servidor | Transporte y documento | Credenciales y permisos | Costo | Encaje para C-03 |
|---|---|---|---|---|
| `context7` | Remoto, `https://mcp.context7.com/mcp`; índice Upstash, snippets actualizados; versión pedida en el prompt | OAuth por defecto; doc recomienda API key (1.000 llamadas/mes en cuenta free) | Gratis; key opcional/recomendada | Panorama general, pero el índice puede refrescarse: no está atado a un artefacto inmutable |
| `@neuledge/context@1` | Local por stdio, SQLite FTS5 en `~/.context/packages/`; versiones conviven y `serve --libs nombre@version` fija el alcance | Sin API key; todo queda en la máquina | Gratis, sin suscripción ni cupos según el repo oficial | Paquetes instalados: `fastapi@0.110.3`, `passlib@1.7.4` |

Se elige el **local `context`**: el riesgo identificado es que la documentación de auth cambie entre versiones y el contrato de C-03 debe quedar atado a FastAPI 0.110.x y passlib 1.7.4. Un paquete `.db` por versión, consultable offline, hace reproducible la decisión y evita que un reindexado remoto altere la respuesta. `context7` sigue habilitado para búsqueda amplia, pero no es fuente de verdad del contrato. Los repos oficiales confirman local-first/privado/sin key (context) e índice remoto con OAuth/key (Context7).

## 4. Instalación y configuración

Comandos ya ejecutados:

```sh
npx -y @neuledge/context@1 install pip/fastapi 0.110.3
npx -y @neuledge/context@1 add https://github.com/notypecheck/passlib --tag 1.7.4 --path docs --name passlib --pkg-version 1.7.4
```

Dos problemas resueltos: `0.110` devolvía 404 porque el registro exige versión exacta (→ `0.110.3`); passlib no está en el registro y se construyó desde el repo fork `notypecheck/passlib`, con `--tag` obligatorio en shell no interactivo y `--path docs` porque la doc vive en esa carpeta. Config global `~/.config/opencode/opencode.json`, sección `mcp`, entrada `context` con `command: ["npx","-y","@neuledge/context@1","serve"]`, `enabled: true`, `type: "local"`, sin secretos. Como esa config queda **fuera del repo**, se documenta acá para reproducibilidad. Dos discrepancias: la doc V2 de OpenCode usa `mcp.servers`/`disabled`, mientras acá se usa el formato V1 (`mcp.<nombre>` + `enabled`), coherente con 1.19.3; el README de context sugiere `["context","serve"]`, reemplazado por `npx` para fijar versión.

## 5. Archivos de la fundación a actualizar

- `.atl/skill-registry.md`: alta de `auth-contract-audit` con su rol y reglas de instalación.
- `AGENTS.md` y `CLAUDE.md` (idénticos): referencia a la skill y al MCP, sin tocar las reglas duras.
- `README.md`: cómo reproducir los comandos `context install`/`context add`.
- `CHANGES.md`: mención en la entrada de `C-03` como apoyo de governance, sin cambiar su estado.
- `docs/skills-mcp/aplicacion.md`: a crear en la Parte 2 con la aplicación concreta.
- `docs/evidencias/`: informes `audit-auth-<change>.md` y capturas de las consultas.

## 6. Fuentes consultadas

- Manifiesto local de opencode-skill-creator (v0.3.7) — file:///C:/Users/Usuario/.config/opencode/skills/opencode-skill-creator/.opencode-skill-creator-manifest.json (consultado 2026-11-18)
- SKILL.md local de opencode-skill-creator — file:///C:/Users/Usuario/.config/opencode/skills/opencode-skill-creator/SKILL.md (consultado 2026-11-18)
- Repo oficial de opencode-skill-creator (Anton Gulin) — https://github.com/antongulin/opencode-skill-creator (consultado 2026-11-18)
- Release v0.3.7 de opencode-skill-creator — https://github.com/antongulin/opencode-skill-creator/releases (consultado 2026-11-18)
- Paquete npm opencode-skill-creator (compatibilidad V1/V2) — https://www.npmjs.com/package/opencode-skill-creator (consultado 2026-11-18)
- Documentación de OpenCode: Skills — https://opencode.ai/docs/skills/ (consultado 2026-11-18)
- Documentación de OpenCode: MCP servers — https://opencode.ai/docs/mcp-servers/ (consultado 2026-11-18)
- Documentación de OpenCode: migración de V1 — https://opencode.ai/docs/migrate-v1 (consultado 2026-11-18)
- Repo oficial de @neuledge/context — https://github.com/neuledge/context (consultado 2026-11-18)
- Documentación oficial de Context7 — https://context7.com/docs (consultado 2026-11-18)
- Repo oficial de Context7 (Upstash) — https://github.com/upstash/context7 (consultado 2026-11-18)
- Repo del fork de passlib usado — https://github.com/notypecheck/passlib (consultado 2026-11-18)
- Config global de OpenCode — file:///C:/Users/Usuario/.config/opencode/opencode.json (consultado 2026-11-18)
- KB del proyecto: `knowledge-base/03_actores_y_roles.md`, `05_reglas_de_negocio.md` (RN-AU/RN-DATOS), `08_arquitectura_propuesta.md` (§Seguridad), `09_decisiones_y_supuestos.md` (DD-07); `CHANGES.md` §C-03 y `AGENTS.md` (consultado 2026-11-18)

Pendiente de verificación: cuota exacta del endpoint remoto de Context7 sin API key (la doc oficial recomienda key/OAuth y publica 1.000 llamadas/mes para cuenta free, pero no detalla el uso anónimo).

Pendiente de verificación: el PDF de consigna `mcp-skills.pdf` no está en el repo; los requisitos transcriptos arriba provienen del enunciado del equipo.
