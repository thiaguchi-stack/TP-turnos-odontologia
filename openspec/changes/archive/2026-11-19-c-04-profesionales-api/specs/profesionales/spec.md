# Spec Delta

## Purpose

Define el contrato observable del catálogo de profesionales del consultorio: la consulta pública de profesionales activos para la reserva online, la administración del catálogo por parte del admin y la visibilidad de la baja lógica de `activo`.

## ADDED Requirements

### Requirement: Listado público de profesionales activos

El sistema SHALL responder 200 a `GET /profesionales` sin exigir JWT y SHALL incluir únicamente profesionales con `activo=true`, para el selector de reserva (RN-PR-01; `knowledge-base/05_reglas_de_negocio.md:32`, `knowledge-base/03_actores_y_roles.md:17`).

#### Scenario: El listado público excluye profesionales inactivos

- **DADO** un profesional activo y otro inactivo persistidos con datos ficticios
- **CUANDO** se envía `GET /profesionales` sin header `Authorization`
- **ENTONCES** la respuesta es 200 y contiene solo el profesional activo, con `id`, `nombre`, `apellido`, `especialidad` y `activo=true`

#### Scenario: El paciente sin cuenta puede consultar el listado

- **DADO** un paciente sin cuenta ni token
- **CUANDO** envía `GET /profesionales` sin header `Authorization`
- **ENTONCES** la respuesta es 200 y no es 401, sin exponer datos de pacientes ni información clínica

### Requirement: Detalle público de un profesional activo

El sistema SHALL responder 200 a `GET /profesionales/{id}` sin JWT solo cuando el profesional existe y está activo; si no existe o está inactivo SHALL responder 404, sin exponer las bajas en la zona pública (RN-PR-01; `knowledge-base/05_reglas_de_negocio.md:32`).

#### Scenario: Detalle de profesional activo

- **DADO** un profesional activo con datos ficticios
- **CUANDO** se envía `GET /profesionales/{id}` sin header `Authorization`
- **ENTONCES** la respuesta es 200 con sus datos de catálogo y `activo=true`

#### Scenario: Detalle de profesional inactivo no se expone

- **DADO** un profesional con `activo=false`
- **CUANDO** se envía `GET /profesionales/{id}` sin header `Authorization`
- **ENTONCES** la respuesta es 404 y el cuerpo no revela los datos del profesional dado de baja

#### Scenario: Detalle de profesional inexistente

- **DADO** un id que no corresponde a ningún profesional
- **CUANDO** se envía `GET /profesionales/{id}`
- **ENTONCES** la respuesta es 404 y no se crea ni modifica ningún registro

### Requirement: Las respuestas de profesional no exponen datos sensibles

El sistema SHALL exponer exclusivamente `id`, `nombre`, `apellido`, `especialidad` y `activo` en las respuestas de profesional; NO SHALL incluir datos de pacientes, credenciales, `password_hash` ni información clínica (RN-AU-04, RN-DATOS-01/02; `knowledge-base/08_arquitectura_propuesta.md:42-45`).

#### Scenario: Campos exactos en la lectura del catálogo

- **DADO** un profesional persistido
- **CUANDO** se consulta el listado o el detalle
- **ENTONCES** cada elemento contiene solo `id`, `nombre`, `apellido`, `especialidad` y `activo`, sin `password_hash` ni claves de credenciales

#### Scenario: El catálogo público no filtra datos de terceros

- **DADO** turnos de pacientes y usuarios del sistema vinculados al consultorio
- **CUANDO** un paciente consulta `GET /profesionales`
- **ENTONCES** la respuesta no contiene datos de esos pacientes ni de esos usuarios

### Requirement: Alta de profesionales por admin

El sistema SHALL permitir a un usuario `admin` autenticado crear profesionales mediante `POST /profesionales`, respondiendo 201 con el registro persistido y `activo=true` por omisión (RN-AU-03, US-006; `knowledge-base/06_funcionalidades.md:59`).

#### Scenario: Admin crea un profesional activo por defecto

- **DADO** un admin autenticado con token vigente
- **CUANDO** envía `POST /profesionales` con `nombre`, `apellido` y `especialidad` válidos ficticios, sin indicar `activo`
- **ENTONCES** la respuesta es 201, el registro queda persistido con `activo=true` y el cuerpo no incluye campos prohibidos

#### Scenario: Nombre o apellido vacío se rechaza

- **DADO** un admin autenticado
- **CUANDO** envía `POST /profesionales` con `nombre` vacío o `apellido` compuesto solo por espacios
- **ENTONCES** la respuesta es 400, no se crea el registro y el mensaje indica el campo inválido

#### Scenario: Activo no booleano se rechaza

- **DADO** un admin autenticado
- **CUANDO** envía `POST /profesionales` con `activo` = `"si"` en lugar de un booleano
- **ENTONCES** la respuesta es 400 y no se persiste ningún profesional

