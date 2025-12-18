@echo off
REM Build script for Zed CMMS System Installer
REM This script builds CMMS.exe, Updater.exe, and the installer

echo ========================================
echo Zed CMMS System - Telepito Build Script
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "CMMS_Project" (
    echo HIBA: CMMS_Project mappa nem talalhato!
    echo Futtassa ezt a scriptet az E:\Artence_CMMS mappaban.
    pause
    exit /b 1
)

REM Navigate to CMMS_Project directory
cd CMMS_Project

REM Check if virtual environment exists
if not exist ".venv" (
    echo FIGYELMEZTETES: Virtual environment nem talalhato (.venv mappa)
    echo A build folytatodik, de lehet, hogy hibak lesznek.
    echo.
) else (
    echo Virtual environment aktivalasa...
    call .venv\Scripts\activate.bat
    if errorlevel 1 (
        echo HIBA: Virtual environment aktivalas sikertelen!
        pause
        exit /b 1
    )
    echo Virtual environment aktivalva.
    echo.
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo HIBA: Python nem talalhato!
    echo Telepitse a Python-t vagy aktivalja a virtual environment-et.
    pause
    exit /b 1
)

REM Run the build script
echo Build script futtatasa...
echo.
python build_installer.py

REM Check if build was successful
if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD SIKERTELEN!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SIKERES!
echo ========================================
echo.
echo A telepito fajl megtalalhato:
echo installer\ZedCMMS_Setup_v*.exe
echo.
pause

