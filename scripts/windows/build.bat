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

:: Get Python version for DLL handling
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

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

:: Create PyInstaller spec file for better control
echo Creating PyInstaller spec file...
python -c "
import PyInstaller.__main__
PyInstaller.__main__.run([
    '--name=NovaExplorer',
    '--windowed',
    '--onedir',
    '--clean',
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.',
    '--add-data=assets;assets',
    '--hidden-import=PySide6.QtCore',
    '--hidden-import=PySide6.QtWidgets',
    '--hidden-import=PySide6.QtGui',
    '--collect-all=PySide6',
    '--collect-all=shiboken6',
    'main.py'
])
" >> "%DEBUG_LOG%" 2>&1

if %errorlevel% neq 0 (
  echo Build failed. Trying alternative method...
  
  :: Alternative: Use --onefile instead of --onedir
  echo Trying onefile build...
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
    echo Both build methods failed. See %DEBUG_LOG%
    type "%DEBUG_LOG%" | more
    pause
    exit /b 1
  )
)

:: Check if build was successful
if not exist "dist\NovaExplorer" (
  echo Build output not found. Checking for onefile build...
  if exist "dist\NovaExplorer.exe" (
    echo Onefile build successful: dist\NovaExplorer.exe
    
    :: Create launcher to handle DLL issues
    echo Creating launcher script...
    python "scripts\windows\create_launcher.py"
    if %errorlevel% equ 0 (
      echo Launcher created: dist\NovaExplorer_Launcher.bat
      echo Use the launcher to run the application.
    )
  ) else (
    echo Build failed. No output found.
    pause
    exit /b 1
  )
) else (
  echo Build successful: dist\NovaExplorer\
  
  :: Create launcher for folder build too
  echo Creating launcher script...
  python "scripts\windows\create_launcher.py"
  if %errorlevel% equ 0 (
    echo Launcher created: dist\NovaExplorer_Launcher.bat
    echo Use the launcher to run the application.
  )
)

echo Build complete.
pause
endlocal