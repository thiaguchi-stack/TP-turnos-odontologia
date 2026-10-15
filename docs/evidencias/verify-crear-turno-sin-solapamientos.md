# Verify — `crear-turno-sin-solapamientos` (change archivado)

Verificación del change archivado en
`openspec/changes/archive/2026-10-10-crear-turno-sin-solapamientos/`, contra la
spec vigente `openspec/specs/turnos/spec.md` (8 requirements, 13 escenarios —
contados con `Select-String` sobre el archivo; el delta del change difiere de la
spec main **solo en el encabezado**: `## ADDED Requirements` → `## Requirements`).

No existe un comando propio de verify en OPSX: la verificación se hizo a mano
corriendo la suite y el lint del repo, y mapeando cada escenario contra los
tests existentes con `grep` de `def test_` sobre `backend/tests/`.

- **Fecha de la corrida**: 2026-10-15.
- **Entorno**: `backend\.venv` (Python 3.14.7, pytest 9.1.1), SQLite en memoria
  (`backend/tests/conftest.py` → `DATABASE_URL=sqlite://`).
- **Salidas crudas**: [pytest-crear-turno-sin-solapamientos.txt](pytest-crear-turno-sin-solapamientos.txt) · [ruff-crear-turno-sin-solapamientos.txt](ruff-crear-turno-sin-solapamientos.txt)

---

## 1. Comandos ejecutados y salida real

