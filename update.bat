@echo off
setlocal

set INSTALL_DIR=%~dp0
if "%INSTALL_DIR:~-1%"=="\" set INSTALL_DIR=%INSTALL_DIR:~0,-1%

echo ==========================================
echo   CASHIER APP - RENAL: UPDATE SCRIPT
echo ==========================================
echo.

:: Stop running app first
echo [1/4] Stopping running app (if any)...
taskkill /FI "WINDOWTITLE eq Cashier Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Cashier Frontend*" /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo Done.
echo.

:: Download and apply latest code
echo [2/4] Downloading latest update...

if exist "%INSTALL_DIR%\.git" (
    git -C "%INSTALL_DIR%" pull origin main
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: git pull failed. Check internet connection.
        pause
        exit /b 1
    )
) else (
    powershell -ExecutionPolicy Bypass -File "%INSTALL_DIR%\update_helper.ps1" -InstallDir "%INSTALL_DIR%"
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Download or extraction failed. See messages above.
        pause
        exit /b 1
    )
)
echo Update downloaded.
echo.

:: Update backend dependencies and run migrations
echo [3/4] Updating backend...
cd /d "%INSTALL_DIR%\backend"
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not activate Python virtual environment.
    pause
    exit /b 1
)
pip install -r requirements.txt --quiet
alembic upgrade head
cd /d "%INSTALL_DIR%"
echo Backend updated.
echo.

:: Rebuild frontend
echo [4/4] Rebuilding frontend...
cd /d "%INSTALL_DIR%\frontend"
call npm install --silent
call npm run build
cd /d "%INSTALL_DIR%"
echo Frontend updated.
echo.

echo ==========================================
echo   UPDATE COMPLETE!
echo.
echo   Run "start.bat" to launch the app.
echo ==========================================
pause
