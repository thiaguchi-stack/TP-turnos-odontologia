# Design — C-02 `core-models`

## Context

Ver `proposal.md` — Why. Puntos del estado actual que condicionan el diseño:

- El change archivado `crear-turno-sin-solapamientos` ya dejó persistencia en el repo: `app/db/base.py` (`Base`), `app/db/session.py` (engine + `get_db` + `SessionLocal`), `app/models/{paciente,profesional,prestacion,sillon,turno,bloqueo}.py`, `app/services/turno_service.py`, `POST /turnos` y una suite de ~72 tests verdes. Esa persistencia es **el safety net** de C-02: cualquier alineación debe mantenerla verde.
- `app/main.py` crea el esquema con `Base.metadata.create_all(bind=engine)` en el `lifespan`; los tests hacen `drop_all`/`create_all` sobre `sqlite://` in-memory (ver `backend/tests/conftest.py`). El default de dev es `sqlite:///./clinica.db` (archivo persistente).
- `app/models/__init__.py` exporta `Bloqueo`, `ESTADOS_TURNO`, `Paciente`, `Prestacion`, `Profesional`, `Sillon`, `Turno`. `estado` es un `String`/`Enum(native_enum=False)` con tupla `ESTADOS_TURNO`, no una clase enum.
- `app/core/security.py` es un stub mínimo (solo `get_secret_key`); no hay hash de contraseñas.
- `mypy strict = true` (`backend/pyproject.toml`) y modelos ya tipados con `Mapped`/`mapped_column`.

Discrepancias detectadas contra la KB (a resolver en este change):

- `Turno.creado_por` (FK → `Usuario`, nullable) **falta** en el modelo actual (`04_modelo_de_datos.md` §Turno).
- `Usuario` y `HorarioAtencion` **no existen**.
- Sin mixin de auditoría (cada modelo repite `creado_en`; `Usuario` debería heredarlo).
- Sin índices explícitos (`profesional_id`, `fecha_hora_inicio`) ni unicidad de `email`; `Paciente` no declara unicidad `(dni, telefono)` pese a la regla de deduplicación.
- No hay `db/seed.py` ni esquema versionado (Alembic).
- El scope del roadmap dice "6 tablas", pero el ERD de la KB incluye **`Sillon`** (DD-09) → en realidad son 7 tablas + `HorarioAtencion` = 8.

## Goals / Non-Goals

**Goals:**

- Modelo de dominio canónico y persistido, tipado y `mypy strict`-limpio, alineado con `04_modelo_de_datos.md`.
- `Usuario`, `HorarioAtencion` y `Turno.creado_por` incorporados; enums tipados; mixin de auditoría; unicidades e índices.
- Seed mínimo idempotente con datos ficticios, consumible por `C-03`.
- Safety net de tests existente verde al cierre; tests nuevos (RED → GREEN → TRIANGULATE → REFACTOR).

**Non-Goals:**

- No se implementa autenticación, JWT, RBAC, hashing productivo (bcrypt/argon2) ni CRUD de usuarios → `C-03`.
- No se implementa `agenda_service` ni la validación de turnos contra `HorarioAtencion`, ni CRUD de horarios → `C-07`/`C-08`.
- No se crean schemas Pydantic de `Usuario`/`HorarioAtencion` (llegan con sus rutas en `C-03`/`C-08`); `HorarioAtencion` es config, no recurso CRUD de v1.
- No se cambia ningún comportamiento observable de `POST /turnos` (RN-TU-01/02/05/06/09 intactas) — por eso no hay delta de la capability `turnos`.
- No se modelan datos clínicos (ficha clínica/odontograma) → backlog v2 (RN-DATOS-02).

## Decisions

**D1 — Absorción incremental de lo existente (no reescritura).** Los modelos actuales coinciden con la KB en nombres y campos, así que C-02 los **edita** (constraints, índices, `creado_por`, mixin, enum) en vez de recrearlos; los tests existentes actúan de red de seguridad. *Alternativa descartada*: reescribir el paquete `models/` — rompería 72 tests sin ganancia y contradiría el compromiso asumido al archivar `crear-turno-sin-solapamientos`.

**D2 — Enums como clases `enum.Enum` (`StrEnum`) + columna `Enum(native_enum=False, validate_strings=True)`.** Se define `EstadoTurno` y `RolUsuario` en módulos de modelo y se conserva `ESTADOS_TURNO = tuple(e.value for e in EstadoTurno)` como alias de compatibilidad para no romper imports/tests durante el refactor (el string sigue siendo el valor persistido, igual que hoy). *Alternativa*: enum nativo de Postgres (`native_enum=True`) — complica SQLite dev y el `DROP TYPE` en migraciones; se descarta para v1.

