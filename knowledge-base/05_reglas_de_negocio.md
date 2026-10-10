# Reglas de Negocio

Convención: `RN-<AREA>-NN`. La implementación debe respetar estas reglas en la capa de servicios (no solo en UI).

## RN-AU — Autenticación y autorización

| ID | Regla |
|----|-------|
| RN-AU-01 | Las rutas de administración exigen JWT válido; el paciente reserva sin autenticarse (solo con datos de contacto + token de cancelación). |
| RN-AU-02 | Un usuario `odontologo` solo ve y modifica turnos del profesional asociado (`usuario.profesional_id`). |
| RN-AU-03 | Solo un usuario `admin` puede crear/editar profesionales, prestaciones, bloqueos, sillones y usuarios. |
| RN-AU-04 | Las contraseñas se guardan hasheadas (bcrypt/argon2); nunca en texto plano. |

## RN-TU — Turnos

| ID | Regla |
|----|-------|
| RN-TU-01 | **No solapamiento**: para un mismo profesional **ni para un mismo sillón/box** no pueden existir dos turnos (ni un turno y un bloqueo) con intervalos que se intersecten. Valida la capa de servicio en toda creación/reprogramación. |
| RN-TU-02 | La duración de un turno es `duracion_minutos` de su prestación; `fin = inicio + duración`. No se permite guardar duraciones arbitrarias. |
| RN-TU-03 | Un paciente no puede reservar sobre: horarios fuera de la agenda configurada del profesional, turnos existentes (del profesional o de su sillón), bloqueos, ni profesionales o sillones inactivos. |
| RN-TU-04 | Estados válidos: `reservado`, `confirmado`, `cancelado`, `completado`. Transiciones: `reservado → confirmado`, `reservado → cancelado`, `confirmado → cancelado`, `confirmado → completado`. |
| RN-TU-05 | La cancelación (admin o paciente con token) libera el horario: solo el rol admin cancela turnos ajenos; el paciente cancela únicamente con el `token_cancelacion` de su turno. |
| RN-TU-06 | Un turno pasado (`fin < ahora`) sin confirmar se puede marcar `completado` (si se atendió) o `cancelado`; no se pueden crear turnos en el pasado. |
| RN-TU-07 | El sistema muestra solo franjas disponibles: agenda semanal − turnos activos − bloqueos, con redondeo a la grilla de prestación y considerando la disponibilidad del sillón (RN-TU-01/09). |
| RN-TU-08 | La reprogramación solo reubica un turno en el mismo profesional (v1); se valida de nuevo contra RN-TU-01/03. |
| RN-TU-09 | Todo turno se asigna a un sillón/box activo (`sillon_id` not null → sillón con `activo=true`). Los turnos de ejemplo/seed respetan esta asignación. |

## RN-PR — Profesionales, prestaciones y bloqueos

| ID | Regla |
|----|-------|
| RN-PR-01 | Un profesional `inactivo` no recibe reservas online (se puede ocultar del selector público). |
| RN-PR-02 | Desactivar una prestación no elimina turnos históricos; impide nuevas reservas con ella. |
| RN-PR-03 | Un bloqueo impide turnos en su intervalo y se tiene en cuenta al calcular franjas disponibles. |
| RN-PR-04 | Al cambiar la duración de una prestación, solo afecta a turnos futuros (los pasados conservan sus horarios). |
| RN-PR-05 | La disponibilidad de un sillón es compartida: si dos profesionales usan el mismo sillón, la restricción por sillón de RN-TU-01 es la que impide el doble uso simultáneo. |

## RN-DATOS — Privacidad de datos de salud (Ley 25.326)

| ID | Regla |
|----|-------|
| RN-DATOS-01 | Los datos personales y de salud de los pacientes se tratan conforme a la Ley 25.326 (Argentina): finalidad determinada, consentimiento en la reserva, acceso solo a personal autorizado. |
| RN-DATOS-02 | No se expone información clínica en rutas públicas: la reserva online recibe únicamente datos de contacto; la ficha clínica es backlog v2. |
| RN-DATOS-03 | Los datos simulados (seed) no incluyen datos reales de pacientes. |