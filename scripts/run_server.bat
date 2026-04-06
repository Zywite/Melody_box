@echo off
cd /d "%~dp0.."
echo ============================================
echo   MelodyBox - Server
echo ============================================
echo.
echo Starting server on http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
pause
