# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **TP-turnos-odontologia**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Árbol de dependencias

```
C-01 foundation-setup
  └── C-02 core-models
        └── C-03 auth-jwt-rbac              ← desbloquea backend + frontend protegido
              │
              ├── C-04 profesionales-api
              │     └── C-06 bloqueos-api
              │           └── C-07 agenda-engine   ← núcleo del dominio (franjas + solapamiento)
              │                 ├── C-08 turnos-agenda-api
              │                 │     └── C-10 turnos-estados-api
              │                 └── C-09 reserva-online-api
              │                       └── C-16 seed-demo
              │
              ├── C-05 prestaciones-api ──┐
              │                          └── (junto a C-04, C-06 → C-07)
              │
              └── C-11 frontend-shell-auth
                    ├── C-12 frontend-reserva-publica     (← C-09 + C-11)
                    ├── C-13 frontend-agenda-admin        (← C-08 + C-10 + C-11)
                    ├── C-14 frontend-catalogos-admin     (← C-04 + C-05 + C-06 + C-11)
                    └── C-15 frontend-odontologo          (← C-10 + C-11)

C-08 + C-09 ✓  → C-17 hardening-privacidad
C-11 + C-12 + C-13 + C-14 + C-15 + C-16 ✓  → C-18 aceptacion-e2e-entrega
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse en paralelo.

```
GATE 0: ninguna
  → C-01 foundation-setup                         [solo]

GATE 1: C-01 ✓
  → C-02 core-models                              [solo]

GATE 2: C-02 ✓
  → C-03 auth-jwt-rbac                            [solo]

GATE 3: C-03 ✓                                    ← PRIMER FORK (3 paralelos)
  → C-04 profesionales-api                        [Agente A]
  → C-05 prestaciones-api                         [Agente B]
  → C-11 frontend-shell-auth                      [Agente C]

GATE 4: C-04 ✓
  → C-06 bloqueos-api                             [Agente A]

GATE 5: C-04 + C-05 + C-06 ✓                      ← FORK (2 paralelos)
  → C-07 agenda-engine                            [Agente A]
  → (C-11 puede seguir/cerrarse)                  [Agente C]

GATE 6: C-07 ✓
  → C-08 turnos-agenda-api                        [Agente A]
  → C-09 reserva-online-api                       [Agente B]

GATE 7: C-08 ✓
  → C-10 turnos-estados-api                       [Agente A]

GATE 8: C-09 + C-11 ✓
  → C-12 frontend-reserva-publica                 [Agente C]
  → C-16 seed-demo                                [Agente B]

GATE 9: C-08 + C-10 + C-11 ✓                      ← FORK (2 paralelos)
  → C-13 frontend-agenda-admin                    [Agente C]
  → C-15 frontend-odontologo                      [Agente C — secuencial con C-13 si hay un solo frontend]

GATE 10: C-04 + C-05 + C-06 + C-11 ✓
  → C-14 frontend-catalogos-admin                 [Agente C]

GATE 11: C-09 + C-10 ✓
  → C-17 hardening-privacidad                     [Agente A]

GATE 12: C-11 + C-12 + C-13 + C-14 + C-15 + C-16 ✓
  → C-18 aceptacion-e2e-entrega                   [Agente A si A ✓ | si no, B]
