# TP-turnos-odontologia — Instrucciones para Agentes

> Este archivo (y su copia `CLAUDE.md`) es lo PRIMERO que todo agente lee al entrar al repo.
> Generado a partir de `knowledge-base/` y `CHANGES.md`. No editar a mano sin re-sincronizar ambos.

---

## Stack Tecnológico

| Capa | Tecnologías | Versión mínima / Nota |
|------|-------------|-----------------------|
| Frontend | React + Vite | React 18+, Vite 5+ |
| Backend | FastAPI (Python) | Python 3.11+, FastAPI 0.110+ |
| ORM | SQLAlchemy 2.x | Modelo relacional, migraciones (Alembic opcional) |
| Validación | Pydantic 2.x | Schemas de request/response |
| Base de datos | SQLite (dev) / PostgreSQL 15+ (prod opcional) | SQLite para entrega local; Postgres vía `DATABASE_URL` |
| Autenticación | JWT (OAuth2 password flow) | Tokens Bearer para roles admin/odontólogo |
| Tests | pytest + httpx (TestClient) | Suite unit + integración |
| Lint/format | Ruff (Python), ESLint/Prettier (TS) | Opcional pero recomendado |

Arquitectura: SPA con zona pública (reserva sin login) + zona protegida (admin/odontólogo). Backend modular por recurso con routers delgados y lógica en capa de servicios. Single-tenant. **Ninguna integración externa en v1.**

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md) · [knowledge-base/08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md)

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. **Leé el archivo relevante ANTES de implementar.**

| Archivo | Cuándo leerlo |
|---------|---------------|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Propósito, alcance v1.0 y fuera de alcance |
| [02_descripcion_general.md](knowledge-base/02_descripcion_general.md) | Stack, arquitectura general, API REST |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Actores, matriz RBAC, rutas públicas |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Entidades, ERD, restricciones, seed |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas codificadas (RN-XX-NN) |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Historias de usuario por épica (US-NNN) |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E y estados del turno |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones, estructura, seguridad, env vars |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | Decisiones de diseño (DD) y supuestos (SU) |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | ⚠️ Inconsistencias y pendientes |

> ⚠️ Revisar `10_preguntas_abiertas.md` antes de codear. Ninguna pregunta **bloquea v1**, pero la Pregunta 8 (horarios semanales fijos, SU-03) condiciona `agenda_service`.

---

## Skills Disponibles

| Agente | Rol | Skills que carga |
|--------|-----|------------------|
| **Orquestación / Fundación** | Coordina las fases de fundación y el state file | `active-orchestrator`, `kb-creator`, `roadmap-generator`, `agents-md-generator` |
| **Discovery / Research** | Investigación de mercado antes de armar la KB | `discovery-research`, `web-scraper`, `find-skills` |
| **Implementación (Backend Core / Backend Aux / Frontend)** | Flujo SDD de OpenSpec sobre los changes | `openspec-explore`, `openspec-propose`, `openspec-apply-change`, `openspec-archive-change`, `openspec-sync-specs`, `openspec-update-change` |

> Nota: hoy **no hay skills de stack instaladas** (FastAPI/React/testing). Si un agente necesita una skill específica, usar `find-skills` para buscar/recomendar e instalar solo con permiso explícito del usuario.

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo). Esta tabla solo mapea skill→rol.

---

## Roadmap de Changes

El plan completo está en [CHANGES.md](CHANGES.md). Resumen:

- **Total**: 18 changes en 6 fases (Fase 0 Cimientos → Fase 5 Datos/privacidad/entrega).
- **Camino crítico (10)**: `C-01 → C-02 → C-03 → C-04 → C-06 → C-07 → C-08 → C-10 → C-13 → C-18`
  (el tramo de reserva online también mide 10: `C-01 → C-02 → C-03 → C-04 → C-06 → C-07 → C-09 → C-11 → C-12 → C-18`).
- **Primer change**: `C-01` (`foundation-setup`) → `/opsx:propose C-01-foundation-setup`.
- **Governance CRITICO**: `C-02` (core-models), `C-03` (auth-jwt-rbac), `C-17` (hardening-privacidad).

**Antes de cualquier `/opsx:propose`**: leé [CHANGES.md](CHANGES.md), verificá que las dependencias estén archivadas, y leé los archivos de "Leer antes" del change.

