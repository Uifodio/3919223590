@echo off
echo Starting Windows-Compatible Workspace Server...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist "projects" mkdir projects
if not exist "logs" mkdir logs
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js

REM Start the server
echo.
echo Starting Workspace Server...
echo Server will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python workspace_server.py

pause