```

### Camino crítico (10 changes — mínimo irreducible)

```
C-01 → C-02 → C-03 → C-04 → C-06 → C-07 → C-08 → C-10 → C-13 → C-18
```

> El camino de la reserva online (`C-01 → C-02 → C-03 → C-04 → C-06 → C-07 → C-09 → C-11 → C-12 → C-18`) tiene también longitud 10; cualquiera de los dos puede citarse como cierre del MVP. El demo end-to-end se logra cuando ambos tramos convergen en `C-18`.

### Plan óptimo con 3 agentes

```
Paso │ Agente A (Backend Core)   │ Agente B (Backend Aux)     │ Agente C (Frontend)
─────┼───────────────────────────┼────────────────────────────┼────────────────────────────
  1  │ C-01 foundation-setup     │            —               │            —
  2  │ C-02 core-models          │            —               │            —
  3  │ C-03 auth-jwt-rbac        │            —               │            —
  4  │ C-04 profesionales-api    │ C-05 prestaciones-api      │ C-11 frontend-shell-auth
  5  │ C-06 bloqueos-api         │            —               │            —
  6  │ C-07 agenda-engine        │            —               │            —
  7  │ C-08 turnos-agenda-api    │ C-09 reserva-online-api    │            —
  8  │ C-10 turnos-estados-api   │ C-16 seed-demo             │ C-12 frontend-reserva-publica
  9  │ C-17 hardening-privacidad │            —               │ C-13 frontend-agenda-admin
 10  │            —              │            —               │ C-15 frontend-odontologo
 11  │            —              │            —               │ C-14 frontend-catalogos-admin
 12  │ C-18 aceptacion-e2e       │            —               │            —
