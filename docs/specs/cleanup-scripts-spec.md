# Spec: cleanup-scripts-spec

Scope: feature

# Spec: cleanup-scripts-spec

Scope: feature

# Especificación de Limpieza de Scripts

## Objetivo
Corregir inconsistencias, bugs y código muerto en los 9 archivos de `scripts/`, unificando paths, idioma y comportamiento cross-platform.

## Archivos involucrados

| Archivo | Cambios |
|---|---|
| `scripts/setup_db.sql` | Actualizar usuario/DB a `postgres`/`spotofy`, o marcar como obsoleto |
| `scripts/validate_setup.py` | Eliminar código muerto (líneas 120-127), rutas absolutas con `Path(__file__).parent` |
| `scripts/presentar.bat` | Quitar `pause` innecesario, mejorar parsing de IP con `powershell` |
| `scripts/presentar.sh` | Asegurar mensajes y errores consistentes con el `.bat` |
| `scripts/run_worker.bat` | Unificar ruta del venv (usar `%~dp0..\\.venv` como run_server.bat) |
| `scripts/run_worker.sh` | Decidir y aplicar consistencia en `cd src` entre worker/server |
| `scripts/run_server.sh` | Hacer `cd src` antes de ejecutar uvicorn, o usar `--app-dir` |
| `scripts/run_server.bat` | Sin cambios (funciona correctamente) |

## Criterios de aceptación

- [ ] `setup_db.sql` refleja las credenciales reales del proyecto
- [ ] `validate_setup.py` sin código muerto, ejecutable desde cualquier directorio
- [ ] `presentar.bat` sin `pause` espurio, IP parseada correctamente
- [ ] `run_worker.sh` y `run_server.sh` consistentes en working directory
- [ ] `run_worker.bat` usa mismo formato de ruta que `run_server.bat`
- [ ] Todos los tests pasan después de los cambios