@echo off
cd /d "%~dp0.."

for /f "tokens=2 delims=:" %%a in ('powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -ne '' -and $_.IPAddress -notmatch '^127' } | Select-Object -First 1).IPAddress"') do set "ip=%%a"
set "ip=%ip: =%"

echo ============================================
echo   MelodyBox - Presentation Mode
echo ============================================
echo.
echo  Local:   http://localhost:8001
echo  Network: http://%ip%:8001
echo.
echo  Press Ctrl+C to stop
echo ============================================
echo.

docker compose up --build
