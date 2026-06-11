---
plan name: cleanup-scripts
plan description: Clean scripts directory issues
plan status: done
---

## Idea
The scripts/ directory has 9 files with several issues: setup_db.sql references wrong DB/user names, validate_setup.py has dead code and fragile relative paths, presentar.bat has a spurious pause command and fragile IP parsing, path inconsistencies between worker/server scripts (cd src vs not cd src, %CD% vs relative venv path), mixed Spanish/English naming, and run_worker.sh does cd src but run_server.sh doesn't. All need to be fixed for consistency and correctness.

## Implementation
- 1. Fix setup_db.sql — actualizar usuario/DB a postgres/spotofy, o eliminar si ya no aplica
- 2. Fix validate_setup.py — eliminar lista de tuplas muerta (líneas 120-127) y hacer rutas absolutas desde script_dir
- 3. Fix presentar.bat — quitar pause tras docker compose up, mejorar parsing de IP con wmic o powershell
- 4. Fix presentar.sh — asegurar consistencia con presentar.bat (mismos mensajes, manejo de errores)
- 5. Fix run_worker.bat — unificar ruta del venv (usar %~dp0..\.venv como run_server.bat)
- 6. Fix run_worker.sh — agregar cd src (igual que .bat) o quitar cd src del .sh según decisión
- 7. Fix run_server.sh — hacer cd src antes de uvicorn, o usar --app-dir para consistencia con start_server.py
- 8. Unificar idioma — scripts .bat/.sh y .py todos en español o todos en inglés (o al menos consistente)
- 9. Ejecutar tests y verificar que sigue funcionando todo

## Required Specs
<!-- SPECS_START -->
- cleanup-scripts-spec
<!-- SPECS_END -->