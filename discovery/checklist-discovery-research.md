# Checklist de Discovery — Sistema de gestión de turnos y agenda para consultorios odontológicos (Argentina)

> **Nota metodológica honesta:** el Q&A interactivo de los 11 puntos de `discovery-research` quedó **incompleto** durante la fundación del proyecto (el `.active-orchestrator-state.json` registra `discovery.status = "incomplete"`: "Discovery parkeado por el usuario para avanzar a kb-creator. Q&A de los 11 puntos sin completar"). Este checklist se **reconstruyó a posteriori** a partir de dos fuentes: (1) el **research de mercado escrito** en `discovery/raw/{argentina,latam,internacional}.md` y su verificación (`discovery/verificacion-fuentes.md`); y (2) la **knowledge-base** (`knowledge-base/01..10`), que es la fuente de verdad del dominio. No se realizó una nueva ronda de preguntas al usuario: los puntos que el research no pudo respaldar quedan marcados **"No evidenciado"** en lugar de completarse por deducción.
>
> **Regla de evidencia:** `(C)` = comprobado en fuente pública · `(A)` = afirmación comercial sin demostración · **No evidenciado** = sin respaldo público verificable. Fecha de consulta de las fuentes de mercado: **2026-10-09**.

---

## 1. Problema

Hoy la coordinación de turnos en un consultorio odontológico argentino se resuelve por **teléfono, WhatsApp y papel**, lo que genera ida y vuelta, **dobles reservas** y tiempo perdido tanto para el paciente como para la recepción.

El mercado argentino relevado muestra que la **reserva online 24/7 ya es estándar** (Doctoralia, Dental Total), pero:
- los grandes jugadores de agenda (Doctoralia, Docturno) **no son sistemas odontológicos** (sin odontograma/fiscalización clínica dental evidenciada) y **no evidencian** facturación AFIP/ARCA ni circuito de obras sociales;
- los sistemas odontológicos locales (DentalSoft, DentalSaaS, Dentiqa) cubren la capa clínica, pero **ninguno demuestra públicamente la prevención de solapamientos** (colisión por profesional y por sillón).

**Problema a resolver:** que el paciente reserve sin llamar y que el consultorio gestione su agenda completa (profesionales, prestaciones, bloqueos) en un solo lugar, **sin dobles reservas**, empezando por el núcleo de turnos.

## 2. Usuarios

| Actor | Descripción | Necesita |
|---|---|---|
| **Paciente** | Cliente del consultorio; reserva sin login | Ver horarios disponibles, reservar, cancelar su turno, no repetir datos |
| **Recepcionista / Admin** | Gestiona la agenda del consultorio | Crear/cancelar/reprogramar turnos, administrar profesionales, prestaciones y bloqueos, confirmar turnos |
| **Odontólogo / Profesional** | Atiende los turnos | Ver su agenda del día, marcar turnos como completados, no sufrir solapamientos |

Fuente: `knowledge-base/01_vision_y_objetivos.md` §Objetivos por actor y `knowledge-base/03_actores_y_roles.md`.

## 3. Casos de uso

- **US-001 / US-002 / US-003 (paciente):** ver franjas disponibles → reservar con datos de contacto → cancelar con token.
- **US-004 (admin):** ver agenda diaria/semanal por profesional.
- **US-005 (admin):** crear, cancelar y reprogramar turnos manualmente.
- **US-006 (admin):** administrar profesionales, prestaciones, bloqueos y sillones/boxes.
- **US-007 (odontólogo):** marcar sus turnos como completados.
- **US-008 (admin):** confirmar turnos reservados.
- **Backlog (v2):** US-101 recordatorios, US-102 cobros/señas, US-103 ficha clínica, US-104 notificaciones al profesional.

Fuente: `knowledge-base/06_funcionalidades.md`.

## 4. Competidores

Se relevaron **34 sistemas** en profundidad (14 de Argentina + 8 de Latinoamérica + 12 internacionales) más **7 referentes LatAm adicionales** citados como ampliación. Tabla resumen por región:

