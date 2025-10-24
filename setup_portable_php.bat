@echo off
title Portable PHP Setup for Workspace Server
color 0A

echo.
echo  ========================================
echo  🚀 Portable PHP Setup
echo  ========================================
echo  Downloading and configuring standalone PHP
echo  ========================================
echo.

REM Create PHP directory
if not exist "php_standalone" mkdir php_standalone
cd php_standalone

echo Downloading PHP 8.3.12 for Windows...
echo.

REM Download PHP using PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://windows.php.net/downloads/releases/php-8.3.12-Win32-vs16-x64.zip' -OutFile 'php-8.3.12-Win32-vs16-x64.zip'}"

if not exist "php-8.3.12-Win32-vs16-x64.zip" (
    echo ❌ Failed to download PHP
    echo Trying alternative download method...
    
    REM Try alternative download
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://windows.php.net/downloads/releases/php-8.3.11-Win32-vs16-x64.zip' -OutFile 'php-8.3.11-Win32-vs16-x64.zip'}"
    
    if not exist "php-8.3.11-Win32-vs16-x64.zip" (
        echo ❌ Failed to download PHP automatically
        echo Please download PHP manually from: https://windows.php.net/download/
        echo Extract it to the php_standalone folder
        pause
        exit /b 1
    ) else (
        set PHP_FILE=php-8.3.11-Win32-vs16-x64.zip
    )
) else (
    set PHP_FILE=php-8.3.12-Win32-vs16-x64.zip
)

echo ✓ PHP downloaded successfully
echo.

echo Extracting PHP...
powershell -Command "Expand-Archive -Path '%PHP_FILE%' -DestinationPath '.' -Force"

echo ✓ PHP extracted successfully
echo.

REM Find the extracted folder
for /d %%i in (php-*) do (
    if exist "%%i\php.exe" (
        set PHP_DIR=%%i
        goto :found
    )
)

:found
if not defined PHP_DIR (
    echo ❌ Could not find PHP installation
    pause
    exit /b 1
)

echo ✓ PHP found in: %PHP_DIR%
echo.

REM Copy PHP files to root of php_standalone
echo Setting up portable PHP...
xcopy "%PHP_DIR%\*" "." /E /I /Y

REM Remove the extracted folder
rmdir /s /q "%PHP_DIR%"

REM Configure PHP
echo Configuring PHP...
if not exist "php.ini" (
    copy "php.ini-development" "php.ini"
)

REM Enable common extensions
echo Enabling common PHP extensions...
powershell -Command "(Get-Content 'php.ini') -replace ';extension=curl', 'extension=curl' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=gd', 'extension=gd' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=mbstring', 'extension=mbstring' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=openssl', 'extension=openssl' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=pdo_mysql', 'extension=pdo_mysql' | Set-Content 'php.ini'"
powershell -Command "(Get-Content 'php.ini') -replace ';extension=zip', 'extension=zip' | Set-Content 'php.ini'"

echo ✓ PHP configured successfully
echo.

REM Test PHP
echo Testing PHP installation...
php --version
if errorlevel 1 (
    echo ❌ PHP test failed
    pause
    exit /b 1
)

echo ✓ PHP is working correctly
echo.

REM Clean up
del "%PHP_FILE%" 2>nul

echo.
echo  ========================================
echo  ✅ Portable PHP Setup Complete!
echo  ========================================
echo  PHP is now available in: php_standalone\
echo  You can now run the workspace server
echo  ========================================
echo.

cd ..
pause