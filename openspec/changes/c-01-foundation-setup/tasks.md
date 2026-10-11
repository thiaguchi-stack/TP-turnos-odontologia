# Tasks

## 1. Estado actual y diagnóstico (delta vs existente)

- [ ] 1.1 Verificar backend existente (main.py, core/config.py, core/__init__.py) para confirmar estructura y evitar duplicados. Verificación: Get-ChildItem backend/app/core backend/app muestra archivos esperados.
- [ ] 1.2 Revisar README actual para decidir dónde añadir instrucciones frontend. Verificación: leer README.md y confirmar ubicación del bloque de arranque.

## 2. Backend - security stub y CORS

- [ ] 2.1 Crear ackend/app/core/security.py (stub) con al menos __init__.py imports sanos (sin lógica auth). Verificación: python -c "from app.core import security; print('ok')" desde ackend/ no falla.
- [ ] 2.2 Modificar ackend/app/main.py para añadir CORS usando astapi.middleware.cors.CORSMiddleware y leer orígenes desde configuración (settings.cors_origins). Verificación: importar app sin error; revisar que endpoints /api/health y handler 400 sigan presentes.

## 3. Configuración - .env.example

- [ ] 3.1 Crear ackend/.env.example con DATABASE_URL, SECRET_KEY, CORS_ORIGINS, TOKEN_EXPIRE_MIN. Valores ficticios, sin secretos reales. Verificación: archivo existe y contiene las variables.
- [ ] 3.2 Crear rontend/.env.example con VITE_API_URL=http://localhost:8000. Verificación: archivo existe con esa clave.

## 4. Frontend scaffold (Vite + React 18 + TS)

- [ ] 4.1 Crear estructura rontend/src/{pages,components,services,shared}. Verificación: directorios creados.
- [ ] 4.2 Crear rontend/package.json con scripts dev, uild, preview, lint (y formato/ts si aplica) y deps base (vite, react@^18, react-dom@^18, react-router-dom, @types/react*, typescript, eslint). Verificación: cat frontend/package.json contiene scripts mínimos.
- [ ] 4.3 Crear rontend/tsconfig.json con modo estricto (sin ny permisivo). Verificación: 	sconfig.json existe y configuración estricto.
- [ ] 4.4 Crear rontend/vite.config.ts con proxy /api hacia http://localhost:8000. Verificación: archivo existe y define proxy.
- [ ] 4.5 Crear rontend/src/services/api.ts wrapper base (fetch) usando import.meta.env.VITE_API_URL o fallback relativo con proxy. Verificación: archivo existe y exporta función/objeto base.
- [ ] 4.6 Crear archivos mínimos para que build/dev no falle (p. ej. rontend/index.html, rontend/src/main.tsx, rontend/src/App.tsx, rontend/src/pages/Home.tsx o stubs mínimos). Verificación: 
pm run build (si deps instaladas) o al menos archivos existen y son válidos.

## 5. Documentación y verificación final

- [ ] 5.1 Actualizar README.md para añadir sección con instrucciones para levantar frontend (cd frontend && npm run dev) junto a backend (uvicorn app.main:app --reload). Mantener español rioplatense. Verificación: README menciona ambos comandos.
- [ ] 5.2 Verificación final: confirmar que ackend/app/core/security.py importa correctamente, CORS configurado en main.py, y archivos frontend mínimos existen según spec. Verificación: ejecutar python -c "from app.core import security; print('ok')" desde ackend/.

## Workflow follow-up

- Validar el change con openspec validate --change c-01-foundation-setup y corregir cualquier fallo antes de archivar.
- Tras validación exitosa, archivar según flujo OPSX.
