# Modelo de Datos

## Dominios

- **Personas**: pacientes y profesionales de la clínica.
- **Catálogos**: prestaciones (con duración variable).
- **Agenda**: turnos y bloqueos por profesional, con turnos asignados a un sillón/box del consultorio.
- **Acceso**: usuarios del sistema (admin/odontólogo).

## ERD

```
Usuario ──┐
          │ (1:1, opcional)
Profesional ◄──┐
   id           │ profesional_id
                │
Prestacion ◄────┤
   id           │ prestacion_id
                │
Sillon ◄────────┤
   id           │ sillon_id
   nombre       │
   activo       │
Turno ──────────┤
   id           │ profesional_id (FK)
   profesional_id│ paciente_id (FK)
   paciente_id   │ prestacion_id (FK)
   prestacion_id │ sillon_id (FK → Sillon)
Bloqueo          │
   id            │ profesional_id (FK)
   profesional_id│ sillon_id (FK → Sillon, nullable)
   sillon_id     │
Paciente ────────┘
   id
```

## Entidades

### Usuario
| Atributo | Tipo | Restricciones |
|----------|------|---------------|
| id | PK | autoincremental |
| email | str | único, not null |
| password_hash | str | not null (hash, nunca texto plano) |
| rol | enum | `admin` \| `odontologo`, not null |
| profesional_id | FK → Profesional | nullable; si rol = odontologo, apunta al profesional asociado |
| activo | bool | default true |

### Profesional
| Atributo | Tipo | Restricciones |
|----------|------|---------------|
| id | PK | autoincremental |
| nombre | str | not null |
| apellido | str | not null |
| especialidad | str | ej. Ortodoncia, Endodoncia, Cirugía |
| activo | bool | default true; los inactivos no reciben reservas |

### Paciente
| Atributo | Tipo | Restricciones |
|----------|------|---------------|
| id | PK | autoincremental |
| nombre | str | not null |
| apellido | str | not null |
| dni | str | not null (se deduplica por dni + teléfono) |
| telefono | str | not null (contacto principal en v1) |
| email | str | nullable (contacto alternativo) |
| obsocial | str | nullable (obra social, informativa en v1 — sin integración) |
| creado_en | datetime | audit |

### Prestacion
| Atributo | Tipo | Restricciones |
|----------|------|---------------|
| id | PK | autoincremental |
| nombre | str | not null, ej. "Limpieza", "Obturación", "Extracción" |
| duracion_minutos | int | not null, > 0 (la duración del turno se deriva de aquí) |
| activa | bool | default true |

### Sillon
| Atributo | Tipo | Restricciones |
|----------|------|---------------|
| id | PK | autoincremental |
| nombre | str | not null, ej. "Sillón 1", "Box 2" (nombre único en la práctica) |
| activo | bool | default true; los inactivos no reciben turnos nuevos |

Recurso físico del consultorio (no es sucursal ni pertenece a un profesional en exclusividad): varios profesionales pueden compartir un sillón, y por eso la disponibilidad se valida por sillón además de por profesional (RN-TU-01, RN-PR-05).

### Turno
| Atributo | Tipo | Restricciones |
|----------|------|---------------|
| id | PK | autoincremental |
| profesional_id | FK → Profesional | not null |
| paciente_id | FK → Paciente | not null |
| prestacion_id | FK → Prestacion | not null |
| sillon_id | FK → Sillon | not null (sillón activo donde se atiende; se asigna al crear/reprogramar, RN-TU-09) |
| fecha_hora_inicio | datetime | not null |
| fecha_hora_fin | datetime | not null (= inicio + duración prestación) |
| estado | enum | `reservado` \| `confirmado` \| `cancelado` \| `completado`, default `reservado` |
| token_cancelacion | str | único; permite al paciente cancelar sin login |
| creado_por | FK → Usuario (nullable) | null = reserva online del paciente |
| creado_en | datetime | audit |
| cancelado_en | datetime | nullable |
| motivo_cancelacion | str | nullable |

### Bloqueo
| Atributo | Tipo | Restricciones |
|----------|------|---------------|
| id | PK | autoincremental |
| profesional_id | FK → Profesional | not null |
| sillon_id | FK → Sillon | nullable; si es null, el bloqueo libera al profesional en cualquier sillón |
| fecha_hora_inicio | datetime | not null |
| fecha_hora_fin | datetime | not null |
| motivo | str | nullable, ej. "Vacaciones", "Congreso" |

## Restricciones clave (integridad de agenda)

- **Sin solapamiento**: para un mismo `profesional_id` **ni para un mismo `sillon_id`** no pueden existir dos turnos (ni un turno y un bloqueo) cuyos intervalos `[inicio, fin)` se intersecten. Se valida a nivel servicio y, en Postgres, con exclusión de rango (opcional).
- **Sillón obligatorio en el turno**: `sillon_id` es not null porque todo turno ocupa un espacio físico concreto del consultorio; hacerlo nullable obligaría a la capa de servicio a inferir el sillón y permitiría turnos "en el aire". En el bloqueo sí es null (un bloqueo de agenda personal libera al profesional en todos los sillones).
- **Duración**: `fecha_hora_fin = fecha_hora_inicio + duracion_minutos(prestacion)`. Nunca se guarda una duración distinta a la de la prestación.
- **Estado**: transiciones válidas: `reservado → confirmado`, `reservado → cancelado`, `confirmado → cancelado`, `confirmado → completado`. Un turno cancelado no vuelve a activarse.

## Seed data (datos simulados)

- 3 profesionales (con especialidades distintas; 1 con usuario `odontologo`).
- 1 usuario admin (email `admin@clinica.local`).
- 4-5 prestaciones con duraciones típicas (Limpieza 30, Obturación 45, Extracción 60, Consulta 20, Ortodoncia ajuste 30).
- 3 sillones/boxes: "Sillón 1", "Sillón 2", "Box 3" (todos `activo=true`).
- Agenda semanal configurada (turnos de ejemplo en franjas fijas, cada uno con sillón asignado — respetando RN-TU-01 y RN-TU-09) para que la UI se vea poblada al entregar el TP.
- Horario de atención por profesional (config semanal simple, p.ej. días hábiles 9-13 y 15-19).