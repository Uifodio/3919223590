@echo off
title Anora Editor - One-Click Professional Setup
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              ANORA EDITOR - ONE-CLICK SETUP                 ║
echo ║              Professional Code Editor for Unity             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔍 Checking requirements...

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python not found. Please install Python first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install --user --break-system-packages -r requirements.txt

if %errorLevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Build executable
echo.
echo 🔨 Building Windows executable...
python build_windows_executable.py

if %errorLevel% neq 0 (
    echo ❌ Failed to build executable
    pause
    exit /b 1
)

echo ✅ Executable built

REM Check if executable was created
if not exist "AnoraEditor.exe" (
    echo ❌ AnoraEditor.exe not found
    pause
    exit /b 1
)

echo ✅ AnoraEditor.exe created

REM Run installer
echo.
echo 🔧 Installing Anora Editor...
call install_anora_editor.bat

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    SETUP COMPLETE!                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🎉 Anora Editor is now a professional Windows application!
echo.
echo 📋 What you can now do:
echo   • Double-click any code file to open in Anora Editor
echo   • Right-click files → 'Open with Anora Editor'
echo   • Use 'Anora Editor' desktop shortcut
echo   • Drag and drop files onto Anora Editor
echo   • Command line: AnoraEditor.exe file.py
echo.

echo ⚠️ Important:
echo   • Restart File Explorer or log out/in for all changes to take effect
echo   • If files don't open, right-click → 'Open with' → 'Choose another app' → 'Anora Editor'
echo.

echo Press any key to exit...
pause >nul