| Región | Cantidad | Sistemas | Hallazgo principal |
|---|---|---|---|
| **Argentina** | 14 | Doctoralia, Docturno, Dental Total, Reservo, DentalSoft, Dentiqa, DoctorYa, DentalSaaS, Bilog, Dentora, DenPro, SimpleTurno, OdontoApp, Nimbo | Agenda/reserva fuerte; cobertura odontológica nativa en DentalSoft/DentalSaaS/Dentiqa; AFIP/ARCA solo en DoctorYa y Reservo |
| **Latinoamérica** | 8 | Dentalink, Clinicorp, Feegow Clinic, Ninsaúde, Doctocliq, AgendaPro, Medilink, Clinicloud | Mayor madurez clínica y de cobros (Dentalink, Clinicorp, Doctocliq); precios mayormente opacos |
| **Internacional** | 12 | Dentally, Open Dental, Curve, Dentrix Ascend, CareStack, tab32, Denticon, Eaglesoft, SoftDent, iDentalSoft, Dentisoft, DentalSoft.es | Booking self-service y anti-doble-reserva maduros; WhatsApp casi inexistente (solo iDentalSoft); sin fiscalidad argentina |
| **LatAm (ampliación)** | 7 | ClinicQ, MR Dental Cloud, Denty.Cloud, Dentalware, OdontoCloude, XDentalCloud, Quiero Agendar | Nuevos entrantes con precio publicado y enfoque dental; ClinicQ con "validación en tiempo real doctor y sillón" |

Listado completo con evidencia por sistema: ver **Sección A del `informe-discovery.md`**. Fuente: `discovery/raw/` y `discovery/verificacion-fuentes.md`.

## 5. Funcionalidades necesarias (MVP v1)

- Reserva online de turnos (**público, sin login**): profesional → fecha → franja disponible → datos personales.
- Agenda diaria/semanal del consultorio por profesional.
- Alta/edición/cancelación/reprogramación de turnos por el admin.
- Gestión de profesionales, prestaciones (con **duración configurable**) y bloqueos de agenda.
- Gestión de **sillones/boxes** como recurso del consultorio.
- Confirmación de turnos reservados.
- Estados de turno: `reservado → confirmado → completado` (y `cancelado`).
- **Prevención de solapamientos por profesional y por sillón/box** (RN-TU-01).
- Cancelación del paciente por **token** (sin login).
- Datos simulados (seed) para la entrega del TP.

Fuente: `knowledge-base/01_vision_y_objetivos.md` §Alcance v1.0 y `knowledge-base/06_funcionalidades.md` (US-001..008).

## 6. Funcionalidades opcionales (backlog, fuera de v1)

| Funcionalidad | Por qué queda como opcional | Evidencia de mercado |
|---|---|---|
| Recordatorios automáticos (email/WhatsApp) | Estándar de mercado, pero amplía el TP | `(C)`/`(A)` en Docturno, DentalSoft, Dentiqa, Doctocliq, AgendaPro |
| Cobros/señas con Mercado Pago | Diferenciador documentado; requiere integración | `(C)` en Docturno, DentalSoft, DoctorYa; OP-01 |
| Ficha clínica / odontograma | Ancla de retención clínica | `(C)` en DentalSoft, DentalSaaS, Dentiqa, Dentalink, Clinicorp |
| Facturación fiscal AFIP/ARCA | Barrera de entrada fuerte y vacío local | `(A)` solo en DoctorYa y Reservo |
| Integración con Google Calendar | Sincronización pedida por consultorios | `(C)` en DentalSoft; **No evidenciado** en Doctoralia/Docturno (OP-04) |
| WhatsApp Business API | Canal rey en LatAm | `(C)` en Dentiqa; OP-03 |

## 7. Reglas de negocio (núcleo codificable)

**Duración de prestaciones**
- RN-PR-02: desactivar una prestación no elimina turnos históricos; impide nuevas reservas.
- RN-PR-04: cambiar la duración de una prestación solo afecta turnos futuros.
- RN-TU-02: `fin = inicio + duracion_minutos(prestación)`; nunca se guarda una duración arbitraria.

