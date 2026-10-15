# Verify — `c-01-foundation-setup`

Verificación del change archivado en `openspec/changes/archive/2026-10-15-c-01-foundation-setup/`, contra la spec vigente `openspec/specs/foundation-setup/spec.md` (7 requirements, 8 escenarios).

No existe un comando propio de verify en OPSX: la verificación se hizo corriendo la suite y el lint del repo, mapeando cada requirement/escenario contra los tests existentes (`backend/tests/test_foundation.py`) y contra los archivos implementados (backend/frontend). Todo en español rioplatense.

- **Fecha de la corrida:** 2026-10-15 (misma fecha de corrida de los runners utilizados para las salidas adjuntas).
- **Entorno:** `backend\.venv` (Python 3.14.7), SQLite en memoria (usado por la suite).
- **Salidas crudas (combinadas para C-01+C-02):** [pytest-c-01-c-02-modelos.txt](pytest-c-01-c-02-modelos.txt) · [ruff-c-01-c-02-modelos.txt](ruff-c-01-c-02-modelos.txt)

---

## 1. Comandos ejecutados y salida real

Desde la raíz del repo:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -v
```

Resumen real (última línea del `pytest-c-01-c-02-modelos.txt`):

```
======================= 112 passed, 1 warning in 11.15s =======================
```

La única warning es `StarletteDeprecationWarning` del framework FastAPI/TestClient (no del código del repo).

```powershell
backend\.venv\Scripts\ruff.exe check backend
backend\.venv\Scripts\ruff.exe format --check backend
```

Salida real relevante (completa en `ruff-c-01-c-02-modelos.txt`):

```
$ backend\.venv\Scripts\ruff.exe check backend
All checks passed!
$ backend\.venv\Scripts\ruff.exe format --check backend
53 files already formatted
```

**Nota:** la primera corrida de esta evidencia detectó 5 archivos sin formatear (heredados de la implementación de C-02). Se aplicó `ruff format backend` y se regeneró la salida: `format --check` queda en exit 0. `ruff check` (lint) pasó siempre al 100 %.

---

## 2. Trazabilidad: spec foundation-setup → implementación y tests

Fuente: [openspec/specs/foundation-setup/spec.md](../../openspec/specs/foundation-setup/spec.md). El mapeo se hace hacia código/config y hacia `backend/tests/test_foundation.py` (que cubre CORS, import de security y valores por defecto).

### Requirement: Estructura monorepo base
| Escenario | Verificación (test o archivo) | Ruta:línea |
|---|---|---|
| Estructura frontend creada; backend existente no se sobreescribe | Directorios creados: `frontend/src/pages`, `frontend/src/components`, `frontend/src/services`, `frontend/src/shared`. Archivos backend existentes conservados: `app/main.py`, `app/core/config.py`, `app/core/security.py`. | `frontend/src/pages/` · `frontend/src/components/` · `frontend/src/services/` · `frontend/src/shared/` · `backend/app/main.py:1` · `backend/app/core/config.py:1` · `backend/app/core/security.py:1` |

### Requirement: Backend core - security stub
| Escenario | Verificación (test o archivo) | Ruta:línea |
|---|---|---|
| Importa `app.core.security` con éxito; sin secretos | `test_security_stub_importa_sin_error()` (importa módulo). `test_security_stub_lee_secret_key_de_config()` valida que `security.get_secret_key()` lee `settings.secret_key`. Stub implementado con docstrings en español; no expone secretos. | `backend/tests/test_foundation.py:10` · `backend/tests/test_foundation.py:15` · `backend/app/core/security.py:35` |

### Requirement: Backend - CORS configurable
| Escenario | Verificación (test o archivo) | Ruta:línea |
|---|---|---|
| CORS habilitado desde config; endpoints siguen funcionando | `test_cors_default_incluye_localhost_frontend()` valida defaults (localhost:5173). `test_cors_origins_parsea_lista_separada_por_coma()` valida parseo de CORS_ORIGINS separados por coma. `test_cors_middleware_permite_origen_configurado()` verifica headers CORS para origen permitido vía TestClient (`/api/health` devuelve 200 con ACAO). `test_cors_middleware_omite_origen_no_permitido()` verifica que origen no permitido no devuelve ACAO pero sigue respondiendo 200. Middleware registrado en `main.py` usando `settings.cors_origins`. | `backend/tests/test_foundation.py:22` · `backend/tests/test_foundation.py:31` · `backend/tests/test_foundation.py:39` · `backend/tests/test_foundation.py:51` · `backend/app/main.py:23-29` · `backend/app/core/config.py:13-23` |

### Requirement: Configuración - .env.example backend
| Escenario | Verificación (test o archivo) | Ruta:línea |
|---|---|---|
| `.env.example` backend presente con variables requeridas | `backend/.env.example` contiene: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `TOKEN_EXPIRE_MIN` (valores ficticios, sin secretos). | `backend/.env.example:1-13` |

### Requirement: Configuración - .env.example frontend
| Escenario | Verificación (test o archivo) | Ruta:línea |
|---|---|---|
| `.env.example` frontend presente con `VITE_API_URL` | `frontend/.env.example` contiene `VITE_API_URL=http://localhost:8000`. | `frontend/.env.example:2` |

