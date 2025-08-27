@echo off
REM Anora Editor - Windows Launcher
REM This file launches Anora Editor

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

REM Launch Anora Editor
python anora_editor.py %*

REM If a file was passed as argument, it will be opened automatically