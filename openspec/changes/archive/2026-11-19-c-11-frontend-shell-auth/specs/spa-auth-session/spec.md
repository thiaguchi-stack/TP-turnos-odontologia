# Spec Delta

## Purpose

Define el comportamiento observable de la SPA del consultorio respecto de la sesión del personal: zonas pública y protegida, ingreso con credenciales, identidad autoritativa, control de acceso por rol, expiración de sesión y formateo de fecha/hora en la zona local del consultorio.

## ADDED Requirements

### Requirement: La zona pública es accesible sin sesión

La SPA SHALL permitir recorrer la home y las pantallas públicas sin token ni datos de usuario. Las pantallas protegidas NO SHALL renderizarse para un visitante: la SPA SHALL redirigirlo al ingreso. La zona pública NO SHALL mostrar datos clínicos ni de terceros.

#### Scenario: Visitante accede a la home

- **DADO** un visitante sin sesión ni token
- **CUANDO** navega a `/`
- **ENTONCES** ve la pantalla pública sin pedir credenciales y sin datos clínicos ni de terceros

#### Scenario: Visitante intenta entrar a una pantalla protegida

- **DADO** un visitante sin sesión
- **CUANDO** navega directamente a una ruta protegida como `/agenda` o `/admin`
- **ENTONCES** la SPA lo redirige al ingreso y no renderiza ningún dato del consultorio

### Requirement: La zona protegida exige sesión vigente y rol habilitado

La SPA SHALL permitir el ingreso a las zonas de agenda y administración solo a usuarios autenticados con rol `admin` u `odontologo`. Un usuario con rol no habilitado SHALL ver la pantalla "Sin acceso" en español rioplatense. La navegación SHALL ocultar las acciones de administración al odontólogo.

#### Scenario: Admin accede a la zona de administración

- **DADO** un admin con sesión vigente y rol `admin`
- **CUANDO** navega a una ruta de administración
- **ENTONCES** la pantalla se renderiza y la navegación muestra las secciones de administración

#### Scenario: Odontólogo no ve ni accede a la administración

- **DADO** un odontólogo con sesión vigente y `profesional_id` asignado
- **CUANDO** abre la navegación e intenta entrar a una ruta de administración
- **ENTONCES** no ve enlaces de administración y la SPA muestra "Sin acceso" en lugar del contenido protegido

### Requirement: El ingreso usa el contrato OAuth2 del backend y muestra estados

La SPA SHALL enviar `POST /auth/login` como `application/x-www-form-urlencoded` con `username` y `password`, nunca como JSON, y SHALL mostrar un estado de carga mientras espera la respuesta. La respuesta SHALL contener `access_token` y `token_type: "Bearer"`; la SPA SHALL NO guardar la contraseña ni pedir `expires_in` ni datos de usuario en esa respuesta.

#### Scenario: Ingreso correcto de admin

- **DADO** un admin con credenciales válidas
- **CUANDO** completa el formulario de ingreso y envía
- **ENTONCES** se muestra el estado de carga, la petición viaja como formulario urlencoded, la SPA guarda el token y redirige a la zona del consultorio

#### Scenario: Credenciales inválidas

- **DADO** un usuario con contraseña incorrecta
- **CUANDO** envía el formulario de ingreso
- **ENTONCES** recibe 401, no guarda token, permanece en el ingreso y muestra un mensaje de error en español rioplatense sin revelar si falló el usuario o la contraseña

#### Scenario: Demasiados intentos fallidos

- **DADO** un backend que responde 429 por exceso de intentos
- **CUANDO** el usuario intenta ingresar
- **ENTONCES** la SPA muestra el mensaje de error devuelto y no guarda token ni habilita la zona protegida

### Requirement: La identidad se hidrata desde el backend y no desde el JWT

Luego de un ingreso correcto y al recargar la aplicación con un token persistido, la SPA SHALL consultar `GET /auth/me` y SHALL tomar de esa respuesta el `id`, `email`, `rol` y `profesional_id` de la sesión. La SPA NO SHALL usar claims decodificados en el cliente como fuente de verdad de la identidad.

#### Scenario: Recarga con token vigente

- **DADO** un odontólogo con token vigente persistido en la pestaña
- **CUANDO** recarga la aplicación
- **ENTONCES** la SPA consulta `/auth/me`, guarda `id`, `email`, `rol` y `profesional_id` de esa respuesta y restaura la navegación correspondiente al rol

#### Scenario: Token rechazado al hidratar

- **DADO** un token vencido o inválido persistido en la pestaña
- **CUANDO** la SPA intenta hidratar la sesión y `/auth/me` responde 401
- **ENTONCES** descarta el token, deja la sesión vacía y redirige al ingreso sin mostrar datos del consultorio

### Requirement: La sesión persiste solo durante la pestaña

La SPA SHALL persistir el token en el almacenamiento de la sesión de la pestaña, de modo que sobreviva a recargas de esa pestaña pero NO SHALL persistirlo en `localStorage` ni entre pestañas nuevas. El cierre de sesión SHALL limpiar token e identidad y llevar al visitante a la zona pública.

#### Scenario: Recarga dentro de la misma pestaña

- **DADO** un admin que ingresó correctamente
- **CUANDO** recarga la misma pestaña
- **ENTONCES** conserva la sesión y vuelve a hidratar la identidad desde `/auth/me`

#### Scenario: Cierre explícito de sesión

- **DADO** un odontólogo con sesión vigente
- **CUANDO** cierra sesión
- **ENTONCES** se borran token e identidad, la navegación vuelve a la zona pública y una nueva visita a una ruta protegida redirige al ingreso

### Requirement: Todo acceso privado pasa por el wrapper con JWT y errores tipados

La SPA SHALL adjuntar el token como `Authorization: Bearer` en toda petición a una ruta privada y NO SHALL adjuntarlo en las públicas. El wrapper HTTP SHALL exponer el código de estado y un mensaje leído de `detalle` o `detail`, según venga en la respuesta (401/403/429 y validaciones 400). Ante un 401 SHALL cerrar la sesión y redirigir al ingreso.

#### Scenario: Petición privada con token

- **DADO** un admin con sesión vigente
- **CUANDO** la SPA consulta una ruta privada de profesionales o prestaciones
- **ENTONCES** la petición incluye el header `Authorization: Bearer <token>` y la respuesta se entrega al llamador con su `status`

#### Scenario: Petición pública sin token

- **DADO** un visitante sin sesión
- **CUANDO** la SPA consulta una ruta pública
- **ENTONCES** la petición no incluye header `Authorization` y el visitante no es redirigido al ingreso

#### Scenario: Expiración de sesión durante una petición

- **DADO** un usuario con token vencido que intenta una petición privada
- **CUANDO** el backend responde 401 con cuerpo `{"detalle": ...}` o `{"detail": ...}`
- **ENTONCES** el wrapper expone el `status` 401 y el mensaje correspondiente, cierra la sesión, borra el token y redirige al ingreso

### Requirement: Las fecha y hora se muestran en la zona del consultorio

Toda fecha u hora visible en la SPA SHALL formatearse en español rioplatense con la zona horaria `America/Argentina/Buenos_Aires` mediante la utilidad compartida existente. Las pantallas NO SHALL implementar formateos propios ni duplicar esa utilidad.

#### Scenario: Fecha mostrada en una pantalla del cascarón

- **DADO** una pantalla del cascarón que muestra la fecha actual
- **CUANDO** se renderiza en una máquina configurada en otra zona horaria
- **ENTONCES** la fecha se muestra en español con la zona `America/Argentina/Buenos_Aires` usando la utilidad compartida, sin lógica de formateo duplicada
