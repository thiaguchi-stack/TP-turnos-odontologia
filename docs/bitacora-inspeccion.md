# Bitácora de inspección — protocolo de revisión entre etapas (TP-turnos-odontologia)

> **Propósito:** dejar registro de los puntos de control ("inspecciones") aplicados al terminar cada etapa de la fundación y de la implementación, qué se revisó en cada uno, qué se decidió y —cuando correspondió— qué se corrigió y por qué. No es un changelog de features: es la traza de **decisiones de metodología** del trabajo, con la evidencia (archivo + sección) que la respalda.
>
> **Materia:** Metodología I · **Integrante:** Thiago Oviedo · **Tipo:** TP individual · **Fecha:** 2026-10-11

**Cómo se lee la tabla:** cada fila es una inspección. *Etapa* = momento del flujo; *Decisión* = veredicto del control (aprobar / ajustar / parkear); *Qué se revisó* = artefactos y secciones mirados; *Qué se corrigió / Por qué no* = acción concreta o justificación de no tocar nada.

---

## 1. Tabla de inspecciones

| # | Etapa | Decisión | Qué se revisó (archivo / sección) | Qué se corrigió / Por qué no |
|---|---|---|---|---|
| I-01 | **Discovery (Etapa 2)** — cierre del research de mercado | **Ajustar** | `docs/discovery/raw/{argentina,latam,internacional}.md` (34 sistemas); `docs/discovery/verificacion-fuentes.md` §Resultado global | Se detectaron **4 URLs muertas/cambiadas y 2 datos de contenido desactualizados**. Se corrigió el raw y quedó asentado en `verificacion-fuentes.md` §3 (C-01…C-07). Ver §2 de esta bitácora. |
| I-02 | **Discovery (Etapa 2)** — verificación de fuentes | **Aprobar** | `verificacion-fuentes.md` §1 (6 fuentes a fondo, una por tipo) y §2 (55 URLs) | Se confirmó que **0 productos son inventados** y que las 4 URLs rotas son rutas secundarias, no dominios inexistentes. No se eliminó ningún sistema del relevamiento. |
| I-03 | **Roadmap / gobernanza** — antes de codear | **Parquear (desvío deliberado)** | `CHANGES.md` §camino crítico; `.active-orchestrator-state.json` §opsx | El change de consigna `crear-turno-sin-solapamientos` se declaró **autónomo**, sin encadenar C-01→C-07, porque **C-02 y C-03 son governance CRITICO** y aún no están archivados. Evita arrastrar governance CRITICO a una regla que se prueba en aislamiento. |
| I-04 | **Exploración (OPSX Explore)** — alcance del change | **Ajustar** | `docs/explore/relevamiento-crear-turno-sin-solapamientos.md` §4.1, §4.2, §4.3 | **Ajuste de alcance:** se acotó el change a **Opción B (dominio + API mínima, sin frontend)** y se decidió **no acoplar `crear_turno` al calendario `HorarioAtencion`** (§4.1), dejando las franjas disponibles (RN-TU-07) para `C-07`. Motivo: SU-03 y la Pregunta 8. |
| I-05 | **KB ↔ modelo de datos** — coherencia sillón/box | **Ajustar** | `knowledge-base/04_modelo_de_datos.md`; `knowledge-base/09_decisiones_y_supuestos.md` (DD-09); `knowledge-base/05_reglas_de_negocio.md` (RN-TU-01) | Se incorporó **`Sillon` como recurso de primera clase** (antes no existía) y se reescribió RN-TU-01 para prohibir solapamiento **por profesional y por sillón/box** (turno–turno y turno–bloqueo). Motivo: el research no mostraba esta regla en ningún competidor; se adoptó como **diferenciador del MVP**. |
| I-06 | **KB ↔ research** — vacíos de mercado | **Aprobar** | `knowledge-base/10_preguntas_abiertas.md` §Vacíos del research (OP-01..OP-04) | No se inventaron datos para cerrar los vacíos: se los dejó como **preguntas abiertas / `No evidenciado`**, distinguiendo lo `(C)` comprobado de lo `(A)` declarado. |
| I-07 | **Implementación (OPSX apply)** — cierre del change | **Aprobar con evidencia** | `openspec/changes/archive/2026-10-10-crear-turno-sin-solapamientos/`; `backend/tests` (58 passed) | El change se cerró **solo con tests verdes** (unit del servicio con borde `[inicio, fin)`, colisión por profesional, colisión por sillón, colisión con bloqueo + integración 409). La spec quedó en `openspec/specs/turnos/spec.md`. |
| I-08 | **Documentación (Etapa 2)** — entregables | **Ajustar** | `docs/discovery/informe-discovery.md`; `docs/discovery/checklist-discovery-research.md` | Se documentó honestamente que el **Q&A interactivo de los 11 puntos quedó incompleto** (parkeado por el usuario según el state file) y se reconstruyó el checklist a partir de los raw + la KB, marcando `No evidenciado` en lo no respaldado. |

