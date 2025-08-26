@echo off
title Nova Explorer - Professional File Manager
color 0A

echo.
echo ========================================
echo    Nova Explorer - Professional Edition
echo ========================================
echo    The Ultimate File Manager + Editor
echo    Perfect for Unity Development
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.11 or later from https://python.org
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found - Installing dependencies...
echo.

:: Install Kivy and dependencies
echo [INSTALL] Installing Kivy 2.3.1...
python -m pip install kivy==2.3.1 --quiet

echo [INSTALL] Installing additional dependencies...
python -m pip install kivymd==1.1.1 pillow==10.1.0 pywin32==306 psutil==5.9.6 pyperclip==1.8.2 send2trash==1.8.3 --quiet

if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install with specific versions
    echo [INFO] Trying alternative installation method...
    
    python -m pip install kivy kivymd pillow pywin32 psutil pyperclip send2trash --quiet
    
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
)

echo.
echo [SUCCESS] All dependencies installed successfully!
echo.
echo [LAUNCH] Starting Nova Explorer...
echo.

:: Launch the application
python main.py

echo.
echo [INFO] Nova Explorer has closed.
pause