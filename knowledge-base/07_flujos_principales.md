# Flujos Principales

## Flujo 1 — Reserva online (paciente)

```
[Página pública] Elige profesional activo
        │
        ▼
Elige fecha → GET /turnos/online/disponibles
        │  (agenda semanal − turnos activos − bloqueos, por profesional y por sillón, RN-TU-07)
        ▼
Elige franja libre
        │  (se valida profesional + sillón: la franja solo se ofrece si hay sillón activo libre, RN-TU-01/09)
        ▼
Carga datos (nombre, apellido, DNI, teléfono, email?, obra social?)
        │  (validación + consentimiento Ley 25.326, RN-DATOS-01)
        ▼
POST /turnos/online  →  alta paciente (dedupe) + turno 'reservado'
        │  (valida solapamiento por profesional y por sillón, RN-TU-01)
        ▼
Éxito: resumen + enlace de cancelación (token)  |  Error: franja ocupada → reeligir
```

**Casos de error**
- Franja ya ocupada por otro usuario al confirmar → error 409 y se actualiza la grilla.
- Sillón ocupado en la franja elegida (p. ej. otro profesional lo usa en el mismo horario) → error 409; esa franja no se ofrece como disponible.
- Datos incompletos / teléfono inválido → error de validación con mensajes por campo.
- Profesional inactivo o fecha fuera de agenda → la franja no se muestra (RN-PR-01).

## Flujo 2 — Gestión de agenda (admin)

```
[Login] POST /auth/login → JWT (rol admin)
        │
        ▼
Vista agenda (profesional + día/semana) — GET /agenda/{profesional_id}/semana
        │
        ├─► Crear turno manual: paciente existente o nuevo → franja libre → elige sillón disponible → 'reservado'/'confirmado'
        ├─► Cancelar turno: motivo opcional → 'cancelado' (libera horario)
        ├─► Reprogramar: reubica (nueva franja + sillón) → revalida solapamiento por profesional y sillón (RN-TU-08)
        ├─► Confirmar turno: 'reservado' → 'confirmado'
        └─► Administrar: alta/edición de profesionales, prestaciones, bloqueos y sillones
```

**Casos de error**
- Solapamiento al crear/reprogramar → rechazo con franjas alternativas sugeridas.
- Sillón/box ocupado en la franja (compartido entre profesionales) → rechazo con sillones alternativos disponibles.
- Transición de estado inválida (ej. completado → confirmado) → error 400.

## Flujo 3 — Confirmación y cancelación

```
Confirmación:  turno 'reservado' --(admin)--> 'confirmado'
                                                    │
        ┌───────────────────────────────────────────┤
        ▼                                           ▼
Cancelación admin (US-005)                Cancelación paciente (US-003)
"cancelado" + motivo                      "cancelado" vía token del enlace
        │                                           │
        ▼                                           ▼
  Horario liberado (GRID)                  Horario liberado (GRID)
```

**Casos de error**
- Paciente intenta cancelar con token de otro turno o ya usado → 403/404.
- Cancelar un turno ya completado → error 400 (transición inválida, RN-TU-04).

## Diagrama de estados del Turno

```
        ┌─────────────────┐
        │    reservado    │──► confirmado ──► completado
        └───────┬─────────┘       ▲
                │                 │
                ▼                 │
            cancelado ◄───────────┘
```

- `reservado`: creado por paciente online o admin.
- `confirmado`: admin confirmó (US-008).
- `completado`: odontólogo marcó atención (US-007).
- `cancelado`: admin o paciente (token); terminal.