#### Scenario: Campos no permitidos se rechazan

- **DADO** un admin autenticado
- **CUANDO** envía `POST /profesionales` con un campo extra como `id` o `estado`
- **ENTONCES** la respuesta es 400 por campo prohibido y no se crea el registro

### Requirement: Edición de profesionales por admin

El sistema SHALL permitir a un usuario `admin` autenticado editar `nombre`, `apellido`, `especialidad` y `activo` de un profesional existente mediante `PUT /profesionales/{id}`, respondiendo 200 con el estado actualizado; un id inexistente SHALL responder 404 (RN-AU-03, US-006; `knowledge-base/06_funcionalidades.md:59`).

#### Scenario: Admin edita datos y alterna activo

- **DADO** un profesional activo persistido y un admin autenticado
- **CUANDO** envía `PUT /profesionales/{id}` con `especialidad` modificada y `activo=false`
- **ENTONCES** la respuesta es 200 con los nuevos valores y el profesional queda inactivo sin borrarse

#### Scenario: Admin reactiva un profesional

- **DADO** un profesional inactivo persistido y un admin autenticado
- **CUANDO** envía `PUT /profesionales/{id}` con `activo=true`
- **ENTONCES** la respuesta es 200 con `activo=true` y el profesional vuelve a aparecer en el listado público

#### Scenario: Edición de profesional inexistente

- **DADO** un admin autenticado y un id inexistente
- **CUANDO** envía `PUT /profesionales/{id}` con datos válidos
- **ENTONCES** la respuesta es 404 y no se crea ningún profesional

#### Scenario: Edición sin datos válidos se rechaza

- **DADO** un admin autenticado
- **CUANDO** envía `PUT /profesionales/{id}` con un cuerpo vacío o con un campo extra
- **ENTONCES** la respuesta es 400 y el profesional permanece sin cambios

### Requirement: Baja lógica de profesionales por admin

El sistema SHALL responder 200 a `DELETE /profesionales/{id}` para un admin y SHALL fijar `activo=false` conservando el registro, incluso si el profesional tiene turnos o usuarios vinculados; un id inexistente SHALL responder 404 (RN-PR-01, RN-AU-03; `knowledge-base/04_modelo_de_datos.md:57`).

#### Scenario: Baja de profesional con turnos preserva el histórico

- **DADO** un profesional activo con turnos históricos y un admin autenticado
- **CUANDO** envía `DELETE /profesionales/{id}`
- **ENTONCES** la respuesta es 200 con `activo=false`, el profesional y sus turnos siguen persistidos y el profesional desaparece del listado público

#### Scenario: Baja de profesional sin turnos también es lógica

- **DADO** un profesional activo sin turnos y un admin autenticado
- **CUANDO** envía `DELETE /profesionales/{id}`
- **ENTONCES** la respuesta es 200 con `activo=false` y el registro no se elimina físicamente

#### Scenario: Baja repetida es idempotente

- **DADO** un profesional ya inactivo y un admin autenticado
- **CUANDO** envía `DELETE /profesionales/{id}` nuevamente
- **ENTONCES** la respuesta es 200 con `activo=false`, sin errores ni registros duplicados

#### Scenario: Baja de profesional inexistente

- **DADO** un admin autenticado y un id inexistente
- **CUANDO** envía `DELETE /profesionales/{id}`
- **ENTONCES** la respuesta es 404 y no se modifica ningún registro

### Requirement: RBAC y JWT en las rutas de administración del catálogo

El sistema SHALL exigir JWT válido y rol `admin` en `POST /profesionales`, `PUT /profesionales/{id}` y `DELETE /profesionales/{id}`; sin token o con token inválido/vencido SHALL responder 401 y con rol `odontologo` SHALL responder 403, sin mutar datos (RN-AU-01/03; `knowledge-base/03_actores_y_roles.md:11-20`, `knowledge-base/08_arquitectura_propuesta.md:41`).

#### Scenario: Sin token se rechaza con 401 en las tres rutas

- **DADO** un profesional existente y ningún header `Authorization`
- **CUANDO** se envían `POST /profesionales`, `PUT /profesionales/{id}` y `DELETE /profesionales/{id}`
- **ENTONCES** las tres respuestas son 401 y el catálogo permanece sin cambios

#### Scenario: Token vencido o firma inválida se rechaza con 401

- **DADO** un JWT con `exp` vencido o firmado con otra clave
- **CUANDO** se envía a una ruta de administración de profesionales
- **ENTONCES** la respuesta es 401 y no se ejecuta la operación

#### Scenario: Odontólogo no puede administrar el catálogo

- **DADO** un odontólogo autenticado con token vigente
- **CUANDO** intenta crear, editar y bajar profesionales mediante las rutas de administración
- **ENTONCES** las tres respuestas son 403, no se muta ningún profesional y se aplica la política de permisos de RN-AU-03
