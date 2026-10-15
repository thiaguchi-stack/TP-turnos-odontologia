# Proposal — C-02 `core-models`

## Why

C-02 es governance **CRITICO** y está en el camino crítico (`C-01 → C-02 → C-03 → …`): sin el modelo de dominio canónico y persistido no puede arrancar `C-03 auth-jwt-rbac` (que necesita `Usuario`, `password_hash` y el seed del admin). Además, el desvío documentado `crear-turno-sin-solapamientos` dejó modelos de persistencia **parciales** en el repo (sin `Usuario`, sin `HorarioAtencion`, sin seed, sin migración, sin mixins de auditoría) cuya persistencia este change absorbe y alinea con la KB (ver `CHANGES.md` línea ~504).

## What Changes

- **Absorción del desvío**: alinear los modelos ya existentes (`app/models/{paciente,profesional,prestacion,sillon,turno,bloqueo}.py`, creados por `crear-turno-sin-solapamientos`) con `knowledge-base/04_modelo_de_datos.md`: convención de nombres de constraints, índices (`profesional_id`, `fecha_hora_inicio`), unicidades (`email`, `dni`+`telefono`, `token_cancelacion`) y mixin de auditoría (`creado_en`).
- **Nuevo modelo `Usuario`**: `email` único, `password_hash` (nunca en claro ni en respuestas — RN-AU-04), enum `RolUsuario{admin,odontologo}`, `profesional_id` FK nullable (1:1 opcional con `Profesional`), `activo` default true.
- **Nuevo modelo `HorarioAtencion`**: config semanal por profesional (SU-03, Pregunta 8 de `10_preguntas_abiertas.md`); consumo real recién en `C-07 agenda-engine`.
- **Nuevo atributo `Turno.creado_por`**: FK → `Usuario`, nullable (null = reserva online del paciente), exigido por la KB y ausente hoy.
- **Enums tipados**: clases `RolUsuario` y `EstadoTurno` (reemplazan la tupla `ESTADOS_TURNO` a nivel de modelo, manteniendo compatibilidad durante el refactoring).
- **`db/seed.py` mínimo e idempotente**: 1 usuario admin (`admin@clinica.local`) + 1 profesional con su usuario odontólogo; datos siempre ficticios (RN-DATOS-03). Consumible por `C-03`.
- **Esquema inicial**: decisión explícita Alembic (migración 001) vs `create_all` — planteada en `design.md`, no resuelta acá.
- **Tests nuevos** (Strict TDD, safety net de 72 tests verdes): creación de cada modelo nuevo, unicidad de `email`/`dni`/`token_cancelacion`, defaults de `estado`/`activo`/`rol`, seed idempotente.

No se modifica el comportamiento de creación de turnos ya especificado: `turno_service.crear_turno`, `POST /turnos` y las reglas RN-TU-01/02/05/06/09 siguen verdes sin cambios de comportamiento observable.

## Capabilities

### New Capabilities

- `modelo-datos`: contrato de integridad del modelo de datos persistido — unicidades (email de usuario, dni+telefono de paciente, token de cancelación), enums y defaults de estado/rol/activo, auditoría `creado_en`, relaciones FK exigidas por la KB (`Turno.creado_por`, `Usuario.profesional_id`) y seed mínimo e idempotente de datos ficticios.

### Modified Capabilities

- (ninguna) — `turnos` y `foundation-setup` no cambian a nivel de requisito: la absorción del desvío es a nivel de implementación/persistencia. Si al alinear los modelos cambiara algún comportamiento observable, se emitiría el delta correspondiente en este mismo change (compromiso asumido al archivar `crear-turno-sin-solapamientos`).

## Impact

- **Backend — modelos**: `app/models/` (nuevos `usuario.py`, `horario_atencion.py`; edits en `turno.py` (+`creado_por`), `paciente.py` (unicidad), `__init__.py`; posible mixin de auditoría en `app/db/` o `app/models/`).
- **Backend — persistencia**: `app/db/seed.py` (nuevo), `app/db/session.py` (ya existe, verificar), `app/main.py` (disparar seed idempotente en startup si se adopta), posible `alembic/` + `alembic.ini` (decisión en design).
- **Dependencias**: posible alta de `alembic` en `pyproject.toml` (solo si se adopta Alembic).
- **Tests**: `backend/tests/` — safety net actual (72 passed) debe seguir verde; tests nuevos de modelos/seed.
- **Sin impacto frontend**: no toca `frontend/`.
- **Consumidores futuros**: `C-03` (login, RBAC, seed admin), `C-07` (`HorarioAtencion` → `agenda_service`), `C-08` (CRUDs de recursos).
