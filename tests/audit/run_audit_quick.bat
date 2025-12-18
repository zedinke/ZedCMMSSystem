@echo off
REM CMMS Audit System - Quick Start Script
REM Ez a script gyorsan elindítja a teljes audit rendszert

echo ========================================
echo CMMS COMPREHENSIVE AUDIT SYSTEM
echo ========================================
echo.

REM Ellenőrizni, hogy a virtuális környezet létezik-e
if not exist "..\..\venv_audit" (
    echo Virtuális környezet nem található. Létrehozás...
    cd ..\..
    python -m venv venv_audit
    cd tests\audit
    echo Virtuális környezet létrehozva.
    echo.
)

REM Aktiválás
echo Virtuális környezet aktiválása...
call ..\..\venv_audit\Scripts\activate.bat

REM Requirements telepítés
echo.
echo Függőségek telepítése...
pip install -q -r requirements_audit.txt

if errorlevel 1 (
    echo.
    echo HIBA: Nem sikerült a függőségek telepítése!
    echo Próbáld manuálisan: pip install -r requirements_audit.txt
    pause
    exit /b 1
)

echo.
echo Függőségek telepítve.
echo.

REM Menü
:MENU
echo ========================================
echo AUDIT OPCIÓK
echo ========================================
echo.
echo 1. Teljes audit futtatása (minden kategória)
echo 2. Csak funkcionális tesztek (CRUD)
echo 3. Csak ISO 9001 + ISO 55001 megfelelőség
echo 4. Csak GDPR + biztonsági audit
echo 5. Kategóriák listázása
echo 6. Kilépés
echo.
set /p choice="Válassz egy opciót (1-6): "

if "%choice%"=="1" goto FULL_AUDIT
if "%choice%"=="2" goto FUNCTIONAL
if "%choice%"=="3" goto ISO
if "%choice%"=="4" goto SECURITY
if "%choice%"=="5" goto LIST
if "%choice%"=="6" goto END

echo Érvénytelen választás!
goto MENU

:FULL_AUDIT
echo.
echo ========================================
echo TELJES AUDIT FUTTATÁSA
echo ========================================
echo.
python run_audit.py -v
goto FINISH

:FUNCTIONAL
echo.
echo ========================================
echo FUNKCIONÁLIS TESZTEK
echo ========================================
echo.
python run_audit.py -c functional -v
goto FINISH

:ISO
echo.
echo ========================================
echo ISO MEGFELELŐSÉGI AUDIT
echo ========================================
echo.
python run_audit.py -c iso9001,iso55001 -v
goto FINISH

:SECURITY
echo.
echo ========================================
echo GDPR + BIZTONSÁGI AUDIT
echo ========================================
echo.
python run_audit.py -c gdpr,security -v
goto FINISH

:LIST
echo.
python run_audit.py -l
echo.
goto MENU

:FINISH
echo.
echo ========================================
echo AUDIT BEFEJEZVE
echo ========================================
echo.
echo Jelentések helye: tests\audit\reports\
echo.
echo Szeretnél megnézni egy másik audit kategóriát?
echo.
set /p again="Igen (I) vagy Nem (N): "
if /i "%again%"=="I" goto MENU
if /i "%again%"=="Y" goto MENU

:END
echo.
echo Viszlát!
pause

