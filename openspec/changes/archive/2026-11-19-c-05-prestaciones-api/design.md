# Design

## Context

Ver `proposal.md` para la motivación. Estado observable del repo al preparar
este change: C-03 archivó auth y dejó `require_role` en
`backend/app/core/deps.py:22-30`, el manejador de errores de auth en
`backend/app/core/handlers.py:14-45` y el router de auth en
`backend/app/routers/auth.py:14-40`; el modelo `Prestacion` ya existe con
`CheckConstraint("duracion_minutos > 0")` en
`backend/app/models/prestacion.py:7-16` y con `activa` default true; C-02 no
requiere migración nueva. `backend/app/main.py:32-34` monta los routers
existentes y `backend/app/main.py:42-45` ya convierte errores de validación de
Pydantic en 400. La tabla `prestacion` ya se usa en
`backend/app/services/turno_service.py:74,83-86,95` para derivar
`fecha_hora_fin` y rechazar prestaciones inactivas.

Restricciones de la KB: RBAC y rutas públicas (`03_actores_y_roles.md:11-29`),
RN-AU-01/03 y RN-PR-02/04 (`05_reglas_de_negocio.md:9-12,28-36`), duración
derivada (`05_reglas_de_negocio.md:19`, `04_modelo_de_datos.md:119`), capa de
servicios y validación Pydantic (`08_arquitectura_propuesta.md:7-11,39-46`) y
datos ficticios (`05_reglas_de_negocio.md:44`). Gobernanza **BAJO**
(`CHANGES.md:213-225`): no hay gate que aprueba, pero rigen las reglas duras de
`AGENTS.md` (servicios, RBAC, voseo, sin código en esta etapa).

## Goals / Non-Goals

**Goals:**

- Exponer el catálogo con contratos HTTP estables: público para lectura,
  admin-only para escritura, con 400/401/403/404 semánticos.
- Mantener la decisión de negocio en un servicio testeable y dejar el router
  delgado (DD-07).
- Garantizar que cambios del catálogo no reescriban la historia de turnos.
- Cubrir cada escenario de la spec con una prueba explícita.

**Non-Goals:**

- Modificar el modelo `Prestacion`, crear migraciones ni agregar tablas.
- Implementar `DELETE /prestaciones`: la baja es lógica (`activa = false`).
- Calcular franjas, solapamientos ni duración de turnos en este change (C-07).
- Tocar `c-04-profesionales-api`, sillones, bloqueos ni frontend.
- Escribir código de producción, correr `apply` o archivar en esta etapa.

## Decisions

1. **Capability nueva, specs existentes intactas.** Se crea
   `specs/prestaciones-api/spec.md` como delta de `## ADDED Requirements`.
   `modelo-datos` y `turnos` ya cubren la integridad persistida y la duración
   derivada al crear; `user-auth` cubre RBAC. Agregar requisitos duplicados
   allí mezclaría responsabilidades; alternativa descartada: extender `turnos`
   con requisitos de catálogo.

2. **Reutilizar el modelo y la constraint existentes.** `Prestacion` ya tiene
   `id`, `nombre`, `duracion_minutos`, `activa` y el check de duración
   (`backend/app/models/prestacion.py:7-16`). No se agrega `DELETE` ni columnas:
   la desactivación es un `PUT` con `activa = false`, conservando las FKs de
   `Turno.prestacion_id`. Alternativa descartada: borrado físico — rompería
   RN-PR-02 y la integridad referencial.

3. **Tres schemas Pydantic explícitos.** `PrestacionCreate` (`nombre`,
   `duracion_minutos: int > 0`), `PrestacionUpdate` (campos opcionales:
   `nombre`, `duracion_minutos` con la misma validación, `activa`) y
   `PrestacionRead` (`id`, `nombre`, `duracion_minutos`, `activa`,
   `from_attributes=True`). Opera `extra="forbid"` en create/update para
   rechazar campos inyectados, igual que `TurnoCreate` en
   `backend/app/schemas/turno.py:6-14`. El PUT se trata como actualización
   parcial para permitir togglear `activa` sin enviar el resto; alternativa
   descartada: reemplazo completo, que complicaría las pantallas de C-14.
   La validación de Pydantic ya produce 400 por el handler global de
   `backend/app/main.py:42-45`.