**Sillones / boxes**
- RN-TU-09: todo turno se asigna a un `sillon_id` **not null** con `activo=true`.
- RN-PR-05: la disponibilidad del sillón es **compartida**: si dos profesionales usan el mismo sillón, la restricción por sillón es la que impide el doble uso simultáneo.
- RN-AU-03: solo el admin puede crear/editar sillones.

**Prevención de solapamientos**
- RN-TU-01: para un mismo profesional **ni para un mismo sillón/box** pueden existir dos registros (turno–turno **o** turno–bloqueo) cuyos intervalos `[inicio, fin)` se intersecten. Se valida en la capa de servicios, en toda creación y reprogramación.
- RN-TU-03: no se reserva sobre agenda fuera de horario, turnos existentes, bloqueos, ni profesionales/sillones inactivos.
- RN-TU-06: no se crean turnos en el pasado.
- RN-PR-01: un profesional inactivo no recibe reservas.
- RN-PR-03: un bloqueo impide turnos en su intervalo.
- **Caso borde:** los intervalos son semiabiertos `[inicio, fin)` — un turno que empieza exactamente cuando termina otro **se permite**; uno que se solape un minuto, no.

**Estados del turno**
- RN-TU-04: estados válidos `reservado`, `confirmado`, `cancelado`, `completado`. Transiciones: `reservado → confirmado`, `reservado → cancelado`, `confirmado → cancelado`, `confirmado → completado`. Un turno cancelado no vuelve a activarse.
- RN-TU-05: la cancelación libera el horario; el paciente solo cancela con el `token_cancelacion` de su turno; el admin puede cancelar turnos ajenos.
- El alta de turno nace **siempre en `reservado`**; el estado no se acepta desde la reserva pública.

Fuente: `knowledge-base/05_reglas_de_negocio.md` §RN-TU, §RN-PR y `knowledge-base/04_modelo_de_datos.md` §Restricciones clave (integridad de agenda).

## 8. Integraciones

**En v1:** **ninguna** integración externa (DD-06). El sistema es single-tenant y autocontenido.

**Backlog (con evidencia de mercado):**
- **WhatsApp Business API** — canal rey en LatAm; evidenciado en Dentiqa (AR) y usado por Docturno, Clinicorp, Doctocliq, AgendaPro (OP-03).
- **Mercado Pago / cobros** — evidenciado en Docturno, DentalSoft, DoctorYa, Doctocliq (OP-01).
- **Facturación electrónica AFIP/ARCA** — barrera de entrada local; **no evidenciado** en Doctoralia/Docturno y solo `(A)` en DoctorYa/Reservo (OP-01).
- **Google Calendar** — `(C)` en DentalSoft; **No evidenciado** en Doctoralia/Docturno (OP-04).

Fuente: `knowledge-base/10_preguntas_abiertas.md` §Vacíos del research (OP-01..04) y `knowledge-base/09_decisiones_y_supuestos.md` §DD-06.

## 9. Restricciones

- **Alcance acotado al núcleo de turnos:** recordatorios, cobros, ficha clínica e integraciones externas quedan **fuera de v1** (DD-03/DD-06).
- **Single-tenant:** un consultorio; sin multi-sucursal ni aislamiento multi-tenant (DD-02).
- **Privacidad (Ley 25.326):** consentimiento en la reserva; sin datos clínicos en rutas públicas; seeds sin datos reales (RN-DATOS-01/02/03, DD-08).
- **Horarios semanales fijos** por profesional (SU-03): la entidad `HorarioAtencion` es config simple, no un CRUD de v1.
- **Inventario pequeño de sillones/boxes** (2–5) (SU-07).
- **Stack:** React + Vite + FastAPI + SQLAlchemy 2 + SQLite dev / Postgres opcional (DD-01).
- **Deploy local** para la entrega (uvicorn + Vite); nube como posibilidad no bloqueante.
- **Texto de interfaz/mensajes en español rioplatense** (regla dura del proyecto).

