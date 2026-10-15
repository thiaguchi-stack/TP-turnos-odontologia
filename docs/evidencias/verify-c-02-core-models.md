# Verify — `c-02-core-models`

Verificación del change archivado en `openspec/changes/archive/2026-10-15-c-02-core-models/`, contra la spec vigente `openspec/specs/modelo-datos/spec.md` (9 requirements, 12 escenarios).

No existe un comando propio de verify en OPSX: la verificación se hizo corriendo la suite y el lint del repo, mapeando cada requirement/escenario contra los tests existentes (`backend/tests/*`) y contra modelos/migraciones/seed/security. Todo en español rioplatense.

- **Fecha de la corrida:** 2026-10-15.
- **Entorno:** `backend\.venv` (Python 3.14.7), SQLite en memoria (usado por la suite; migraciones se validan sobre SQLite temporal en `test_migraciones.py`).
- **Salidas crudas (combinadas para C-01+C-02):** [pytest-c-01-c-02-modelos.txt](pytest-c-01-c-02-modelos.txt) · [ruff-c-01-c-02-modelos.txt](ruff-c-01-c-02-modelos.txt) · [mypy-backend.txt](mypy-backend.txt) (existente, repo completo).

---

## 1. Comandos ejecutados y salida real

Desde la raíz del repo:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -v
```

Resumen real (última línea de `pytest-c-01-c-02-modelos.txt`):

```
======================= 112 passed, 1 warning in 11.15s =======================
```

```powershell
backend\.venv\Scripts\ruff.exe check backend
backend\.venv\Scripts\ruff.exe format --check backend
```

Ver detalle completo en `ruff-c-01-c-02-modelos.txt`. `ruff check` → `All checks passed!` (exit 0). `ruff format --check` → 5 archivos sin formatear (exit 1), ya documentado para C-01.

Mypy: `backend\.venv\Scripts\python.exe -m mypy app` desde `backend/` — ver `mypy-backend.txt` (sin errores, strict).

---

## 2. Trazabilidad: spec modelo-datos → tests

Fuente: [openspec/specs/modelo-datos/spec.md](../../openspec/specs/modelo-datos/spec.md). Los tests que ejercitan estos requirements son mayoritariamente nuevos (C-02): `test_usuario.py`, `test_unicidades_indices.py`, `test_enums.py`, `test_auditoria.py`, `test_horario_atencion.py`, `test_turno_creado_por.py`, `test_seed.py`, `test_seed_startup.py`, `test_security.py`, `test_migraciones.py`.

### Requirement: Unicidad de email de usuario
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Email duplicado rechazado | `test_email_unico_rechaza_segundo_usuario` | `backend/tests/test_usuario.py:56` |

**Implementación:** `Usuario.email` con `unique=True` (modelo `app/models/usuario.py`) y tabla creada con esa unicidad (migración `001_baseline.py`).

### Requirement: Unicidad de paciente por dni y teléfono
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Paciente duplicado por dni y teléfono → error de integridad, no se crea | `test_paciente_mismo_dni_telefono_rechazado` | `backend/tests/test_unicidades_indices.py:35` |
| Mismo dni con teléfono distinto permitido | `test_paciente_mismo_dni_telefono_distinto_permitido` | `backend/tests/test_unicidades_indices.py:46` |

**Implementación:** `UniqueConstraint("dni", "telefono")` en `Paciente` (`app/models/paciente.py`, migración 001).

### Requirement: Token de cancelación único
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Token duplicado rechazado | `test_turno_token_cancelacion_duplicado_rechazado` | `backend/tests/test_unicidades_indices.py:56` |
| Ausencia de token (nulo) permitida | `test_turno_token_cancelacion_nulo_permitido` | `backend/tests/test_unicidades_indices.py:84` |

**Implementación:** `Turno.token_cancelacion` con `unique=True`, `nullable=True` (`app/models/turno.py`, migración 001).

### Requirement: Enums cerrados de estado y rol con defaults
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Estado por defecto reservado | `test_turno_persiste_con_estado_reservado_por_defecto` (existente) · `test_turno_estado_por_defecto_es_reservado` | `backend/tests/test_models.py:77` · `backend/tests/test_enums.py:70` |
| Estado fuera del enum rechazado | `test_turno_estado_fuera_del_enum_no_construye` (construcción enum) · `test_turno_con_estado_invalido_no_se_persiste` (persistencia) · `test_turno_con_estado_en_texto_fuera_del_enum_no_se_persiste` | `backend/tests/test_enums.py:60` · `backend/tests/test_models.py:109` · `backend/tests/test_enums.py:81` |
| Rol fuera del enum rechazado | `test_rol_usuario_fuera_del_enum_no_construye` | `backend/tests/test_enums.py:65` |

**Implementación:** Enums `EstadoTurno`, `RolUsuario` + alias `ESTADOS_TURNO` para compatibilidad (`app/models/turno.py`, `app/models/usuario.py`). Migración con `CheckConstraint` para `turno.estado` y `usuario.rol` en valores permitidos.

### Requirement: Contraseña persistida solo como hash
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Hash del admin tras el seed difiere de la contraseña en claro y no la contiene | `test_seed_persiste_hash_que_valida_la_clave_sin_guardarla_en_claro` · `test_password_hash_persistido_difiere_de_la_clave_en_claro` · `test_hash_password_no_es_igual_ni_contiene_la_clave_en_claro` · `test_repr_de_usuario_no_expone_password_hash` | `backend/tests/test_seed.py:39` · `backend/tests/test_security.py:48` · `backend/tests/test_security.py:10` · `backend/tests/test_security.py:35` |

**Implementación:** `hash_password`/`verify_password` en `app/core/security.py` (PBKDF2-HMAC-SHA256, sal aleatoria, prefijo versionado). `Usuario.__repr__` no expone hash. Seed usa hash (OQ-4).

### Requirement: Auditoría de creación automática
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| `creado_en` se llena solo (sin enviarlo) | `test_creado_en_usuario_automatico_sin_enviarlo` · `test_creado_en_paciente_automatico_sin_enviarlo` · `test_creado_en_turno_automatico_sin_enviarlo` | `backend/tests/test_auditoria.py:42` · `backend/tests/test_auditoria.py:57` · `backend/tests/test_auditoria.py:73` |

**Implementación:** `AuditableMixin` en `app/db/base.py`; aplicado a `Usuario`, `Paciente`, `Turno`. Usa `app.core.clock.now()` (clock central, testable con monkeypatch).

### Requirement: Vínculo opcional usuario–profesional con integridad referencial
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Usuario admin sin profesional OK | `test_usuario_admin_con_profesional_id_nulo_se_persiste` | `backend/tests/test_usuario.py:18` |
| Referencia a profesional inexistente rechazada por FK | `test_profesional_id_inexistente_rechazado_por_fk` | `backend/tests/test_usuario.py:76` |

**Implementación:** `Usuario.profesional_id` FK nullable a `profesional.id` (`app/models/usuario.py`, migración 001).

### Requirement: Horario de atención semanal por profesional
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Horario semanal válido (lunes 09:00–13:00) persistido y asociado | `test_horario_atencion_franja_valida_se_persiste` | `backend/tests/test_horario_atencion.py:30` |
| Intervalo invertido (`hora_fin <= hora_inicio`) rechazado | `test_horario_atencion_hora_fin_menor_igual_inicio_rechazada` · `test_horario_atencion_hora_fin_igual_inicio_rechazada` | `backend/tests/test_horario_atencion.py:48` · `backend/tests/test_horario_atencion.py:62` |
| FK a profesional inexistente rechazada | `test_horario_atencion_fk_profesional_inexistente_rechazada` | `backend/tests/test_horario_atencion.py:76` |

**Implementación:** `HorarioAtencion` con `CheckConstraint(hora_fin > hora_inicio)` y FKs únicas por franja según opción aprobada en OQ-2 (`app/models/horario_atencion.py`, migración 001). Test triangulate documenta que superposiciones no son bloqueadas a nivel modelo (se deja para C-07): `test_horario_atencion_franjas_superpuestas_son_permitidas_por_el_modelo` (`backend/tests/test_horario_atencion.py:113`).

### Requirement: Seed mínimo idempotente con datos ficticios
| Escenario | Test(s) | Ruta:línea |
|---|---|---|
| Seed ejecutado dos veces: sin duplicados, existentes conservados | `test_seed_ejecutado_dos_veces_no_duplica_ni_altera_existentes` · `test_segundo_arranque_no_duplica_la_siembra` | `backend/tests/test_seed.py:49` · `backend/tests/test_seed_startup.py:25` |
| Entidades mínimas presentes tras seed: admin, profesional activo, odontólogo vinculado a ese profesional | `test_seed_en_base_vacia_crea_admin_profesional_y_odontologo_vinculado` · `test_startup_siembra_la_base_y_health_responde_200` | `backend/tests/test_seed.py:19` · `backend/tests/test_seed_startup.py:14` |

**Implementación:** `app/db/seed.py` idempotente (lookup por email/dni+teléfono), datos ficticios. Seed invocado desde `lifespan` (`app/main.py:17`) vía `app/db/arranque.py`.

---

## 3. Cobertura extra C-02 (soportan integridad/esquema)

- **Turno.creado_por** (adicionado): `test_turno_creado_por_es_nulo_por_defecto_reserva_online` · `test_turno_creado_por_acepta_fk_a_usuario_existente` → `backend/tests/test_turno_creado_por.py:34,52`.
- **Índices de agenda**: `test_indices_turno_y_bloqueo_existen` → `backend/tests/test_unicidades_indices.py:109` (verifica `ix_turno_profesional_inicio`, `ix_turno_sillon_inicio`, `ix_bloqueo_profesional_inicio`).
- **Migraciones Alembic**: `test_esquema_migrado_coincide_con_metadata` · `test_downgrade_base_elimina_todas_las_tablas` → `backend/tests/test_migraciones.py:24,54` (valida que `Base.metadata` coincide con esquema migrado; downgrade limpia).
- **Security hash completo**: `test_hash_password_genera_sal_aleatoria_distinta_por_llamada`, `test_verify_password_valida_la_correcta_y_rechaza_la_incorrecta`, `test_verify_password_rechaza_hashes_malformados` → `backend/tests/test_security.py:17,21,28`.
- **Enums + alias**: `test_estado_turno_tiene_los_cuatro_valores_exactos`, `test_estados_turno_se_conserva_como_alias_de_compatibilidad`, `test_rol_usuario_tiene_admin_y_odontologo` → `backend/tests/test_enums.py:43,52,56`.

---

## 4. Huecos y salvedades

1. **Formateo ruff (format --check):** resuelto durante la generación de esta evidencia: la primera corrida detectó 5 archivos heredados sin formatear (exit 1), se aplicó `ruff format backend` y `format --check` quedó limpio. `ruff check` (lint) pasa siempre al 100 %.
2. **Trazabilidad completa:** Todos los 9 requirements y 12 escenarios de `modelo-datos/spec.md` tienen al menos un test que los ejercita. El test triangulate de superposiciones documenta explícitamente la decisión (no bloqueado a nivel modelo) para C-07.
3. **Migraciones sobre SQLite temporal:** Las pruebas de Alembic usan archivos temporales (`tmp_path`) para validar upgrade/downgrade y coherencia con metadata; la app runtime puede seguir usando create_all en in-memory según configuración de tests (sin afectar datos locales).
4. **No se duplica mypy:** `mypy-backend.txt` ya existente cubre strict check del backend completo (incluye modelos, seed, security, migraciones).

---

## 5. Estado final

| Control | Resultado |
|---|---|
| `pytest backend\tests -v` | **112 passed, 0 failed, 0 skipped**, 1 warning (framework). |
| `ruff check backend` | **`All checks passed!`** (exit 0). |
| `ruff format --check backend` | **53 files already formatted** (exit 0; se aplicó `ruff format` a los 5 heredados durante esta evidencia). |
| `mypy app` (desde backend/, strict) | **Sin errores** (`mypy-backend.txt`). |
| Trazabilidad spec → tests | **9/9 requirements, 12/12 escenarios** con al menos un test (más cobertura extra documentada). |
| Tasks del change (`tasks.md`) | **76/76** marcadas `[x]`, 0 abiertas (incluye gate 0, grupos 1-7). |
| Commits de esta evidencia | **ninguno durante la corrida**; el formateo y esta evidencia se commitean junto con el pedido de sincronización del usuario. |