4. **Servicio con la decisión, router delgado.** `app/services/prestacion_service.py`
   expone `listar_activas`, `crear` y `actualizar`; valida duración y existencia,
   y lanza errores de dominio (`PrestacionRechazadaError`,
   `PrestacionNoEncontradaError`) mapeados por el router a 400/404. El router
   `app/routers/prestaciones.py` declara `APIRouter(prefix="/prestaciones")`,
   inyecta `get_db` y `require_role(RolUsuario.ADMIN)` solo en POST/PUT, y se
   monta en `app/main.py`. Alternativa descartada: lanzar `HTTPException`
   desde el servicio — acoplaría la lógica de negocio a FastAPI (DD-07).

5. **RBAC por dependencia explícita, sin middleware global.** `GET
   /prestaciones` queda público (`03_actores_y_roles.md:22-29`) y no lee token
   ni datos de pacientes; POST/PUT llevan `require_role(RolUsuario.ADMIN)`.
   Sin token, `OAuth2PasswordBearer` responde 401; con odontólogo,
   `verificar_rol` eleva `AccesoDenegadoError` y el handler responde 403
   (`backend/app/core/handlers.py:27-29`). Alternativa descartada: proteger
   todo el router — dejaría el selector público en 401 (RN-AU-01).

6. **No retroactividad por inmutabilidad del turno.** Un cambio de duración no
   ejecuta `UPDATE` sobre `Turno`: `fecha_hora_fin` quedó calculada al crear con
   la duración vigente (`backend/app/services/turno_service.py:95`) y
   `turno_service.crear_turno` volverá a derivarla para los turnos nuevos.
   La desactivación tampoco toca turnos: solo cambia `activa` y
   `turno_service.py:83-86` ya impide nuevas reservas. Alternativa descartada:
   recalcular `fecha_hora_fin` de turnos futuros ya creados — exigiría
   revalidar solapamiento y podría alterar horarios confirmados, fuera del
   scope de `CHANGES.md:215-219`. **Supuesto registrado:** "turnos futuros" de
   RN-PR-04 se interpreta como turnos creados con posterioridad al cambio; si
   se exigiera recomputar turnos futuros ya persistidos, cambian la spec y las
   tasks, no solo el código.

7. **Verificación en dos niveles.** Unit tests del servicio (lista de activas,
   alta, actualización, duración, inexistente) y tests de integración con
   `TestClient` para 200/201/400/401/403/404 y persistencia
   (`08_arquitectura_propuesta.md:58-62`). Los fixtures usan usuarios con
   contraseñas ficticias y helper de token análogo a
   `backend/tests/test_auth_api.py:65-90`; no se usan datos reales
   (RN-DATOS-03).

## Risks / Trade-offs

- [Dos changes editan `main.py` en paralelo] → C-04 también debe montar su
  router; al hacer `apply` de C-05 se agrega solo `include_router` de
  prestaciones y se resuelve cualquier conflicto de merge sin tocar el
  directorio de C-04.
- [PUT parcial vs. contrato REST estricto] → se documenta en la spec que los
  campos omitidos conservan su valor; el comportamiento cubre desactivación y
  edición de duración sin enviar el resto.
- [RBAC omitido en una ruta nueva] → checklist de dependencias en `tasks.md` y
  auditoría ligera de `auth-contract-audit` al revisar los escenarios 401/403.
- [Interpretación de RN-PR-04] → supuesto 6 explícito; cambio de interpretación
  requiere revisar la spec antes de implementar.
- [Datos de prueba con información real] → usar solo nombres y contactos
  ficticios como los de `backend/tests/conftest.py:17-76` (RN-DATOS-03).
- [Validación duplicada Pydantic + servicio] → intencional: la API responde
  400 y el servicio queda seguro si se llama desde otro cambio (C-07/C-09).

## Migration Plan

Sin migración de esquema: el modelo `Prestacion` y su constraint ya existen
desde C-02. Rollback: quitar `app.include_router` de prestaciones, el router,
el servicio y los schemas; no hay datos de pacientes reales ni borrado físico
de turnos (RN-DATOS-03, RN-PR-02).

## Open Questions

Ninguna diferible: la única ambigüedad material (si RN-PR-04 exige recalcular
turnos futuros ya creados) quedó resuelta como supuesto registrado en la
Decisión 6 y reflejada en la spec; cambiarla exige revisar los artefactos, no
diferirla a la implementación.
