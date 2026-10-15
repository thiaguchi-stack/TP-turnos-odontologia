# Spec Delta

## Purpose

Garantiza la integridad del modelo de datos persistido del consultorio: unicidades de personas y usuarios, enums y defaults de estado/rol, auditoría de creación, vínculos referenciales opcional usuario–profesional, configuración semanal de horarios (SU-03) y un seed mínimo idempotente con datos ficticios.

## ADDED Requirements

### Requirement: Unicidad de email de usuario

El sistema SHALL rechazar la persistencia de dos usuarios con el mismo `email`, garantizando un único registro por dirección de email.

#### Scenario: Email duplicado rechazado

- **WHEN** se persiste un segundo usuario con un `email` ya existente
- **THEN** la operación falla con error de integridad y no se crea el registro

### Requirement: Unicidad de paciente por dni y teléfono

El sistema SHALL rechazar la persistencia de un paciente cuya combinación de `dni` y `telefono` ya exista, para deduplicar personas (KB §Paciente).

#### Scenario: Paciente duplicado por dni y teléfono

- **WHEN** se persiste un paciente con mismo `dni` y `telefono` que uno existente
- **THEN** la operación falla con error de integridad y no se crea el registro

#### Scenario: Mismo dni con teléfono distinto permitido

- **WHEN** se persiste un paciente con `dni` ya usado pero `telefono` distinto
- **THEN** el registro se crea normalmente

### Requirement: Token de cancelación único

El sistema SHALL garantizar que `token_cancelacion` sea único entre turnos; dos turnos no SHALL poder compartir el mismo token, y la ausencia de token (nulo) SHALL permitirse.

#### Scenario: Token duplicado rechazado

- **WHEN** se persiste un turno cuyo `token_cancelacion` coincide con el de otro turno
- **THEN** la operación falla con error de integridad y no se crea el registro

### Requirement: Enums cerrados de estado y rol con defaults

El sistema SHALL persistir `estado` de turno únicamente con los valores `reservado`, `confirmado`, `cancelado` o `completado` (default `reservado` al crear sin indicar estado), y `rol` de usuario únicamente con `admin` u `odontologo`; cualquier otro valor SHALL ser rechazado.

#### Scenario: Estado por defecto reservado

- **WHEN** se persiste un turno sin indicar estado
- **THEN** el registro queda con estado `reservado`

#### Scenario: Estado fuera del enum rechazado

- **WHEN** se intenta persistir un turno con estado `"reprogramado"`
- **THEN** la operación falla y no se crea el registro

#### Scenario: Rol fuera del enum rechazado

- **WHEN** se intenta persistir un usuario con rol `"superadmin"`
- **THEN** la operación falla y no se crea el registro

### Requirement: Contraseña persistida solo como hash

El sistema SHALL persistir las contraseñas únicamente como hash irreversible: el valor almacenado en `password_hash` SHALL ser distinto de la contraseña en claro (RN-AU-04).

#### Scenario: Hash del admin tras el seed

- **WHEN** se ejecuta el seed que crea el usuario admin
- **THEN** el `password_hash` almacenado difiere de la contraseña en claro y no la contiene

### Requirement: Auditoría de creación automática

El sistema SHALL registrar automáticamente `creado_en` al persistir usuarios, pacientes y turnos, sin que el cliente deba enviarlo.

#### Scenario: creado_en se llena solo

- **WHEN** se persiste un paciente sin enviar `creado_en`
- **THEN** el registro tiene `creado_en` con la fecha y hora actuales

### Requirement: Vínculo opcional usuario–profesional con integridad referencial

El sistema SHALL permitir usuarios con `profesional_id` nulo (rol admin) y usuarios vinculados a un profesional existente; SHALL rechazar cualquier `profesional_id` que no corresponda a un profesional persistido.

#### Scenario: Usuario admin sin profesional

- **WHEN** se persiste un usuario rol `admin` con `profesional_id` nulo
- **THEN** el registro se crea correctamente

#### Scenario: Referencia a profesional inexistente

- **WHEN** se persiste un usuario con `profesional_id` inexistente
- **THEN** la operación falla con error de integridad y no se crea el registro

### Requirement: Horario de atención semanal por profesional

El sistema SHALL persistir la configuración de horarios semanales fijos por profesional (día de la semana, hora de inicio y hora de fin) con integridad referencial al profesional, y SHALL rechazar intervalos cuya hora final no sea posterior a la de inicio (SU-03).

#### Scenario: Horario semanal válido

- **WHEN** se persiste un horario lunes 09:00–13:00 para un profesional existente
- **THEN** el registro se guarda asociado a ese profesional

#### Scenario: Intervalo invertido rechazado

- **WHEN** se persiste un horario con `hora_fin` menor o igual a `hora_inicio`
- **THEN** la operación falla y no se crea el registro

### Requirement: Seed mínimo idempotente con datos ficticios

El sistema SHALL proveer un seed que al ejecutarse garantice la existencia de al menos un usuario admin, un profesional activo y un usuario odontólogo vinculado a ese profesional; ejecutarlo repetidamente NO SHALL duplicar registros y sus datos SHALL ser siempre ficticios (RN-DATOS-03).

#### Scenario: Seed ejecutado dos veces

- **WHEN** se ejecuta el seed en una base ya sembrada
- **THEN** no se crean registros duplicados y los usuarios/profesionales existentes se conservan

#### Scenario: Entidades mínimas presentes tras el seed

- **WHEN** se ejecuta el seed en una base vacía
- **THEN** existe un usuario admin, un profesional activo y un usuario odontólogo con `profesional_id` apuntando a ese profesional