```

> El frontend (Agente C) es el cuello de botella (5 changes secuenciales); si hay un 4º agente disponible conviene asignarlo a las páginas de admin (`C-13/C-14`).

---

## FASE 0 — Cimientos

### [C-01] `foundation-setup`
- **Estado**: `[x]` implementado (archive pendiente)
- **Scope**: Scaffolding del monorepo + infraestructura base
  - Estructura: `backend/app/{core,models,schemas,services,routers,db}`, `backend/tests/`, `frontend/src/{pages,components,services,shared}`
  - `backend/`: app FastAPI mínima con `GET /api/health`, `core/config.py` (Pydantic Settings), `core/security.py` stub, CORS desde `CORS_ORIGINS`
  - `frontend/`: Vite + React 18 + TypeScript, react-router, `vite.config.ts` con proxy `/api → backend`; `services/api.ts` (fetch wrapper base)
  - `.env.example` en ambos sub-proyectos: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `TOKEN_EXPIRE_MIN`, `VITE_API_URL`
  - `pyproject.toml` (FastAPI, SQLAlchemy 2, Pydantic 2, pytest, httpx, ruff) y `package.json` (ESLint/Prettier)
  - Scripts de arranque documentados (`uvicorn app.main:app --reload`, `npm run dev`)
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Propósito del sistema
  - `knowledge-base/02_descripcion_general.md` §Stack tecnológico
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios, §Variables de entorno

---

### [C-02] `core-models`
- **Estado**: `[ ]` pendiente
- **Scope**: Modelos de dominio + migración inicial + seed mínimo
  - Modelos SQLAlchemy 2.x (`Mapped`/`mapped_column`): `Usuario`, `Profesional`, `Paciente`, `Prestacion`, `Turno`, `Bloqueo`
  - Enums: `RolUsuario{admin,odontologo}`, `EstadoTurno{reservado,confirmado,cancelado,completado}`
  - Mixin de auditoría (`creado_en`); convención de nombres de constraints; `Turno.token_cancelacion` único
  - `db/session.py` (engine + `get_db`), `db/seed.py` mínimo (1 admin, 1 profesional + su usuario)
  - Migración 001 (Alembic opcional) con las 6 tablas y FKs/índices (`profesional_id`, `fecha_hora_inicio`)
  - Modelo de **HorarioAtencion** semanal por profesional (config simple; ver Supuesto `SU-03` y gap de agenda)
  - Tests: creación de cada modelo, unicidad de `email`/`dni`/`token`, defaults de estado
- **Dependencias**: C-01
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Entidades, §Restricciones clave
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones (Repository/ORM)
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-01, DD-02, DD-05
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DATOS

---

## FASE 1 — Acceso y seguridad

### [C-03] `auth-jwt-rbac`
- **Estado**: `[ ]` pendiente
- **Scope**: Autenticación JWT (OAuth2 password flow) + RBAC para admin/odontólogo
  - `POST /auth/login` → JWT Bearer (`sub`, `rol`, `profesional_id`, `exp`), hash bcrypt/argon2
  - Dependencias FastAPI: `get_current_user`, `require_role("admin")`, `require_odontologo_own` (RN-AU-02)
  - `GET /auth/me` (usuario actual); CRUD de usuarios del sistema solo admin (RN-AU-03)
  - Rate limiting en login (p.ej. 5/60s por IP+email); nunca loguear/devolver `password_hash` (RN-AU-04)
  - Seed del admin (`admin@clinica.local`) consumible desde `C-02`
  - Tests: login OK/fallido, token expirado, acceso denegado por rol, hash nunca expuesto
- **Dependencias**: C-02
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §Actores, §RBAC
  - `knowledge-base/05_reglas_de_negocio.md` §RN-AU
  - `knowledge-base/07_flujos_principales.md` §Flujo 2 — Gestión de agenda
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad

---

## FASE 2 — Catálogos y motor de agenda (backend)

> `C-04`, `C-05` y `C-11` pueden proponerse en paralelo tras `C-03`. `C-06` espera `C-04`; `C-07` espera a los tres catálogos.

### [C-04] `profesionales-api`
- **Estado**: `[ ]` pendiente
- **Scope**: CRUD de profesionales + listado público
  - Modelos/schemas Pydantic: `ProfesionalCreate/Update/Read`
  - `GET /profesionales` (público: solo activos, para el selector de reserva), `GET /profesionales/{id}`
  - `POST/PUT/DELETE /profesionales` (admin; DELETE = desactivar si tiene turnos, RN-PR-01)
  - Validación de `activo`; filtrado de inactivos en endpoints públicos
  - Tests: CRUD admin, listado público excluye inactivos, permisos por rol
- **Dependencias**: C-03
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Profesional
  - `knowledge-base/06_funcionalidades.md` §US-006
  - `knowledge-base/05_reglas_de_negocio.md` §RN-PR (RN-PR-01)
  - `knowledge-base/03_actores_y_roles.md` §RBAC

---

### [C-05] `prestaciones-api`
- **Estado**: `[ ]` pendiente
- **Scope**: CRUD de prestaciones con duración variable
  - Schemas `PrestacionCreate/Update/Read`; validación `duracion_minutos > 0`
  - `GET /prestaciones` (público: activas, para reserva), `POST/PUT /prestaciones` (admin)
  - Desactivación que no borra turnos históricos (RN-PR-02); cambio de duración solo afecta turnos futuros (RN-PR-04)
  - Tests: CRUD, validación de duración, exclusión de inactivas en listado público
- **Dependencias**: C-03
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Prestacion
  - `knowledge-base/05_reglas_de_negocio.md` §RN-PR (RN-PR-02, RN-PR-04)
  - `knowledge-base/06_funcionalidades.md` §US-006

---

### [C-06] `bloqueos-api`
- **Estado**: `[ ]` pendiente
- **Scope**: CRUD de bloqueos de agenda por profesional
  - Schemas `BloqueoCreate/Read`; `GET/POST/DELETE /bloqueos` (admin)
  - Validación de intervalo (`fin > inicio`) y de pertenencia a un profesional existente (`C-04`)
  - Los bloqueos se persisten para ser considerados por el motor de agenda (RN-PR-03)
  - Tests: CRUD, validación de rango, permisos admin-only
- **Dependencias**: C-04
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Bloqueo
  - `knowledge-base/05_reglas_de_negocio.md` §RN-PR (RN-PR-03)
  - `knowledge-base/06_funcionalidades.md` §US-006

---

### [C-07] `agenda-engine`
- **Estado**: `[ ]` pendiente
- **Scope**: Motor de agenda — servicio puro y testeable (sin HTTP)
  - `agenda_service.disponibles(profesional_id, fecha)` → franjas libres = `HorarioAtencion` semanal − turnos activos − bloqueos, redondeo a grilla de prestación (RN-TU-07, RN-TU-03)
  - `agenda_service.validar_solapamiento(profesional_id, inicio, fin)` reutilizable por crear/reprogramar (RN-TU-01)
  - Cálculo de `fecha_hora_fin = inicio + duracion_minutos(prestacion)` (RN-TU-02)
  - Validador de transiciones de estado `reservado|confirmado|cancelado|completado` (RN-TU-04)
  - Rechazo de turnos en el pasado y profesionales inactivos (RN-TU-06, RN-PR-01)
  - Tests unitarios exhaustivos: franjas, solapamiento borde-a-borde `[inicio,fin)`, duración derivada, transiciones
- **Dependencias**: C-04, C-05, C-06
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Restricciones clave (integridad de agenda)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TU
  - `knowledge-base/07_flujos_principales.md` §Flujo 1, §Diagrama de estados del Turno
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones (Capa de servicios), §Estrategia de pruebas
  - `knowledge-base/10_preguntas_abiertas.md` §Pregunta 8 (horarios semanales fijos, SU-03)

---

## FASE 3 — Turnos (backend, flujo end-to-end)

### [C-08] `turnos-agenda-api`
- **Estado**: `[ ]` pendiente
- **Scope**: Agenda y gestión de turnos por admin/odontólogo
  - `GET /agenda/{profesional_id}/dia|semana` (turnos + bloqueos en eje horario, filtro por estado)
  - `GET /turnos` (filtrado por rol: odontólogo solo los de su `profesional_id`, RN-AU-02)
  - `POST /turnos` (admin crea manual: paciente nuevo o existente por dedupe, `reservado`/`confirmado`)
  - `PUT /turnos/{id}` (reprogramar en el mismo profesional, revalida `agenda_engine`, RN-TU-08)
  - `DELETE /turnos/{id}` (cancelar con `motivo_cancelacion` opcional, libera horario, RN-TU-05)
  - Errores semánticos: 409 solapamiento (con franjas alternativas), 400 transición inválida
  - Tests de integración: agenda, crear, reprogramar, cancelar, aislamiento por rol
- **Dependencias**: C-07
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-004, §US-005
  - `knowledge-base/07_flujos_principales.md` §Flujo 2
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TU (RN-TU-01, 05, 08), §RN-AU (RN-AU-02)
  - `knowledge-base/04_modelo_de_datos.md` §Turno

---

### [C-09] `reserva-online-api`
- **Estado**: `[ ]` pendiente
- **Scope**: Reserva pública del paciente sin login + cancelación por token
  - `GET /turnos/online/disponibles?profesional_id&fecha` (usa `agenda_engine`, RN-TU-07)
  - `POST /turnos/online` — valida datos (nombre, apellido, DNI, teléfono, email?, obra social?), consentimiento Ley 25.326, dedupe de `Paciente` por `dni`+`telefono`, crea `Turno` en `reservado`, devuelve resumen + enlace con `token_cancelacion`
  - Revalidación de solapamiento al confirmar → 409 y grilla actualizada (RN-TU-01)
  - `DELETE /turnos/online/cancelar/{token}` — cancela solo el turno del token, idempotencia/errores claros (RN-TU-05)
  - No expone datos de salud ni de otros pacientes (RN-DATOS-02)
  - Tests: reserva E2E, franja ocupada 409, dedupe, cancelación con token válido/inválido
- **Dependencias**: C-07
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-001, §US-002, §US-003
  - `knowledge-base/07_flujos_principales.md` §Flujo 1
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TU, §RN-DATOS
  - `knowledge-base/03_actores_y_roles.md` §Rutas públicas
  - `knowledge-base/04_modelo_de_datos.md` §Paciente, §Turno (token)

---

### [C-10] `turnos-estados-api`
- **Estado**: `[ ]` pendiente
- **Scope**: Ciclo de vida del turno — confirmación y completado
  - `POST /turnos/{id}/confirmar` — `reservado → confirmado` (admin, RN-TU-04, US-008)
  - `POST /turnos/{id}/completar` — `confirmado → completado` (odontólogo dueño del profesional, RN-AU-02, US-007)
  - Reutiliza el validador de transiciones de `agenda_engine`; rechaza transiciones inválidas con 400
  - Historial visible en la agenda (estados + `creado_en`/`cancelado_en`)
  - Tests: transiciones válidas e inválidas, permiso odontólogo por `profesional_id`
- **Dependencias**: C-08
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-007, §US-008
  - `knowledge-base/07_flujos_principales.md` §Flujo 3, §Diagrama de estados del Turno
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TU-04, §RN-AU-02

---

## FASE 4 — Frontend

### [C-11] `frontend-shell-auth`
- **Estado**: `[ ]` pendiente
- **Scope**: Cascarón de la SPA + autenticación en el cliente
  - Router con zonas pública y protegida (`ProtectedRoute`); layout, navegación por rol
  - `services/api.ts`: wrapper fetch con interceptor JWT (Bearer), manejo de 401 → logout
  - Store de sesión (context/Zustand): usuario, rol, `profesional_id`; persistencia del token
  - Página `Login` conectada a `POST /auth/login`; errores y estado de carga
  - Utilidades compartidas de fecha/hora (`shared/utils`) en zona horaria local del consultorio
  - Tests/smoke: login OK, redirección por rol, expiración de sesión
- **Dependencias**: C-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §Actores, §Rutas públicas
  - `knowledge-base/08_arquitectura_propuesta.md` §SPA con zona pública + privada, §Estructura de directorios (frontend)
  - `knowledge-base/07_flujos_principales.md` §Flujo 2 (Login)

---

### [C-12] `frontend-reserva-publica`
- **Estado**: `[ ]` pendiente
- **Scope**: Zona pública de reserva online (US-001/002/003)
  - `Home/Reserva`: selector de profesional activo → fecha → `GrillaDeHorarios` (franjas disponibles)
  - `FormTurno`: nombre, apellido, DNI, teléfono, email?, obra social?; validación por campo + checkbox de consentimiento (Ley 25.326)
  - Confirmación: resumen del turno + enlace de cancelación (copia/descarga)
  - Pantalla de cancelación por token (`/turnos/online/cancelar/:token`) con estados éxito/error
  - Actualización de la grilla ante 409 (franja ocupada) sin recargar
  - Smoke manual del flujo completo contra el backend local
- **Dependencias**: C-09, C-11
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-001, §US-002, §US-003
  - `knowledge-base/07_flujos_principales.md` §Flujo 1
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios (frontend)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DATOS (consentimiento)

---

### [C-13] `frontend-agenda-admin`
- **Estado**: `[ ]` pendiente
- **Scope**: Agenda y gestión de turnos para recepcionista/admin (US-004/005/008)
  - `Agenda`: vista por profesional + día/semana (turnos y bloqueos en eje horario), filtro por estado
  - Crear turno manual (paciente nuevo/existente), reprogramar (drag o modal), cancelar con motivo
  - Confirmar turno (`reservado → confirmado`) desde la agenda
  - Manejo de 409 con sugerencia de franjas alternativas; 400 transición inválida
  - Integración con `GET /agenda/...`, `POST/PUT/DELETE /turnos`, `POST /turnos/{id}/confirmar`
- **Dependencias**: C-08, C-10, C-11
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-004, §US-005, §US-008
  - `knowledge-base/07_flujos_principales.md` §Flujo 2, §Flujo 3
  - `knowledge-base/03_actores_y_roles.md` §RBAC
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios (frontend)

---

### [C-14] `frontend-catalogos-admin`
- **Estado**: `[ ]` pendiente
- **Scope**: Administración de catálogos y bloqueos (US-006)
  - Pantallas CRUD de profesionales (con activación/desactivación), prestaciones (duración en minutos) y bloqueos por profesional
  - Formularios con validación (duración > 0, rango de bloqueo) y feedback de errores del backend
  - Navegación desde el layout admin (C-11)
  - Smoke: alta/baja/edición reflejadas en los endpoints de catálogo
- **Dependencias**: C-04, C-05, C-06, C-11
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-006
  - `knowledge-base/04_modelo_de_datos.md` §Profesional, §Prestacion, §Bloqueo
  - `knowledge-base/05_reglas_de_negocio.md` §RN-PR

---

### [C-15] `frontend-odontologo`
- **Estado**: `[ ]` pendiente
- **Scope**: Vista del odontólogo (US-007)
  - Agenda propia (día/semana) limitada al `profesional_id` del usuario logueado
  - Acción "marcar completado" sobre turnos confirmados (`POST /turnos/{id}/completar`)
  - Sin acceso a agenda de otros profesionales ni a catálogos (oculto por rol)
  - Smoke: odontólogo ve y completa solo sus turnos
- **Dependencias**: C-10, C-11
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-007
  - `knowledge-base/03_actores_y_roles.md` §RBAC (RN-AU-02)
  - `knowledge-base/07_flujos_principales.md` §Flujo 3

---

## FASE 5 — Datos, privacidad y entrega

### [C-16] `seed-demo`
- **Estado**: `[ ]` pendiente
- **Scope**: Datos simulados para la entrega del TP
  - 3 profesionales (especialidades distintas; 1 con usuario `odontologo`)
  - 1 admin (`admin@clinica.local`) + 4-5 prestaciones (Limpieza 30, Obturación 45, Extracción 60, Consulta 20, Ortodoncia ajuste 30)
  - Horario de atención semanal por profesional (días hábiles 9-13 y 15-19)
  - Agenda semanal poblada con turnos de ejemplo en distintos estados para que la UI se vea completa
  - Script idempotente `db/seed.py` (re-ejecutable) documentado en el README
  - Garantiza datos ficticios, sin datos reales (RN-DATOS-03)
- **Dependencias**: C-09
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Seed data
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DATOS (RN-DATOS-03)
  - `knowledge-base/08_arquitectura_propuesta.md` §Deploy (entrega local)

---

### [C-17] `hardening-privacidad`
- **Estado**: `[ ]` pendiente
- **Scope**: Endurecimiento de seguridad y protección de datos de salud (Ley 25.326)
  - Rate limiting en reserva pública y login; validación estricta de entrada (Pydantic) y rechazo de estados inyectados
  - CORS restringido a `CORS_ORIGINS`; headers de seguridad; secretos solo en `.env`
  - Minimización de datos: la reserva pública no expone información clínica ni de terceros (RN-DATOS-01/02)
  - Consentimiento explícito registrado con la reserva; acceso a datos solo a personal autorizado (RBAC)
  - Tests de seguridad: aislamiento por rol, token de cancelación ajeno 403/404, no filtración de `password_hash`, no fugas de datos entre pacientes
- **Dependencias**: C-09, C-10
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DATOS, §RN-AU
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad
  - `knowledge-base/03_actores_y_roles.md` §RBAC, §Rutas públicas
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-08

---

### [C-18] `aceptacion-e2e-entrega`
- **Estado**: `[ ]` pendiente
- **Scope**: Suite de aceptación end-to-end + preparación de la entrega
  - Test de integración E2E: reserva online → aparece en agenda → confirmación → completado → cancelación por token libera la franja
  - Casos de error cubiertos: 409 solapamiento, 400 transición inválida, 403 token ajeno, datos inválidos
  - Smoke manual del frontend documentado (pasos de verificación) contra el seed demo
  - `README.md` de entrega: cómo levantar backend/frontend, correr seed, ejecutar tests y la demo guiada
  - Checklist de reglas RN-AU/RN-TU/RN-PR/RN-DATOS verificadas por test
- **Dependencias**: C-12, C-13, C-14, C-15, C-16
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/07_flujos_principales.md` §Flujo 1, §Flujo 2, §Flujo 3
  - `knowledge-base/08_arquitectura_propuesta.md` §Estrategia de pruebas, §Deploy
  - `knowledge-base/06_funcionalidades.md` (todas las US de v1.0)
  - `knowledge-base/01_vision_y_objetivos.md` §Alcance v1.0, §Métricas de éxito
  - `knowledge-base/10_preguntas_abiertas.md` (cierre de pendientes no bloqueantes)

