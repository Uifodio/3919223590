@echo off
setlocal enabledelayedexpansion
echo ========================================
echo Nova Explorer - ABSOLUTE DEPENDENCY FIX
echo ========================================
echo.

:: Create debug log
set "DEBUG_LOG=%~dp0absolute_fix.log"
echo [%date% %time%] Absolute fix started > "%DEBUG_LOG%"

:: Find Python with multiple methods
set "PYTHON_CMD="
set "PYTHON_VERSION="

echo Finding Python installation...
call :log "Searching for Python installation"

:: Method 1: Try python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
        set "PYTHON_VERSION=%%i"
        call :log "Found python: %%i"
    )
    set "PYTHON_CMD=python"
    goto :python_found
)

:: Method 2: Try python3 command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python3 --version 2^>^&1') do (
        set "PYTHON_VERSION=%%i"
        call :log "Found python3: %%i"
    )
    set "PYTHON_CMD=python3"
    goto :python_found
)

:: Method 3: Try py command
py --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('py --version 2^>^&1') do (
        set "PYTHON_VERSION=%%i"
        call :log "Found py: %%i"
    )
    set "PYTHON_CMD=py"
    goto :python_found
)

:: Method 4: Search common Python locations
call :log "Searching common Python locations"
for %%p in (
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Python313\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python313\python.exe"
) do (
    if exist %%p (
        set "PYTHON_CMD=%%p"
        call :log "Found Python at: %%p"
        goto :python_found
    )
)

:: No Python found - install it
call :log "No Python found, installing Python 3.11"
echo No Python found. Installing Python 3.11...
echo.

:: Download Python 3.11.8
call :log "Downloading Python 3.11.8"
echo Downloading Python 3.11.8...
powershell -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python311-installer.exe' -UseBasicParsing } catch { Write-Host 'Download failed: ' + $_.Exception.Message }" >> "%DEBUG_LOG%" 2>&1

if exist "python311-installer.exe" (
    call :log "Python installer downloaded successfully"
    echo Installing Python 3.11.8...
    python311-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 >> "%DEBUG_LOG%" 2>&1
    
    :: Wait for installation
    call :log "Waiting for installation to complete"
    timeout /t 20 /nobreak >nul
    
    :: Clean up
    del python311-installer.exe
    call :log "Python installer cleaned up"
    
    :: Refresh PATH
    call :log "Refreshing PATH"
    set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts"
    
    echo Python 3.11 installation completed!
    set "PYTHON_CMD=python"
) else (
    call :log "ERROR: Failed to download Python installer"
    echo ERROR: Failed to download Python installer
    echo Check debug log: %DEBUG_LOG%
    pause
    exit /b 1
)

:python_found
call :log "Using Python: %PYTHON_CMD%"
echo Using Python: %PYTHON_VERSION%
echo.

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

:: Upgrade pip with multiple methods
call :log "Upgrading pip"
echo Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "WARNING: Failed to upgrade pip, trying alternative method"
    %PYTHON_CMD% -m ensurepip --upgrade >> "%DEBUG_LOG%" 2>&1
)

:: Install dependencies with multiple fallback methods
call :log "Installing dependencies with multiple methods"
echo.
echo Installing dependencies (this may take a few minutes)...
echo.

:: Method 1: Try requirements.txt
call :log "Method 1: Installing from requirements.txt"
%PYTHON_CMD% -m pip install -r requirements.txt >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (
    call :log "Method 1 successful"
    goto :verify_deps
)

:: Method 2: Install packages individually with specific versions
call :log "Method 2: Installing packages individually"
echo Trying individual package installation...

:: PySide6
call :log "Installing PySide6"
%PYTHON_CMD% -m pip install PySide6==6.6.1 >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "Trying PySide6 without version"
    %PYTHON_CMD% -m pip install PySide6 >> "%DEBUG_LOG%" 2>&1
)

:: Pillow
call :log "Installing Pillow"
%PYTHON_CMD% -m pip install Pillow==10.1.0 >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "Trying Pillow without version"
    %PYTHON_CMD% -m pip install Pillow >> "%DEBUG_LOG%" 2>&1
)
if %errorlevel% neq 0 (
    call :log "Trying PIL instead of Pillow"
    %PYTHON_CMD% -m pip install PIL >> "%DEBUG_LOG%" 2>&1
)

