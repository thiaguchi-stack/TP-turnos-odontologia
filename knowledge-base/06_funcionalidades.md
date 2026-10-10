# Funcionalidades

Épicas e historias de usuario. Convención: `US-NNN`. Cada US referencia las reglas de negocio que la constriñen.

## Épica 1 — Reserva online (paciente, público)

### US-001 · Ver horarios disponibles
> Como **paciente**, quiero ver los horarios libres de un profesional en una fecha, para elegir sin llamar.

- **Criterios de aceptación**
  - El paciente elige profesional → fecha → ve grilla de franjas disponibles.
  - Solo se muestran franjas válidas por RN-TU-03/07 (agenda − turnos − bloqueos − inactivos), considerando también la disponibilidad de sillón/box (RN-TU-01/09).
  - Los horarios se muestran en la zona horaria local del consultorio.
- **Reglas**: RN-TU-01, RN-TU-03, RN-TU-07, RN-TU-09, RN-PR-01

### US-002 · Reservar un turno
> Como **paciente**, quiero reservar un turno con mis datos, para asegurar mi espacio.

- **Criterios de aceptación**
  - Formulario: nombre, apellido, DNI, teléfono, email (opcional), obra social (opcional).
  - Validación: datos obligatorios presentes, teléfono con formato mínimo, email válido si se carga (RN-DATOS-01: consentimiento).
  - Al reservar: se crea o reutiliza el paciente (dedupe por dni/teléfono), se crea el turno `reservado` con sillón/box asignado (RN-TU-09).
  - La franja elegida deja de aparecer en la grilla en tiempo real (RN-TU-01).
  - Respuesta de éxito con resumen del turno + enlace de cancelación (token).
- **Reglas**: RN-TU-01, RN-TU-02, RN-TU-03, RN-DATOS-01

### US-003 · Cancelar turno (paciente)
> Como **paciente**, quiero cancelar mi turno con mi enlace, para liberar el horario.

- **Criterios de aceptación**
  - El enlace con `token_cancelacion` cancela solo el turno del paciente dueño del token (RN-TU-05).
  - Tras cancelar, el horario vuelve a la grilla disponible.
  - Un token ya usado o inexistente devuelve error claro.
- **Reglas**: RN-TU-04, RN-TU-05

## Épica 2 — Gestión de agenda (recepcionista/admin, odontólogo)

### US-004 · Ver agenda diaria/semanal
> Como **recepcionista**, quiero ver la agenda del día/semana por profesional, para administrar los turnos.

- **Criterios de aceptación**
  - Vista por profesional + día (y semana), con turnos y bloqueos en el eje horario.
  - Filtro de estado (reservado/confirmado/cancelado/completado).
- **Reglas**: RN-AU-01, RN-AU-03

### US-005 · Crear, cancelar y reprogramar turnos
> Como **recepcionista**, quiero crear/cancelar/reprogramar turnos manualmente, para atender a pacientes que llaman.

- **Criterios de aceptación**
  - Crear en nombre del paciente (o reutilizar paciente existente), eligiendo sillón/box y validando su disponibilidad en la franja (RN-TU-01/09).
  - Cancelar con motivo opcional (RN-TU-05).
  - Reprogramar = reubicar en otro horario del mismo profesional, elegir sillón y revalidar solapamiento por profesional y por sillón (RN-TU-08).
- **Reglas**: RN-TU-01, RN-TU-02, RN-TU-05, RN-TU-08, RN-TU-09

### US-006 · Administrar profesionales, prestaciones, bloqueos y sillones
> Como **recepcionista**, quiero mantener el catálogo, los sillones/boxes y los bloqueos, para reflejar la realidad del consultorio.

- **Criterios de aceptación**
  - Alta/baja/edición de profesionales (con activación/desactivación, RN-PR-01).
  - Alta/edición de prestaciones con duración en minutos (RN-PR-02, RN-PR-04).
  - Alta/baja de bloqueos por profesional (RN-PR-03).
  - Alta/edición/baja de sillones/boxes (activación/desactivación, RN-AU-03, RN-TU-09).
- **Reglas**: RN-AU-03, RN-PR-01..04

### US-007 · Marcar turno completado (odontólogo)
> Como **odontólogo**, quiero marcar mis turnos como completados, para reflejar la atención.

- **Criterios de aceptación**
  - Solo puede operar sobre turnos de su profesional asociado (RN-AU-02).
  - Transición válida: `confirmado → completado` (RN-TU-04).
- **Reglas**: RN-AU-02, RN-TU-04

## Épica 3 — Confirmación

### US-008 · Confirmar turno reservado
> Como **recepcionista**, quiero confirmar turnos reservados, para asegurar la asistencia.

- **Criterios de aceptación**
  - Un turno `reservado` pasa a `confirmado`; el paciente puede seguir cancelando hasta su inicio (RN-TU-05).
  - El cambio queda visible en la agenda e historial.
- **Reglas**: RN-TU-04

## Backlog (fuera de v1.0)

- US-101 Recordatorios automáticos por email/WhatsApp antes del turno.
- US-102 Cobro de señas/deuda con Mercado Pago.
- US-103 Ficha clínica y anamnesis.
- US-104 Notificaciones al profesional ante cancelaciones.