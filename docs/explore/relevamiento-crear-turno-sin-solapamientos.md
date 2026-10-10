# Relevamiento — Explore: crear turno sin solapamientos (profesional y sillón/box)

> **Fase**: OPSX Explore (relevamiento previo a la propuesta)
> **Fecha**: 2026-10-10
> **Change candidato**: crear un turno evitando solapamientos por profesional y por sillón/box
> **Regla de consigna**: la implementación puede ser una API o un módulo con lógica de dominio; **no exige interfaz gráfica**.
> **Documento**: solo relevamiento. No se generaron artefactos de propose (`proposal.md`, `design.md`, `tasks.md`).

---

## 1. Problema a cubrir

### 1.1 La regla central (RN-TU-01)

Para un mismo `profesional_id` **ni** para un mismo `sillon_id` pueden existir dos
registros (turno–turno **o** turno–bloqueo) cuyos intervalos se **intersecten**.
La validación ocurre en la capa de servicio, en toda creación **y** en toda
reprogramación (RN-TU-08).

```
  eje temporal -------------------------------------------------->
  Turno A (prof P, sillón S1):     [09:00 ---- 09:30)
                                    fin = 09:00 + 30min (prestación)

  Caso 1 — mismo profesional P, sillón distinto S2:
  Turno B (prof P, sillón S2):            [09:15 ------- 09:45)
                                           ^
                                           RECHAZADO  (colisiona por PROFISSIONAL)

  Caso 2 — profesional distinto P2, MISMO sillón S1 (recurso compartido, RN-PR-05):
  Turno C (prof P2, sillón S1):    [09:20 ----- 09:50)
                                    ^
                                    RECHAZADO  (colisiona por SILLÓN)

  Caso 3 — borde: empieza exactamente cuando termina A:
  Turno D (prof P, sillón S1):           [09:30 ---- 10:00)
                                          ^
                                          PERMITIDO   (intervalos semiabiertos [inicio, fin))

  Caso 4 — bloqueo del profesional (sillón null = libera en TODOS los sillones):
  Bloqueo (prof P, sillon=null):  [15:00 ---- 19:00)
  Turno E (prof P, cualquier sillón):   [16:00 -- 16:30)
                                         ^
                                         RECHAZADO  (colisiona con BLOQUEO)
```

### 1.2 Reglas asociadas que el mismo cambio debe respetar

| ID | Regla | Implicación directa en el código |
|----|-------|----------------------------------|
| RN-TU-02 | `fin = inicio + duracion_minutos(prestacion)`; nunca duración arbitraria | El `fin` se **deriva**, nunca llega en el request |
| RN-TU-04 | Estados: `reservado → confirmado` / `→ cancelado`; `confirmado → completado` / `→ cancelado` | El alta nace siempre en `reservado`; no se acepta `estado` desde fuera (regla dura) |
| RN-TU-06 | No se crean turnos en el pasado | Validación de `inicio >= ahora` |
| RN-TU-09 | `sillon_id` NOT NULL y sillón `activo=true` | Sin sillón no hay turno; el sillón se asigna al crear |
| RN-PR-01 | Profesional `activo=false` no recibe reservas | Validación previa al solapamiento |
| RN-PR-03 | El bloqueo impide turnos en su intervalo | El bloqueo entra en la misma comparación que los turnos |

### 1.3 Fórmula de franjas disponibles (si entra en alcance)

```
  franjas_disponibles(prof, fecha) =
        HorarioAtencion semanal del profesional        (agenda configurada, SU-03)
      − turnos activos (estado != cancelado)           del profesional
      − turnos activos que ocupan algún sillón         por sillon_id
      − bloqueos del profesional                       (sillon_id null → todos)
      recortado a la grilla de la prestación           (duracion_minutos)
```

> `franjas` es la **lectura**; `crear_turno` es la **escritura**. Son simétricas
> pero no idénticas: `franjas` necesita el calendario (SU-03), `crear_turno` con
> validar solapamiento **no lo necesita**. Ver §4.1 — es la palanca de alcance.

