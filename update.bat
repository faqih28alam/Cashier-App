@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   CASHIER APP - RENAL: UPDATE SCRIPT
echo ==========================================
echo.

:: Check git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Git is not installed. Please install Git and try again.
    pause
    exit /b
)

:: Stop running app first
echo [1/4] Stopping running app (if any)...
taskkill /FI "WINDOWTITLE eq Cashier Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Cashier Frontend*" /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo Done.
echo.

:: Pull latest code
echo [2/4] Downloading latest update...
git pull origin main
if %errorlevel% neq 0 (
    echo Error: Failed to download update. Check your internet connection.
    pause
    exit /b
)
echo Update downloaded.
echo.

:: Update backend
echo [3/4] Updating Backend...
cd backend
call venv\Scripts\activate
pip install -r requirements.txt --quiet
alembic upgrade head
cd ..
echo Backend updated.
echo.

:: Rebuild frontend
echo [4/4] Rebuilding Frontend...
cd frontend
call npm install --silent
call npm run build
cd ..
echo Frontend updated.
echo.

echo ==========================================
echo   UPDATE COMPLETE!
echo.
echo   Run "start.bat" to launch the app.
echo ==========================================
pause
