@echo off
setlocal enabledelayedexpansion
echo ========================================
echo Nova Explorer - NUCLEAR RESET
echo ========================================
echo.
echo WARNING: This will completely reset everything!
echo - Remove all Python packages
echo - Clean all cache and temporary files
echo - Reinstall Python and all dependencies
echo.
set /p "CONFIRM=Are you sure? Type 'YES' to continue: "
if not "%CONFIRM%"=="YES" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Starting nuclear reset...
echo.

:: Create debug log
set "DEBUG_LOG=%~dp0nuclear_reset.log"
echo [%date% %time%] Nuclear reset started > "%DEBUG_LOG%"

:: Step 1: Find and uninstall all Python packages
call :log "Step 1: Uninstalling all packages"
echo Step 1: Uninstalling all packages...

:: Find Python
set "PYTHON_CMD="
python --version >nul 2>&1 && set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
    python3 --version >nul 2>&1 && set "PYTHON_CMD=python3"
)
if not defined PYTHON_CMD (
    py --version >nul 2>&1 && set "PYTHON_CMD=py"
)

if defined PYTHON_CMD (
    call :log "Found Python: %PYTHON_CMD%"
    echo Found Python: %PYTHON_CMD%
    
    :: Uninstall all packages
    echo Uninstalling all packages...
    %PYTHON_CMD% -m pip freeze | %PYTHON_CMD% -m pip uninstall -y >> "%DEBUG_LOG%" 2>&1
    
    :: Clean pip cache
    echo Cleaning pip cache...
    %PYTHON_CMD% -m pip cache purge >> "%DEBUG_LOG%" 2>&1
) else (
    call :log "No Python found for uninstall"
    echo No Python found for uninstall
)

:: Step 2: Clean all temporary and cache directories
call :log "Step 2: Cleaning cache directories"
echo.
echo Step 2: Cleaning cache directories...

:: Clean pip cache directories
for %%d in (
    "%USERPROFILE%\AppData\Local\pip\Cache"
    "%USERPROFILE%\AppData\Roaming\pip\Cache"
    "%LOCALAPPDATA%\pip\Cache"
    "%APPDATA%\pip\Cache"
) do (
    if exist %%d (
        echo Cleaning: %%d
        rmdir /s /q %%d 2>nul
    )
)

:: Clean Python cache directories
for %%d in (
    "%USERPROFILE%\AppData\Local\Python"
    "%USERPROFILE%\AppData\Roaming\Python"
    "%LOCALAPPDATA%\Python"
    "%APPDATA%\Python"
) do (
    if exist %%d (
        echo Cleaning: %%d
        rmdir /s /q %%d 2>nul
    )
)

:: Clean project cache
if exist "build" (
    echo Cleaning build directory...
    rmdir /s /q build
)
if exist "dist" (
    echo Cleaning dist directory...
    rmdir /s /q dist
)
if exist "__pycache__" (
    echo Cleaning __pycache__...
    rmdir /s /q __pycache__
)
if exist "*.spec" (
    echo Cleaning spec files...
    del *.spec
)

:: Step 3: Uninstall Python completely
call :log "Step 3: Uninstalling Python"
echo.
echo Step 3: Uninstalling Python...

:: Try to uninstall Python using Windows uninstaller
for %%p in (
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Python313\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe"
) do (
    if exist %%p (
        echo Found Python installation: %%p
        for /f "tokens=*" %%i in ('dir /b "%%~dp*unins*.exe" 2^>nul') do (
            echo Uninstalling: %%i
            "%%~dp%%i" /SILENT
        )
    )
)

:: Step 4: Download and install fresh Python 3.11
call :log "Step 4: Installing fresh Python 3.11"
echo.
echo Step 4: Installing fresh Python 3.11...

:: Download Python 3.11.8
echo Downloading Python 3.11.8...
powershell -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python311-fresh.exe' -UseBasicParsing } catch { Write-Host 'Download failed: ' + $_.Exception.Message }" >> "%DEBUG_LOG%" 2>&1

if exist "python311-fresh.exe" (
    call :log "Python installer downloaded"
    echo Installing Python 3.11.8...
    python311-fresh.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_dev=0 >> "%DEBUG_LOG%" 2>&1
    
    :: Wait for installation
    echo Waiting for installation to complete...
    timeout /t 30 /nobreak >nul
    
    :: Clean up
    del python311-fresh.exe
    call :log "Python installer cleaned up"
    
    :: Refresh PATH
    set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts"
    
    echo Python 3.11 installation completed!
) else (
    call :log "ERROR: Failed to download Python installer"
    echo ERROR: Failed to download Python installer
    pause
    exit /b 1
)

:: Step 5: Install dependencies with fresh Python
call :log "Step 5: Installing dependencies with fresh Python"
echo.
echo Step 5: Installing dependencies with fresh Python...

:: Find the fresh Python
set "PYTHON_CMD="
python --version >nul 2>&1 && set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
    for %%p in (
        "C:\Python311\python.exe"
        "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    ) do (
        if exist %%p (
            set "PYTHON_CMD=%%p"
            goto :found_fresh_python
        )
    )
)

:found_fresh_python
if not defined PYTHON_CMD (
    call :log "ERROR: Fresh Python not found"
    echo ERROR: Fresh Python not found
    pause
    exit /b 1
)

call :log "Using fresh Python: %PYTHON_CMD%"
echo Using fresh Python: %PYTHON_CMD%
%PYTHON_CMD% --version

:: Upgrade pip
echo Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip >> "%DEBUG_LOG%" 2>&1

:: Install dependencies one by one with verification
echo.
echo Installing dependencies...

:: PySide6
echo Installing PySide6...
%PYTHON_CMD% -m pip install PySide6==6.6.1 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -c "import PySide6; print('✓ PySide6 installed')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (echo ✓ PySide6) else (echo ✗ PySide6 FAILED)

:: Pillow
echo Installing Pillow...
%PYTHON_CMD% -m pip install Pillow==10.1.0 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -c "import PIL; print('✓ Pillow installed')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (echo ✓ Pillow) else (echo ✗ Pillow FAILED)

:: pywin32
echo Installing pywin32...
%PYTHON_CMD% -m pip install pywin32==306 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -c "import win32api; print('✓ pywin32 installed')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (echo ✓ pywin32) else (echo ✗ pywin32 FAILED)

:: Other packages
echo Installing other packages...
%PYTHON_CMD% -m pip install psutil==5.9.6 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -m pip install pyperclip==1.8.2 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -m pip install send2trash==1.8.3 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -m pip install pyinstaller==6.2.0 >> "%DEBUG_LOG%" 2>&1

:: Final verification
call :log "Final verification"
echo.
echo Final verification...
%PYTHON_CMD% -c "import PySide6, PIL, win32api, psutil, pyperclip, send2trash, PyInstaller; print('All dependencies OK')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (
    call :log "Nuclear reset successful"
    echo.
    echo ========================================
    echo ✅ NUCLEAR RESET COMPLETE!
    echo ========================================
    echo.
    echo Everything has been reset and reinstalled.
    echo You can now run:
    echo - debug.bat (to verify everything works)
    echo - build.bat (to create the EXE)
    echo.
) else (
    call :log "Nuclear reset failed"
    echo.
    echo ❌ Nuclear reset failed
    echo Check debug log: %DEBUG_LOG%
    echo.
)

echo Debug log saved to: %DEBUG_LOG%
pause

:log
echo [%date% %time%] %~1 >> "%DEBUG_LOG%"
goto :eof