@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Nova Explorer - Auto Install & Run
echo ========================================
echo.

:: Check if Python 3.11 is available
python --version 2>&1 | findstr "3.11" >nul
if %errorlevel% neq 0 (
    echo Python 3.11 not found. Installing Python 3.11...
    echo.
    
    :: Download Python 3.11.8
    echo Downloading Python 3.11.8...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python311-installer.exe' -UseBasicParsing } catch { Write-Host 'Download failed: ' + $_.Exception.Message }"
    
    if exist "python311-installer.exe" (
        echo Installing Python 3.11.8...
        python311-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1
        
        :: Wait for installation
        timeout /t 15 /nobreak >nul
        
        :: Clean up
        del python311-installer.exe
        
        :: Refresh PATH
        call refreshenv.cmd 2>nul || (
            set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts"
        )
        
        echo Python 3.11 installation completed!
    ) else (
        echo ERROR: Failed to download Python installer
        pause
        exit /b 1
    )
) else (
    echo Python 3.11 found.
)

:: Verify Python 3.11
python --version 2>&1 | findstr "3.11" >nul
if %errorlevel% neq 0 (
    echo ERROR: Python 3.11 still not available after installation
    pause
    exit /b 1
)

:: Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

:: Create necessary directories
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "assets" mkdir assets

:: Create default config if needed
if not exist "config\config.json" (
    python -c "import json; config={'theme':'dark','font_size':12,'auto_save':True,'show_hidden':False,'recent_files':[],'recent_folders':[]}; open('config/config.json','w').write(json.dumps(config,indent=2))"
)

:: Run the application
echo.
echo ========================================
echo Starting Nova Explorer...
echo ========================================
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error.
    pause
)

endlocal