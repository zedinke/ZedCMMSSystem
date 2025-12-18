@echo off
echo Installing CMMS requirements...
echo.

REM Find Python executable
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH!
    echo Please install Python 3.12 or add it to PATH.
    pause
    exit /b 1
)

echo Using Python:
python --version
python -c "import sys; print(sys.executable)"
echo.

echo Installing requirements from requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install requirements!
    pause
    exit /b 1
)

echo.
echo Checking critical modules...
python -c "import qrcode; print('  [OK] qrcode')" || echo "  [FAIL] qrcode"
python -c "import flet; print('  [OK] flet')" || echo "  [FAIL] flet"
python -c "from passlib.context import CryptContext; print('  [OK] passlib')" || echo "  [FAIL] passlib"
python -c "import sqlalchemy; print('  [OK] sqlalchemy')" || echo "  [FAIL] sqlalchemy"

echo.
echo Installation complete!
pause

