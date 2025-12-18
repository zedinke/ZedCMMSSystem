@echo off
setlocal
REM Navigate to project folder
cd /d E:\Artence_CMMS\CMMS_Project

REM Optional: stop any running python main.py processes to avoid conflicts
REM Note: wmic is deprecated in Windows 11, using tasklist instead
for /f "tokens=2" %%A in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH 2^>nul ^| findstr /i "main.py"') do (
  taskkill /PID %%A /F >nul 2>&1
)

REM Start the app using the venv Python
set PYTHONIOENCODING=utf-8
E:\Artence_CMMS\.venv\Scripts\python.exe main.py

REM Pause to keep window open if started by double-click
pause
