# Proposal

## Why

C-03 dejó lista la autenticación JWT y el RBAC (`require_role("admin")` en `backend/app/core/deps.py`), pero el consultorio todavía no puede administrar su catálogo de profesionales: el modelo `Profesional` existe (`backend/app/models/profesional.py:7-14`) y el seed ya crea datos ficticios, mas no hay schemas, servicio ni endpoints. Sin el listado público, la futura reserva online (C-09/C-12) no tiene de dónde tomar el selector de profesional, y sin el CRUD admin no se puede reflejar la realidad del consultorio (US-006; `knowledge-base/06_funcionalidades.md:55-63`). C-04 es el primer change del fork de Fase 2 y desbloquea C-06 (`CHANGES.md:193-204`).

## What Changes

- Schemas Pydantic `ProfesionalCreate` / `ProfesionalUpdate` / `ProfesionalRead`, con `extra="forbid"` y validación de `nombre`, `apellido`, `especialidad` y `activo` (booleano estricto).
- `GET /profesionales`: endpoint público que devuelve solo profesionales activos, para el selector de reserva (RN-PR-01; `knowledge-base/05_reglas_de_negocio.md:32`).
- `GET /profesionales/{id}`: detalle público de un profesional activo; un profesional inactivo o inexistente responde 404 para no exponer bajas en la zona pública.
- `POST /profesionales`, `PUT /profesionales/{id}` y `DELETE /profesionales/{id}`: operaciones de administración con JWT válido y rol `admin` (RN-AU-03; `knowledge-base/03_actores_y_roles.md:17`).
- `DELETE` implementado como baja lógica: fija `activo=false` y conserva el registro, aun cuando el profesional tenga turnos o usuarios asociados, para preservar el histórico y la integridad referencial.
- Lógica de negocio en un servicio (`app/services/profesional_service.py`) y routers delgados que solo validan dependencias y traducen errores a HTTP (DD-07).
- Tests unitarios del servicio y de integración con `TestClient`: CRUD admin, exclusión de inactivos en el listado público, 401/403 por rol y 404/400 de negocio, con datos ficticios (RN-DATOS-03).
- **Sin código de producción en esta etapa**: el alcance de este change es planning; la implementación requiere un pedido nuevo para `apply`.

## Capabilities

### New Capabilities

- `profesionales`: contrato observable del catálogo de profesionales — consulta pública de activos para la reserva, alta/edición/baja administradas y reglas de visibilidad de `activo`.

### Modified Capabilities

- Ninguna. `modelo-datos` ya especifica la persistencia del profesional, el vínculo usuario–profesional y el seed (sin cambios de requisitos); `user-auth` ya especifica JWT y RBAC (sin cambios). C-04 agrega el comportamiento del catálogo, no modifica esos contratos.

## Impact

- Backend (planificado, no implementado): nuevos `app/schemas/profesional.py`, `app/services/profesional_service.py`, `app/routers/profesionales.py`, ajuste de `app/services/errores.py` y registro del router en `app/main.py`; tests nuevos en `backend/tests/`.
- APIs: nuevas rutas `/profesionales` y `/profesionales/{id}`; sin cambios en `/auth/*` ni en `/turnos`.
- Dependencias: C-03 archivada (`openspec/changes/archive/2026-11-18-c-03-auth-jwt-rbac/`); desbloquea C-06 (`CHANGES.md:479`).
- KB / reglas duras: RN-PR-01, RN-AU-01/03, RN-DATOS-03, DD-07 y `AGENTS.md` §Reglas Duras ("lógica en servicios", "nunca exponer datos de terceros en rutas públicas", datos ficticios). Sin integraciones externas, pagos ni ficha clínica.
- Gobernanza: BAJO (`CHANGES.md:204`); no requiere aprobación previa de governance, pero sí un request nuevo para pasar a implementación.