---

## 2. Estado del código

**El repo es documentación pura.** Verificado con glob/listado de directorios:

| Recurso | Estado |
|---------|--------|
| `src/`, `tests/`, `backend/`, `frontend/`, `app/`, `api/`, `server/`, `e2e/` | **no existen** |
| Archivos `*.py` o `*.ts`/`*.tsx` fuera de `node_modules` | **ninguno** |
| `pyproject.toml`, `package.json` raíz, `.env`/`.env.example` | **no existen** |
| `knowledge-base/` (10 archivos), `CHANGES.md`, `AGENTS.md`, `CLAUDE.md` | completos y vigentes |
| `docs/discovery/`, `discovery/sources/` | research de mercado completo |
| `openspec/config.yaml` | inicializado (`schema: spec-driven`), sin `context` ni `rules` cargados |
| `openspec list --json` | `changes: []`, root válido |
| `openspec list --specs` | **no hay specs** (`openspec/specs/` solo con `.gitkeep`) |

**No existe ningún change archivado.** Toda la capa de código que este change
necesita se construye **desde cero**.

### 2.1 Hay que construir desde cero

```
  objetivo: crear_turno() sin solapamiento
  +----------------------------------------------+
  |                                              |
  |   [x] nada existe todavía                    |
  |                                              |
  |   1. models/   Profesional, Prestacion,      |
  |                Sillon, Turno, Bloqueo        |
  |   2. db/       session + engine SQLite       |
  |   3. services/ turno_service.crear_turno     |
  |                (valida solapamiento)         |
  |   4. schemas/  TurnoCreate / TurnoRead       |
  |   5. routers/  POST /turnos (delgado)  <- op |
  |   6. tests/    unit (borde [inicio,fin))     |
  |                + integration (409)           |
  |                                              |
  |   * = opcional según alcance (§4.2)          |
  +----------------------------------------------+
```

---

## 3. Insumos reutilizables (todo ya está definido en la KB)

| Insumo | Fuente | Qué aporta al change |
|--------|--------|----------------------|
| Modelo de datos (entidades + ERD) | `knowledge-base/04_modelo_de_datos.md` | Definición exacta de `Turno`, `Sillon`, `Bloqueo`, `Prestacion`, `Profesional` con tipos y restricciones; `sillon_id` NOT NULL; restricción de integridad de agenda en intervalos `[inicio, fin)` |
| Reglas de negocio | `knowledge-base/05_reglas_de_negocio.md` §RN-TU, §RN-PR | RN-TU-01/02/04/06/09 y RN-PR-01/03/05 codificables sin ambigüedad |
| Flujos E2E y estados | `knowledge-base/07_flujos_principales.md` | Forma de los errores (409 franja ocupada, 400 transición inválida) y diagrama de estados |
| Arquitectura y estructura | `knowledge-base/08_arquitectura_propuesta.md` | Routers delgados + `services/` testeable; estructura `backend/app/{models,schemas,services,routers,db}`; estrategia de pruebas unit → integración |
| Supuestos / decisiones | `knowledge-base/09_decisiones_y_supuestos.md` | DD-05 (duración derivada), DD-07 (capa de servicios), DD-09 (solapamiento por profesional **y** sillón), SU-02/SU-03/SU-07 |
| Roadmap | `CHANGES.md` §C-07 `agenda-engine`, §C-08 `turnos-agenda-api` | Ubicación en el plan, dependencias y governance esperados |
| Preguntas abiertas | `knowledge-base/10_preguntas_abiertas.md` Pregunta 8 | Condiciona SU-03 (horarios semanales) |
| Reglas duras | `AGENTS.md` §Reglas | Ningún `any`, lógica nunca en routers, tests obligatorios antes de cerrar change, datos ficticios, texto en español rioplatense |

---

## 4. Decisiones abiertas que impactan la propuesta

### 4.1 — SU-03: ¿hace falta calendario de horarios por fecha?

