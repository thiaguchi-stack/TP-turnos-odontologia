# Informe de aplicación — Skill propia y MCP en C-03

Fecha: 2026-11-18. Change: `c-03-auth-jwt-rbac` (**preparado, NO implementado**). Alcance: Parte 2 del TP `mcp-skills.pdf`.

## 1. Resultados

- **Skill propia**: `auth-contract-audit`, generada con la skill creadora `opencode-skill-creator` v0.3.7 (invocada de verdad, con staging en `%TEMP%\opencode-skills\`). `skill_validate` devolvió `{"valid": true, "message": "Skill is valid!"}`.
- **MCP**: servidor local `context` (`@neuledge/context@1 serve`) operativo con `fastapi@0.110.3` (824 secciones) y `passlib@1.7.4` (152 secciones). Se ejecutaron `list`, `query` y cuatro llamadas a `context_get_docs`.
- **Change C-03**: `openspec status` indica los 4 artefactos en `done` (`isPlanningComplete: true`), `openspec validate --strict` limpio, **14 escenarios verificables** y **20 tareas** con verificación explícita. `completedTasks: 0/20`: ninguna tarea de implementación se ejecutó.
- **Fundación**: skill registrada y referenciada; MCP documentado como tooling de desarrollo, no como integración del producto.

## 2. Evidencias

| Archivo | Qué demuestra |
|---|---|
| [investigacion.md](investigacion.md) | Ficha de la Parte 1: necesidad, diseño de la skill, comparación de dos MCP, elección y fuentes |
| [../evidencias/skill-auth-contract-audit.md](../evidencias/skill-auth-contract-audit.md) | Solicitud a la creadora, staging, frontmatter final y validación |
| [../evidencias/mcp-context-query.txt](../evidencias/mcp-context-query.txt) | Salida real de `context list` y `context query` |
| [../evidencias/mcp-context-c03.md](../evidencias/mcp-context-c03.md) | Cuatro solicitudes a `context_get_docs`, con aporte a decisiones de `design.md`/`tasks.md` |
| [../evidencias/audit-auth-c-03-auth-jwt-rbac.md](../evidencias/audit-auth-c-03-auth-jwt-rbac.md) | Auditoría de las 8 reglas, mapa regla→escenario→tarea y correcciones antes/después |
| [../evidencias/nueva-sesion-skill-mcp.md](../evidencias/nueva-sesion-skill-mcp.md) | Comprobación en sesión nueva: descubrimiento por instrucciones y resultado de la invocación |
| [../../openspec/changes/c-03-auth-jwt-rbac/](../../openspec/changes/c-03-auth-jwt-rbac/) | `proposal.md`, `design.md`, `specs/user-auth/spec.md`, `tasks.md` |

## 3. Archivos modificados y motivo

| Archivo | Modificación y motivo |
|---|---|
| `.agents/skills/auth-contract-audit/SKILL.md` | Skill nueva: procedimiento de auditoría de auth adaptado a RN-AU y DD-07. |
| `.atl/skill-registry.md` | Alta de la skill (trigger, ruta y compact rules) para que el orquestador la resuelva. |
| `AGENTS.md` / `CLAUDE.md` | Fila de skill propia, sección `## Integraciones MCP` y mención de apoyo a C-03; se mantuvieron idénticos. |
| `README.md` | Enlaces al entregable `docs/skills-mcp/` y a la config reproducible. |
| `docs/skills-mcp/investigacion.md` | Ficha de investigación (Parte 1). |
| `docs/skills-mcp/README.md` | Instalación, config V1 sin secretos, comprobación, límites y problemas resueltos del MCP. |
| `docs/evidencias/README.md` | Índice de las nuevas evidencias. |
| `docs/evidencias/*` (5 archivos) | Evidencias de creadora, MCP, auditoría y sesión nueva. |
| `openspec/changes/c-03-auth-jwt-rbac/**` | Artefactos del change preparado. |
| `CHANGES.md` | Nota de preparación de C-03; el estado sigue `[ ] pendiente`. |

La config del MCP quedó en `~/.config/opencode/opencode.json` (fuera del repo); por eso se documentó en `docs/skills-mcp/README.md`. La KB no se modificó: las reglas ya cubrían el caso y la auditoría las cita.

## 4. Revisión crítica (detección → fuente → antes/después)

1. **Rutas públicas sin prueba reproducible**. La skill detectó que `tasks.md` decía "verificar manualmente". Fuente: RN-AU-01 y `03_actores_y_roles.md:22-28`. *Antes*: sin comando ni códigos. *Después*: test con `TestClient`, aserción de que ninguna ruta `/turnos/online` lleva dependencia de auth, router de prueba **solo en la suite** con 200 y 400 (nunca 401) y comando `pytest -k "publico" -q`. Los endpoints reales se revalidan en C-09.
2. **RN-AU-04 sin escenario de logging**. *Antes*: solo un grep propuesto. *Después*: escenario con `caplog`, login 401 + 200 y aserción de ausencia de contraseña y `password_hash`; tarea `-k "sin_filtracion" -q`.
3. **Expiración divergente**. `backend/app/core/config.py:12` tiene 60 min; la KB fija 480 (`08_arquitectura_propuesta.md:55`). *Antes*: sin tarea. *Después*: tarea 1.5 alinea el default o exige aprobación del desvío en el gate.
4. **Texto en inglés** en `tasks.md`. *Después*: español rioplatense, según `AGENTS.md`.
5. **Consulta MCP sin resultados**. `topic="OAuth2 password flow JWT dependency get_current_user"` devolvió `results: []`; el mensaje sugirió acortar. *Después*: reintentos con `OAuth2PasswordRequestForm` y `get_current_user`, que sí aportaron. Documentado sin ocultar el fallo.
6. **Encabezados mal formados** (`##1.` sin espacio) en la evidencia de sesión nueva. *Después*: `## 1.` y así sucesivamente.
7. **Referencia rota en la fundación (corregida)**: `.atl/skill-registry.md` (y el `SKILL.md` de `skill-registry`) citan `_shared/skill-resolver.md`, que el generador nunca crea. Detectado en la comprobación de sesión nueva. *Antes*: referencia a un archivo inexistente. *Después*: `_shared/skill-resolver.md` en la raíz del repo con el protocolo de resolución (cuándo leer el registry, qué bloques inyectar, precedencia de rutas y los gotchas de la Skill tool), más un paso 4C en el generador `skill-registry` que crea el archivo solo si falta, sin sobrescribirlo, y reporta su estado en el resumen. Cambio aditivo e idempotente: no altera la generación del registry ni el escaneo de skills; validado con `skill_validate`.

## 5. Limitaciones

- La Skill tool **no expuso `auth-contract-audit`** en la sesión de proposición (`Skill "auth-contract-audit" not found`) ni en la de verificación. El descubrimiento por `AGENTS.md`/registry funciona y el procedimiento se ejecutó manualmente desde `SKILL.md`, pero la invocación mediante la herramienta queda **sin comprobar**; requiere una sesión que cargue la skill. La creadora sí se invocó porque estaba registrada en la sesión.
- El MCP es solo lectura de documentación; sin credenciales ni datos reales de pacientes. Ante conflicto, prevalece la KB. Quedó pendiente verificar la cuota exacta de Context7 sin API key.
- **No hay video, ZIP ni `ENTREGA.md`**: requieren grabación y datos del equipo. **No hay commits**: la regla dura del repo exige pedido explícito.
- C-03 sigue en governance CRITICO: hace falta aprobación humana y resolver `SU-HASH-LEGADO` y `SU-RATELIMIT` antes de cualquier implementación. No se escribió código de producción ni se corrieron tests de implementación.
