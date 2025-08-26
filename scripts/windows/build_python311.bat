@echo off
setlocal enabledelayedexpansion

:: Change to project root directory
cd /d "%~dp0..\.."

set "DEBUG_LOG=%~dp0build_python311_debug.log"
echo [%date% %time%] Python 3.11 Build started > "%DEBUG_LOG%"

:: Check if Python 3.11 is available
python --version 2>&1 | findstr "3.11" >nul
if %errorlevel% neq 0 (
  echo Python 3.11 not found. This script requires Python 3.11 for better PyInstaller compatibility.
  echo Current Python version:
  python --version
  echo.
  echo Please install Python 3.11 from https://www.python.org/downloads/release/python-3118/
  echo Or use the regular build.bat which will try to work with your current Python version.
  pause
  exit /b 1
)

:: Verify required files exist
echo Verifying required files...
python "scripts\windows\verify_files.py"
if %errorlevel% neq 0 (
  echo File verification failed. Missing required files.
  pause
  exit /b 1
)

:: Upgrade pip quietly
python -m pip install --upgrade pip >> "%DEBUG_LOG%" 2>&1

:: Install build requirements
python -m pip install -r "requirements_windows.txt" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 echo Failed to install requirements >> "%DEBUG_LOG%"

:: Run preflight check
python "scripts\windows\preflight_check.py"
if %errorlevel% neq 0 (
  echo Preflight failed. See %DEBUG_LOG% and console output above.
  pause
  exit /b 1
)

:: Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist NovaExplorer.spec del /q NovaExplorer.spec

:: Build with PyInstaller (onefile for better compatibility)
echo Building with PyInstaller (onefile)...
pyinstaller --noconfirm --clean ^
  --name "NovaExplorer" ^
  --onefile ^
  --windowed ^
  --icon assets\icon.ico ^
  --add-data "assets;assets" ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtWidgets ^
  --hidden-import PySide6.QtGui ^
  --collect-all PySide6 ^
  --collect-all shiboken6 ^
  main.py >> "%DEBUG_LOG%" 2>&1

if %errorlevel% neq 0 (
  echo Build failed. See %DEBUG_LOG%
  type "%DEBUG_LOG%" | more
  pause
  exit /b 1
)

:: Check if build was successful
if exist "dist\NovaExplorer.exe" (
  echo Build successful: dist\NovaExplorer.exe
  echo.
  echo Testing the executable...
  echo dist\NovaExplorer.exe --version
  dist\NovaExplorer.exe --version
) else (
  echo Build failed. No output found.
  pause
  exit /b 1
)

echo Build complete.
pause
endlocal