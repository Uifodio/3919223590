@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Nova Explorer - Auto Installer & Debug
echo ========================================
echo.

:: Create debug log file
set "DEBUG_LOG=%~dp0debug_install.log"
echo [%date% %time%] Starting installation... > "%DEBUG_LOG%"

:: Function to log debug info
call :log "Installation started"

:: Check Python installation
call :log "Checking Python installation..."
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log "Python not found in PATH, trying python3..."
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        call :log "Python3 not found, installing Python..."
        
        :: Try to find existing Python installations
        call :log "Searching for existing Python installations..."
        for /f "tokens=*" %%i in ('dir /b /s "C:\Python*" 2^>nul') do (
            call :log "Found Python installation: %%i"
        )
        for /f "tokens=*" %%i in ('dir /b /s "C:\Users\%USERNAME%\AppData\Local\Programs\Python*" 2^>nul') do (
            call :log "Found Python installation: %%i"
        )
        
        :: Download and install Python 3.11 (more stable than 3.13 for PySide6)
        call :log "Downloading Python 3.11.8..."
        powershell -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe' -UseBasicParsing } catch { Write-Host 'Download failed: ' + $_.Exception.Message }"
        
        if exist "python-installer.exe" (
            call :log "Python installer downloaded successfully"
            call :log "Installing Python 3.11.8..."
            python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1
            
            :: Wait for installation
            call :log "Waiting for installation to complete..."
            timeout /t 15 /nobreak >nul
            
            :: Clean up installer
            del python-installer.exe
            call :log "Python installer cleaned up"
        ) else (
            call :log "ERROR: Failed to download Python installer"
            echo ERROR: Failed to download Python installer
            pause
            exit /b 1
        )
        
        :: Refresh environment variables
        call :log "Refreshing environment variables..."
        call refreshenv.cmd 2>nul || (
            call :log "refreshenv not available, manually updating PATH"
            set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts"
        )
        
        call :log "Python installation completed"
    ) else (
        call :log "Python3 found, creating python symlink"
        :: Create python symlink if python3 exists
        where python3 >nul 2>&1
        if %errorlevel% equ 0 (
            for /f "tokens=*" %%i in ('where python3') do (
                call :log "Python3 found at: %%i"
                :: Try to create a symlink or copy
                copy "%%i" "python.exe" >nul 2>&1
            )
        )
    )
) else (
    call :log "Python found in PATH"
)

:: Verify Python is working
call :log "Verifying Python installation..."
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR: Python still not accessible after installation"
    echo ERROR: Python installation failed. Check debug log: %DEBUG_LOG%
    pause
    exit /b 1
)

:: Get Python version for logging
for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
    call :log "Python version: %%i"
)

:: Check and install pip
call :log "Checking pip installation..."
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log "Installing pip..."
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        call :log "ERROR: Failed to install pip"
        echo ERROR: Failed to install pip
        pause
        exit /b 1
    )
)

:: Upgrade pip
call :log "Upgrading pip..."
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    call :log "WARNING: Failed to upgrade pip, continuing anyway"
)

:: Install requirements with detailed error reporting
call :log "Installing required packages..."
echo Installing required packages...
python -m pip install -r requirements_windows.txt
if %errorlevel% neq 0 (
    call :log "ERROR: Failed to install requirements"
    echo ERROR: Failed to install requirements. Check debug log: %DEBUG_LOG%
    echo.
    echo Trying to install packages individually...
    call :log "Attempting individual package installation"
    
    :: Try installing packages individually
    python -m pip install PySide6>=6.6.1
    python -m pip install Pillow>=10.1.0
    python -m pip install pywin32>=306
    python -m pip install psutil>=5.9.6
    python -m pip install watchdog>=3.0.0
    python -m pip install pyperclip>=1.8.2
    python -m pip install pyinstaller>=6.2.0
    python -m pip install send2trash>=1.8.3
    
    call :log "Individual package installation completed"
)

:: Create necessary directories
call :log "Creating necessary directories..."
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "assets" mkdir assets
if not exist "temp" mkdir temp

:: Create default config if it doesn't exist
if not exist "config\config.json" (
    call :log "Creating default configuration..."
    python -c "import json; config={'theme':'dark','font_size':12,'auto_save':True,'show_hidden':False,'recent_files':[],'recent_folders':[]}; open('config/config.json','w').write(json.dumps(config,indent=2))"
    if %errorlevel% neq 0 (
        call :log "ERROR: Failed to create default config"
    )
)

:: Test import of key modules
call :log "Testing module imports..."
python -c "import sys; print('Python path:', sys.path)" 2>&1 | findstr /v "DeprecationWarning" >> "%DEBUG_LOG%"
python -c "import PySide6; print('PySide6 version:', PySide6.__version__)" 2>&1 | findstr /v "DeprecationWarning" >> "%DEBUG_LOG%"
python -c "import os; print('Current directory:', os.getcwd())" 2>&1 | findstr /v "DeprecationWarning" >> "%DEBUG_LOG%"

:: Run installation test
call :log "Running installation test..."
echo.
echo ========================================
echo Running Installation Test...
echo ========================================
python test_install.py
set "TEST_EXIT_CODE=%errorlevel%"
call :log "Test exit code: %TEST_EXIT_CODE%"

if %TEST_EXIT_CODE% neq 0 (
    echo.
    echo ========================================
    echo INSTALLATION TEST FAILED
    echo ========================================
    echo.
    echo The installation test failed. This means there are issues with the setup.
    echo Check the debug log for details: %DEBUG_LOG%
    echo.
    echo Would you like to continue anyway? (y/n)
    set /p "CONTINUE="
    if /i not "%CONTINUE%"=="y" (
        echo Installation aborted.
        pause
        exit /b 1
    )
) else (
    echo.
    echo ========================================
    echo INSTALLATION TEST PASSED!
    echo ========================================
    echo.
)

:: Run the application with error handling
call :log "Starting application..."
echo.
echo ========================================
echo Starting Nova Explorer...
echo ========================================
echo.

python main.py
set "APP_EXIT_CODE=%errorlevel%"

:: Log the exit code
call :log "Application exited with code: %APP_EXIT_CODE%"

:: If the application exits with an error, show detailed info
if %APP_EXIT_CODE% neq 0 (
    echo.
    echo ========================================
    echo APPLICATION ERROR - Debug Information
    echo ========================================
    echo.
    echo Exit code: %APP_EXIT_CODE%
    echo Debug log: %DEBUG_LOG%
    echo.
    echo Python version:
    python --version
    echo.
    echo Installed packages:
    python -m pip list
    echo.
    echo Current directory:
    cd
    echo.
    echo Files in current directory:
    dir /b
    echo.
    echo ========================================
    echo Check the debug log for detailed information:
    echo %DEBUG_LOG%
    echo ========================================
    pause
)

endlocal
exit /b %APP_EXIT_CODE%

:log
echo [%date% %time%] %~1 >> "%DEBUG_LOG%"
echo [%date% %time%] %~1
goto :eof