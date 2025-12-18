@echo off
REM MySQL Optimalizálás Alkalmazása - Windows Script
REM FONTOS: Futtasd Administrator-ként!

echo ==========================================
echo MySQL Szerver Optimalizálás Alkalmazása
echo ==========================================
echo.

REM Backup készítése
echo 1. Backup készítése a jelenlegi konfigról...
set MYSQL_CONFIG=C:\ProgramData\MySQL\MySQL Server 8.0\my.ini
if exist "%MYSQL_CONFIG%" (
    copy "%MYSQL_CONFIG%" "%MYSQL_CONFIG%.backup.%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
    echo    ✓ Backup készült
) else (
    echo    ⚠ MySQL konfigurációs fájl nem található: %MYSQL_CONFIG%
    echo    Keresd meg a my.ini fájlt és módosítsd manuálisan!
    pause
    exit /b 1
)

REM Konfiguráció alkalmazása
echo.
echo 2. Optimalizált konfiguráció alkalmazása...
echo    FONTOS: Ellenőrizd az innodb_buffer_pool_size értékét!
echo    Módosítsd a fájlban a RAM méretéhez igazítva.
echo.
echo    A konfigurációs fájl: installer\mysql_optimized_config.ini
echo    Másold át a tartalmát a %MYSQL_CONFIG% fájlba!
echo.
pause

REM MySQL újraindítása
echo.
echo 3. MySQL újraindítása...
net stop MySQL80
if %errorlevel% neq 0 (
    echo    ✗ Hiba a MySQL leállítása során!
    echo    Visszaállítás: copy "%MYSQL_CONFIG%.backup.*" "%MYSQL_CONFIG%"
    pause
    exit /b 1
)

timeout /t 3 /nobreak >nul

net start MySQL80
if %errorlevel% neq 0 (
    echo    ✗ Hiba a MySQL indítása során!
    echo    Visszaállítás: copy "%MYSQL_CONFIG%.backup.*" "%MYSQL_CONFIG%"
    pause
    exit /b 1
)

echo    ✓ MySQL sikeresen újraindult

REM Ellenőrzés
echo.
echo 4. MySQL állapot ellenőrzése...
timeout /t 2 /nobreak >nul
sc query MySQL80 | findstr "STATE"

echo.
echo ==========================================
echo ✓ Optimalizálás alkalmazva!
echo ==========================================
echo.
echo Futtasd a következő parancsot az ellenőrzéshez:
echo   python -m utils.mysql_optimizer production
echo.
pause