**Pregunta 8** de `10_preguntas_abiertas.md`: *¿los horarios del profesional son
semanales fijos (SU-03) o cambian por fecha?* — impacto MEDIO, **no bloquea v1**,
pero *"si cambian por fecha, ajustar `agenda_service` antes de implementar"*.

**Hallazgo clave**: la regla de **no solapamiento** es *ajena* al calendario. Solo
compara el nuevo intervalo contra turnos y bloqueos existentes. El calendario
(`HorarioAtencion`) hace falta **solo** para calcular *franjas disponibles*
(RN-TU-07), que es la lectura pública.

```
  impacto de SU-03 sobre cada pieza:

  crear_turno() ──► solapamiento + duración + estado + pasado   [ SIN SU-03 ]
  franjas()     ──► agenda − turnos − bloqueos                  [ CON SU-03 ]
```

**Recomendación**: preservar el supuesto SU-03 (**horarios semanales fijos**,
config simple, sin CRUD) y **no** acoplar `crear_turno` al modelo
`HorarioAtencion`. Si la pregunta 8 se resuelve luego a "cambian por fecha", el
núcleo de este change no se toca — solo se ajusta el cálculo de franjas.

### 4.2 — Alcance mínimo: ¿API + dominio, sin frontend?

La consigna admite *"una API o un módulo con lógica de dominio"*. Opciones:

| Opción | Contenido | Tamaño | Acomoda la consigna |
|--------|-----------|--------|---------------------|
| **A — Módulo de dominio puro** | `services/` + models + tests unitarios. Sin HTTP | mínimo | ✅ sí |
| **B — Dominio + API mínima** | Opción A + `POST /turnos` delgado + integration test | chico-medio | ✅ sí, más fiel a la KB |
| **C — Línea del roadmap completa** | C-01→C-07 (foundation, core-models **CRITICO**, auth **CRITICO**, catálogos) y luego el motor | muy grande | ✅ pero fuera de alcance de un change |

**Recomendación**: **Opción B**. La regla se demuestra de forma verificable con
`POST /turnos → 409`, y respeta DD-07 (routers delgados). **Sin frontend.**

### 4.3 — ¿Dependemos de C-01…C-07 del roadmap?

`C-07 agenda-engine` tiene dependencias C-04+C-05+C-06 (→ C-03 → C-02 → C-01),
y **C-02 `core-models` y C-03 `auth-jwt-rbac` son governance CRITICO** (no se
codean sin análisis y aprobación previa). Hoy ningún cambio del roadmap está
archivado → **ninguna dependencia está satisfecha**.

**Pregunta abierta (la más importante)**: ¿este change es

1. **un change de la consigna autónomo** (corte vertical propio: solo los modelos
   y el servicio que la regla necesita, sin auth ni catálogos completos), o
2. **una reetiquetatura de `C-07`** (con lo cual primero hay que ejecutar el
   camino C-01 → C-07, incluidos dos changes CRITICO)?

**Recomendación**: (1) autónomo, acotado y autocontenido, declarando
explícitamente en el proposal que **es un desvío deliberado del árbol de
dependencias** y que su persistencia será absorbida/alinida por `C-02`
posteriormente. Evita arrastrar governance CRITICO a una regla que se puede
probar en aislamiento.

### 4.4 — Otras decisiones menores a confirmar

- **¿Quién crea el turno?** ¿un solo `POST /turnos` (admin, si hay auth) o
  también la reserva pública (con token)? → mínimo: un solo camino, `reservado`.
- **¿Franjas disponibles en el mismo change?** → recomendación: **no** (§4.1);
  dejar RN-TU-07 para `C-07`.
- **¿Bloqueos en el alcance?** → **sí**: RN-TU-01 menciona turno–bloqueo
  explícitamente; omitirlos dejaría la regla incompleta.
- **¿Alembic?** → la KB lo declara opcional; para un change acotado, `create_all`
  + SQLite alcanza.

---

