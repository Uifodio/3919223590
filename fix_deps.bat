@echo off
setlocal enabledelayedexpansion
echo ========================================
echo Nova Explorer - Fix Dependencies
echo ========================================
echo.

:: Find Python
set "PYTHON_CMD="
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :python_found
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    goto :python_found
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :python_found
)

echo ERROR: Python not found
echo Please run run.bat first to install Python.
pause
exit /b 1

:python_found
echo Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

:: Upgrade pip first
echo Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip

:: Install missing dependencies
echo.
echo Installing missing dependencies...
echo.

echo Installing Pillow...
%PYTHON_CMD% -m pip install Pillow==10.1.0
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Pillow
    pause
    exit /b 1
)

echo.
echo Installing pywin32...
%PYTHON_CMD% -m pip install pywin32==306
if %errorlevel% neq 0 (
    echo ERROR: Failed to install pywin32
    pause
    exit /b 1
)

:: Verify all dependencies
echo.
echo Verifying all dependencies...
%PYTHON_CMD% -c "import PySide6, PIL, psutil, pyperclip, send2trash, win32api, PyInstaller; print('All dependencies installed successfully!')"
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ ALL DEPENDENCIES INSTALLED!
    echo ========================================
    echo.
    echo You can now run:
    echo - debug.bat (to verify everything works)
    echo - build.bat (to create the EXE)
    echo.
) else (
    echo.
    echo ❌ Some dependencies still missing
    echo Check the error messages above
    echo.
)

pause