### Requirement: Frontend scaffold Vite + React 18 + TS
| Escenario | Verificación (test o archivo) | Ruta:línea |
|---|---|---|
| Scripts dev/build/preview; tsconfig estricto | `frontend/package.json` incluye `dev`, `build`, `preview`, `lint`, `format`, `format:check`, `typecheck`. Dependencias: `react@^18.3.1`, `react-dom@^18.3.1`, `react-router-dom@^6.26.2`, `vite@^5.4.6`, `typescript@^5.6.2`, `eslint@^9.10.0`, `prettier@^3.3.3`. `frontend/tsconfig.json` con `"strict": true`. | `frontend/package.json:6-14` · `frontend/package.json:15-34` · `frontend/tsconfig.json:10` |

### Requirement: Proxy API y api.ts base
| Escenario | Verificación (test o archivo) | Ruta:línea |
|---|---|---|
| `vite.config.ts` define proxy `/api → http://localhost:8000`; `api.ts` existe y exporta wrapper base | Proxy configurado con `target: "http://localhost:8000"`, `changeOrigin: true`. `frontend/src/services/api.ts` exporta `apiFetch<T>(ruta, opciones)` usando `import.meta.env.VITE_API_URL ?? ""` y hace fetch con JSON. | `frontend/vite.config.ts:8-13` · `frontend/src/services/api.ts:1-20` |

### Requirement: Scripts de arranque documentados
| Escenario | Verificación (test o archivo) | Ruta:línea |
|---|---|---|
| README menciona levantar frontend con `npm run dev` junto a backend (`uvicorn app.main:app --reload`); texto en español rioplatense | `README.md` incluye: `cd frontend && npm run dev` y `backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend` (y variantes). Texto en español rioplatense. | `README.md:144-160` · `README.md:110-140` |

---

## 3. Huecos y salvedades

1. **Sin frontend UI ejecutada en runtime para capturas:** C-01 crea scaffold + archivos mínimos (App.tsx, main.tsx, index.html, Home.tsx, date utils). No hay pantallas funcionales de negocio aún (llegan con C-11+). `docs/evidencias/capturas/` **sigue pendiente** (estado ya indicado en `README.md`).
2. **Formateo ruff (format --check):** resuelto durante la generación de esta evidencia: se detectaron 5 archivos heredados sin formatear, se aplicó `ruff format backend` y `format --check` quedó limpio (53 files already formatted). `ruff check` pasa 100 %.
3. **Trazabilidad a tests:** C-01 cuenta con `test_foundation.py` que cubre CORS, import de security, config. Estructura/frontend/.env no tienen tests unitarios (son requisitos de presencia/config de scaffold) — la verificación es directa por archivo + escenarios (adecuado para scaffolding).
4. **No hay mypy específico para C-01 nuevo:** mypy ya tiene archivo `mypy-backend.txt` con salida limpia del repo completo (28 archivos). No se duplica.

---

## 4. Estado final

| Control | Resultado |
|---|---|
| `pytest backend\tests -v` | **112 passed, 0 failed, 0 skipped**, 1 warning (framework). |
| `ruff check backend` | **`All checks passed!`** (exit 0). |
| `ruff format --check backend` | **53 files already formatted** (exit 0; se aplicó `ruff format` a los 5 heredados durante esta evidencia). |
| Trazabilidad spec → implementación/tests | **7/7 requirements, 8/8 escenarios** verificados (estructura, security, CORS, .env, scaffold, proxy/api, docs). |
| Tasks del change (`tasks.md`) | **31/31** marcadas `[x]`, 0 abiertas. |
| Commits de esta evidencia | **ninguno durante la corrida**; el formateo y esta evidencia se commitean junto con el pedido de sincronización del usuario. |