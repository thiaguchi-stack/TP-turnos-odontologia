# Registro de aprobación de governance — C-03 `auth-jwt-rbac`

- **Fecha**: 2026-11-18
- **Change**: `c-03-auth-jwt-rbac` (carpeta original `openspec/changes/c-03-auth-jwt-rbac/`, hoy archivada en `openspec/changes/archive/2026-11-18-c-03-auth-jwt-rbac/`)
- **Governance**: **CRITICO** (`AGENTS.md:124`, `CHANGES.md:181`)
- **Aprobado por**: usuario, con confirmación explícita en sesión: *“apruebo el governance, lo demás lo hago manualmente yo así que ignoralo”*.
- **Alcance de la aprobación**: habilita escribir código de producción y ejecutar las tareas 1.2 a 5.3. **No** habilita marcar `[x]` en `CHANGES.md` ni archivar el change sin completar y verificar todas las tareas.

## Decisiones del gate (no diferibles a apply)

| Supuesto / desvío | Decisión aprobada | Justificación | Impacto |
|---|---|---|---|
| `SU-HASH-LEGADO` (`design.md:79-87,151-153`) | **Alternativa (a)**: `CryptContext` con `bcrypt` como esquema activo y `pbkdf2_sha256` conservado solo como esquema legado, con **rehash en el primer login correcto**. | Mantiene el seed idempotente de C-02 y la escenario de login del admin sin rewrite de datos; el esquema activo pasa a bcrypt (RN-AU-04) sin falsificar hash existentes. | Tasks 2.1, 3.1 y 5.1: verificar el hash del admin sembrado, migrarlo al primer login y no loguear contraseña ni hash. |
| `SU-RATELIMIT` (`design.md:98-104,154-155`) | **Contador en memoria**, 5 intentos fallidos por 60 s por IP + email, con respuesta 429 al sexto intento aunque la contraseña sea correcta. | Entrega local single-tenant, sin integraciones externas (DD-02/03/06). Se documenta que el contador se reinicia al reiniciar el proceso y no cubre múltiples instancias. | Tasks 3.4 y 4.1; sin Redis ni persistencia en v1. |
| Divergencia de expiración (`design.md:56-59,125-128`) | Alinear `Settings().token_expire_min` al **default de 480 minutos** de la KB (`08_arquitectura_propuesta.md:50-56`). **No se aprueba desvío.** | La KB prevalece sobre el valor actual de `backend/app/core/config.py:12` (60). | Tasks 1.5 y 2.2: aseverar `Settings().token_expire_min == 480` y que el token decodificado expira con ese valor. |

## Fuera de alcance de este gate

El usuario realiza manualmente el video, el ZIP `TP-Skills-MCP-Apellido*.zip` y `ENTREGA.md`; no deben reclamarse ni bloquear la implementación.

## Verificación previa ya realizada

- Artefactos SDD completos y validados: `openspec validate c-03-auth-jwt-rbac --strict --json` → `valid: true`, `issues: []`.
- Auditoría de contrato de auth: `docs/evidencias/audit-auth-c-03-auth-jwt-rbac.md`.
- Apoyo técnico versionado (solo firmas/hashing, nunca reglas de negocio): `docs/evidencias/mcp-context-c03.md` (FastAPI 0.110.3, passlib 1.7.4).
- Estado al aprobar: `openspec status --change c-03-auth-jwt-rbac --json` → `state: ready`, `20` tareas pendientes, `planningArtifacts: proposal, specs, design, tasks`.

## Conclusión

**Gate CRITICO cerrado — listo para implementar.** La restricción de `design.md:15-17` (“no autoriza escribir código”) queda levantada por esta aprobación humana; se aplica TDD estricto y se pausa ante cualquier hallazgo que cambie el diseño.

**Actualización 2026-11-19:** la implementación terminó (20/20 tareas verificadas) y el change quedó archivado en `openspec/changes/archive/2026-11-18-c-03-auth-jwt-rbac/` (`CHANGES.md:172-173`).
