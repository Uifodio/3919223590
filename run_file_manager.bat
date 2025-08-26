@echo off
title Windows File Manager
echo Starting Windows File Manager...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.6 or higher from https://python.org
    pause
    exit /b 1
)

REM Run the file manager
python file_manager.py

REM If there was an error, pause to show the message
if errorlevel 1 (
    echo.
    echo An error occurred while running the file manager.
    pause
)