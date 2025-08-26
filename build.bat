@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Nova Explorer - Build EXE
echo ========================================
echo.

:: Check if Python 3.11 is available
python --version 2>&1 | findstr "3.11" >nul
if %errorlevel% neq 0 (
    echo ERROR: Python 3.11 required for building.
    echo Please run run.bat first to install Python 3.11.
    pause
    exit /b 1
)

:: Install build dependencies
echo Installing build dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

:: Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist NovaExplorer.spec del /q NovaExplorer.spec

:: Build with PyInstaller (onefile for reliability)
echo Building EXE with PyInstaller...
pyinstaller --noconfirm --clean ^
  --name "NovaExplorer" ^
  --onefile ^
  --windowed ^
  --add-data "assets;assets" ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtWidgets ^
  --hidden-import PySide6.QtGui ^
  --collect-all PySide6 ^
  --collect-all shiboken6 ^
  main.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

:: Check if build was successful
if exist "dist\NovaExplorer.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your EXE is ready: dist\NovaExplorer.exe
    echo.
    echo You can now:
    echo - Run the EXE directly
    echo - Copy it to any Windows computer
    echo - Set it as Unity's external editor
    echo.
) else (
    echo ERROR: Build completed but EXE not found
    pause
    exit /b 1
)

echo Build complete!
pause
endlocal