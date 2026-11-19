# Proposal

## Why

C-03 (`auth-jwt-rbac`) ya está archivado y dejó las dependencias de JWT/RBAC
listas, pero el catálogo de prestaciones todavía no tiene API: la reserva pública
no puede elegir qué se va a atender y `C-07 agenda-engine` no podrá derivar
`fecha_hora_fin = inicio + duracion_minutos` sin una fuente confiable de
duración (RN-TU-02, `05_reglas_de_negocio.md:19`). Este change habilita ese
catálogo con duración variable respetando que dar de baja una prestación no borra
turnos históricos (RN-PR-02) y que cambiar su duración solo afecta turnos futuros
(RN-PR-04, `05_reglas_de_negocio.md:33,35`).

## What Changes

- Schemas Pydantic `PrestacionCreate` / `PrestacionUpdate` / `PrestacionRead`,
  con `extra="forbid"` y validación `duracion_minutos > 0` en request y en la
  capa de servicio (`04_modelo_de_datos.md:71-77`).
- `GET /prestaciones`: listado público sin JWT que devuelve solo prestaciones
  `activa = true`, para el selector de reserva (RN-PR-02;
  `03_actores_y_roles.md:18,22-28`).
- `POST /prestaciones` y `PUT /prestaciones/{id}` protegidos con
  `require_role("admin")`: sin token → 401, rol odontólogo → 403 (RN-AU-01/03,
  `03_actores_y_roles.md:11-20`).
- Desactivación mediante el mismo `PUT` (`activa = false`): la prestación deja
  de aparecer en el listado público y de admitir turnos nuevos, pero los turnos
  ya creados se conservan con su horario original (RN-PR-02/04).
- No se expone ni se loguea información clínica: el catálogo solo contiene
  nombre, duración y estado; los datos de prueba son ficticios (RN-DATOS-02/03,
  `05_reglas_de_negocio.md:43-44`).
- Decisiones de negocio en `app/services/prestacion_service.py`; los routers
  quedan delgados y solo delegan (DD-07, `08_arquitectura_propuesta.md:8`).
- Tests unitarios del servicio y de integración con `TestClient`: CRUD,
  validación de duración, exclusión de inactivas en el público, 401/403 y
  no retroactividad.
- **Solo planificación**: este change no escribe código de producción, no corre
  `apply` ni archiva; eso requiere un pedido nuevo.

## Capabilities

### New Capabilities

- `prestaciones-api`: catálogo de prestaciones del consultorio — alta, edición,
  desactivación y listado público de activas, con duración válida y reglas de
  no retroactividad sobre turnos existentes.

### Modified Capabilities

- Ninguna. `modelo-datos` ya especifica la integridad persistida (unicidades,
  enums, seed) y el modelo `Prestacion` con su constraint `duracion_minutos > 0`
  ya existe en `backend/app/models/prestacion.py:7-16`; `turnos` ya especifica
  la duración derivada en el momento de crear y el rechazo de prestaciones
  inactivas (`openspec/specs/turnos/spec.md:11-30,107-130`); `user-auth` ya
  define RBAC y 401/403 (`openspec/specs/user-auth/spec.md`). C-05 agrega
  comportamiento de catálogo, no cambia esos requisitos.

## Impact

- Backend (planificado, no implementado): `app/schemas/prestacion.py`,
  `app/services/prestacion_service.py`, `app/routers/prestaciones.py`,
  `app/main.py` y `backend/tests/`; reutiliza el modelo `Prestacion` de C-02 y
  `require_role("admin")` de C-03 sin tocarlos.
- APIs: nuevas `GET /prestaciones` (pública), `POST /prestaciones` y
  `PUT /prestaciones/{id}` (admin). Sin cambios en `/auth/*` ni en `/turnos`.
- Dependencias: C-03 archivada en
  `openspec/changes/archive/2026-11-18-c-03-auth-jwt-rbac/`. Desbloquea, junto
  a C-04 y C-06, el gate 5 de `C-07 agenda-engine` (`CHANGES.md:69-72,254`).
- Gobernanza: `governance BAJO` (`CHANGES.md:213-225`); no requiere gate
  aprobado, pero respeta las reglas duras de `AGENTS.md` (servicios, RBAC,
  voseo, datos ficticios).
- Fuera de alcance: sillones/bloqueos (C-04/C-06), motor de agenda (C-07),
  reserva online (C-09), frontend (C-14), pagos, recordatorios y ficha clínica.
- Coexistencia: se trabaja únicamente en
  `openspec/changes/c-05-prestaciones-api/`; el change paralelo
  `c-04-profesionales-api` no se modifica.
