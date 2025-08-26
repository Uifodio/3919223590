@echo off
setlocal enabledelayedexpansion

:: Create debug log
set "DEBUG_LOG=%~dp0debug_build.log"
echo [%date% %time%] Build script started > "%DEBUG_LOG%"

echo ========================================
echo Nova Explorer - Build EXE
echo ========================================
echo.

:: Function to log debug info
call :log "Build script started"

:: Check for any Python installation
call :log "Checking Python installations..."

:: Check python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
        call :log "Found python: %%i"
        echo Found Python: %%i
    )
    set "PYTHON_CMD=python"
    goto :python_found
)

:: Check python3 command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python3 --version 2^>^&1') do (
        call :log "Found python3: %%i"
        echo Found Python3: %%i
    )
    set "PYTHON_CMD=python3"
    goto :python_found
)

:: Check py command (Windows Python Launcher)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('py --version 2^>^&1') do (
        call :log "Found py: %%i"
        echo Found py: %%i
    )
    set "PYTHON_CMD=py"
    goto :python_found
)

:: No Python found
call :log "ERROR: No Python found"
echo ERROR: No Python installation found.
echo Please run run.bat first to install Python.
pause
exit /b 1

:python_found
call :log "Using Python command: %PYTHON_CMD%"

:: Check if we have Python 3.11 (preferred)
%PYTHON_CMD% --version 2>&1 | findstr "3.11" >nul
if %errorlevel% equ 0 (
    call :log "Python 3.11 found - optimal for building"
    echo Python 3.11 found - optimal for building!
) else (
    call :log "Python 3.11 not found, using available Python"
    echo Python 3.11 not found, but will try with available Python.
    echo Current version:
    %PYTHON_CMD% --version
    echo.
)

:: Test Python functionality
call :log "Testing Python functionality"
%PYTHON_CMD% -c "import sys; print('Python working:', sys.version)" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR: Python not working properly"
    echo ERROR: Python not working properly
    echo Check debug log: %DEBUG_LOG%
    pause
    exit /b 1
)

:: Install build dependencies
call :log "Installing build dependencies"
echo Installing build dependencies...
%PYTHON_CMD% -m pip install --upgrade pip >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "WARNING: Failed to upgrade pip"
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

%PYTHON_CMD% -m pip install -r requirements.txt >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR: Failed to install dependencies"
    echo ERROR: Failed to install dependencies
    echo Check debug log: %DEBUG_LOG%
    pause
    exit /b 1
)

:: Test PyInstaller
call :log "Testing PyInstaller"
%PYTHON_CMD% -c "import PyInstaller; print('PyInstaller version:', PyInstaller.__version__)" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR: PyInstaller not available"
    echo ERROR: PyInstaller not available
    echo Check debug log: %DEBUG_LOG%
    pause
    exit /b 1
)

:: Clean previous builds
call :log "Cleaning previous builds"
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist NovaExplorer.spec del /q NovaExplorer.spec

:: Build with PyInstaller (onefile for reliability)
call :log "Starting PyInstaller build"
echo Building EXE with PyInstaller...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean ^
  --name "NovaExplorer" ^
  --onefile ^
  --windowed ^
  --add-data "assets;assets" ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtWidgets ^
  --hidden-import PySide6.QtGui ^
  --collect-all PySide6 ^
  --collect-all shiboken6 ^
  main.py >> "%DEBUG_LOG%" 2>&1

set "BUILD_EXIT_CODE=%errorlevel%"
call :log "PyInstaller exited with code: %BUILD_EXIT_CODE%"

if %BUILD_EXIT_CODE% neq 0 (
    call :log "ERROR: Build failed"
    echo ERROR: Build failed
    echo Check debug log: %DEBUG_LOG%
    echo.
    echo Last 20 lines of debug log:
    powershell -Command "Get-Content '%DEBUG_LOG%' | Select-Object -Last 20"
    pause
    exit /b 1
)

:: Check multiple possible locations for the EXE
call :log "Checking build output locations"
set "EXE_FOUND="

:: Check dist directory
if exist "dist\NovaExplorer.exe" (
    set "EXE_FOUND=dist\NovaExplorer.exe"
    call :log "Found EXE in dist\NovaExplorer.exe"
    goto :exe_found
)

:: Check if dist directory exists and list contents
if exist "dist" (
    call :log "dist directory exists, listing contents:"
    dir dist >> "%DEBUG_LOG%" 2>&1
    for /f "tokens=*" %%i in ('dir dist /b 2^>nul') do (
        call :log "dist contains: %%i"
    )
)

:: Check current directory
if exist "NovaExplorer.exe" (
    set "EXE_FOUND=NovaExplorer.exe"
    call :log "Found EXE in current directory: NovaExplorer.exe"
    goto :exe_found
)

:: Check build directory
if exist "build" (
    call :log "build directory exists, searching for EXE..."
    for /r build %%i in (NovaExplorer.exe) do (
        if exist "%%i" (
            set "EXE_FOUND=%%i"
            call :log "Found EXE in build: %%i"
            goto :exe_found
        )
    )
)

:: No EXE found
call :log "ERROR: No EXE found in any expected location"
echo ERROR: Build completed but EXE not found
echo.
echo Checking what was created:
if exist "dist" (
    echo dist directory contents:
    dir dist
    echo.
)
if exist "build" (
    echo build directory contents:
    dir build
    echo.
)
echo.
echo Check debug log: %DEBUG_LOG%
pause
exit /b 1

:exe_found
call :log "EXE found at: %EXE_FOUND%"

:: If EXE is not in dist, copy it there
if not "%EXE_FOUND%"=="dist\NovaExplorer.exe" (
    call :log "Copying EXE to dist directory"
    if not exist "dist" mkdir dist
    copy "%EXE_FOUND%" "dist\NovaExplorer.exe" >> "%DEBUG_LOG%" 2>&1
    if %errorlevel% equ 0 (
        call :log "Successfully copied EXE to dist\NovaExplorer.exe"
    ) else (
        call :log "ERROR: Failed to copy EXE to dist directory"
    )
)

:: Verify final EXE exists
if exist "dist\NovaExplorer.exe" (
    call :log "Build successful: dist\NovaExplorer.exe"
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
    call :log "ERROR: Final EXE verification failed"
    echo ERROR: EXE not found in dist directory after copy attempt
    echo Check debug log: %DEBUG_LOG%
    pause
    exit /b 1
)

call :log "Build completed successfully"
echo Build complete!
pause
endlocal

:log
echo [%date% %time%] %~1 >> "%DEBUG_LOG%"
echo [%date% %time%] %~1
goto :eof