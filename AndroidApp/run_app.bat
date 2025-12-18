@echo off
REM Próbáljuk megtalálni az emulátort és az adb-t

setlocal enabledelayedexpansion

REM Android SDK szokásos helyei
set "ANDROID_SDK_PATHS=C:\Users\%USERNAME%\AppData\Local\Android\Sdk ^
                      C:\Android\Sdk ^
                      %ANDROID_HOME%"

for %%i in (%ANDROID_SDK_PATHS%) do (
    if exist "%%i\platform-tools\adb.exe" (
        set "ADB=%%i\platform-tools\adb.exe"
        set "EMULATOR=%%i\emulator\emulator.exe"
        goto found_sdk
    )
)

:not_found_sdk
echo Android SDK nem található. Kérjük állítsd be az ANDROID_HOME környezeti változót.
exit /b 1

:found_sdk
echo ADB megtalálva: !ADB!
echo Elérhető eszközök:
"!ADB!" devices

echo.
echo Alkalmazás indítása...
"!ADB!" shell am start -n com.artence.cmms/.MainActivity

echo.
echo Logcat indítása (Ctrl+C a leállításhoz):
"!ADB!" logcat

endlocal

