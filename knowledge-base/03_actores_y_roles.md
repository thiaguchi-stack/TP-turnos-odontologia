# Actores y Roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa |
|-------|-------------|-----------------|
| **Paciente** | Cliente de la clínica que reserva un turno online | Sin autenticación: entra a la página pública, elige profesional/fecha/hora, carga sus datos. Puede cancelar con un enlace/token de su turno |
| **Recepcionista / Admin** | Personal administrativo del consultorio | Con login: gestiona la agenda completa (turnos, profesionales, prestaciones, bloqueos), confirma y cancela turnos |
| **Odontólogo / Profesional** | Profesional de la clínica | Con login: ve su propia agenda (día/semana) y marca turnos como completados |

## RBAC — Matriz de permisos

| Recurso | Paciente (público) | Recepcionista/Admin | Odontólogo |
|---------|--------------------|---------------------|------------|
| Turnos online (reserva) | Crear, cancelar propio | — | — |
| Agenda (turnos) | - (solo franjas libres) | CRUD completo | Listar propios, marcar completado |
| Profesionales | Leer lista (para reservar) | CRUD | Leer |
| Prestaciones | Leer (para reservar) | CRUD | Leer |
| Bloqueos | - | CRUD | - |
| Usuarios del sistema | - | CRUD (admin) | - |

## Rutas públicas

- `/` — home con reserva online (selección de profesional, fecha, franja).
- `/turnos/online/disponibles` — consulta de franjas disponibles (API).
- `/turnos/online` — creación de reserva (API).
- `/turnos/online/cancelar/:token` — cancelación del paciente vía enlace (API).

Todo lo demás requiere autenticación JWT con rol `admin` o `odontologo`.