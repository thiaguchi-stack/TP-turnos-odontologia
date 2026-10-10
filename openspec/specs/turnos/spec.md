# turnos Specification

## Purpose

Garantiza la integridad de agenda al crear un turno: duración derivada de la
prestación, estado inicial `reservado` y ausencia de solapamientos por
profesional y por sillón/box, contra turnos y bloqueos existentes.

## Requirements

### Requirement: Creación con duración derivada y estado inicial reservado

El sistema SHALL crear un turno con `fecha_hora_fin` igual a `fecha_hora_inicio`
más la `duracion_minutos` de la prestación elegida, y con estado inicial
siempre `reservado`. La solicitud de creación SHALL admitir únicamente
`profesional_id`, `paciente_id`, `prestacion_id`, `sillon_id` y
`fecha_hora_inicio`; cualquier `fecha_hora_fin` o `estado` enviado SHALL ser
rechazado.

#### Scenario: Turno exitoso con duración derivada de la prestación

- **GIVEN** un profesional activo, un sillón activo y una prestación de 30 minutos, sin turnos ni bloqueos en esa franja
- **WHEN** se crea un turno del profesional en ese sillón para el 2026-11-05 09:00
- **THEN** la respuesta es 201 y el turno se persiste con `fecha_hora_fin` = 2026-11-05 09:30 y estado `reservado`

#### Scenario: Solicitud con campos prohibidos fecha_hora_fin o estado

- **GIVEN** datos de creación válidos que además incluyen `fecha_hora_fin` arbitraria y `estado` = "confirmado"
- **WHEN** se envía la solicitud de creación
- **THEN** la respuesta es 400 y no se crea ningún turno

### Requirement: Sin solapamiento con turnos del mismo profesional

Para un mismo `profesional_id`, el sistema SHALL rechazar la creación de un
turno cuyo intervalo `[fecha_hora_inicio, fecha_hora_fin)` intersecte el de un
turno existente no cancelado del mismo profesional, sin generar ningún registro
(RN-TU-01).

#### Scenario: Colisión por profesional con sillón distinto

- **GIVEN** un turno "reservado" del profesional P1 en el sillón S1 para [09:00, 09:30) del 2026-11-05
- **WHEN** se intenta crear un segundo turno de P1 en el sillón S2 (distinto) para las 09:15 de esa fecha
- **THEN** la respuesta es 409 indicando la colisión por profesional y no se crea ningún turno

### Requirement: Sin solapamiento con turnos del mismo sillón

Para un mismo `sillon_id`, el sistema SHALL rechazar la creación de un turno
cuyo intervalo `[fecha_hora_inicio, fecha_hora_fin)` intersecte el de un turno
existente no cancelado de cualquier otro profesional, sin generar ningún
registro (RN-TU-01, RN-PR-05).

#### Scenario: Colisión por sillón con profesional distinto

- **GIVEN** un turno "reservado" del profesional P1 en el sillón S1 para [09:00, 09:30) del 2026-11-05
- **WHEN** se intenta crear un turno del profesional P2 (distinto) en el sillón S1 para las 09:20 de esa fecha
- **THEN** la respuesta es 409 indicando la colisión por sillón y no se crea ningún turno

### Requirement: Sin solapamiento con bloqueos del profesional

El sistema SHALL rechazar la creación de un turno cuyo intervalo intersecte un
bloqueo del mismo profesional — con `sillon_id` nulo (libera todos los sillones)
o asignado al sillón del turno — sin generar ningún registro (RN-TU-01,
RN-PR-03).

#### Scenario: Colisión con bloqueo del profesional

- **GIVEN** un bloqueo del profesional P1 con `sillon_id` nulo para [15:00, 19:00) del 2026-11-05
- **WHEN** se intenta crear un turno de P1 en cualquier sillón para las 16:00 de esa fecha
- **THEN** la respuesta es 409 indicando la colisión con un bloqueo y no se crea ningún turno

#### Scenario: Bloqueo de otro profesional no afecta

- **GIVEN** un bloqueo del profesional P2 para [15:00, 19:00) del 2026-11-05
- **WHEN** se crea un turno del profesional P1 para las 16:00 de esa fecha en un sillón sin turnos
- **THEN** la respuesta es 201 y el turno se crea normalmente

### Requirement: Intervalos de agenda semiabiertos inicio fin

Los intervalos de agenda SHALL tratarse como semiabiertos `[inicio, fin)`: un
turno que inicia exactamente en `fecha_hora_fin` de otro SHALL permitirse, y un
turno cuyo intervalo empieza antes de esa hora SHALL rechazarse con 409
(RN-TU-01).

#### Scenario: Borde permitido — inicia exactamente cuando termina otro

- **GIVEN** un turno del profesional P1 en el sillón S1 para [09:00, 09:30) del 2026-11-05
- **WHEN** se crea un turno de P1 en S1 para las 09:30 de esa fecha
- **THEN** la respuesta es 201 porque [09:00, 09:30) y [09:30, fin) no se intersectan

#### Scenario: Borde rechazado — inicia 1 minuto antes del fin

- **GIVEN** un turno del profesional P1 en el sillón S1 para [09:00, 09:30) del 2026-11-05
- **WHEN** se intenta crear un turno de P1 en S1 para las 09:29 de esa fecha
- **THEN** la respuesta es 409 y no se crea ningún turno

### Requirement: Sin turnos en el pasado

El sistema SHALL rechazar con 400 la creación de un turno cuyo
`fecha_hora_inicio` sea anterior a la fecha y hora actuales (RN-TU-06).

#### Scenario: Turno en el pasado

- **GIVEN** la fecha y hora actuales
- **WHEN** se intenta crear un turno con `fecha_hora_inicio` en el pasado
- **THEN** la respuesta es 400 y no se crea ningún turno

### Requirement: Solo recursos activos admiten turnos nuevos

El sistema SHALL rechazar con 400 la creación de un turno si el profesional está
inactivo (RN-PR-01), si el sillón está inactivo o no existe (RN-TU-09), o si la
prestación está inactiva (RN-PR-02); en todos los casos sin generar ningún
registro.

#### Scenario: Profesional inactivo

- **GIVEN** un profesional con `activo` = false
- **WHEN** se intenta crear un turno para ese profesional
- **THEN** la respuesta es 400 y no se crea ningún turno

#### Scenario: Sillón inactivo

- **GIVEN** un sillón con `activo` = false
- **WHEN** se intenta crear un turno en ese sillón
- **THEN** la respuesta es 400 y no se crea ningún turno

#### Scenario: Prestación inactiva

- **GIVEN** una prestación con `activa` = false
- **WHEN** se intenta crear un turno con esa prestación
- **THEN** la respuesta es 400 y no se crea ningún turno

### Requirement: Los turnos cancelados liberan la agenda

El sistema SHALL permitir crear un turno cuyo intervalo intersecte el de un
turno existente en estado `cancelado`, porque la cancelación libera el horario
(RN-TU-05).

#### Scenario: Creación sobre un turno cancelado

- **GIVEN** un turno del profesional P1 en el sillón S1 para [09:00, 09:30) del 2026-11-05 en estado `cancelado`
- **WHEN** se crea un turno de P1 en S1 para las 09:10 de esa fecha
- **THEN** la respuesta es 201 y el turno se crea normalmente
