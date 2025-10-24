@echo off
title Complete Workspace Server Setup
color 0A

echo.
echo  ========================================
echo  🚀 Complete Workspace Server Setup
echo  ========================================
echo  Professional Multi-Project Environment
echo  ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✓ Python found: 
python --version
echo.

REM Create necessary directories
echo Creating workspace directories...
if not exist "projects" mkdir projects
if not exist "logs" mkdir logs
if not exist "sites" mkdir sites
if not exist "uploads" mkdir uploads
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "php_standalone" mkdir php_standalone
echo ✓ Directories created
echo.

REM Download and setup portable PHP
echo Setting up portable PHP...
cd php_standalone

REM Try to download PHP 8.3.12
echo Downloading PHP 8.3.12...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri 'https://windows.php.net/downloads/releases/php-8.3.12-Win32-vs16-x64.zip' -OutFile 'php-8.3.12-Win32-vs16-x64.zip' } catch { Write-Host 'Failed to download 8.3.12, trying 8.3.11...'; Invoke-WebRequest -Uri 'https://windows.php.net/downloads/releases/php-8.3.11-Win32-vs16-x64.zip' -OutFile 'php-8.3.11-Win32-vs16-x64.zip' } }"

REM Check which file was downloaded
if exist "php-8.3.12-Win32-vs16-x64.zip" (
    set PHP_FILE=php-8.3.12-Win32-vs16-x64.zip
) else if exist "php-8.3.11-Win32-vs16-x64.zip" (
    set PHP_FILE=php-8.3.11-Win32-vs16-x64.zip
) else (
    echo ❌ Failed to download PHP automatically
    echo Please download PHP manually from: https://windows.php.net/download/
    echo Extract it to the php_standalone folder
    cd ..
    pause
    exit /b 1
)

echo ✓ PHP downloaded: %PHP_FILE%
echo.

echo Extracting PHP...
powershell -Command "Expand-Archive -Path '%PHP_FILE%' -DestinationPath '.' -Force"

REM Find the extracted folder and move files
for /d %%i in (php-*) do (
    if exist "%%i\php.exe" (
        echo ✓ Found PHP in: %%i
        xcopy "%%i\*" "." /E /I /Y
        rmdir /s /q "%%i"
        goto :php_extracted
    )
)

:php_extracted
if not exist "php.exe" (
    echo ❌ PHP extraction failed
    cd ..
    pause
    exit /b 1
)

REM Configure PHP
echo Configuring PHP...
if not exist "php.ini" (
    copy "php.ini-development" "php.ini"
)

REM Enable common extensions
echo Enabling PHP extensions...
powershell -Command "(Get-Content 'php.ini') -replace ';extension=curl', 'extension=curl' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=gd', 'extension=gd' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=mbstring', 'extension=mbstring' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=openssl', 'extension=openssl' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=pdo_mysql', 'extension=pdo_mysql' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=zip', 'extension=zip' | Set-Content 'php.ini'"

REM Test PHP
echo Testing PHP...
php --version
if errorlevel 1 (
    echo ❌ PHP test failed
    cd ..
    pause
    exit /b 1
)

echo ✓ PHP configured and working
echo.

REM Clean up
del "%PHP_FILE%" 2>nul
cd ..

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo ✓ Python dependencies installed
echo.

REM Create demo project
echo Creating demo project...
if not exist "sites\demo" mkdir sites\demo
echo ^<!DOCTYPE html^> > sites\demo\index.html
echo ^<html^> >> sites\demo\index.html
echo ^<head^> >> sites\demo\index.html
echo     ^<title^>Demo Project^</title^> >> sites\demo\index.html
echo     ^<style^>body{font-family:Arial;margin:40px;background:#f0f0f0;}^</style^> >> sites\demo\index.html
echo ^</head^> >> sites\demo\index.html
echo ^<body^> >> sites\demo\index.html
echo     ^<h1^>Welcome to Workspace Server!^</h1^> >> sites\demo\index.html
echo     ^<p^>This is a demo project running through the reverse proxy.^</p^> >> sites\demo\index.html
echo     ^<p^>Server time: ^<script^>document.write(new Date())^</script^>^</p^> >> sites\demo\index.html
echo ^</body^> >> sites\demo\index.html
echo ^</html^> >> sites\demo\index.html

echo ✓ Demo project created
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Workspace Server.lnk'); $Shortcut.TargetPath = '%~dp0start_workspace.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Windows-Compatible Workspace Server'; $Shortcut.Save()"

echo ✓ Desktop shortcut created
echo.

echo.
echo  ========================================
echo  ✅ Setup Complete!
echo  ========================================
echo  Your workspace server is ready to use!
echo.
echo  Features installed:
echo  • Portable PHP 8.3.x
echo  • Python Flask server
echo  • Modern web interface
echo  • Reverse proxy functionality
echo  • Multi-project support
echo.
echo  To start the server:
echo  1. Run: start_workspace.bat
echo  2. Or double-click the desktop shortcut
echo  3. Open: http://localhost:8000
echo.
echo  ========================================
echo.

pause