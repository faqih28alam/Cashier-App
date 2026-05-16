@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   CASHIER APP - RENAL: LAUNCHER
echo ==========================================
echo.

:: Check if setup was run
if not exist "backend\venv" (
    echo Error: Please run setup.bat first!
    pause
    exit /b
)

:: Detect current local IP (skip loopback, link-local, and virtual adapter ranges)
for /f %%i in ('powershell -nologo -command "(Get-NetIPAddress -AddressFamily IPv4 -Type Unicast | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -notlike '192.168.255.*' } | Sort-Object -Property InterfaceIndex | Select-Object -First 1).IPAddress"') do set CURRENT_IP=%%i
if "%CURRENT_IP%"=="" set CURRENT_IP=localhost

:: Read configured IP from .env.local
set CONFIGURED_IP=localhost
for /f "tokens=2 delims=/" %%a in ('findstr "NEXT_PUBLIC_API_URL" frontend\.env.local 2^>nul') do set CONFIGURED_IP=%%a
:: strip trailing :8000
for /f "tokens=1 delims=:" %%a in ("%CONFIGURED_IP%") do set CONFIGURED_IP=%%a

:: Warn if IP has changed since last setup
if not "%CURRENT_IP%"=="%CONFIGURED_IP%" (
    echo ==========================================
    echo   WARNING: IP address has changed!
    echo   Was: %CONFIGURED_IP%
    echo   Now: %CURRENT_IP%
    echo.
    echo   Phone access will NOT work until you
    echo   re-run setup.bat to rebuild the app.
    echo ==========================================
    echo.
)

:: Start Backend in a new minimized window
echo Starting Backend (FastAPI)...
cd backend
start "Cashier Backend" /min cmd /c "venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000"
cd ..

:: Start Frontend in a new minimized window
echo Starting Frontend (Next.js)...
cd frontend
start "Cashier Frontend" /min cmd /c "npm run start"
cd ..

:: Wait for services to warm up
echo Waiting for services to start...
timeout /t 8 /nobreak

:: Open the browser
echo Opening Cashier App...
start http://localhost:3000

echo.
echo ==========================================
echo   SYSTEM IS RUNNING
echo.
echo   Access from this PC:   http://localhost:3000
echo   Access from phone/PC:  http://%CURRENT_IP%:3000
echo   (phone must be on the same Wi-Fi)
echo.
echo   Backend API: http://%CURRENT_IP%:8000
echo.
echo   Keep this window open.
echo   Close this window to stop the app.
echo ==========================================
pause

:: Kill background processes on close
echo Shutting down...
taskkill /FI "WINDOWTITLE eq Cashier Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Cashier Frontend*" /F >nul 2>&1
exit
