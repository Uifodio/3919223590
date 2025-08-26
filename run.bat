@echo off
setlocal enabledelayedexpansion

:: Create debug log
set "DEBUG_LOG=%~dp0debug_run.log"
echo [%date% %time%] Run script started > "%DEBUG_LOG%"

echo ========================================
echo Nova Explorer - Auto Install & Run
echo ========================================
echo.

:: Function to log debug info
call :log "Script started"

:: Check all Python versions
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
call :log "No Python found in PATH"
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
    timeout /t 15 /nobreak >nul
    
    :: Clean up
    del python311-installer.exe
    call :log "Python installer cleaned up"
    
    :: Refresh PATH
    call :log "Refreshing PATH"
    call refreshenv.cmd 2>nul || (
        set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts"
        call :log "Manually updated PATH"
    )
    
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
call :log "Using Python command: %PYTHON_CMD%"

:: Check if we have Python 3.11
%PYTHON_CMD% --version 2>&1 | findstr "3.11" >nul
if %errorlevel% neq 0 (
    call :log "Python 3.11 not found, but Python is available"
    echo Python found but not 3.11. Will try to use available Python.
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

:: Install dependencies
call :log "Installing dependencies"
echo.
echo Installing dependencies...
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

:: Create necessary directories
call :log "Creating directories"
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "assets" mkdir assets

:: Create default config if needed
if not exist "config\config.json" (
    call :log "Creating default config"
    %PYTHON_CMD% -c "import json; config={'theme':'dark','font_size':12,'auto_save':True,'show_hidden':False,'recent_files':[],'recent_folders':[]}; open('config/config.json','w').write(json.dumps(config,indent=2))" >> "%DEBUG_LOG%" 2>&1
    if %errorlevel% neq 0 (
        call :log "WARNING: Failed to create default config"
    )
)

:: Test application import
call :log "Testing application import"
%PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); from src.main_window import MainWindow; print('Import successful')" >> "%DEBUG_LOG%" 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR: Failed to import application modules"
    echo ERROR: Failed to import application modules
    echo Check debug log: %DEBUG_LOG%
    pause
    exit /b 1
)

:: Run the application
call :log "Starting application"
echo.
echo ========================================
echo Starting Nova Explorer...
echo ========================================
echo.

%PYTHON_CMD% main.py
set "APP_EXIT_CODE=%errorlevel%"
call :log "Application exited with code: %APP_EXIT_CODE%"

if %APP_EXIT_CODE% neq 0 (
    echo.
    echo Application exited with an error.
    echo Check debug log: %DEBUG_LOG%
    pause
)

endlocal
exit /b %APP_EXIT_CODE%

:log
echo [%date% %time%] %~1 >> "%DEBUG_LOG%"
echo [%date% %time%] %~1
goto :eof