---

## Reglas Duras (específicas del proyecto)

> No existe `~/.claude/CLAUDE.md` global en esta máquina: por eso este archivo incluye también las reglas universales (commit/build/gobernanza) que normalmente se heredarían del global. Si el global se agrega más adelante, migrar allí lo universal y dejar acá solo lo del proyecto.

Son contrato: romperlas es un defecto. Formato `NUNCA X → hacer Y`.

**Arquitectura backend**

- NUNCA lógica de negocio en routers → va en `app/services/` (routers delgados, DD-07); agenda, estados y franjas se validan en servicios testeables.
- NUNCA `fecha_hora_fin` arbitraria → siempre derivada: `fin = inicio + duracion_minutos(prestación)` (RN-TU-02).
- NUNCA permitir solapamiento para un mismo profesional ni para un mismo sillón/box (turno–turno o turno–bloqueo) → validar en toda creación/reprogramación (RN-TU-01).
- NUNCA crear turnos en el pasado ni para profesionales `activo=false` (RN-TU-06, RN-PR-01).
- NUNCA guardar, devolver ni loguear contraseñas en claro → hash bcrypt/argon2; `password_hash` jamás sale en una respuesta ni en logs (RN-AU-04).
- NUNCA exponer rutas privadas sin JWT válido ni saltear RBAC → `require_role("admin")` / `require_odontologo_own`; el odontólogo solo ve/modifica turnos de su `profesional_id` (RN-AU-01/02/03).
- NUNCA aceptar `estado` desde la reserva pública → el paciente crea el turno solo en `reservado`; transiciones validadas en el servicio (RN-TU-04).
- NUNCA cambiar duración de prestación ni desactivarla con efecto retroactivo → solo afecta turnos futuros y no borra históricos (RN-PR-02/04).

**Frontend (React/TS)**

- NUNCA usar `any` → tipado estricto; componentes en PascalCase; `tsconfig` estricto.
- NUNCA llamar endpoints privados sin el interceptor JWT → `services/api.ts` inyecta Bearer y maneja 401 → logout.
- NUNCA calcular fechas/horas fuera de la utilidad compartida → usar `shared/utils` en la zona horaria local del consultorio.

**Tests**

- NUNCA cerrar un change sin tests → pytest (`services` unit + `TestClient` integration); cubrir RN-AU/TU/PR/DATOS y errores 400/403/409.
- NUNCA testear `agenda_service` vía HTTP → es un servicio puro; tests unitarios primero (franjas, solapamiento borde-a-borde `[inicio,fin)`, transiciones).

**Privacidad (Ley 25.326)**

- NUNCA exponer datos clínicos ni de terceros en rutas públicas → la reserva recibe solo datos de contacto + consentimiento explícito (RN-DATOS-01/02).
- NUNCA incluir datos reales de pacientes en el repositorio ni en ningún ejemplo → seeds, tests, fixtures y capturas siempre con datos ficticios (RN-DATOS-03).

**Alcance y gobernanza**

- NUNCA implementar recordatorios, cobros/pagos, ficha clínica/odontograma ni integraciones externas en v1 → backlog v2 (DD-03/06).
- NUNCA asumir multi-tenant → single-tenant (un consultorio) (DD-02).
- NUNCA empezar a codear un change con governance **CRITICO** (`C-02`, `C-03`, `C-17`) sin análisis y aprobación previa → análisis primero, sin código sin confirmación.
- NUNCA commitear/buildear/deployar sin pedido explícito del usuario; commits en Conventional Commits y sin co-autoría IA.

**Lenguaje**

- NUNCA texto de UI/API en inglés → español rioplatense (voseo) en toda la interfaz y los mensajes.

---

## Flujo de Trabajo

```
1. Leer la KB relevante (knowledge-base/)        → entender el dominio
2. Identificar el change en CHANGES.md           → respetar dependencias y governance
3. /opsx:propose C-NN-nombre                     → proposal + design + specs + tasks
4. Implementar las tasks (cargando skills)       → respetando las reglas duras
5. /opsx:archive C-NN-nombre + marcar [x]        → cerrar el change
```

Aplicar TODAS las reglas duras en cada paso. Ante conflicto entre la KB y este archivo, las reglas duras prevalecen.
