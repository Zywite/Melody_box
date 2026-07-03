# Spec: project-structure-cleanup

Scope: feature

# Especificación: Limpieza de Estructura del Proyecto

## Objetivo
Eliminar ruido, artefactos, archivos mal ubicados y configuraciones obsoletas del proyecto MelodyBox para que la estructura refleje fielmente el código activo.

---

## Paso 1: Mover `worker.py` a `src/app/worker.py`

**Problema:** `src/worker.py` está fuera del paquete `app/`, rompiendo la convención de que todo el código fuente vive dentro de `src/app/`.

**Acción:**
1. Mover archivo a `src/app/worker.py`
2. En `worker.py`: cambiar imports de `app.core.config` a `core.config` (relativo al nuevo location)
3. En `src/app/main.py`: cambiar `from worker import WorkerSettings` a `from app.worker import WorkerSettings`
4. Verificar que `arq` WorkerSettings se importe correctamente

**Verificación:** `python -c "from app.worker import WorkerSettings"` sin errores.

---

## Paso 2: Mover `rate_limit_standalone.py` a `scripts/`

**Problema:** `src/tests/scripts/rate_limit_standalone.py` es una utilidad, no un test. Está dentro de `tests/` incorrectamente.

**Acción:**
1. Mover a `scripts/rate_limit_standalone.py`
2. Ajustar paths internos si usa rutas relativas (revisar si hay imports a `src.app`)
3. Verificar que `tests/scripts/` quede vacío y eliminarlo

**Verificación:** El script `python scripts/rate_limit_standalone.py` funcione sin errores de import.

---

## Paso 3: Limpiar `.gitignore`

**Problema:** Múltiples artefactos de build están commiteados o no ignorados.

**Acción:**
1. Agregar a `.gitignore`:
   - `*.egg-info/`
   - `.pytest_cache/`
   - `.ruff_cache/`
   - `.coverage`
   - `coverage.xml`
   - `.venv/`
   - `frontend/dist/`
   - `docs/*.aux`, `docs/*.log`, `docs/*.fls`, `docs/*.out`, `docs/*.synctex.gz`
   - `__pycache__/` (verificar si ya está)
2. Ejecutar `git rm -r --cached` para cada artefacto ya commiteado
3. Commit de limpieza

**Verificación:** `git status` no muestra archivos de build/coverage/cache.

---

## Paso 4: Eliminar carpetas vacías del frontend

**Problema:** `auth/`, `playlist/`, `search/`, `upload/` dentro de `components/` están vacías.

**Acción:**
1. Eliminar las 4 carpetas
2. Buscar con grep cualquier import que las referencie (ninguna debería existir)

**Verificación:** `rg "@/components/auth/|@/components/playlist/|@/components/search/|@/components/upload/"` sin resultados.

---

## Paso 5: Eliminar `public/static/`

**Problema:** Carpeta legacy no usada por Vite. `public/static/css/style.css` no es referenciado por el frontend actual.

**Acción:**
1. Buscar referencias a `public/static/` o `style.css` en: `nginx.conf`, `Dockerfile`, `index.html`, `main.js`
2. Si no hay referencias (esperado), eliminar `public/static/` completo
3. Si hay referencias, actualizarlas a `frontend/dist/assets/`

**Verificación:** `rg "public/static" --include "*.conf" --include "*.html" --include "*.js"` sin resultados. Build de frontend sigue funcionando.

---

## Paso 6: Renombrar `africa!.mp3`

**Problema:** El `!` en `africa!.mp3` causa problemas en scripts shell y batch.

**Acción:**
1. Renombrar `src/data/music/africa!.mp3` a `src/data/music/africa.mp3`
2. Buscar referencias al nombre original en código o scripts

**Verificación:** No hay referencias al nombre en el código (es data file para pruebas).

---

## Paso 7: Eliminar `data/music/` duplicado en raíz

**Problema:** `data/music/` existe tanto en raíz como en `src/data/music/`. El de raíz está vacío.

**Acción:**
1. Eliminar `data/music/` de la raíz
2. Verificar que ningún script o config referencie `data/music/` (relativo a raíz en vez de `src/data/music/`)

**Verificación:** La app no usa rutas a `data/music/` desde la raíz.

---

## Paso 8: Eliminar `melodybox.egg-info/`

**Problema:** Artefacto de build de setuptools commiteado.

**Acción:**
1. Después de paso 3 (.gitignore actualizado), ejecutar `git rm -r --cached melodybox.egg-info/`

**Verificación:** `git status` limpio para esta carpeta.

---

## Paso 9: Limpiar artefactos LaTeX de `docs/`

**Problema:** 21 archivos `.aux`, `.log`, `.fls`, `.out`, `.synctex.gz` ensucian `docs/`.

**Acción:**
1. Eliminar todos los archivos con esas extensiones en `docs/`
2. Mantener solo: `.tex`, `.md`, `.pdf`, `.png`, `.drawio`

**Verificación:** `Get-ChildItem docs -Recurse -Include *.aux,*.log,*.fls,*.out,*.synctec.gz` devuelve 0 resultados.

---

## Paso 10: Manejar `tsconfig.json`

**Problema:** Config de TypeScript presente pero 0 archivos `.ts`.

**Acción:**
1. Opción A (recomendada): Eliminar `tsconfig.json` y `vue-tsc` de devDependencies
2. Opción B: Conservar si se planea migración futura, pero agregar nota en ARCHITECTURE.md

**Verificación:** `npm run build` sigue funcionando.