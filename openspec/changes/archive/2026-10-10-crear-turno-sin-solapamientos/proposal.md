# Proposal — crear-turno-sin-solapamientos

## Why

El corazón del dominio odontológico es la regla RN-TU-01: **no se puede atender
dos veces al mismo tiempo ni ocupar el mismo sillón dos veces** (consigna del TP,
regla de negocio verificable recomendada por la cátedra). Es una regla del MVP
(`DD-09`, `SU-02`) que se puede demostrar de forma automática con tests de
servicio y con un endpoint que devuelve `409` ante colisión, por lo que conviene
construirla ahora y de forma aislada, sin arrastrar la complejidad del roadmap
completo.

## Desvío deliberado vs. roadmap

Este change **no sigue el árbol de dependencias de `CHANGES.md`**. En el roadmap
la validación de solapamiento vive en `C-07 agenda-engine`, que depende de
`C-04 → C-03 → C-02 → C-01`, y **`C-02 core-models` y `C-03 auth-jwt-rbac` son
governance CRITICO** (no se codean sin análisis y aprobación previa); hoy
**ningún change del roadmap está archivado**, es decir, ninguna dependencia está
satisfecha.

Se adopta por tanto un **change autónomo y acotado** (recomendación §4.3 del
relevamiento `docs/explore/relevamiento-crear-turno-sin-solapamientos.md`): un
corte vertical propio con los **modelos mínimos** que la regla necesita, el
**servicio `crear_turno`** y un **`POST /turnos` delgado**, sin frontend, sin
auth y sin cálculo de franjas. La persistencia y los modelos que este change
crea serán absorbidos/alineados por `C-02 core-models` cuando se ejecute
legítimamente (con su governance CRITICO aprobado). Este desvío es una decisión
deliberada para poder verificar la regla en aislamiento dentro del TP.

## What Changes

- Modelos SQLAlchemy mínimos (desde cero: el repo es documentación pura):
  `Profesional`, `Paciente` (stub, FK de `Turno.paciente_id` es NOT NULL),
  `Prestacion`, `Sillon`, `Turno`, `Bloqueo`, más `db/session.py` con engine
  SQLite y `create_all` (sin Alembic en este corte).
- `services/turno_service.crear_turno(...)`: lógica de negocio en la capa de
  servicios (DD-07) — deriva `fecha_hora_fin = inicio + duracion_minutos(prestación)`
  (RN-TU-02), valida solapamiento contra turnos activos **y** bloqueos, por
  `profesional_id` **y** por `sillon_id`, con intervalos semiabiertos
  `[inicio, fin)` (RN-TU-01, RN-PR-03, RN-PR-05), rechaza turnos en el pasado
  (RN-TU-06), profesional inactivo (RN-PR-01), sillón inexistente/inactivo
  (RN-TU-09) y prestación inactiva (RN-PR-02); el turno nace siempre en
  `reservado` (RN-TU-04).
- Schemas Pydantic `TurnoCreate` / `TurnoRead`: el request **no acepta
  `fecha_hora_fin` ni `estado`** (regla dura; duración derivada, estado fijo).
- Router `POST /turnos` delgado (DD-07): `201` con el turno creado,
  `409` ante solapamiento, `400` ante datos inválidos o entidades
  inactivas/inexistentes.
- Tests: unitarios del servicio (feliz, colisión por profesional, colisión por
  sillón, colisión con bloqueo, borde `[inicio, fin)`, pasado, entidades
  inactivas) + integración del endpoint (`201` / `409` / `400`).

## Capabilities

### New Capabilities

- `turnos`: creación de turnos con duración derivada de la prestación e
  integridad de agenda (sin solapamiento por profesional ni por sillón/box,
  contra turnos y bloqueos), incluyendo las validaciones de elegibilidad
  (profesional/sillón/prestación activos, sin turnos en el pasado) y el estado
  inicial `reservado`.

### Modified Capabilities

_(ninguna: `openspec list --specs` devuelve specs vacíos — es la primera
capability del proyecto)_

## Impact

- **Código nuevo** (no hay código existente): `backend/app/models/*`,
  `backend/app/schemas/turno.py`, `backend/app/services/turno_service.py`,
  `backend/app/routers/turnos.py`, `backend/app/db/session.py`,
  `backend/app/main.py`, `backend/tests/{test_turno_service,test_turnos_api}.py`,
  `backend/pyproject.toml`.
- **API**: se agrega `POST /turnos` (sin autenticación en este corte — ver
  alcance).
- **Roadmap**: se anota una entrada de trazabilidad en `CHANGES.md` mapeando
  este change OPSX alineado a `C-07`/`C-08`; no se modifican los otros changes.
- **Sin impacto** en frontend, auth, seeds, privacidad ni en los changes
  archivados (no hay ninguno).

## Alcance

### Dentro del alcance

- Modelos mínimos + sesión SQLite (`create_all`), con constraints de la
  `knowledge-base/04_modelo_de_datos.md` que la regla necesita.
- `turno_service.crear_turno(...)` con todas las validaciones de RN-TU-01/02/04/06/09
  y RN-PR-01/02/03/05 aplicables a la creación.
- `POST /turnos` (router delgado) → `201` / `409` / `400`.
- Tests unit + integración que cubren los escenarios del delta spec.

### Fuera del alcance

- **Frontend** (la consigna admite "una API o un módulo con lógica de dominio").
- **Franjas disponibles / `HorarioAtencion` / RN-TU-07** — la regla de
  solapamiento es ajena al calendario (§4.1 del relevamiento); queda para `C-07`.
- **Auth JWT y RBAC** (`C-03`, governance CRITICO): `POST /turnos` nace sin
  protección de rol en este corte autónomo; el endurecimiento lo absorbe `C-03`.
- **Reprogramación (RN-TU-08), transiciones de estado posteriores
  (RN-TU-04/05, `C-10`), cancelación por token, reserva pública (`C-09`),
  seed demo, Alembic, datos ficticios de ejemplo más allá de los necesarios
  para los tests.**