---

## 2. Detalle de las correcciones de fuentes (inspección I-01)

Fuente: `docs/discovery/verificacion-fuentes.md` §3. Se listan tal como quedaron registradas, sin inventar datos.

**2.1 URLs muertas o cambiadas**

| ID | Raw | URL citada | Situación verificada | Acción aplicada |
|---|---|---|---|---|
| C-01 | argentina (Docturno) | `profesionales.docturno.com/planes` | 404 (la base `profesionales.docturno.com` existe) | Se mantiene la URL base; se removió la cita de la ruta `/planes`. |
| C-02 | argentina (DoctorYa) | `doctorya.com.ar/planes` | Redirige a `/login`; los precios ya **no son públicos** | Se re-marcó "precios publicados" como **ya no públicos** en la tabla. |
| C-03 | argentina (SimpleTurno) | `simpleturno.com/precios` | 404 (existen `simpleturno.com` y `/rubros/odontologia`) | Se removió la cita de `/precios`. |
| C-04 | argentina (Nimbo) | `nimbo-x.com/ar/clinica-dental` | 404 (existen `/ar` y `/ar/precios`) | Se usó `/ar` y `/ar/precios` en la fuente. |

**2.2 Correcciones de contenido**

| ID | Raw | Dato previo | Verificación | Acción |
|---|---|---|---|---|
| C-05 | internacional (tab32) | Odontograma/perio **No evidenciado** | La página de pricing lista "Clinical Charting — **Odontogram, perio charting**…" | Se actualizó a **Comprobado**. |
| C-06 | internacional (tab32) | AutoRemind sin detalle | "**Included Year 1**, 500 msg/mes, luego USD 69/mes, overage USD 0,08/msg" | Se enriqueció la celda con el detalle. |
| C-07 | argentina (Doctoralia PRO) | — | `pro.doctoralia.com/ar` responde **200 con `www`** | Sin cambio de contenido; la URL es válida. |

**2.3 Integridad del repo**

- Los raw citan notas internas `discovery/sources/{doctoralia-argentina,dental-total,tm-dental}.md` que **no existen** en el repositorio (verificado por `glob`). Quedó registrado como referencia a limpiar o crear (no se creó un archivo ficticio).
- Se desambiguaron y verificaron **4 marcas "DentalSoft/Dentisoft" distintas** (AR, España, EE.UU., Perú), todas con dominio propio.

---

## 3. Lección del protocolo

El protocolo de inspección entre etapas evitó dos fallas típicas de un TP:

1. **Afirmar lo no verificado.** La regla de distinguir **funcionalidad comprobada `(C)` / afirmación comercial `(A)` / "No evidenciado"** obligó a no deducir por analogía. El resultado más contundente fue el de **prevención de solapamientos**: *ningún* competidor la demuestra públicamente, y aun así se dejó escrito como "No evidenciado" (no como "inexistente"). Esa misma honestidad fue la que justificó convertir la correctitud de la agenda en el **diferenciador técnico del MVP**.

2. **Codear sin base.** La inspección de gobernanza (I-03) detectó a tiempo que el camino crítico de `CHANGES.md` pasaba por dos changes **CRITICO** (C-02, C-03) no archivados. En lugar de saltear la puerta de gobernanza, se documentó un **desvío deliberado y autónomo**, y la inspección del alcance (I-04) lo acotó a dominio + API, **sin acoplar `crear_turno` al calendario** para no quedar rehén de la Pregunta 8 (SU-03).

La conclusión del ejercicio es que revisar no es "buscar errores al final", sino **decidir explícitamente qué se corrige, qué se parkea y qué se documenta como pendiente** — con el archivo y la sección que lo respaldan. Las inspecciones I-02, I-06 y I-07 muestran el caso opuesto: cuando la evidencia alcanza, la decisión correcta es **no tocar nada** y aprobar.
