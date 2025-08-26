@echo off
setlocal enabledelayedexpansion

:: Change to project root directory
cd /d "%~dp0..\.."

set "DEBUG_LOG=%~dp0build_debug.log"
echo [%date% %time%] Build started > "%DEBUG_LOG%"

:: Verify required files exist
echo Verifying required files...
python "scripts\windows\verify_files.py"
if %errorlevel% neq 0 (
  echo File verification failed. Missing required files.
  pause
  exit /b 1
)

:: Ensure Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo Python not found. Run install_and_run.bat first.
  echo See %DEBUG_LOG%
  pause
  exit /b 1
)

:: Upgrade pip quietly
python -m pip install --upgrade pip >> "%DEBUG_LOG%" 2>&1

:: Install build requirements
python -m pip install -r "requirements_windows.txt" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 echo Failed to install requirements >> "%DEBUG_LOG%"

:: Run preflight check (auto-installs missing)
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

:: Build with PyInstaller (one-folder, windowed)
echo Building with PyInstaller...
pyinstaller --noconfirm --clean ^
  --name "NovaExplorer" ^
  --windowed ^
  --icon assets\icon.ico ^
  --add-data "assets;assets" ^
  main.py >> "%DEBUG_LOG%" 2>&1

if %errorlevel% neq 0 (
  echo Build failed. See %DEBUG_LOG%
  type "%DEBUG_LOG%" | more
  pause
  exit /b 1
)

echo Build complete. Output in dist\NovaExplorer
pause
endlocal