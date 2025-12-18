@echo off
REM CMMS Android App - Telefonra Telepítő Script
REM Ez a script lefordítja és telepíti az appot az Android telefonra

echo ========================================
echo CMMS Android - Telefonra Telepítés
echo ========================================
echo.

REM Ellenőrizz, hogy van-e csatlakoztatott telefon
echo Telefonok keresése...
adb devices | findstr /v "List" | findstr /v "^$" > nul

if errorlevel 1 (
    echo.
    echo HIBA: Nincs csatlakoztatott Android telefon!
    echo.
    echo Ellenőrizd:
    echo 1. USB kábellel csatlakoztattad-e a telefonod?
    echo 2. USB Debugging engedélyezve van-e?
    echo 3. Az adb devices parancs működik-e?
    echo.
    pause
    exit /b 1
)

echo Csatlakoztatott eszközök:
adb devices
echo.

REM Build
echo ========================================
echo APK FORDÍTÁSA...
echo ========================================
echo.

cd E:\Artence_CMMS\AndroidApp

echo Build indítása (Debug mód)...
gradlew.bat assembleDebug

if errorlevel 1 (
    echo.
    echo HIBA: Build sikertelen!
    echo Nézd meg a hibaüzenetet fent.
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Build sikeres!
echo.

REM Telepítés
echo ========================================
echo TELEPÍTÉS A TELEFONRA...
echo ========================================
echo.

echo Telepítés indítása...
gradlew.bat installDebug

if errorlevel 1 (
    echo.
    echo HIBA: Telepítés sikertelen!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ TELEPÍTÉS SIKERES!
echo ========================================
echo.
echo Az alkalmazás telepítve van a telefonodra!
echo.
echo Következő lépések:
echo 1. Nyisd meg az alkalmazásokat
echo 2. Keresd az "CMMS" appot
echo 3. Indítsd el az alkalmazást
echo 4. Login: a.geleta / Gele007ta
echo.
echo Tesztelési útmutató: PHONE_TESTING_GUIDE.md
echo.

pause

