@echo off
echo ========================================
echo Perfect File Manager - Auto Installer
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    echo.
    
    :: Download Python installer
    echo Downloading Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe'"
    
    :: Install Python silently
    echo Installing Python...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Wait for installation
    timeout /t 10 /nobreak >nul
    
    :: Clean up installer
    del python-installer.exe
    
    :: Refresh environment variables
    call refreshenv.cmd 2>nul || (
        echo Refreshing environment variables...
        set PATH=%PATH%;C:\Python311;C:\Python311\Scripts
    )
    
    echo Python installation completed!
    echo.
) else (
    echo Python is already installed.
    echo.
)

:: Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    python -m ensurepip --upgrade
    echo.
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo Installing required packages...
python -m pip install -r requirements.txt

:: Create necessary directories
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "assets" mkdir assets

:: Create default config if it doesn't exist
if not exist "config\config.json" (
    echo Creating default configuration...
    python -c "import json; config={'theme':'dark','font_size':12,'auto_save':True,'show_hidden':False,'recent_files':[],'recent_folders':[]}; open('config/config.json','w').write(json.dumps(config,indent=2))"
)

:: Run the application
echo.
echo ========================================
echo Starting Perfect File Manager...
echo ========================================
echo.

python main.py

:: If the application exits with an error, pause to show the error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error.
    pause
)