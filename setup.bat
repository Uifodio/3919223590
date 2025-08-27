@echo off
REM Anora Editor - Windows Setup Script
REM This script sets up Anora Editor for Windows

echo Setting up Anora Editor...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://python.org and try again.
    pause
    exit /b 1
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo To run Anora Editor:
echo   run_anora.bat
echo.
echo To install file associations (run as Administrator):
echo   install_windows_default_editor.ps1
echo.
echo To run directly with Python:
echo   python anora_editor.py
echo.
pause