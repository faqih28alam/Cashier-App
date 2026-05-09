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

if not exist .env.local (
    echo Creating .env.local...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000> .env.local
)

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
echo   You can now start the application by 
echo   running "start.bat"
echo ==========================================
pause
