# prestaciones-api Specification

## Purpose

Define el contrato observable del catálogo de prestaciones: alta, edición y
desactivación por personal administrativo, listado público de las activas,
duración siempre válida y reglas que impiden borrar o reprogramar turnos ya
creados al modificar el catálogo.

## Requirements

### Requirement: Alta de prestación con duración válida

El sistema SHALL crear una prestación mediante `POST /prestaciones` solo si
`duracion_minutos` es un entero mayor que cero, respondiendo 201 con `id`,
`nombre`, `duracion_minutos` y `activa` (RN-AU-03;
`04_modelo_de_datos.md:71-77`, `05_reglas_de_negocio.md:11`). Una duración no
positiva o un campo no permitido SHALL rechazarse con 400 sin persistir nada.

#### Scenario: Admin crea una prestación con duración válida

- **DADO** un admin autenticado con token vigente
- **CUANDO** envía `POST /prestaciones` con `nombre` = "Limpieza" y `duracion_minutos` = 30
- **ENTONCES** la respuesta es 201, la prestación queda persistida con `activa` = true y el cuerpo no contiene datos de pacientes ni información clínica

#### Scenario: Duración cero rechazada

- **DADO** un admin autenticado
- **CUANDO** envía `POST /prestaciones` con `duracion_minutos` = 0
- **ENTONCES** la respuesta es 400, no se crea la prestación y el mensaje indica que la duración debe ser mayor que cero

#### Scenario: Duración negativa rechazada

- **DADO** un admin autenticado
- **CUANDO** envía `POST /prestaciones` con `duracion_minutos` = -5
- **ENTONCES** la respuesta es 400 y no se crea ninguna prestación

#### Scenario: Campo no permitido en el alta

- **DADO** un admin autenticado y datos de alta válidos
- **CUANDO** envía `POST /prestaciones` incluyendo un campo extra como `estado` = "activa"
- **ENTONCES** la respuesta es 400 y no se crea la prestación

### Requirement: Listado público solo de prestaciones activas

El sistema SHALL responder `GET /prestaciones` sin exigir JWT y SHALL incluir
únicamente las prestaciones con `activa` = true, para el selector de reserva
(RN-PR-02, RN-AU-01; `03_actores_y_roles.md:18,22-28`,
`05_reglas_de_negocio.md:33`). La respuesta SHALL exponer solo `id`, `nombre`,
`duracion_minutos` y `activa` (RN-DATOS-02; `05_reglas_de_negocio.md:43`).

#### Scenario: Paciente sin token consulta el catálogo

- **DADO** un paciente sin cuenta ni token y dos prestaciones activas
- **CUANDO** envía `GET /prestaciones` sin header `Authorization`
- **ENTONCES** la respuesta es 200 (nunca 401) y contiene solo esas dos prestaciones activas

#### Scenario: Prestación inactiva excluida del listado

- **DADO** una prestación activa y otra con `activa` = false
- **CUANDO** se consulta `GET /prestaciones` sin token
- **ENTONCES** la respuesta no incluye la prestación inactiva

#### Scenario: El listado no expone datos ajenos al catálogo

- **DADO** prestaciones activas en el catálogo
- **CUANDO** un paciente consulta `GET /prestaciones`
- **ENTONCES** cada item tiene solo `id`, `nombre`, `duracion_minutos` y `activa`, sin datos de pacientes, turnos ni contraseñas

### Requirement: Las escrituras del catálogo exigen JWT de admin

El sistema SHALL exigir un JWT válido en `POST /prestaciones` y en
`PUT /prestaciones/{id}` y SHALL permitir ambas operaciones solo a usuarios con
`rol` = "admin": sin token → 401, con rol distinto → 403
(RN-AU-01/03; `03_actores_y_roles.md:11-20`,
`08_arquitectura_propuesta.md:41`).

#### Scenario: Alta sin token

- **DADO** ninguna credencial
- **CUANDO** se envía `POST /prestaciones` sin header `Authorization`
- **ENTONCES** la respuesta es 401 y no se crea ninguna prestación

#### Scenario: Edición sin token

- **DADO** una prestación existente y ninguna credencial
- **CUANDO** se envía `PUT /prestaciones/{id}` sin header `Authorization`
- **ENTONCES** la respuesta es 401 y la prestación queda sin cambios

#### Scenario: Odontólogo intenta crear una prestación

