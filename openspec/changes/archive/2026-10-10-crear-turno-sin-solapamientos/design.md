# Design — crear-turno-sin-solapamientos

## Context

El repo es documentación pura (KB + `CHANGES.md` + `openspec/`): no existe
código, `pyproject.toml` ni specs archivadas. Este change debe construir desde
cero el corte vertical mínimo para verificar RN-TU-01 en aislamiento. La
motivación y el desvío deliberado respecto del roadmap (dependencias `C-02`/
`C-03` governance CRITICO sin archivar) están en `proposal.md`; los requisitos
observables, en `specs/turnos/spec.md`.

Restricciones que condicionan el diseño (reglas duras de `AGENTS.md`):

- Lógica de negocio solo en `app/services/` (routers delgados, DD-07).
- Nunca aceptar `fecha_hora_fin` ni `estado` desde el request; duración
  derivada de la prestación (RN-TU-02).
- Sin auth en este corte, pero tampoco datos clínicos ni de terceros.
- Tests obligatorios antes de cerrar el change; texto en español rioplatense.

## Goals / Non-Goals

**Goals:**

- `crear_turno(...)` correcto y testeable unitariamente: duración derivada,
  estado `reservado`, solapamiento por profesional **y** por sillón contra
  turnos no cancelados y bloqueos, con intervalos `[inicio, fin)`.
- `POST /turnos` que expone la regla con códigos `201` / `409` / `400`.
- Estructura de carpetas y modelos alineados a `knowledge-base/04` y
  `08_arquitectura_propuesta.md` para que `C-02`/`C-07`/`C-08` puedan absorber
  este código sin reescribirlo.

**Non-Goals:**

- Franjas disponibles / `HorarioAtencion` / RN-TU-07 (queda en `C-07`).
- Auth JWT, RBAC, rate limiting (`C-03`/`C-17`).
- Reprogramación (RN-TU-08), transiciones posteriores (`C-10`), reserva
  pública (`C-09`), seed demo, frontend, Alembic.

## Decisions

### D1 — Estructura y modelos mínimos propios (corte autónomo)

Se crea `backend/app/{models,schemas,services,routers,db,core}` con los modelos
que la regla necesita, tomados textualmente de `knowledge-base/04`: `Usuario`
se **omite** (solo lo usaban auth/seed); `Paciente` entra como stub mínimo
(nombre, apellido, dni, teléfono) porque `Turno.paciente_id` es NOT NULL.

- **Por qué sobre depender de `C-02`**: `C-02` es governance CRITICO y no está
  archivado; bloquear la regla en dos changes críticos es justo lo que el
  relevamiento §4.3 recomienda evitar.
- **Riesgo aceptado**: modelos duplicados respecto de `C-02`. Mitigación:
  nombres de tablas/columnas idénticos a la KB para que la absorción sea un
  merge, no un rewrite.

### D2 — Firma del servicio: sin `estado` ni `fecha_hora_fin`

```python
def crear_turno(
    db: Session, *,
    profesional_id: int,
    paciente_id: int,
    prestacion_id: int,
    sillon_id: int,
    fecha_hora_inicio: datetime,
) -> Turno: ...
```

- `fecha_hora_fin` se deriva dentro del servicio
  (`inicio + prestacion.duracion_minutos`, RN-TU-02) y el estado nace en
  `reservado` (RN-TU-04). Que la firma **no acepte** esos parámetros es la
  garantía estructural de la regla dura, más allá del schema HTTP.
- **Orden de validaciones** (baratas primero, solapamiento al final para no
  comparar contra datos inválidos): FKs existentes → profesional/sillón/
  prestación activos → `inicio >= ahora` → solapamiento → persistir.
- **Errores de dominio**: excepciones propias (`TurnoRechazadoError` con
  motivo, `TurnoSolapadoError`) en lugar de tuplas/`None`, para que el router
  las mapee a `400`/`409` sin lógica de negocio y los tests unitarios puedan
  assertear sin HTTP.
- **Alternativa descartada**: devolver `(turno, error)` — propaga `Optional`
  y obliga a ramificar en el caller; las excepciones ya son el idioma de
  FastAPI.

### D3 — Detección de solapamiento en SQL, en una transacción

Condición de intersección de intervalos semiabiertos
`[inicio, fin)` (coincide con la restricción de la KB §Restricciones clave):

```sql
existente.fecha_hora_inicio < :fin_nuevo
AND existente.fecha_hora_fin   > :inicio_nuevo
```

Se consultan tres conjuntos, todos excluyendo `estado = 'cancelado'`
(RN-TU-05: cancelar libera el horario):

