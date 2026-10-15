# Visión y Objetivos

## Propósito del sistema

Una página de turnos online para los clientes de una clínica odontológica: el paciente reserva su turno sin llamar ni escribir, y el consultorio gestiona la agenda completa (profesionales, prestaciones, bloqueos) en un solo lugar.

Contexto: hoy la coordinación de turnos odontológicos se hace por teléfono/WhatsApp/papel, lo que genera ida y vuelta, dobles reservas y tiempo perdido. El mercado argentino relevado (Doctoralia, Dental Total) muestra que la **reserva online 24/7** ya es estándar, pero ningún jugador relevado combina agenda + gestión clínica + facturación local en una sola pieza: este sistema ataca ese espacio empezando por el núcleo (turnos), dejando la expansión clínica/financiera documentada como backlog.

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|-------|--------------------|------------------------|
| Paciente | Reservar un turno online sin llamar | Ver horarios disponibles, cancelar su turno, no repetir datos |
| Recepcionista / Admin | Gestionar la agenda del consultorio | Crear/cancelar/reprogramar turnos, administrar profesionales, prestaciones y bloqueos, confirmar turnos |
| Odontólogo / Profesional | Ver su agenda del día | Marcar turnos como completados, no sufrir solapamientos |

## Alcance v1.0

- Reserva online de turnos (público, sin login del paciente): selección de profesional → fecha → franja disponible → datos personales.
- Agenda diaria/semanal del consultorio por profesional.
- Alta/edición/cancelación/reprogramación de turnos por el admin.
- Gestión de profesionales, prestaciones (con duración configurable) y bloqueos de agenda.
- Confirmación de turnos reservados.
- Estados de turno: reservado → confirmado → completado (y cancelado).
- Prevención de solapamientos por profesional y por sillón/box (RN-TU-01).
- Datos simulados (seed) para la entrega del TP.

## Fuera de alcance

- **Recordatorios automáticos** (email/WhatsApp) — backlog v2.
- **Cobros, señas, facturación** (Mercado Pago, AFIP/ARCA) — backlog v2.
- **Ficha clínica, anamnesis, odontograma, imágenes/radiografías** — backlog v2.
- **Integraciones externas** (WhatsApp Business API, Google Calendar, APIs públicas) — backlog v2.
- **Multi-consultorio / multi-tenant** — fuera de alcance por decisión (escala: un consultorio).
- **Pagos de obras sociales/prepagas y liquidaciones** — backlog v3.

## Métricas de éxito

- % de turnos reservados online vs. telefónicos (incremento de adopción).
- Tiempo medio de reserva < 2 minutos.
- Cero solapamientos de turnos por profesional y por sillón/box.
- Reducción de ausencias percibida por el consultorio (a medir cuando existan recordatorios).