**D3 — Mixin de auditoría reutilizable.** `app/db/base.py` gana un mixin (p. ej. `MixinAuditoria`) con `creado_en: Mapped[datetime] = mapped_column(DateTime, default=lambda: clock.now())`, aplicado a `Usuario`, `Paciente` y `Turno` (los que la KB marca con `creado_en` audit). Se preserva el default Python vía `clock.now()` ya usado (nada de `server_default`, para mantener consistencia con `app/core/clock.py` y los tests con reloj controlado).

**D4 — Unicidades a nivel de base de datos.** `usuario.email` unique; `paciente(dni, telefono)` unique compuesta (regla de deduplicación de la KB); `turno.token_cancelacion` unique (ya existe, se conserva). *Alternativa*: deduplicar solo en servicios — no protege ante escrituras concurrentes ni seed; se prefiere constraint + (si hiciera falta) validación de servicio.

**D5 — Índices explícitos para la agenda.** Índice compuesto en `turno(profesional_id, fecha_hora_inicio)` y en `turno(sillon_id, fecha_hora_inicio)`, más índices en `bloqueo(profesional_id, fecha_hora_inicio)`; cubren las consultas de solapamiento de `turno_service` (`[inicio, fin)`) y las futuras listas de agenda (`C-08`).

**D6 — Seed como función testeable, disparada desde el `lifespan`.** `app/db/seed.py` expone `seed_minimo(db: Session) -> None` idempotente (lookup por `email`/`(dni, telefono)` antes de insertar) y `main.py` la invoca en startup. Los tests llaman la función directamente (sin depender del startup) → testeable sin HTTP, coherente con la regla dura de no testear servicios puros vía HTTP.

**D7 — Privacidad (RN-DATOS-01/02/03).** `Paciente` no incorpora campos clínicos; `obsocial` queda como dato administrativo informativo y **no deberá** exponerse ni aceptarse en la reserva pública. El modelo no abre rutas nuevas, así que no hay superficie pública nueva en C-02; se deja asentado como restricción para `C-09`/`C-11` (schema de reserva solo con datos de contacto) y `C-17`. Seed, tests y fixtures usan únicamente datos ficticios.

**D8 — `Sillon` se mantiene como entidad de primera clase.** El ERD de la KB y DD-09 lo incluyen y `turno_service` ya valida solapamiento por `sillon_id`; "consolidar" implicaría borrar una entidad y romper la regla RN-TU-01. El alcance real queda en **8 tablas** (Usuario, Profesional, Paciente, Prestacion, Sillon, Turno, Bloqueo, HorarioAtencion), no las "6" que menciona el scope del roadmap → ver OQ-3 (actualizar `CHANGES.md`).

## Decisiones abiertas (requieren aprobación humana — governance CRITICO)

**OQ-1 — ¿Alembic en C-02 o `create_all` + seed?**
*Recomendación*: **adoptar Alembic** con una revisión baseline `001` autogenerada desde `Base.metadata` (env.py con `target_metadata`), `alembic.ini` y `alembic/versions/`. Justificación: el default de dev es un archivo persistente (`sqlite:///./clinica.db`) y `create_all` **no agrega columnas** a tablas existentes — `Turno.creado_por` y las nuevas tablas romperían cualquier base ya creada, obligando a "borrar la base" en cada change futuro (C-04+ alterarán el esquema varias veces). Alternativa si se rechaza: mantener `create_all` y documentar en `README` que hay que borrar `clinica.db` al cambiar el modelo; se eliminarían las tareas del grupo 6.
*Impacto en decisiones*: si se adopta, definir en la implementación si el `lifespan` corre `alembic upgrade head` o sigue con `create_all` (los tests in-memory usan `create_all` sobre metadata y no deben pasar por Alembic).

**OQ-2 — Forma de `HorarioAtencion` (SU-03 / Pregunta 8).**
*Recomendación*: tabla simple de franjas: `id`, `profesional_id` (FK not null), `dia_semana` (`int` 0–6 con 0=lunes ISO), `hora_inicio`/`hora_fin` (`Time`), unique `(profesional_id, dia_semana, hora_inicio)` y `CheckConstraint(hora_fin > hora_inicio)`; **sin** `activo` ni CRUD en v1 (config cargada por seed/script). Soportar "9–13 y 15–19" con dos filas por día. Consumo real en `C-07`.
*Alternativas*: (a) tabla de turnos de atención tipo calendario por fecha — excede SU-03 y la Pregunta 8, se descarta para v1; (b) un `JSON` de config por profesional — no relacional, dificulta la validación de franjas; se descarta.
*Pendiente de confirmar*: convención de `dia_semana` (ISO 0–6 vs 1–7 vs enum de texto).

