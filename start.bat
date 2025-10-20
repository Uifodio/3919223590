@echo off
title Modern Server Administrator
color 0A

echo.
echo  ========================================
echo  🚀 Modern Server Administrator
echo  ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✓ Python found: 
python --version

REM Check if required packages are installed
echo.
echo Checking dependencies...
python -c "import flask, psutil" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✓ Dependencies ready

REM Create demo folder if it doesn't exist
if not exist "demo_website" (
    echo.
    echo Creating demo website...
    python demo.py
)

echo.
echo Starting Modern Server Administrator...
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

REM Start the application
python web_server_admin.py

pause