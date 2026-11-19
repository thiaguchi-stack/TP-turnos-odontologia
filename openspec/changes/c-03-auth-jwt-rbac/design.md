# Design

## Context

Ver `proposal.md` para la motivación. Estado observable del repo al preparar este
change: C-01 dejó `core/config.py` (Pydantic Settings), `core/security.py` como
stub, CORS por `CORS_ORIGINS` y `.env.example` con `SECRET_KEY` y
`TOKEN_EXPIRE_MIN` (`CHANGES.md:135,137`); C-02 archivó el modelo `Usuario` con
`rol`, `profesional_id` opcional y `password_hash`, más un seed idempotente con
un admin y un odontólogo (`CHANGES.md:152-158`). La KB fija RN-AU-01..04
(`05_reglas_de_negocio.md:9-12`), la matriz RBAC y las rutas públicas
(`03_actores_y_roles.md:11-29`), DD-02/07/08 (`09_decisiones_y_supuestos.md:8,13-14`)
y la arquitectura de seguridad (`08_arquitectura_propuesta.md:39-56`).

Restricción de gobernanza: C-03 es `governance CRITICO`
(`CHANGES.md:181`, `AGENTS.md:124`). Este documento es análisis previo: no
autoriza escribir código de producción ni ejecutar apply.

## Goals / Non-Goals

**Goals:**

- Centralizar la verificación de JWT y RBAC en dependencias reutilizables, con
  la decisión de negocio en `auth_service` (DD-07).
- Emitir y validar tokens con los claims que el resto del sistema necesita
  (`sub`, `rol`, `profesional_id`, `exp`) sin exponer `password_hash`.
- Mantener la reserva pública accesible sin cuenta ni token (DD-04,
  `03_actores_y_roles.md:22-28`).
- Dejar cada comportamiento cubierto por un escenario verificable y una tarea
  con verificación explícita.

**Non-Goals:**

- Login de pacientes, alta pública de cuentas o recuperación de contraseña
  (DD-04; backlog).
- Proveedores de identidad, OAuth externo, pagos, WhatsApp ni recordatorios
  (DD-03/06).
- Multitenancy: un solo consultorio, sin claim de tenant (DD-02).
- Cambiar el modelo de datos de C-02 ni las reglas de turnos de la spec
  `turnos`; C-03 solo agrega comportamiento de acceso.

## Decisions

1. **OAuth2 password flow con `OAuth2PasswordBearer` + `OAuth2PasswordRequestForm`.**
   El login recibe `username`/`password` como formulario y `POST /auth/login`
   devuelve `access_token` Bearer; las rutas privadas declaran el esquema Bearer
   como dependencia. Apoyo técnico: la doc versionada de FastAPI 0.110.3 muestra
   `OAuth2PasswordRequestForm` como dependencia de clase con `username`,
   `password` y `scopes`, y describe `get_current_user` como dependencia que
   recibe el token del sub-dependiente `oauth2_scheme` y lo convierte en el
   usuario actual. Alternativas descartadas: Basic Auth (no entrega token
   reutilizable para la SPA) e IdP externo (DD-06, sin integraciones en v1).
   `grant_type` no se exige estritamente: se usa el formulario estándar porque
   el cliente es propio (C-11).

2. **Firma y claims del JWT.** Firma HS256 con `SECRET_KEY` leída de `.env`
   y expiración `TOKEN_EXPIRE_MIN` (default 480 según `08_arquitectura_propuesta.md:50-56`;
   el código actual de `backend/app/core/config.py:12` tiene 60, divergencia que
   debe alinearse a la KB o aprobarse explícitamente antes de implementar).
   Claims: `sub` = id de usuario, `rol` = enum `RolUsuario`, `profesional_id`
   (nulo para admin) y `exp`. Alternativa descartada: sesiones server-side — no
   encaja con la SPA separada ni con la decisión JWT de la KB
   (`08_arquitectura_propuesta.md:11`). La expiración se valida en la decodificación:
   un `exp` vencido produce 401, no 403.

3. **Hash de contraseñas con passlib `CryptContext`.** RN-AU-04 admite
   bcrypt/argon2 y la doc versionada de passlib 1.7.4 recomienda bcrypt como
   elección "battle tested" con la librería `bcrypt` instalada, y muestra el
   patrón `pwd_context.hash(...)` / `pwd_context.verify(...)` con una instancia
   global. El código de C-02 ya dejó preparada la migración: el formato del hash
   está versionado y `verify_password` se conserva para el esquema legado
   (`backend/app/core/security.py:7-9,21-29,58-78`). Se adopta `CryptContext` con bcrypt como esquema activo y
   `verify`/`hash` como única vía de verificación; nunca se registra la
   contraseña en claro ni el hash en respuestas o logs. Alternativas
   descartadas: guardar contraseñas en claro (prohibido por RN-AU-04), MD5/SHA1
   (no irreversibles en la práctica) y argon2 como esquema único (requiere
   dependencia adicional; queda como opción futura, no como decisión de dominio).