## 5. Escenarios candidatos para la spec

Formato `dado / cuando / entonces`. **Tres**: uno feliz, uno de error de negocio,
uno de borde.

### Escenario 1 — Feliz

```
DADO   un profesional activo P, un sillón activo S1, una prestación de 30 minutos
       y ningún turno ni bloqueo en esa franja
CUANDO creo un turno de P en S1 para el 2026-11-05 09:00
ENTONCES el turno se crea con fecha_hora_fin = 2026-11-05 09:30,
         estado = "reservado",
         y P y S1 quedan ocupados en [09:00, 09:30)
```

### Escenario 2 — Error de negocio (solapamiento)

```
DADO   existe un turno "reservado" de P1 en sillón S1 para [09:00, 09:30)
       y S1 además es usado por otro profesional P2 en el mismo horario
CUANDO intento crear un turno de P1 (en el sillón S2, distinto) para 09:15
ENTONCES la creación se rechaza con 409 sin generar ningún turno,
         porque P1 ya está ocupado en [09:15, 09:45) — colisión por PROFISSIONAL
       (y simétricamente: crear P2 en S1 en esa franja también daría 409
        por colisión de SILLÓN, cubriendo RN-PR-05)
```

### Escenario 3 — Borde (intervalo semiabierto `[inicio, fin)`)

```
DADO   existe un turno de P1 en S1 para [09:00, 09:30)  (fin derivado, RN-TU-02)
CUANDO creo un turno de P1 en S1 para 09:30 con una prestación de 60 minutos
ENTONCES la creación tiene ÉXITO — 09:30 es el fin abierto del turno previo,
         los intervalos [09:00, 09:30) y [09:30, 10:30) no se intersectan
       (y un turno que empiece a 09:29 o termine a 09:31 sí debe rechazarse)
```

---

## 6. Recomendación de alcance mínimo para la propuesta

**Slug sugerido del change**: `crear-turno-sin-solapamiento`
*alternativas*: `turnos-sin-solapamiento`, `agenda-engine-min`

**Alcance (Opción B de §4.2)**:

- [ ] Modelos SQLAlchemy mínimos: `Profesional`, `Prestacion`, `Sillon`, `Turno`,
      `Bloqueo` (+ `Paciente` stub si la FK es not-null; se puede crear con datos
      ficticios mínimos o relajar el FK en el corte autónomo — **decidir en
      propose**).
- [ ] `services/turno_service.crear_turno(...)`: deriva `fin` (RN-TU-02),
      valida solapamiento contra turnos activos **y** bloqueos por
      `profesional_id` y por `sillon_id` con intervalos `[inicio, fin)`,
      valida profesional/sillón activo (RN-PR-01/09) y rechaza pasado (RN-TU-06).
- [ ] `POST /turnos` delgado (Pydantic `TurnoCreate` **sin** `fecha_hora_fin` y
      **sin** `estado`) → 201 / **409** solapamiento / 400 datos inválidos.
- [ ] Persistencia SQLite + `db/session`.
- [ ] Tests: unitarios del servicio (borde `[inicio, fin)`, choque por
      profesional, choque por sillón, choque con bloqueo) + integración 409.

**Fuera de alcance** (declararlo explícitamente en el proposal):

- Frontend (consigna no lo exige).
- Franjas disponibles / `HorarioAtencion` (RN-TU-07) → queda para `C-07`.
- Auth JWT y RBAC (C-03, governance CRITICO) — se crea turnos sin distinguir rol
  en este corte, **o** se omite el router HTTP y se entrega solo el módulo
  (Opción A) si se quiere evitar tocar rutas privadas.
- Reprogramación, estados posteriores, cancelación por token, seed demo.

---

## 7. Handoff

- Este documento **no** es un artefacto de propose.
- Siguiente paso: `/opsx:propose crear-turno-sin-solapamiento`
  (previo: resolver §4.3 — autónomo vs. encadenado a C-01…C-07 — porque define
  todo el resto de la propuesta).
