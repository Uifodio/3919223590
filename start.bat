@echo off
title Modern Server Administrator - Production Server
color 0A
cls

echo.
echo  ================================================================
echo  |                                                              |
echo  |           MODERN SERVER ADMINISTRATOR v2.0                  |
echo  |                    PRODUCTION SERVER                        |
echo  |                                                              |
echo  ================================================================
echo.

REM Check if Python is available
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [ERROR] Please install Python 3.7+ and try again
    echo.
    echo [INFO] Download Python from: https://www.python.org/downloads/
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python is available
echo.

REM Check if required packages are installed
echo [INFO] Checking required packages...
python -c "import flask, werkzeug, psutil" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Some packages are missing, installing...
    echo [INFO] Installing Flask, Werkzeug, and psutil...
    pip install flask werkzeug psutil
    if errorlevel 1 (
        echo [ERROR] Failed to install required packages
        echo [ERROR] Please run: pip install flask werkzeug psutil
        pause
        exit /b 1
    )
    echo [OK] Packages installed successfully
) else (
    echo [OK] All required packages are available
)

echo.
echo [INFO] Starting Modern Server Administrator...
echo [INFO] Server will be available at: http://localhost:3000
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Start the server administrator
python web_server_admin.py

echo.
echo [INFO] Server stopped
pause