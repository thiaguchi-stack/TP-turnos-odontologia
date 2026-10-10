# Arquitectura Propuesta

## Patrones y decisiones de diseño

| Patrón | Aplicación |
|--------|------------|
| **API REST** | Recursos por dominio (`profesionales`, `prestaciones`, `sillones`, `turnos`, `bloqueos`, `auth`); JSON, códigos HTTP semánticos, Pydantic valida request/response. |
| **Capa de servicios** | Los routers de FastAPI quedan delgados; la lógica de negocio (validación de agenda, estados, franjas disponibles) vive en servicios reutilizables y testeables. |
| **Repository/ORM** | SQLAlchemy 2.x (modelos + queries tipadas). Cambio de SQLite → Postgres solo altera `DATABASE_URL`. |
| **SPA con zona pública + privada** | React + react-router; la zona privada exige JWT en cada request (interceptor). |
| **Auth JWT** | Login admin/odontólogo → token Bearer con `sub` (user id) y `rol`; expiración configurable. La cancelación del paciente usa token por turno (sin cuenta). |

## Estructura de directorios

```
backend/
├── app/
│   ├── core/            # config, security (password hash, JWT), deps
│   ├── models/          # SQLAlchemy: usuario, profesional, paciente, prestacion, sillon, turno, bloqueo
│   ├── schemas/         # Pydantic: request/response por recurso
│   ├── services/        # agenda_service (franjas, solapamiento), turno_service, auth_service
│   ├── routers/         # auth, profesionales, prestaciones, sillones, turnos (online + admin), bloqueos
│   ├── db/              # sesion, engine, seed (datos simulados)
│   └── main.py          # creación de la app FastAPI, CORS, mount routers
├── tests/               # pytest: unit (services) + integration (TestClient)
├── pyproject.toml       # deps, ruff
└── .env.example         # DATABASE_URL, SECRET_KEY, CORS_ORIGINS, TOKEN_EXPIRE_MIN

frontend/
├── src/
│   ├── pages/           # Home/Reserva, Agenda, Login, Admin(profesionales/prestaciones/bloqueos)
│   ├── components/      # GrillaDeHorarios, FormTurno, AgendaList, etc.
│   ├── services/        # api.ts (fetch wrapper con JWT), tipos TS
│   └── shared/          # estilos, utils de fecha/hora
├── vite.config.ts       # proxy /api → backend en dev
└── .env.example         # VITE_API_URL
```

## Seguridad

- **Auth**: JWT Bearer obligatorio en toda ruta privada (RN-AU-01); middleware/dependencia de FastAPI verifica `rol` (RN-AU-02/03).
- **Passwords**: hash bcrypt/argon2 (RN-AU-04); nunca se devuelven ni se loguean.
- **Validación de entrada**: Pydantic en backend; los datos de la reserva pública se validan y no permiten inyección de estados arbitrarios (el paciente no elige estado).
- **CORS**: solo orígenes permitidos (frontend dev en `http://localhost:5173`); en la reserva pública no se exponen datos de otros pacientes.
- **Protección de datos de salud**: datos de contacto únicamente en v1 y con consentimiento (RN-DATOS-01/02); sin información clínica en rutas públicas.
- **Secretos**: en `.env`, nunca en el repo (`SECRET_KEY` de JWT, `DATABASE_URL`, etc.).

## Variables de entorno

| Variable | Default (dev) | Descripción |
|----------|---------------|-------------|
| `DATABASE_URL` | `sqlite:///./clinica.db` | Conexión de base de datos |
| `SECRET_KEY` | (generar) | Clave de firma de JWT |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes permitidos |
| `TOKEN_EXPIRE_MIN` | `480` | Expiración del JWT (8 h) |
| `VITE_API_URL` | `/api` (proxy) | URL del backend desde el frontend |

## Estrategia de pruebas (alineada al flujo del TP)

1. **Unit (servicios)**: agenda_service (franjas disponibles, solapamientos por profesional y por sillón), turnos (transiciones de estado), reglas RN-TU-01..09.
2. **Integration (API)**: TestClient de FastAPI — reserva online end-to-end, CRUD agenda, auth por rol, casos de error (409, 400, 403).
3. **Frontend**: smoke manual del flujo de reserva en dev; se documentan pasos de verificación.

## Deploy

- **Entrega TP**: correr localmente (backend `uvicorn`, frontend `npm run dev` con proxy). Opcional: contenedor Docker simple con SQLite para demo.
- **Post-TP (backlog)**: Postgres + deploy en Railway/Render (backend) y Vercel/Netlify (frontend). **No** es parte del alcance v1.0.