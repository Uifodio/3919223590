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

REM Check PHP availability
echo.
echo Checking PHP availability...
python -c "import subprocess; subprocess.run(['php', '--version'], capture_output=True, text=True, timeout=5)" 2>nul
if errorlevel 1 (
    echo ⚠️  PHP not detected - PHP servers will not work
    echo    Use the 'Install PHP' button in the application to auto-install PHP
) else (
    echo ✓ PHP detected and ready
)

REM Check Node.js availability
python -c "import subprocess; subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)" 2>nul
if errorlevel 1 (
    echo ⚠️  Node.js not detected - Node.js servers will not work
) else (
    echo ✓ Node.js detected and ready
)

echo.
echo Starting Modern Server Administrator...
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

REM Start the application
python web_server_admin.py

pause