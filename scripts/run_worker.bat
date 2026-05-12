@echo off
cd /d "%~dp0.."
echo ============================================
echo   MelodyBox - Worker (ARQ)
echo ============================================
echo.
if not exist ".venv\" (
    echo Error: No se encontro el entorno virtual (.venv)
    pause
    exit /b 1
)
echo Starting ARQ worker...
echo.
cd src
.venv\Scripts\python.exe -m arq worker.WorkerSettings
pause
