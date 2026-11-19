# user-auth Specification

## Purpose

Define el contrato observable de acceso del personal del consultorio: login con
JWT, identidad del usuario actual, autorización por rol y por profesional, y
protección contra credenciales inválidas, tokens vencidos y abuso de intentos,
sin exponer contraseñas ni bloquear la reserva pública.

## Requirements

### Requirement: Inicio de sesión válido entrega JWT con claims de identidad y rol

El sistema SHALL aceptar `POST /auth/login` con usuario y contraseña válidos y
SHALL responder 200 con un token Bearer cuyos claims incluyen `sub`, `rol`,
`profesional_id` y `exp` (RN-AU-01; `08_arquitectura_propuesta.md:11`). El token
SHALL corresponder al usuario autenticado y la respuesta SHALL omitir
`password_hash` (RN-AU-04).

#### Scenario: Login de admin con credenciales válidas

- **DADO** el usuario admin del seed con contraseña válida y `profesional_id` nulo
- **CUANDO** se envía `POST /auth/login` con ese usuario y contraseña
- **ENTONCES** la respuesta es 200, contiene `access_token` tipo `Bearer` y el JWT decodificado tiene `sub` igual al id del admin, `rol` = "admin", `profesional_id` nulo y `exp` posterior al momento actual, y la respuesta no contiene `password_hash`

#### Scenario: Login de odontólogo con credenciales válidas

- **DADO** un usuario odontólogo activo vinculado al profesional P1
- **CUANDO** se envía `POST /auth/login` con sus credenciales
- **ENTONCES** la respuesta es 200 y el JWT decodificado tiene `rol` = "odontologo" y `profesional_id` = P1, sin incluir `password_hash` en el cuerpo

### Requirement: Credenciales inválidas se rechazan con 401

El sistema SHALL responder 401 ante usuario inexistente o contraseña incorrecta,
sin entregar token y sin revelar cuál de los dos datos falló
(RN-AU-01, RN-AU-04).

#### Scenario: Contraseña incorrecta

- **DADO** un usuario existente
- **CUANDO** se envía `POST /auth/login` con una contraseña incorrecta
- **ENTONCES** la respuesta es 401, no contiene `access_token` y el mensaje no distingue entre usuario inexistente y contraseña incorrecta

### Requirement: Toda ruta privada exige JWT válido y expirado se rechaza

El sistema SHALL exigir un JWT válido en cada ruta privada; sin token, con firma
inválida o con `exp` vencido SHALL responder 401 (RN-AU-01;
`03_actores_y_roles.md:29`, `08_arquitectura_propuesta.md:41`).

#### Scenario: Acceso sin token

- **DADO** una ruta privada
- **CUANDO** se envía una solicitud sin header `Authorization`
- **ENTONCES** la respuesta es 401 y no se ejecuta la operación solicitada

#### Scenario: Token expirado

- **DADO** un JWT firmado correctamente con `exp` anterior al momento actual
- **CUANDO** se envía en el header `Authorization: Bearer` a una ruta privada
- **ENTONCES** la respuesta es 401 con indicación de que el token expiró y no se otorga acceso

### Requirement: El usuario actual se consulta sin exponer datos sensibles

El sistema SHALL devolver en `GET /auth/me` la identidad del usuario autenticado
y SHALL excluir `password_hash` del cuerpo de la respuesta (RN-AU-04;
`08_arquitectura_propuesta.md:42`).

#### Scenario: Consulta del usuario autenticado

- **DADO** un usuario odontólogo autenticado con token vigente
- **CUANDO** se envía `GET /auth/me` con ese token
- **ENTONCES** la respuesta es 200 con `id`, `email`, `rol` y `profesional_id` del usuario, y no contiene la clave `password_hash` ni el valor del hash

#### Scenario: La contraseña y el hash no se filtran en logs

- **DADO** un intento de login fallido y luego uno válido con `caplog` activo
- **CUANDO** se procesan ambas solicitudes
- **ENTONCES** los registros de log no contienen la contraseña en claro ni el valor de `password_hash`, y los códigos son 401 y 200 respectivamente (RN-AU-04)

### Requirement: RBAC limita la administración al rol admin

El sistema SHALL permitir la gestión de usuarios del sistema únicamente a
usuarios con `rol` = "admin" y SHALL responder 403 a cualquier otro rol
(RN-AU-03; `03_actores_y_roles.md:20`).

#### Scenario: Admin crea un usuario

- **DADO** un admin autenticado con token vigente
- **CUANDO** solicita crear un usuario odontólogo con `profesional_id` existente
- **ENTONCES** la respuesta es 201, el usuario queda persistido con contraseña hasheada y la respuesta no incluye `password_hash`

#### Scenario: Odontólogo intenta crear un usuario

- **DADO** un odontólogo autenticado con token vigente
- **CUANDO** intenta crear un usuario mediante la ruta de administración de usuarios
- **ENTONCES** la respuesta es 403, no se crea ningún usuario y la operación no se registra como exitosa

### Requirement: El odontólogo solo accede a turnos de su profesional

El sistema SHALL restringir a un usuario `odontologo` la consulta y
modificación de turnos a aquellos cuyo `profesional_id` coincide con el de su
usuario; cualquier otro profesional SHALL responder 403
(RN-AU-02; `AGENTS.md:100`).

#### Scenario: Odontólogo consulta sus propios turnos

- **DADO** un odontólogo vinculado al profesional P1 con token vigente
- **CUANDO** solicita el listado de turnos sin indicar otro profesional o indicando P1
- **ENTONCES** la respuesta es 200 y solo contiene turnos de P1

#### Scenario: Odontólogo intenta consultar turnos de otro profesional

- **DADO** un odontólogo vinculado al profesional P1 con token vigente y existencia del profesional P2
- **CUANDO** solicita turnos indicando `profesional_id` = P2
- **ENTONCES** la respuesta es 403 y no se devuelve ningún turno de P2

### Requirement: Rate limiting en login devuelve 429

El sistema SHALL limitar los intentos fallidos de login a 5 por ventana de 60
segundos por IP y email; al superar el límite SHALL responder 429
(`CHANGES.md:177`), sin entregar token.

#### Scenario: Sexto intento fallido dentro de la ventana

- **DADO** una misma IP y email con 5 intentos fallidos de login en los últimos 60 segundos
- **CUANDO** se realiza un sexto intento de login
- **ENTONCES** la respuesta es 429, no se verifica la contraseña ni se entrega `access_token`, con independencia de que la contraseña sea correcta

### Requirement: Las rutas públicas de reserva no exigen JWT

El sistema NO SHALL exigir JWT en las rutas públicas de reserva
(`/turnos/online/disponibles`, `/turnos/online`, `/turnos/online/cancelar/:token`);
la respuesta NO SHALL depender de un token del paciente
(RN-AU-01, RN-DATOS-02; `03_actores_y_roles.md:22-28`).

#### Scenario: Consulta pública de franjas sin token

- **DADO** un paciente sin cuenta ni token
- **CUANDO** consulta `GET /turnos/online/disponibles` sin header `Authorization`
- **ENTONCES** la respuesta no es 401: es 200 con las franjas libres correspondientes, sin exponer datos clínicos ni de terceros

#### Scenario: Reserva pública no permite elegir estado

- **DADO** un paciente sin cuenta ni token y datos de contacto válidos con consentimiento
- **CUANDO** envía `POST /turnos/online` sin `Authorization` e incluyendo `estado` = "confirmado"
- **ENTONCES** la respuesta es 400 por el campo prohibido, nunca 401 por falta de token, y no se crea un turno con estado distinto de `reservado` (RN-TU-04)
