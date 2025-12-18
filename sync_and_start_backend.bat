@echo off
REM CMMS Backend Teljes Szinkronizáció és Indítás (SSH Kulcs-alapú)
REM Ez a script SSH kulccsal csatlakozik - JELSZÓ NEM SZÜKSÉGES!

set SSH_KEY=%USERPROFILE%\.ssh\cmms_key
set SSH_HOST=root@116.203.226.140
set SSH_OPTS=-i "%SSH_KEY%" -o StrictHostKeyChecking=no

echo ========================================
echo CMMS Backend Szinkronizáció (SSH Kulcs)
echo ========================================
echo.
echo SSH Kulcs: %SSH_KEY%
echo SSH Host: %SSH_HOST%
echo.

echo 1. API könyvtár feltöltése...
scp -r %SSH_OPTS% E:\Artence_CMMS\CMMS_Project\api %SSH_HOST%:/opt/cmms-backend/
if errorlevel 1 (
    echo HIBA: API feltöltés sikertelen
    pause
    exit /b 1
)

echo 2. Services könyvtár feltöltése...
scp -r %SSH_OPTS% E:\Artence_CMMS\CMMS_Project\services %SSH_HOST%:/opt/cmms-backend/

echo 3. Database könyvtár feltöltése...
scp -r %SSH_OPTS% E:\Artence_CMMS\CMMS_Project\database %SSH_HOST%:/opt/cmms-backend/

echo 4. Config könyvtár feltöltése...
scp -r %SSH_OPTS% E:\Artence_CMMS\CMMS_Project\config %SSH_HOST%:/opt/cmms-backend/

echo 5. Utils könyvtár feltöltése...
scp -r %SSH_OPTS% E:\Artence_CMMS\CMMS_Project\utils %SSH_HOST%:/opt/cmms-backend/

echo 6. Localization könyvtár feltöltése...
scp -r %SSH_OPTS% E:\Artence_CMMS\CMMS_Project\localization %SSH_HOST%:/opt/cmms-backend/

echo.
echo ========================================
echo Fájlok feltöltve! Backend indítása...
echo ========================================
echo.

ssh %SSH_OPTS% %SSH_HOST% "cd /opt/cmms-backend && export PYTHONPATH=/opt/cmms-backend && pkill -9 -f uvicorn 2>/dev/null ; sleep 2 ; /opt/cmms-backend/venv/bin/python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &"

echo.
echo Várunk 8 másodpercet a szerver indulására...
timeout /t 8 >nul

echo.
echo ========================================
echo Backend teszt...
echo ========================================
echo.

curl -s http://116.203.226.140:8000/api/health/

echo.
echo.
echo Ha látsz {"status":"ok"} választ, akkor MŰKÖDIK!
echo.
echo Ellenőrizd:
echo   curl http://116.203.226.140:8000/api/health/
echo.
echo Log megtekintése (SSH kulccsal):
echo   ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no root@116.203.226.140 "tail -f /tmp/backend.log"
echo.
echo Backend újraindítása:
echo   ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no root@116.203.226.140 "pkill -9 -f uvicorn"
echo.

pause