---

## Tabla resumen

| ID | Change | Fase | Governance | Dependencias |
|----|--------|------|-----------|--------------|
| C-01 | foundation-setup | 0 — Cimientos | BAJO | — |
| C-02 | core-models | 0 — Cimientos | CRITICO | C-01 |
| C-03 | auth-jwt-rbac | 1 — Acceso | CRITICO | C-02 |
| C-04 | profesionales-api | 2 — Catálogos/agenda | BAJO | C-03 |
| C-05 | prestaciones-api | 2 — Catálogos/agenda | BAJO | C-03 |
| C-06 | bloqueos-api | 2 — Catálogos/agenda | MEDIO | C-04 |
| C-07 | agenda-engine | 2 — Catálogos/agenda | ALTO | C-04, C-05, C-06 |
| C-08 | turnos-agenda-api | 3 — Turnos | ALTO | C-07 |
| C-09 | reserva-online-api | 3 — Turnos | ALTO | C-07 |
| C-10 | turnos-estados-api | 3 — Turnos | MEDIO | C-08 |
| C-11 | frontend-shell-auth | 4 — Frontend | MEDIO | C-03 |
| C-12 | frontend-reserva-publica | 4 — Frontend | MEDIO | C-09, C-11 |
| C-13 | frontend-agenda-admin | 4 — Frontend | MEDIO | C-08, C-10, C-11 |
| C-14 | frontend-catalogos-admin | 4 — Frontend | BAJO | C-04, C-05, C-06, C-11 |
| C-15 | frontend-odontologo | 4 — Frontend | BAJO | C-10, C-11 |
| C-16 | seed-demo | 5 — Datos/privacidad/entrega | BAJO | C-09 |
| C-17 | hardening-privacidad | 5 — Datos/privacidad/entrega | CRITICO | C-09, C-10 |
| C-18 | aceptacion-e2e-entrega | 5 — Datos/privacidad/entrega | MEDIO | C-12, C-13, C-14, C-15, C-16 |