**OQ-3 — Alcance de tablas y actualización del roadmap.** *Recomendación*: mantener `Sillon` y `HorarioAtencion` → 8 tablas; corregir el scope de `[C-02]` en `CHANGES.md` ("6 tablas" → 8) al aprobar el change.
*Sin resolver*: si C-02 debe además adelantar la consistencia "rol odontólogo ⇒ `profesional_id` no nulo" o delegarla a `C-03` (recomendación: delegar a `C-03`, donde vive el CRUD de usuarios; en C-02 solo se exige integridad referencial de la FK, que es lo que especifica el delta).

**OQ-4 — ¿Seed con hash desde C-02 o esperar a C-03?**
*Recomendación*: extender el stub `app/core/security.py` con `hash_password`/`verify_password` usando `hashlib.pbkdf2_hmac` (stdlib, sin dependencia nueva, formato versionado con sal) para que el seed pueda persistir el admin **nunca en claro** (RN-AU-04); `C-03` podrá migrar a bcrypt/argon2 conservando `verify_password`. Alternativa: sembrar el admin en C-03 (deja el seed de C-02 sin usuario admin y debilita la especificación del seed).

## Risks / Trade-offs

- **Romper los ~72 tests verdes al tipar enums/`creado_por`** → mitigación: refactor por pasos con `pytest` como gate (safety net → RED → GREEN → TRIANGULATE → REFACTOR); alias `ESTADOS_TURNO` para no romper imports.
- **Doble fuente de esquema (Alembic + `create_all` en lifespan/tests)** → mitigación: si se aprueba OQ-1, Alembic es la fuente para dev/prod y `create_all` queda solo para la base in-memory de tests; documentar en `README`.
- **`mypy strict` sobre mixins y enums nuevos** → mitigación: mixin con `Mapped[...]` explícito y verificar `mypy app` antes de cerrar.
- **Extender `security.py` invade `C-03`** → mitigación: solo hash/verify mínimo, sin JWT ni dependencias; OQ-4 lo aprueba explícitamente y C-03 extiende.
- **`HorarioAtencion` diseñado sin consumo real** (puede quedar corto para `C-07`) → mitigación: alcance mínimo declarado (franjas por día) y OQ-2 abierta; el seed con franjas reales (9–13/15–19) hace de prueba de uso.
- **Privacidad**: `Paciente.obsocial` podría filtrarse en una respuesta pública futura → mitigación: restricción anotada para `C-09`/`C-11`/`C-17`; sin rutas nuevas en C-02.

## Migration Plan

1. **Gate de aprobación** (governance CRITICO): confirmar OQ-1…OQ-4 antes de escribir código.
2. Safety net: `pytest` verde (línea base) y `mypy app` sin errores.
3. Incorporar enums + mixin sin perder compatibilidad (tests existentes deben seguir verdes).
4. Agregar `Usuario`, `creado_por`, `HorarioAtencion`, unicidades e índices (tests nuevos RED → GREEN).
5. `db/seed.py` + (según OQ-4) hash mínimo en `security.py`; tests de idempotencia.
6. (Si OQ-1) Alembic baseline `001` + instrucciones de `upgrade`/`downgrade` en `README`.
7. Actualizar `CHANGES.md` (alcance 8 tablas, marcar C-02) al archivar. **Rollback**: `downgrade` de la revisión `001` o, sin Alembic, borrar `clinica.db` y recrear desde `create_all`.

## Open Questions

- OQ-1, OQ-2, OQ-3, OQ-4 (arriba): todas afectan el corte de tareas y requieren aprobación antes de implementar. No hay unknowns diferibles adicionales.

## Aprobación (gate 0.2 — governance CRITICO superado)

Aprobadas por el usuario:

- **OQ-1 = Alembic SÍ**: revisión baseline `001` con las tablas del modelo. La dev usa SQLite archivo (`clinica.db`) y `create_all` no agrega columnas; se documenta el flujo (`alembic upgrade head`) en el `README`. Los tests in-memory siguen usando `create_all` sobre la metadata.
- **OQ-2 = `HorarioAtencion` simple**: `profesional_id` FK, `dia_semana` ISO 0–6, `hora_inicio`/`hora_fin` (`Time`) con `CheckConstraint(hora_fin > hora_inicio)` y unique `(profesional_id, dia_semana, hora_inicio)`. **Sin CRUD en v1.**
- **OQ-3 = 8 tablas** (Usuario, Profesional, Paciente, Prestacion, Sillon, Turno, Bloqueo, HorarioAtencion). La regla "rol odontólogo ⇒ `profesional_id` no nulo" queda **delegada a C-03** (no se valida en C-02).
- **OQ-4 = hash mínimo `pbkdf2`** en `app/core/security.py` (stdlib `hashlib`, sal por usuario, iteraciones documentadas) para sembrar el admin sin contraseña en claro; bcrypt/argon2 queda para C-03.