Desde la raíz del repo:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -v
```

Resumen real (última línea del `.txt`):

```
======================== 58 passed, 1 warning in 0.94s ========================
```

La única warning es del propio framework
(`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead`,
en `backend/.venv/Lib/site-packages/fastapi/testclient.py:1`) — no viene de código
del repo.

```powershell
backend\.venv\Scripts\ruff.exe check backend
backend\.venv\Scripts\ruff.exe format --check backend
```

Salida real (completa):

```
All checks passed!
31 files already formatted
```

Ambos con exit code `0`.

> Nota de entorno: **no existe `.venv` en la raíz**; el venv real del repo es
> `backend\.venv` (es el que indica el `README.md` §Instalación). El `python` del
> PATH de la máquina (3.14.7 sin dependencias, `ModuleNotFoundError: No module
> named 'fastapi'`) **no sirve** para correr la suite.

---

## 2. Trazabilidad: escenarios de la spec → tests

Fuente de escenarios: [openspec/specs/turnos/spec.md](../../openspec/specs/turnos/spec.md).
Cada fila fue verificada con `grep "def test_"` + lectura del cuerpo del test
(`backend/tests/test_turno_service.py`, `backend/tests/test_turnos_api.py`,
`backend/tests/test_schemas.py`, `backend/tests/test_models.py`), no de nombres
sugeridos.

### Requirement: Creación con duración derivada y estado inicial reservado

| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Turno exitoso con duración derivada de la prestación (201, `fin` = inicio + 30 min, `reservado`) | `test_turno_feliz_con_fin_derivado_y_estado_reservado` · `test_duracion_derivada_respeta_minutos_de_la_prestacion` · `test_creacion_feliz_responde_201_con_fin_derivado_y_reservado` (HTTP 201) | `backend/tests/test_turno_service.py:32` · `backend/tests/test_turno_service.py:42` · `backend/tests/test_turnos_api.py:20` |
| Solicitud con campos prohibidos `fecha_hora_fin` o `estado` → 400, sin crear turno | `test_crear_turno_no_acepta_estado_ni_fecha_hora_fin` (nivel servicio, `TypeError`) · `test_solicitud_con_campos_prohibidos_responde_400` (HTTP 400 + 0 filas) · de schema: `test_turno_create_rechaza_campo_estado`, `test_turno_create_rechaza_campo_fecha_hora_fin`, `test_turno_create_rechaza_campo_desconocido`, `test_turno_create_acepta_exactamente_los_cinco_campos` | `backend/tests/test_turno_service.py:48` · `backend/tests/test_turnos_api.py:32` · `backend/tests/test_schemas.py:33` · `backend/tests/test_schemas.py:38` · `backend/tests/test_schemas.py:43` · `backend/tests/test_schemas.py:23` |

### Requirement: Sin solapamiento con turnos del mismo profesional

| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Colisión por profesional con sillón distinto → 409, sin crear turno | `test_colision_por_profesional_con_sillon_distinto` (assert `motivo == "profesional"`) · `test_409_colision_por_profesional_con_sillon_distinto` (HTTP 409 + 1 fila) | `backend/tests/test_turno_service.py:67` · `backend/tests/test_turnos_api.py:48` |

### Requirement: Sin solapamiento con turnos del mismo sillón

| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Colisión por sillón con profesional distinto → 409, sin crear turno | `test_colision_por_sillon_con_profesional_distinto` (assert `motivo == "sillón"`) · `test_409_colision_por_sillon_con_profesional_distinto` (HTTP 409 + 1 fila) | `backend/tests/test_turno_service.py:76` · `backend/tests/test_turnos_api.py:64` |

### Requirement: Sin solapamiento con bloqueos del profesional

| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Colisión con bloqueo del profesional (`sillon_id` nulo) → 409 | `test_colision_con_bloqueo_de_sillon_nulo` · `test_409_colision_con_bloqueo_del_profesional` (HTTP 409 + 0 filas) | `backend/tests/test_turno_service.py:96` · `backend/tests/test_turnos_api.py:86` |
| (misma regla, bloqueo **asignado** al sillón del turno — cubre el "o asignado al sillón" del requirement) | `test_colision_con_bloqueo_del_mismo_sillon` · simétrico: `test_bloqueo_de_un_sillon_no_afecta_a_otro_sillon` | `backend/tests/test_turno_service.py:113` · `backend/tests/test_turno_service.py:130` |
| Bloqueo de otro profesional no afecta → 201 | `test_bloqueo_de_otro_profesional_no_afecta` (nivel **servicio**: crea el turno y assert `id is not None`) | `backend/tests/test_turno_service.py:148` |

### Requirement: Intervalos de agenda semiabiertos inicio fin

| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Borde permitido — inicia exactamente cuando termina otro → 201 | `test_borde_inicio_exactamente_al_fin_es_permitido` · `test_201_borde_inicio_igual_al_fin_de_otro_turno` (HTTP 201, 2 filas) | `backend/tests/test_turno_service.py:169` · `backend/tests/test_turnos_api.py:156` |
| Borde rechazado — inicia 1 minuto antes del fin → 409, sin crear turno | `test_borde_inicio_un_minuto_antes_del_fin_es_rechazado` (nivel **servicio**: `pytest.raises(TurnoSolapadoError)`) | `backend/tests/test_turno_service.py:180` |

### Requirement: Sin turnos en el pasado

| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Turno en el pasado → 400, sin crear turno | `test_turno_en_el_pasado_es_rechazado` · `test_400_turno_en_el_pasado` (HTTP 400 + 0 filas) | `backend/tests/test_turno_service.py:202` · `backend/tests/test_turnos_api.py:108` |

### Requirement: Solo recursos activos admiten turnos nuevos

| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Profesional inactivo → 400 | `test_profesional_inactivo_es_rechazado` · `test_400_profesional_inactivo` (HTTP 400 + 0 filas) | `backend/tests/test_turno_service.py:207` · `backend/tests/test_turnos_api.py:120` |
| Sillón inactivo → 400 | `test_sillon_inactivo_es_rechazado` · `test_400_sillon_inactivo` | `backend/tests/test_turno_service.py:213` · `backend/tests/test_turnos_api.py:132` |
| Prestación inactiva → 400 | `test_prestacion_inactiva_es_rechazada` · `test_400_prestacion_inactiva` | `backend/tests/test_turno_service.py:218` · `backend/tests/test_turnos_api.py:144` |
| (caso extra del requirement: sillón **inexistente** / FKs inexistentes) | `test_fk_inexistente_es_rechazado` (parametrizado: `profesional_id`, `paciente_id`, `prestacion_id`, `sillon_id` = 9999) · `test_fk_inexistente_no_deja_registros_en_turno` — **solo nivel servicio** | `backend/tests/test_turno_service.py:233` · `backend/tests/test_turno_service.py:249` |

### Requirement: Los turnos cancelados liberan la agenda

| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Creación sobre un turno cancelado → 201 | `test_turno_cancelado_no_bloquea_la_agenda` · `test_201_creacion_sobre_turno_cancelado` (HTTP 201 + 2 filas) | `backend/tests/test_turno_service.py:187` · `backend/tests/test_turnos_api.py:172` |

### Cobertura de modelos/apoyo usada por la spec

| Afirmación de la spec | Test(s) | Ruta:línea |
|---|---|---|
| Estado inicial `reservado` por defecto (modelo) | `test_turno_persiste_con_estado_reservado_por_defecto` · `test_turno_estado_restringido_a_valores_del_enum` · `test_turno_con_estado_invalido_no_se_persiste` | `backend/tests/test_models.py:77` · `backend/tests/test_models.py:99` · `backend/tests/test_models.py:109` |
| `sillon_id` NOT NULL + FK; `fecha_hora_fin` NOT NULL; `Bloqueo.sillon_id` nullable | `test_turno_sillon_id_es_not_null_y_fk` · `test_turno_fecha_hora_fin_es_not_null` · `test_bloqueo_persiste_con_sillon_id_nulo` | `backend/tests/test_models.py:129` · `backend/tests/test_models.py:135` · `backend/tests/test_models.py:139` |
| `POST /turnos` acepta exactamente los 5 campos del requirement | `test_turno_create_acepta_exactamente_los_cinco_campos` | `backend/tests/test_schemas.py:23` |

**Resultado honesto del mapeo**: los **13 escenarios / 8 requirements** de la
spec tienen al menos un test que los ejercita. Ver "huecos" abajo para lo que
queda cubierto solo parcialmente.

---

## 3. Huecos y salvedades (sin mentir)

1. **Dos escenarios cubiertos solo a nivel servicio, no a nivel HTTP:**
   - *"Bloqueo de otro profesional no afecta"* (spec: "la respuesta es 201") →
     solo `backend/tests/test_turno_service.py:148`. No hay test de API que
     haga `POST /turnos` esperando 201 en ese caso.
   - *"Borde rechazado — inicia 1 minuto antes del fin"* (spec: "la respuesta es
     409") → solo `backend/tests/test_turno_service.py:180`
     (`pytest.raises(TurnoSolapadoError)`), sin test HTTP que espere 409.
   - Riesgo residual bajo: el mapeo excepción → HTTP (`TurnoSolapadoError` →
     409, `TurnoRechazadoError` → 400) sí está cubierto por otros tests de la
     API, pero **este escenario en particular no lo verifica de punta a punta**.
2. **Sin frontend → sin capturas de UI.** El change fue API + servicio por
   decisión de alcance (Opción B, `docs/explore/relevamiento-crear-turno-sin-solapamientos.md`
   §4.2 y bitácora I-04): no hay interfaz que capturar. `docs/evidencias/capturas/`
   queda **pendiente** hasta `C-11` del roadmap.
3. **Sin mypy todavía**: el type-checker no está adoptado en el repo (no figura
   en `backend/pyproject.toml` ni en los comandos del `README.md`), así que no
   hay `mypy-*.txt` que generar. Pendiente.
4. **La suite tiene 58 tests, no solo los de este change**: incluye health, db,
   startup, fixture, errores y los modelos/schemas creados por el mismo change.
   No existe un marker de "tests del change"; el listado §2 es el que delimita
   cuáles responden a la spec.
5. **Tests extra sin escenario en la spec** (no son huecos, son cobertura de más):
   parametrizado de FKs inexistentes (`backend/tests/test_turno_service.py:233`),
   bloqueo de un sillón que no afecta a otro (`:130`), duración derivada con
   prestación de 45 min (`:42`).

---

## 4. Estado final

| Control | Resultado |
|---|---|
| `pytest backend\tests -v` | **58 passed, 0 failed, 0 skipped**, 1 warning (del framework), 0.94 s |
| `ruff check backend` | **`All checks passed!`** (exit 0) |
| `ruff format --check backend` | **`31 files already formatted`** (exit 0) |
| Trazabilidad spec → tests | 8/8 requirements, 13/13 escenarios con al menos un test (2 de ellos solo a nivel servicio — ver §3) |
| Tasks del change (`tasks.md`) | 18 de 18 marcadas `[x]`, 0 abiertas (grep de `- [ ]` = 0) |
| Commits hechos para esta evidencia | **ninguno** (regla dura del repo: solo se commitea con pedido explícito) |