**Primer change recomendado**: `C-01` (foundation-setup) → `/opsx:propose C-01-foundation-setup`

---

## Changes OPSX de la consigna (desvíos deliberados)

> Changes del TP que no siguen el árbol de dependencias y se proponen de forma autónoma. Cada uno declara su desvío en su `proposal.md` y es absorbido por el change del roadmap que le corresponde.
>
> ✅ **Ciclo completo cerrado**: `crear-turno-sin-solapamientos` (explore → propose → apply → verify → archive) el 2026-10-10. Resto del TP puede continuar con `C-01`.

| Change OPSX | Alineado a | Desvío declarado |
|-------------|-----------|------------------|
| `crear-turno-sin-solapamientos` | C-07 `agenda-engine`, C-08 `turnos-agenda-api` | Autónomo y acotado: modelos mínimos + `turno_service.crear_turno` + `POST /turnos`, sin auth ni franjas (RN-TU-07). C-02/C-03 son governance CRITICO y no están archivados; su persistencia se absorbe en `C-02`. |

---

## Supuestos y gaps resueltos al armar el roadmap

- **Horario de atención por profesional (gap del modelo de datos)**: `04_modelo_de_datos.md` menciona "agenda semanal configurada" y `SU-03` asume horarios fijos, pero no define una entidad. Se resuelve incorporando un modelo configurable `HorarioAtencion` (semanal) dentro de `C-02`/`C-07`, tratado como config simple y no como recurso CRUD de v1. Pregunta 8 de `10_preguntas_abiertas.md` queda así cubierta para v1.
- **Deploy local vs. nube**: `10_preguntas_abiertas.md` Pregunta 5 no bloquea; el roadmap asume entrega local (uvicorn + Vite) y deja el deploy en nube como backlog (coherente con `08 §Deploy`).
- **Alembic**: la KB lo declara opcional; se adopta migración inicial numerada (`001`, `002`) para trazabilidad, sin bloquear el flujo si no se usa.
- **Recordatorios/pagos/ficha clínica**: fuera de alcance v1 (US-101..104); no generan changes.
- **Discovery incompleto**: `.active-orchestrator-state.json` marca `discovery.status = incomplete`, pero la KB está completa y es la fuente de verdad; no afectó el scope.
