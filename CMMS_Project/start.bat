@echo off
setlocal enabledelayedexpansion
REM ========================================
REM CMMS Desktop Application Launcher
REM Portable version - works on any machine
REM ========================================

REM Get the directory where this batch file is located (includes trailing backslash)
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash for cleaner path handling
set "PROJECT_ROOT=%SCRIPT_DIR:~0,-1%"
REM Virtual environment in CMMS_Project\.venv
set "VENV_DIR=%PROJECT_ROOT%\.venv"

REM Verify PROJECT_ROOT is set correctly
if "%PROJECT_ROOT%"=="" (
    echo ERROR: Failed to determine project root directory!
    pause
    exit /b 1
)

REM Navigate to project folder (CMMS_Project)
cd /d "%PROJECT_ROOT%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to navigate to project directory: %PROJECT_ROOT%
    echo.
    echo Please check that the directory exists and you have access to it.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ========================================
    echo ERROR: Python not found!
    echo ========================================
    echo.
    echo Python 3.10 or later is required.
    echo Please install Python from: https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo ========================================
echo CMMS Desktop Application
echo ========================================
echo.
echo Python version:
python --version
echo.

REM Check if virtual environment exists
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo ========================================
    echo Creating virtual environment...
    echo ========================================
    echo.
    
    REM Create virtual environment
    python -m venv "%VENV_DIR%"
    
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    
    echo Virtual environment created successfully!
    echo.
)

REM Check if requirements are installed
echo ========================================
echo Checking dependencies...
echo ========================================
echo.

"%VENV_DIR%\Scripts\python.exe" -c "import flet" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Dependencies not found. Installing...
    echo.
    
    REM Upgrade pip first
    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip --quiet
    
    REM Install requirements
    echo Installing requirements from requirements.txt...
    if not exist "requirements.txt" (
        echo ERROR: requirements.txt not found in: %PROJECT_ROOT%
        echo.
        echo Please make sure you copied the entire CMMS_Project folder.
        pause
        exit /b 1
    )
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt --quiet
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install requirements!
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
    
    echo Dependencies installed successfully!
    echo.
) else (
    echo Dependencies are already installed.
    echo.
)

REM Optional: stop any running python main.py processes to avoid conflicts
echo Stopping any existing CMMS processes...
for /f "tokens=2" %%A in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH 2^>nul ^| findstr /i "main.py"') do (
    taskkill /PID %%A /F >nul 2>&1
)

echo ========================================
echo Starting CMMS Application...
echo ========================================
echo.
echo The FastAPI server will start automatically
echo in the background when the app launches.
echo.
echo API URL: http://localhost:8000
echo Swagger UI: http://localhost:8000/api/docs
echo.
echo ========================================
echo.

REM Start the app using the venv Python
REM The app will automatically start the FastAPI server in background
if not exist "main.py" (
    echo ERROR: main.py not found in: %PROJECT_ROOT%
    echo.
    echo Please make sure you copied the entire CMMS_Project folder.
    pause
    exit /b 1
)
set PYTHONIOENCODING=utf-8
"%VENV_DIR%\Scripts\python.exe" main.py

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo Application exited with error code: %ERRORLEVEL%
    echo ========================================
    echo.
)

REM Pause to keep window open if started by double-click
pause

