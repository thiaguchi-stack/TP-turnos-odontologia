# Proposal

## Why

C-01 y C-02 ya están archivados: el modelo `Usuario` persiste roles,
`profesional_id` y `password_hash`, pero todavía no existe ningún mecanismo para
autenticarse ni para aplicar RBAC. Sin eso, las rutas privadas de la Fase 2 no
pueden distinguir entre admin y odontólogo y la reserva pública quedaría mezclada
con el acceso del personal (RN-AU-01/02/03, `03_actores_y_roles.md:11-29`).
Este change prepara ese contrato antes de habilitar la implementación: C-03 es
`governance CRITICO` y requiere análisis y aprobación humana previa
(`CHANGES.md:181`, `AGENTS.md:124`).

## What Changes

- `POST /auth/login` con OAuth2 password flow: credenciales válidas devuelven un
  JWT Bearer con claims `sub`, `rol`, `profesional_id` y `exp` (RN-AU-01;
  `08_arquitectura_propuesta.md:11,41`).
- `GET /auth/me`: devuelve el usuario actual sin `password_hash`
  (RN-AU-04; `08_arquitectura_propuesta.md:42`).
- Dependencias reutilizables `get_current_user`, `require_role("admin")` y
  `require_odontologo_own`: JWT válido en toda ruta privada, admin para
  usuarios y catálogos, odontólogo limitado a su `profesional_id`
  (RN-AU-01/02/03; `AGENTS.md:100`).
- CRUD de usuarios del sistema solo para `admin`; credenciales inválidas → 401,
  rol insuficiente → 403 (RN-AU-03).
- Verificación de contraseñas con hash bcrypt/argon2 y rate limiting en login
  (5 intentos / 60 s por IP + email) con respuesta 429 al excederlo
  (RN-AU-04; `CHANGES.md:177`).
- Configuración de firma por `.env` (`SECRET_KEY`, `TOKEN_EXPIRE_MIN`), sin
  secretos en el repositorio (`08_arquitectura_propuesta.md:46,50-56`).
- Rutas públicas de reserva (`/turnos/online/*`) siguen sin exigir JWT y no
  aceptan `estado` elegido por el paciente (RN-AU-01, RN-TU-04, RN-DATOS-02).
- Tests unitarios de servicios de auth y de integración con `TestClient`,
  cubriendo 401/403/429 y la ausencia de `password_hash` en respuestas.
- **Sin código de producción, apply, tests de implementación ni archive en esta
  etapa**: solo artefactos SDD y evidencias de auditoría.

## Capabilities

### New Capabilities

- `user-auth`: identidad y acceso del personal del consultorio — login JWT,
  usuario actual, verificación de contraseñas, RBAC por rol y por
  `profesional_id`, y límite de intentos de login.

### Modified Capabilities

- Ninguna. `modelo-datos` ya especifica la persistencia del hash y el seed
  idempotente (C-02); `turnos` ya especifica la creación sin solapamientos
  (change archivado). C-03 agrega comportamiento de acceso, no cambia esos
  requisitos. La compatibilidad del hash PBKDF2 del seed de C-02 con el
  algoritmo exigido por RN-AU-04 se registra como supuesto a validar en
  `design.md`, no como cambio de requisito de `modelo-datos`.

## Impact

- Backend (planificado, no implementado): `app/core/security.py` y `deps.py`,
  `app/schemas/auth.py`, `app/services/auth_service.py`,
  `app/routers/auth.py`, `app/main.py` y `tests/`; sobre el `Usuario` de C-02.
- APIs: nuevas `/auth/login` y `/auth/me`; CRUD de usuarios protegido; sin
  cambios en las rutas públicas de reserva.
- Dependencias: C-02 archivada (`openspec/changes/archive/2026-10-15-c-02-core-models/`).
  Desbloquea C-04, C-05 y C-11 (`CHANGES.md:24,58-64`).
- KB / reglas duras: RN-AU-01..04, RN-DATOS-01/02, DD-02, DD-07, DD-08 y
  `AGENTS.md` §Reglas Duras. Sin integraciones externas, pagos, recordatorios
  ni ficha clínica (DD-03/06, `AGENTS.md:122`).
- Gobernanza: `governance CRITICO`; los artefactos quedan listos para revisión,
  pero la implementación requiere aprobación explícita del humano.
