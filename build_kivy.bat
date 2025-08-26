@echo off
echo ========================================
echo Nova Explorer - Kivy Build Script
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python first.
    pause
    exit /b 1
)

echo Installing Kivy dependencies...
python -m pip install kivy==2.2.1 kivymd==1.1.1 pillow==10.1.0 pywin32==306 psutil==5.9.6 pyperclip==1.8.2 send2trash==1.8.3 pyinstaller==6.2.0

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
python -m PyInstaller --onefile --windowed --name "NovaExplorer" main.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo Your EXE is ready: dist\NovaExplorer.exe
echo.
pause