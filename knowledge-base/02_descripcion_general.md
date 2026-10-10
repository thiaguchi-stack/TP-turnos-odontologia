# Descripción General

## Stack tecnológico

| Capa | Tecnologías | Versión mínima / Nota |
|------|-------------|-----------------------|
| Frontend | React + Vite | React 18+, Vite 5+ |
| Backend | FastAPI (Python) | Python 3.11+, FastAPI 0.110+ |
| ORM | SQLAlchemy 2.x | Modelo relacional, migraciones (Alembic opcional) |
| Validación | Pydantic 2.x | Schemas de request/response |
| Base de datos | SQLite (dev) / PostgreSQL 15+ (prod opcional) | SQLite para entrega local; Postgres vía cambio de `DATABASE_URL` |
| Autenticación | JWT (OAuth2 password flow) | Tokens Bearer para roles admin/odontólogo |
| Tests | pytest + httpx (TestClient) | Suite unit + integración |
| Lint/format | Ruff (Python), ESLint/Prettier (TS) | Opcional pero recomendado |

## Arquitectura general

```
Paciente (navegador)          Admin / Odontólogo (navegador)
        │                                 │
        ▼                                 ▼
┌─────────────────┐            ┌──────────────────────────┐
│  React + Vite   │  HTTP/JSON │        FastAPI (API)     │
│  (SPA pública:  │───────────▶│  routers → services →    │
│   reserva;      │            │  models (SQLAlchemy)     │
│  + login admin) │◀───────────│  auth JWT, Pydantic      │
└─────────────────┘            └────────────┬─────────────┘
                                            ▼
                                     ┌──────────────┐
                                     │  SQLite / PG │
                                     │  (un tenant) │
                                     └──────────────┘
```

- **Frontend**: SPA con dos zonas — pública (reserva online, sin autenticación) y protegida (login admin/odontólogo, agenda y administración).
- **Backend**: API REST modular por recursos (`profesionales`, `prestaciones`, `sillones`, `turnos`, `bloqueos`, `auth`). Lógica de negocio en capa de servicios para mantener los routers delgados.
- **Persistencia**: single-tenant. SQLite en dev/entrega; el modelo SQLAlchemy permite saltar a Postgres sin reescribir.
- **Decisión clave**: ningún servicio externo en v1 (sin WhatsApp, sin pagos, sin calendarios) — foco en el flujo de turnos.

## Integraciones externas

| Servicio | Propósito | Tipo |
|----------|-----------|------|
| (ninguna en v1) | — | — |

Las integraciones candidatas para v2 (WhatsApp Business API, Mercado Pago, Google Calendar) están documentadas en `10_preguntas_abiertas.md`.

## API REST (resumen)

| Recurso | Métodos | Descripción |
|---------|---------|-------------|
| `/auth/login` | POST | Login admin/odontólogo → JWT |
| `/profesionales` | GET, POST, PUT, DELETE | CRUD de profesionales (admin) |
| `/prestaciones` | GET, POST, PUT | CRUD de prestaciones con duración (admin) |
| `/sillones` | GET, POST, DELETE | Gestión de sillones/boxes del consultorio (admin) |
| `/bloqueos` | GET, POST, DELETE | Bloqueos de agenda por profesional (admin) |
| `/turnos/online/disponibles` | GET | Franjas disponibles para reserva pública |
| `/turnos/online` | POST, DELETE | Reserva/cancelación pública del paciente |
| `/turnos` | GET, POST, PUT | Agenda y gestión de turnos (admin/odontólogo) |
| `/agenda/{profesional_id}/dia|semana` | GET | Vista de agenda por profesional (admin/odontólogo) |