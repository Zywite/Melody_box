---
plan name: cleanup-project-structure
plan description: Clean project structure issues
plan status: done
---

## Idea
Limpiar la estructura del proyecto MelodyBox para eliminar ruido (artefactos, carpetas vacías, archivos fuera de lugar, configuraciones fantasma) y estandarizar la organización. ~12 issues identificados en el audit, clasificados en 3 áreas: (1) mover archivos mal ubicados a su lugar correcto, (2) limpiar .gitignore + eliminar artefactos commiteados, (3) eliminar/renombrar archivos problemáticos. Cada paso es seguro y reversible (git permite ver diff).

## Implementation
- 1. Mover `src/worker.py` a `src/app/worker.py` — actualizar imports en worker.py (rutas relativas) y en app/main.py (import del worker). Verificar que arq WorkerSettings siga funcionando.
- 2. Mover `src/tests/scripts/rate_limit_standalone.py` a `scripts/rate_limit_standalone.py` — archivo de utilidad, no de test. Ajustar paths internos si usa rutas relativas.
- 3. Limpiar `.gitignore` — agregar: `*.egg-info/`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `coverage.xml`, `.venv/`, `frontend/dist/`, `docs/*.aux`, `docs/*.log`, `docs/*.fls`, `docs/*.out`, `docs/*.synctex.gz`, `__pycache__/` (ya debe estar). Luego `git rm --cached` para los artefactos ya commiteados.
- 4. Eliminar `frontend/src/components/auth/`, `playlist/`, `search/`, `upload/` — 4 carpetas vacías sin uso. Verificar que ningún import las referencie.
- 5. Eliminar `public/static/` completo — verificar que no haya referencias en nginx.conf, Dockerfile o index.html. Si hay referencias, actualizarlas.
- 6. Renombrar `src/data/music/africa!.mp3` a `src/data/music/africa.mp3` — quitar el signo de exclamación que rompe scripts shell.
- 7. Eliminar `data/music/` de la raíz del proyecto (vacío, duplicado de `src/data/music/`). Verificar que no haya referencias en config.
- 8. Eliminar `melodybox.egg-info/` del working tree — artefacto de build. Si está en .gitignore post-paso 3, hacer `git rm -r --cached`.
- 9. Limpiar `docs/` de artefactos LaTeX — eliminar archivos .aux, .log, .fls, .out, .synctex.gz. Solo mantener .tex, .md, .pdf, .png, .drawio.
- 10. Eliminar `tsconfig.json` del frontend (proyecto JS, no TS). Opcional: si se planea migrar a TS en el futuro, dejarlo pero agregar `.ts` a `.gitignore.

## Required Specs
<!-- SPECS_START -->
- clean-code-spec
- project-structure-cleanup
<!-- SPECS_END -->