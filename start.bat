@echo off
echo Starting Modern Server Administrator...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Start the server administrator
echo Starting server administrator on http://localhost:5000
echo Press Ctrl+C to stop
echo.

python web_server_admin.py

pause