Fuente: `knowledge-base/09_decisiones_y_supuestos.md`, `knowledge-base/01_vision_y_objetivos.md` §Fuera de alcance, `CHANGES.md` §Supuestos y gaps.

## 10. Riesgos

| Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|
| El Q&A de Discovery quedó incompleto | Alta (ocurrido) | Medio | KB completa como fuente de verdad; este checklist reconstruido; preguntas abiertas documentadas |
| Los horarios del profesional no son semanales fijos (Pregunta 8) | Media | Medio | SU-03 preservado; `crear_turno` no acoplado a `HorarioAtencion` (ver `docs/explore/relevamiento-crear-turno-sin-solapamientos.md` §4.1) |
| Precios/datos de mercado cambian o rutas se caen | Media | Bajo | Verificación de 55 URLs documentada; correcciones C-01..C-07 registradas |
| Alcance del TP se amplía (recordatorios/cobros/ficha) | Media | Alto | Backlog explícito (DD-03/DD-06); reglas duras del proyecto |
| Datos de salud mal tratados (Ley 25.326) | Baja | Alto | Privacidad desde el diseño (DD-08, RN-DATOS); consentimiento; seeds ficticios |
| Autosugestión: "ningún competidor lo tiene" llevado a exceso | Media | Bajo | El informe distingue `(C)` / `(A)` / "No evidenciado"; los vacíos son "no evidenciados", no "inexistentes" |

Fuente: `knowledge-base/10_preguntas_abiertas.md`, `docs/explore/relevamiento-crear-turno-sin-solapamientos.md`, `discovery/verificacion-fuentes.md`.

## 11. Preguntas abiertas

**Preguntas del dominio (knowledge-base) — ninguna bloquea v1:**
1. ¿El enlace de cancelación por email es suficiente o hace falta recordatorio automático (US-101)?
2. ¿Se integra WhatsApp Business API para recordatorios (v2)?
3. ¿Entran cobros/señas con Mercado Pago en el TP (US-102)?
4. ¿Se integra ficha clínica/odontograma (US-103)?
5. ¿El deploy es local (demo) o en la nube (Railway/Render)?
6. ¿La cancelación del paciente requiere aviso al consultorio (US-104)?
7. ¿La obra social queda solo informativa o se valida cobertura?
8. ¿Los horarios del profesional son semanales fijos (SU-03) o cambian por fecha? *(impacto MEDIO; si cambian, ajustar `agenda_service`)*

**Puntos que el Discovery dejó "No evidenciado" (a completar con demo o fuente directa):**
- Prevención de solapamientos explícita: **No evidenciado** en todos los competidores relevados (salvo afirmaciones parciales: ClinicQ "validación en tiempo real doctor y sillón"; DentalSaaS "detección de solapamientos" sin demo).
- Facturación fiscal AFIP/ARCA: **No evidenciado** en Doctoralia/Docturno y solo `(A)` en DoctorYa/Reservo.
- Cumplimiento explícito de **Ley 25.326**: **No evidenciado** en la gran mayoría de los competidores.
- WhatsApp Business API (mecanismo técnico): **No evidenciado** en casi toda la oferta de EE.UU./UK; en LatAm mayormente `(A)`.
- Lista de espera, cancelación/reprogramación full self-service: celdas mayormente **No evidenciado** en el relevamiento.
- Precios de los EHR dentales maduros (Dentalink, Ninsaúde, Medilink): **No publicados**.
- SPAs sin render (OdontoApp, Reservo AR, Dental Total): funcionalidades internas **No evidenciado** por imposibilidad de fetch.

Fuente: `knowledge-base/10_preguntas_abiertas.md` §Preguntas abiertas y §Vacíos del research; raw de internacional §Registro de "No evidenciado".

> **Cierre:** ninguna pregunta abierta bloquea el MVP v1. Las que condicionan decisiones (Pregunta 8, recordatorios en la consigna) se resuelven antes del informe final o se dejan documentadas como backlog.