:: pywin32
call :log "Installing pywin32"
%PYTHON_CMD% -m pip install pywin32==306 >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "Trying pywin32 without version"
    %PYTHON_CMD% -m pip install pywin32 >> "%DEBUG_LOG%" 2>&1
)
if %errorlevel% neq 0 (
    call :log "Trying alternative pywin32 installation"
    %PYTHON_CMD% -m pip install --only-binary=all pywin32 >> "%DEBUG_LOG%" 2>&1
)

:: Other packages
call :log "Installing other packages"
%PYTHON_CMD% -m pip install psutil==5.9.6 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -m pip install pyperclip==1.8.2 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -m pip install send2trash==1.8.3 >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -m pip install pyinstaller==6.2.0 >> "%DEBUG_LOG%" 2>&1

:: Method 3: Try with --user flag if admin rights are an issue
call :log "Method 3: Trying with --user flag"
%PYTHON_CMD% -m pip install --user Pillow >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -m pip install --user pywin32 >> "%DEBUG_LOG%" 2>&1

:: Method 4: Try with --force-reinstall
call :log "Method 4: Trying with --force-reinstall"
%PYTHON_CMD% -m pip install --force-reinstall Pillow >> "%DEBUG_LOG%" 2>&1
%PYTHON_CMD% -m pip install --force-reinstall pywin32 >> "%DEBUG_LOG%" 2>&1

:verify_deps
:: Verify all dependencies
call :log "Verifying all dependencies"
echo.
echo Verifying dependencies...
echo.

:: Test each dependency individually
set "ALL_GOOD=true"

:: PySide6
%PYTHON_CMD% -c "import PySide6; print('✓ PySide6 OK')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    echo ✗ PySide6 FAILED
    set "ALL_GOOD=false"
) else (
    echo ✓ PySide6 OK
)

:: Pillow/PIL
%PYTHON_CMD% -c "import PIL; print('✓ Pillow OK')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    %PYTHON_CMD% -c "import Image; print('✓ PIL OK')" >> "%DEBUG_LOG%" 2>&1
    if %errorlevel% neq 0 (
        echo ✗ Pillow/PIL FAILED
        set "ALL_GOOD=false"
    ) else (
        echo ✓ PIL OK
    )
) else (
    echo ✓ Pillow OK
)

:: pywin32
%PYTHON_CMD% -c "import win32api; print('✓ pywin32 OK')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    echo ✗ pywin32 FAILED
    set "ALL_GOOD=false"
) else (
    echo ✓ pywin32 OK
)

:: Other packages
%PYTHON_CMD% -c "import psutil; print('✓ psutil OK')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (echo ✓ psutil OK) else (echo ✗ psutil FAILED & set "ALL_GOOD=false")

%PYTHON_CMD% -c "import pyperclip; print('✓ pyperclip OK')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (echo ✓ pyperclip OK) else (echo ✗ pyperclip FAILED & set "ALL_GOOD=false")

%PYTHON_CMD% -c "import send2trash; print('✓ send2trash OK')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (echo ✓ send2trash OK) else (echo ✗ send2trash FAILED & set "ALL_GOOD=false")

%PYTHON_CMD% -c "import PyInstaller; print('✓ PyInstaller OK')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% equ 0 (echo ✓ PyInstaller OK) else (echo ✗ PyInstaller FAILED & set "ALL_GOOD=false")

echo.
if "%ALL_GOOD%"=="true" (
    call :log "All dependencies verified successfully"
    echo ========================================
    echo ✅ ALL DEPENDENCIES INSTALLED!
    echo ========================================
    echo.
    echo You can now run:
    echo - debug.bat (to verify everything works)
    echo - build.bat (to create the EXE)
    echo.
) else (
    call :log "Some dependencies still missing"
    echo.
    echo ❌ Some dependencies still missing
    echo.
    echo Trying final recovery method...
    echo.
    
    :: Final recovery: Try installing from wheel files
    call :log "Final recovery: Installing from wheels"
    %PYTHON_CMD% -m pip install --only-binary=all --force-reinstall Pillow pywin32 >> "%DEBUG_LOG%" 2>&1
    
    echo Final verification...
    %PYTHON_CMD% -c "import PIL, win32api; print('Final check OK')" >> "%DEBUG_LOG%" 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Final recovery successful!
    ) else (
        echo ❌ Final recovery failed
        echo Check debug log: %DEBUG_LOG%
    )
)

echo.
echo Debug log saved to: %DEBUG_LOG%
pause

:log
echo [%date% %time%] %~1 >> "%DEBUG_LOG%"
goto :eof