4. **Compatibilidad con el hash PBKDF2 del seed de C-02 — SUPUESTO A VALIDAR.**
   `CHANGES.md:155` registra que C-02 sembró el admin con hash PBKDF2, mientras
   RN-AU-04 pide bcrypt/argon2. La KB no dice cómo migrar ese hash: **no se decide
   acá de forma unilateral**. Alternativas a resolver en el gate de governance:
   (a) `CryptContext` con bcrypt activo y `pbkdf2_sha256` como esquema legado,
   con rehash en el primer login correcto; o (b) regenerar el hash del seed con
   bcrypt antes de implementar. Cualquiera de las dos debe conservar
   idempotencia del seed y la scenaria de login del admin. Impacto: define el
   contenido exacto de las tasks de seguridad y de los fixtures de test.

5. **RBAC por dependencias explícitas, no middleware global.** `get_current_user`
   resuelve el usuario; `require_role("admin")` y `require_odontologo_own`
   aplican RN-AU-02/03. Se colocan en los routers que corresponda y se dejan
   sin protección las rutas públicas enumeradas en `03_actores_y_roles.md:22-28`.
   Alternativa descartada: middleware global `auth` — invertiría el default y
   dejaría la reserva pública expuesta a 401 (RN-AU-01). La decisión de negocio
   (qué rol puede qué) vive en `auth_service`; los routers solo invocan la
   dependencia (DD-07, `AGENTS.md:95`).

6. **Rate limiting en memoria por IP + email (SUPUESTO A VALIDAR).** 5 intentos
   fallidos por 60 s y 429 al excederlo (`CHANGES.md:177`). En v1, single-tenant
   y sin integraciones externas (DD-02/06), el contador puede vivir en memoria;
   eso implica que se reinicia al reiniciar el proceso y no cubre múltiples
   instancias. Alternativa descartada: Redis/servicio externo (fuera de alcance
   v1). Si el humano requiere persistencia del límite, cambia el enfoque y las
   tasks de tests: validar en el gate, no durante apply.

7. **Schemas de respuesta sin `password_hash`.** Modelos Pydantic explícitos
   (`TokenRead`, `UsuarioRead`) con campos permitidos; el hash nunca se serializa
   y se prohíbe loguearlo (RN-AU-04, `08_arquitectura_propuesta.md:42`).
   Alternativa descartada: devolver el modelo ORM directamente — filtraría mal
   los campos y acoplaría la API a la persistencia.

8. **Verificación en dos niveles.** Unit tests del servicio de auth (hash,
   claims, expiración, decisión de rol) y tests de integración con `TestClient`
   para 200/201/401/403/429 y ausencia de `password_hash`
   (`08_arquitectura_propuesta.md:58-62`). La lógica se prueba en servicios, no
   dentro de los routers (DD-07).

## Risks / Trade-offs

- [Hash legado PBKDF2 vs. RN-AU-04] → resolver la alternativa 4 antes de
  implementar; si se elige rehash en login, cubrirlo con un test que verifique
  que el admin del seed puede entrar y que el hash cambia de esquema.
- [Contador de rate limit en memoria] → documentar el reinicio ante restart;
  no usar en más de una instancia; validar supuesto 6 en el gate.
- [Default de expiración divergente] → `backend/app/core/config.py:12` usa 60
  minutos y la KB fija 480 (`08_arquitectura_propuesta.md:55`): alinear el
  default con la KB o dejar registrada la aprobación del desvío en el gate
  (tarea 1.5 de `tasks.md`).
- [Claims de rol guardados en el token] → un cambio de rol no se refleja hasta
  que expire el token; mitigación: `TOKEN_EXPIRE_MIN` configurable y
  `get_current_user` recarga el usuario desde la DB en cada request para
  comprobar que sigue activo.
- [Dependencias olvidadas en rutas privadas nuevas] → checklist de RBAC en las
  tasks y auditoría `auth-contract-audit` al revisar C-04/C-05/C-11.
- [Secretos en el repo] → solo `.env` / `.env.example` sin valores reales
  (`08_arquitectura_propuesta.md:46`); nunca fixture con credenciales reales.
- [Gate de gobernanza] → mientras no haya aprobación humana, este change queda
  en estado "artefactos preparados"; no se corre apply ni se archiva.

## Migration Plan

Sin migración de esquema: C-02 ya persiste `password_hash`, `rol` y
`profesional_id`. La única compatibilidad a resolver es la del valor del hash
del seed (ver Decisión 4); su alternativa elegida se registra antes de
implementar. Rollback de la configuración: restaurar `.env` previo y dejar de
montar los routers de auth; no hay datos de pacientes reales involucrados
(RN-DATOS-03).

## Open Questions

- `SU-HASH-LEGADO`: ¿se admite `pbkdf2_sha256` como esquema legado con rehash en
  el primer login, o se regenera el hash del seed? No es diferible a apply:
  define fixtures y tasks; debe responderse en el gate de governance.
- `SU-RATELIMIT`: ¿alcanza el contador en memoria para la entrega local del TP
  o se exige persistencia? Tampoco es diferible a apply; la KB no lo define.
- Apoyo técnico consultado: `context_get_docs` sobre FastAPI 0.110.3 y passlib
  1.7.4. La documentación solo confirma firmas y patrón de hashing; **nunca es
  fuente de reglas de negocio**. Ante conflicto, prevalecen la KB y `AGENTS.md`.
  Detalle y recortes en `docs/evidencias/mcp-context-c03.md`.
