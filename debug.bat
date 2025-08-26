@echo off
echo ========================================
echo Nova Explorer - Build Diagnostics
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please run run.bat first to install Python.
    pause
    exit /b 1
)

:: Run diagnostics
echo Running build diagnostics...
python debug_build.py

echo.
echo Diagnostics complete. Check the output above.
pause