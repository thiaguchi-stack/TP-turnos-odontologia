# Explore previo — `crear-turno-sin-solapamientos`

Resumen de la exploración que se hizo **antes** de la propuesta del change
archivado, con sus fuentes. No se inventa nada: cada punto cita el archivo del
repo que lo respalda.

> **Nota de rutas**: la consigna de esta evidencia referenciaba
> `docs/explore/relevamiento-servicios-turnos-odontologia.md`; **ese archivo no
> existe en el repo**. El relevamiento real del change es
> [`docs/explore/relevamiento-crear-turno-sin-solapamientos.md`](../explore/relevamiento-crear-turno-sin-solapamientos.md)
> (único archivo de `docs/explore/`, verificado con `Get-ChildItem docs -Recurse`).
> Todas las citas de abajo salen de ahí.

- **Fase**: OPSX Explore (relevamiento previo a la propuesta), 2026-10-10.
- **Regla de consigna considerada**: la implementación puede ser una API o un
  módulo con lógica de dominio; **no exige interfaz gráfica**
  (relevamiento, encabezado).
- Fuentes complementarias: `openspec/changes/archive/2026-10-10-crear-turno-sin-solapamientos/proposal.md`,
  `docs/bitacora-inspeccion.md` (inspecciones I-03/I-04), `.active-orchestrator-state.json`
  (sección `opsx`).

---

## 1. El problema a cubrir (§1 del relevamiento)

La regla central es **RN-TU-01**: para un mismo `profesional_id` ni para un
mismo `sillon_id` pueden existir dos registros (turno–turno **o** turno–bloqueo)
cuyos intervalos se intersecten; la validación vive en la **capa de servicio**
y aplica a toda creación y reprogramación (RN-TU-08).

Casos que el relevamiento dibujó en el eje temporal (§1.1) y que hoy están
implementados y testeados:

| Caso original | Resultado esperado | Hoy en el repo |
|---|---|---|
| Mismo profesional, sillón distinto, horario que choca | RECHAZADO (colisión por profesional) | `backend/tests/test_turno_service.py:67` |
| Profesional distinto, **mismo** sillón (recurso compartido, RN-PR-05) | RECHAZADO (colisión por sillón) | `backend/tests/test_turno_service.py:76` |
| Borde: empieza exactamente cuando termina el anterior | PERMITIDO (intervalos semiabiertos `[inicio, fin)`) | `backend/tests/test_turno_service.py:169` |
| Bloqueo del profesional con `sillon_id = null` (libera todos los sillones) | RECHAZADO (colisión con bloqueo) | `backend/tests/test_turno_service.py:96` |

Reglas asociadas que el mismo change debía respetar (§1.2, tabla del
relevamiento): **RN-TU-02** (fin derivado, nunca duración arbitraria),
**RN-TU-04** (el alta nace en `reservado` y `estado` no llega desde fuera),
**RN-TU-06** (sin turnos en el pasado), **RN-TU-09** (sillón NOT NULL y activo),
**RN-PR-01** (profesional activo), **RN-PR-03** (el bloqueo impide turnos).

## 2. Estado del código al explorar (§2)

> "**El repo es documentación pura.**"

Verificado en ese momento: no existían `src/`, `backend/`, `frontend/`, ni
archivos `*.py`/`*.ts`; tampoco `pyproject.toml` ni specs
(`openspec list --specs` devolvía vacío, solo `.gitkeep`). Sí estaban completos
`knowledge-base/` (10 archivos), `CHANGES.md`, `AGENTS.md`/`CLAUDE.md` y el
research de `discovery/`. Conclusión: **todo el backend de este change se
construyó desde cero** (models → db → service → schemas → router → tests, §2.1).

Hoy ese estado quedó materializado: `backend/app/{core,models,schemas,services,routers,db}`
+ `backend/tests/` (58 tests verdes).

## 3. Insumos reutilizados de la KB (§3)

El relevamiento listó qué archivo de `knowledge-base/` aportaba qué, y todo eso
se usó sin re-inventarlo:

| Insumo | Fuente | Uso en el change |
|---|---|---|
| Entidades y restricciones (`sillon_id` NOT NULL, intervalos `[inicio, fin)`) | `knowledge-base/04_modelo_de_datos.md` | Modelos SQLAlchemy del change |
| RN-TU / RN-PR codificables | `knowledge-base/05_reglas_de_negocio.md` | `turno_service.crear_turno` |
| Forma de los errores (409 franja ocupada, 400 inválido) | `knowledge-base/07_flujos_principales.md` | Mensajes en español del servicio/API |
| Routers delgados + `services/` testeable | `knowledge-base/08_arquitectura_propuesta.md` | Estructura `backend/app/…` (DD-07) |
| DD-05 / DD-07 / DD-09, SU-02/SU-03 | `knowledge-base/09_decisiones_y_supuestos.md` | Duración derivada, capa de servicios, doble solapamiento |
| Ubicación en el plan | `CHANGES.md` (C-07, C-08) | Declaración del desvío |
| Reglas duras | `AGENTS.md` | Sin lógica en routers, tests obligatorios, español rioplatense |

## 4. Decisiones abiertas que se resolvieron (§4)

1. **SU-03 / Pregunta 8 (¿horarios semanales o por fecha?) → §4.1**: hallazgo
   clave del relevamiento: *la regla de no solapamiento es ajena al calendario*.
   `crear_turno` solo compara contra turnos y bloqueos existentes; el modelo
   `HorarioAtencion` hace falta **solo** para calcular franjas disponibles
   (RN-TU-07). Decisión: **no acoplar `crear_turno` al calendario**, dejar
   franjas para `C-07`. Confirmado en `docs/bitacora-inspeccion.md` I-04.
2. **Alcance → §4.2**: se compararon 3 opciones (A: solo dominio; B: dominio +
   API mínima; C: seguir el roadmap completo) y se eligió la **Opción B** —
   `POST /turnos` delgado que demuestra la regla con un `409` verificable,
   **sin frontend** (la consigna no lo exige). Confirmado en I-04.
3. **Dependencias del roadmap → §4.3**: el change **no** sigue el árbol
   `C-01 → … → C-07`, porque `C-02 core-models` y `C-03 auth-jwt-rbac` son
   governance **CRITICO** y no estaban archivados. Se recomendó (y se adoptó)
   un **change autónomo**, declarado como desvío deliberado. Fuentes:
   `proposal.md` §"Desvío deliberado vs. roadmap", bitácora I-03 y
   `.active-orchestrator-state.json` → `opsx.note`.
4. **Otras (§4.4)**: un solo camino de creación (`reservado`, sin auth en este
   corte); franjas fuera de alcance; **bloqueos sí dentro de alcance**
   (RN-TU-01 los menciona); sin Alembic en este corte (`create_all` + SQLite).

## 5. Escenarios candidatos (§5) → qué terminó siendo la spec

El relevamiento propuso **3 escenarios** (feliz / error de negocio / borde). La
spec que quedó archivada (`openspec/specs/turnos/spec.md`) los **amplió a 13
escenarios en 8 requirements**: además de los 3 originales agregó colisión con
bloqueo, bloqueo de otro profesional, borde rechazado, turno en el pasado,
recursos inactivos (3) y creación sobre turno cancelado. El detalle de esa
trazabilidad está en [verify-crear-turno-sin-solapamientos.md](verify-crear-turno-sin-solapamientos.md).

## 6. Alcance mínimo recomendado (§6) vs. entregado

Checklist del relevamiento y su estado real (tasks del change: 18/18 `[x]`):

- [x] Modelos SQLAlchemy mínimos: `Profesional`, `Prestacion`, `Sillon`,
      `Turno`, `Bloqueo` + `Paciente` stub (se resolvió en propose: la FK es
      NOT NULL, se creó el stub con datos ficticios — ver `proposal.md`).
- [x] `services/turno_service.crear_turno(...)`: fin derivado, solapamiento
      contra turnos activos **y** bloqueos, por profesional **y** por sillón,
      `[inicio, fin)`, recursos activos, sin pasado.
- [x] `POST /turnos` delgado con `TurnoCreate` sin `fecha_hora_fin` ni `estado`
      → 201 / 409 / 400.
- [x] Persistencia SQLite + `db/session`.
- [x] Tests: unitarios del servicio (borde, choques) + integración 409.

**Fuera de alcance declarado** (§6 + `proposal.md`): frontend, franjas
disponibles (RN-TU-07 → `C-07`), auth JWT/RBAC (C-03, CRITICO), reprogramación,
estados posteriores, cancelación por token, seed demo.

## 7. Handoff (§7)

El documento cerró con: *"Siguiente paso: `/opsx:propose crear-turno-sin-solapamiento`"*,
previa resolución de §4.3. Eso es exactamente lo que registró el state file
(`opsx.cycle = ["explore","propose","apply","verify","archive"]`, `done: true`)
y `CHANGES.md`: ciclo completo cerrado el **2026-10-10**.
