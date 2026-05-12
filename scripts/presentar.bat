@echo off
cd /d "%~dp0.."

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /R "IPv4"') do set "ip=%%a"
set "ip=%ip: =%"

echo ============================================
echo   MelodyBox - Modo Presentacion
echo ============================================
echo.
echo  Local:   http://localhost:8001
echo  Red:     http://%ip%:8001
echo.
echo  Presiona Ctrl+C para detener
echo ============================================
echo.

docker compose up --build
pause