1. turnos del `profesional_id`;
2. turnos del `sillon_id` (cualquier profesional, RN-PR-05);
3. bloqueos del `profesional_id` donde `sillon_id IS NULL OR sillon_id = :sillon_id`
   (RN-PR-03: `sillon_id` nulo libera en todos los sillones).

La escritura ocurre dentro de `db.commit()` inmediato; toda la validación corre
en la misma sesión.

- **Por qué query y no constraint**: SQLite no soporta exclusión de rangos; la
  KB lo deja como opcional para Postgres. El servicio es la fuente de verdad en
  v1; el constraint será una segunda barrera cuando exista Postgres.
- **Alternativa descartada**: cargar todos los turnos del día a memoria y
  filtrar en Python — funciona igual en un TP, pero la query es la que escala
  y deja la regla en un solo lugar reutilizable por `C-07`.

### D4 — Schemas Pydantic estrictos y errores en 400

- `TurnoCreate` con exactamente los 5 campos del request y
  `model_config = ConfigDict(extra="forbid")`: enviar `fecha_hora_fin`,
  `estado` o cualquier campo desconocido produce validación fallida (→ 400),
  cubriendo el escenario "campos prohibidos".
- `TurnoRead` expone el turno completo (con `fecha_hora_fin`, `estado`), sin
  datos de terceros ni clínicos.
- FastAPI devuelve **422** por defecto ante errores de Pydantic; se agrega un
  handler de `RequestValidationError` en `main.py` que responde **400** con el
  detalle, para alinearse con la tira de códigos de la consigna
  (`400/409/201`) sin lógica condicional en el router.
- **Mapeo**: `TurnoSolapadoError → 409` (con `detalle` que nombra el motivo:
  profesional / sillón / bloqueo), `TurnoRechazadoError → 400`,
  validación de request → 400, éxito → `201`.

### D5 — Router delgado `POST /turnos`

`routers/turnos.py` expone un único endpoint que decodifica el schema,
invoca `crear_turno` y mapea excepciones a códigos. Sin dependencia de rol
(desvío declarado en `proposal.md`; `C-03` la añadirá). **No** se registran
rutas privadas adicionales ni se toca auth.

### D6 — Persistencia SQLite con `create_all`

- `db/session.py`: engine desde `DATABASE_URL` (default `sqlite:///./clinica.db`),
  `SessionLocal`, `get_db` para el router; `Base` declarativo en `db/base.py`.
- `main.py` llama `Base.metadata.create_all` al arrancar. **Sin Alembic** en
  este corte (la KB lo declara opcional; el change es autónomo y descartable).
- Tests usan SQLite en memoria (`sqlite://` + `StaticPool`) para aislar cada
  fixture.

### D7 — Estrategia de tests

- **Unit (`tests/test_turno_service.py`)**: todos los escenarios del spec sin
  pasar por HTTP — feliz con duración derivada, choque por profesional, por
  sillón, con bloqueo (nulo y con sillón), borde 09:30 permitido / 09:29
  rechazado, pasado, profesional/sillón/prestación inactivos, campos
  prohibidos garantizados por la firma, turno cancelado no bloquea.
- **Integration (`tests/test_turnos_api.py`)**: `TestClient` sobre la app con
  DB en memoria — `201` feliz, `409` colisión (los tres motivos), `400`
  pasado/inactivos/extra fields, `TurnoRead` con `estado="reservado"` y fin
  derivado.
- Fechas: siempre **futuras fijas** (p. ej. `2026-11-05 09:00`) para que el
  rechazo por pasado sea determinista; datos siempre ficticios (RN-DATOS-03).

## Risks / Trade-offs

- **Modelos duplicados con `C-02`** → mitigación: mismos nombres de la KB;
  al archivar `C-02` este change se declara precursor y su código se fusiona.
- **`POST /turnos` sin auth mientras exista** → mitigación: solo datos de
  contacto/agenda, sin información clínica; documentado en el proposal y en la
  entrada de `CHANGES.md`; `C-03`/`C-17` lo endurecen. No se commitea ni
  deploya a producción (entrega local del TP).
- **Condición de carrera entre validación y commit** → SQLite serializa
  escrituras (una única writer connection); en Postgres futura agregar
  exclusión de rango como segunda barrera.
- **Turnos fuera del horario de atención** → aceptado: sin `HorarioAtencion`
  la regla verificable es el solapamiento; RN-TU-03/07 quedan para `C-07`.
- **`create_all` sin migraciones** → si `C-02` altera el esquema, hay que
  recrear la DB local; aceptable en dev con SQLite descartable.

## Open Questions

- Ninguno que impacte specs, enfoque o desglose de tasks. La absorción de
  estos modelos por `C-02` (nombres finales de constraints/índices) se
  resuelve al ejecutar `C-02`, sin cambiar el comportamiento especificado
  aquí.
