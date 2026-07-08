@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   CASHIER APP - RENAL: RESTORE DATABASE
echo ==========================================
echo.

set SOURCE=%~1

if "%SOURCE%"=="" (
    echo Usage: drag-and-drop the backup .db file onto this script,
    echo        or run: loadDB.bat "C:\path\to\backup.db"
    echo.
    set /p SOURCE="Enter full path to the backup .db file: "
)

if not exist "%SOURCE%" (
    echo Error: File not found: %SOURCE%
    pause
    exit /b
)

:: Basic sanity check - must be a real SQLite file
for /f "delims=" %%i in ('powershell -nologo -command "$b=[System.IO.File]::ReadAllBytes('%SOURCE%'); if ($b.Length -lt 16) { 'no' } else { $h=[System.Text.Encoding]::ASCII.GetString($b[0..15]); if ($h -eq 'SQLite format 3') { 'yes' } else { 'no' } }"') do set IS_SQLITE=%%i

if not "%IS_SQLITE%"=="yes" (
    echo Error: "%SOURCE%" does not look like a valid SQLite database file.
    echo Aborting - nothing was changed.
    pause
    exit /b
)

echo.
echo This will REPLACE the current cashier.db with:
echo   %SOURCE%
echo.
echo The app will be stopped first. The current database will be
echo saved as a backup before it gets replaced.
echo.
set /p CONFIRM="Type YES to continue: "
if /i not "%CONFIRM%"=="YES" (
    echo Cancelled. Nothing was changed.
    pause
    exit /b
)

echo.
echo [1/4] Stopping app...
taskkill /FI "WINDOWTITLE eq Cashier Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Cashier Frontend*" /F >nul 2>&1
timeout /t 3 /nobreak >nul

echo [2/4] Backing up current database...
for /f %%i in ('powershell -nologo -command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
if exist "backend\cashier.db" (
    copy /y "backend\cashier.db" "backend\cashier_before_restore_%TS%.db" >nul
    echo   Saved as backend\cashier_before_restore_%TS%.db
) else (
    echo   No existing cashier.db found, skipping.
)

echo [3/4] Restoring database...
copy /y "%SOURCE%" "backend\cashier.db" >nul
if %errorlevel% neq 0 (
    echo Error: Failed to copy the backup file. Nothing was overwritten if this failed before copying.
    pause
    exit /b
)

echo [4/4] Done.
echo.
echo ==========================================
echo   RESTORE COMPLETE
echo   Run start.bat to launch the app.
echo ==========================================
pause
