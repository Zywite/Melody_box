@echo off
cd /d "%~dp0.."
echo ============================================
echo   MelodyBox - Server
echo ============================================
echo.
if not exist ".venv\" (
    echo Error: No se encontro el entorno virtual (.venv)
    echo Ejecuta: python -m venv .venv
    echo Luego: .venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)
echo Starting server on http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.
set PYTHONPATH=%CD%\src
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
pause
