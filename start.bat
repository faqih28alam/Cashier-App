@echo off
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
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:8000
echo.
echo   Keep this window open to stop the app.
echo ==========================================
pause

:: Kill background processes on close
echo Shutting down...
taskkill /FI "WINDOWTITLE eq Cashier Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Cashier Frontend*" /F >nul 2>&1
exit
