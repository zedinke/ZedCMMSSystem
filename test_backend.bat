@echo off
REM CMMS Backend Diagnostics - Batch verzió (ha nincs PowerShell)
REM Ez a script teszteli, hogy a backend szerver elérhető-e

echo.
echo ========================================
echo CMMS Backend Diagnosztika
echo ========================================
echo.

setlocal enabledelayedexpansion

REM 1. HEALTH CHECK
echo 1. Health Check...
echo.
curl -s http://116.203.226.140:8000/api/health/ >nul
if errorlevel 1 (
    echo HIBA: Backend szerver nem elérhető!
    echo.
    echo Nyomj egy gombot...
    pause
    exit /b 1
)

echo OK - Szerver válaszol
echo.

REM 2. LOGIN TESZT
echo 2. Login tesztelése...
echo.

curl -s -X POST http://116.203.226.140:8000/api/v1/auth/login ^
    -H "Content-Type: application/json" ^
    -d "{\"username\":\"a.geleta\",\"password\":\"Gele007ta\"}" > temp_login.json

if errorlevel 1 (
    echo HIBA: Login sikertelen
    del temp_login.json
    pause
    exit /b 1
)

echo Login válasz:
type temp_login.json
echo.

REM Extract token (simple method)
echo.
echo Az alábbi lépéseket MANUÁLISAN végezd el PowerShell-ben az eredmények megtekintéséhez:
echo.
echo Nyisd meg a PowerShell-t és futtasd:
echo   cd E:\Artence_CMMS
echo   powershell -ExecutionPolicy Bypass -File test_backend.ps1
echo.

del temp_login.json

pause

