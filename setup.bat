@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   CASHIER APP - RENAL: SETUP SCRIPT
echo ==========================================
echo.

:: 1. Check Requirements
echo [1/4] Checking requirements...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed. Please install Python 3.9+ and try again.
    pause
    exit /b
)

node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js and try again.
    pause
    exit /b
)
echo Requirements met.
echo.

:: Detect local IP address (skip loopback, link-local, and virtual adapter ranges)
for /f %%i in ('powershell -nologo -command "(Get-NetIPAddress -AddressFamily IPv4 -Type Unicast | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -notlike '192.168.255.*' } | Sort-Object -Property InterfaceIndex | Select-Object -First 1).IPAddress"') do set LOCAL_IP=%%i
if "%LOCAL_IP%"=="" set LOCAL_IP=localhost
echo Detected local IP: %LOCAL_IP%
echo.

:: 2. Setup Backend
echo [2/4] Setting up Backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Installing backend dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file...
    copy .env.example .env
)

echo Running database migrations...
alembic upgrade head

echo Seeding initial data...
python seed.py

cd ..
echo Backend setup complete.
echo.

:: 3. Setup Frontend
echo [3/4] Setting up Frontend...
cd frontend

echo Installing frontend dependencies...
call npm install

echo Writing .env.local...
echo NEXT_PUBLIC_API_URL=http://localhost:8000>.env.local

echo Building frontend (this may take a minute)...
call npm run build

cd ..
echo Frontend setup complete.
echo.

:: 4. Finalize
echo [4/4] Finalizing...
echo ==========================================
echo   SETUP COMPLETE!
echo.
echo   Run "start.bat" to launch the app.
echo.
echo   Access from this PC:   http://localhost:3000
echo   Access from phone/PC:  http://%LOCAL_IP%:3000
echo   (phone must be on the same Wi-Fi)
echo ==========================================
pause
