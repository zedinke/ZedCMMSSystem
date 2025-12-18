@echo off
REM =========================================================
REM ANDROID CMMS MVP - AUTOMATED BUILD & RUN SCRIPT
REM =========================================================
REM Ezt a script-et a projekt mappában kell futtatni:
REM E:\Artence_CMMS\AndroidApp\
REM =========================================================

setlocal enabledelayedexpansion
color 0A
cls

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   ANDROID CMMS MVP - BUILD & EMULATOR AUTOMATION      ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM =========================================================
REM STEP 1: Check Gradle
REM =========================================================
echo [1/5] Gradle ellenőrzése...
if not exist gradlew.bat (
    echo ❌ HIBA: gradlew.bat nem található!
    echo    Biztos, hogy az AndroidApp mappában vagy?
    pause
    exit /b 1
)
echo ✅ Gradle OK

REM =========================================================
REM STEP 2: Clean Build
REM =========================================================
echo.
echo [2/5] Clean build...
call gradlew.bat clean
if errorlevel 1 (
    echo ❌ Clean sikertelen!
    pause
    exit /b 1
)
echo ✅ Clean OK

REM =========================================================
REM STEP 3: Build Debug APK
REM =========================================================
echo.
echo [3/5] Debug APK buildelése...
call gradlew.bat assembleDebug
if errorlevel 1 (
    echo ❌ Build sikertelen!
    pause
    exit /b 1
)
echo ✅ Build OK

REM =========================================================
REM STEP 4: Check Emulator
REM =========================================================
echo.
echo [4/5] Emulator ellenőrzése...
adb devices > nul 2>&1
if errorlevel 1 (
    echo ⚠️  ADB nem elérhető - kézzel kell indítani az emulatort
    echo.
    echo Emulator indítása a Device Manager-ből:
    echo   Tools ^> Device Manager ^> Launch in Emulator
    echo.
    echo Vagy parancssorból:
    echo   emulator -avd "Pixel 7 Pro API 34"
    echo.
    pause
) else (
    echo ✅ ADB OK
)

REM =========================================================
REM STEP 5: Install & Run
REM =========================================================
echo.
echo [5/5] APK telepítése...
adb install -r app\build\outputs\apk\debug\app-debug.apk
if errorlevel 1 (
    echo ❌ Telepítés sikertelen!
    echo.
    echo Ellenőrizd:
    echo   1. Emulator fut-e? (Device Manager-ből indítsd)
    echo   2. Eszköz csatlakozik-e? (adb devices)
    pause
    exit /b 1
)
echo ✅ Telepítés OK

REM =========================================================
REM STEP 6: Launch App
REM =========================================================
echo.
echo [6/6] Alkalmazás indítása...
adb shell am start -n com.artence.cmms/.ui.screens.login.LoginActivity
timeout /t 2

REM =========================================================
REM SUCCESS
REM =========================================================
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              ✅ BUILD & INSTALL SIKERES!              ║
echo ╠════════════════════════════════════════════════════════╣
echo ║                                                        ║
echo ║  Alkalmazás az emulator-on fut!                        ║
echo ║                                                        ║
echo ║  LOGIN ADATOK:                                         ║
echo ║  ├─ Email: admin@example.com                           ║
echo ║  └─ Password: Admin123456                              ║
echo ║                                                        ║
echo ║  LOGCAT (valós idejű naplók):                         ║
echo ║  ├─ Nyisd meg az Android Studio-t                      ║
echo ║  └─ View ^> Tool Windows ^> Logcat                     ║
echo ║                                                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.
pause