- **DADO** un odontólogo autenticado con token vigente
- **CUANDO** envía `POST /prestaciones` con datos válidos
- **ENTONCES** la respuesta es 403 con un mensaje en español rioplatense y no se crea ninguna prestación

#### Scenario: Odontólogo intenta editar una prestación

- **DADO** un odontólogo autenticado y una prestación existente
- **CUANDO** envía `PUT /prestaciones/{id}` con datos válidos
- **ENTONCES** la respuesta es 403 y la prestación conserva sus valores originales

### Requirement: Edición de prestación por admin

El sistema SHALL permitir a un admin actualizar `nombre`,
`duracion_minutos` y `activa` de una prestación existente mediante
`PUT /prestaciones/{id}`, respondiendo 200 con el estado final. Un id
inexistente SHALL responder 404 y una duración no positiva SHALL responder 400,
sin modificar ningún registro.

#### Scenario: Admin edita nombre y duración

- **DADO** un admin autenticado y una prestación de 30 minutos
- **CUANDO** envía `PUT /prestaciones/{id}` con `nombre` = "Limpieza profunda" y `duracion_minutos` = 45
- **ENTONCES** la respuesta es 200 y la prestación queda persistida con los nuevos valores

#### Scenario: Edición de prestación inexistente

- **DADO** un admin autenticado y un id que no corresponde a ninguna prestación
- **CUANDO** envía `PUT /prestaciones/{id}` con datos válidos
- **ENTONCES** la respuesta es 404 y no se crea ninguna prestación

#### Scenario: Edición con duración inválida

- **DADO** un admin autenticado y una prestación de 30 minutos
- **CUANDO** envía `PUT /prestaciones/{id}` con `duracion_minutos` = 0
- **ENTONCES** la respuesta es 400 y la prestación conserva su duración original de 30 minutos

### Requirement: Desactivar una prestación no elimina turnos históricos

El sistema SHALL hacer que `PUT /prestaciones/{id}` con `activa` = false retire
la prestación del listado público e impida reservas nuevas con ella, sin borrar
ni alterar turnos ya creados (RN-PR-02; `05_reglas_de_negocio.md:33`,
`openspec/specs/turnos/spec.md:126-130`).

#### Scenario: Baja con turno histórico asociado

- **DADO** un admin autenticado, una prestación activa con un turno ya creado y su `fecha_hora_fin` original
- **CUANDO** desactiva la prestación mediante `PUT /prestaciones/{id}` con `activa` = false
- **ENTONCES** la respuesta es 200, el turno sigue persistido con su `fecha_hora_fin` original y la prestación no aparece en `GET /prestaciones`

#### Scenario: Prestación inactiva rechaza turnos nuevos

- **DADO** una prestación desactivada y un profesional y sillón activos
- **CUANDO** se intenta crear un turno con esa prestación
- **ENTONCES** la respuesta es 400 con un mensaje que indica que la prestación está inactiva y no se crea el turno

#### Scenario: Reactivación vuelve a publicar la prestación

- **DADO** una prestación desactivada que no aparece en el listado público
- **CUANDO** un admin la reactiva mediante `PUT /prestaciones/{id}` con `activa` = true
- **ENTONCES** la respuesta es 200 y la prestación vuelve a incluirse en `GET /prestaciones`

### Requirement: Cambio de duración sin efecto retroactivo

El sistema SHALL aplicar una nueva `duracion_minutos` solo a los turnos que se
creen después del cambio; los turnos ya persistidos SHALL conservar la
`fecha_hora_fin` calculada con la duración vigente al crearlos (RN-PR-04,
RN-TU-02; `05_reglas_de_negocio.md:19,35`,
`04_modelo_de_datos.md:119`).

#### Scenario: Turno ya creado conserva su horario

- **DADO** un turno creado con una prestación de 30 minutos cuya duración se cambia luego a 60
- **CUANDO** se consulta el turno existente tras el cambio de duración
- **ENTONCES** su `fecha_hora_fin` sigue siendo la original calculada con 30 minutos

#### Scenario: Turno nuevo usa la duración actualizada

- **DADO** una prestación cuya duración pasó de 30 a 60 minutos
- **CUANDO** se crea un turno nuevo con esa prestación
- **ENTONCES** su `fecha_hora_fin` se deriva con 60 minutos, sin que el cliente pueda enviar una duración propia
