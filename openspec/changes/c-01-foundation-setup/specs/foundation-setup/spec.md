# Spec Delta

## Purpose

Completar el scaffolding mínimo del monorepo: backend con CORS configurable y stub de seguridad; frontend Vite + React 18 + TypeScript con estructura, proxy API y api.ts base; archivos .env.example; y tooling/scripts documentados, sin reescribir lo ya existente.

## ADDED Requirements

### Requirement: Estructura monorepo base
El sistema DEBE mantener/establecer la estructura base acordada: ackend/app/{core,models,schemas,services,routers,db} y ackend/tests/ ya existentes se conservan; rontend/src/{pages,components,services,shared} DEBE existir. El scaffold NO DEBE duplicar archivos ya presentes.

#### Scenario: Estructura frontend creada
- WHEN: se inicializa el scaffolding frontend
- THEN: deben existir rontend/src/pages, rontend/src/components, rontend/src/services, rontend/src/shared
- AND: NO DEBEN sobreescribirse archivos backend existentes (app/main.py, app/core/config.py, modelos/servicios/routers ya presentes)

### Requirement: Backend core - security stub
El backend DEBE tener pp/core/security.py con un stub mínimo que permita importar sin errores. Puede exponer interfaces mínimas para futuras fases (C-03) pero NO DEBE implementar lógica de autenticación/JWT aún.

#### Scenario: Importa security stub
- WHEN: se importa pp.core.security
- THEN: la importación DEBE tener éxito
- AND: NO DEBE contener secretos ni credenciales

### Requirement: Backend - CORS configurable
pp/main.py DEBE habilitar CORS leyendo orígenes permitidos desde configuración (settings.cors_origins). El valor DEBE poder venir de CORS_ORIGINS (separados por coma) en entorno, con valores por defecto razonables para dev.

#### Scenario: CORS habilitado desde config
- WHEN: se inicia la app FastAPI
- THEN: el middleware CORS DEBE estar registrado usando settings.cors_origins
- AND: los endpoints existentes (/api/health, validación) DEBEN seguir funcionando

### Requirement: Configuración - .env.example backend
DEBE existir ackend/.env.example con al menos: DATABASE_URL, SECRET_KEY, CORS_ORIGINS, TOKEN_EXPIRE_MIN. Debe ser suficiente para iniciar la app en desarrollo (SQLite por defecto). NO DEBE contener valores reales.

#### Scenario: Backend .env.example presente
- WHEN: se revisa el repo
- THEN: ackend/.env.example DEBE existir y listar las variables requeridas

### Requirement: Configuración - .env.example frontend
DEBE existir rontend/.env.example con VITE_API_URL apuntando al backend en desarrollo (http://localhost:8000).

#### Scenario: Frontend .env.example presente
- WHEN: se revisa el repo
- THEN: rontend/.env.example DEBE existir con VITE_API_URL

### Requirement: Frontend scaffold Vite + React 18 + TS
DEBE existir rontend/package.json con dependencias para ite, eact@^18, eact-dom@^18, eact-router-dom, tipos y tooling (typescript, eslint, prettier si configurado). Los scripts DEBEN incluir dev, uild, preview, lint.

#### Scenario: Frontend scripts disponibles
- WHEN: se consulta scripts en rontend/package.json
- THEN: DEBE incluir dev, uild, preview
- AND: configuración TypeScript estricto (tsconfig sin ny permisivo) o equivalente

### Requirement: Proxy API y api.ts base
rontend/vite.config.ts DEBE configurar proxy de /api a http://localhost:8000. rontend/src/services/api.ts DEBE proveer un wrapper base (fetch) preparado para futuras fases (sin lógica de auth aún). NO DEBE romper imports.

#### Scenario: Proxy y api base presentes
- WHEN: se inspeccionan archivos frontend
- THEN: ite.config.ts DEBE definir proxy /api → backend
- AND: src/services/api.ts DEBE existir y exportar un wrapper base

### Requirement: Scripts de arranque documentados
README (o documentación equivalente) DEBE incluir instrucciones para levantar frontend con 
pm run dev junto con backend (uvicorn app.main:app --reload). El texto DEBE estar en español rioplatense.

#### Scenario: README menciona frontend dev
- WHEN: se lee README.md
- THEN: DEBE mencionar cd frontend && npm run dev o equivalente
- AND: mantener coherencia con stack KB

## MODIFIED Requirements
*(ninguno)*

## REMOVED Requirements
*(ninguno)*

## RENAMED Requirements
*(ninguno)*
