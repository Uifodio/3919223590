@echo off
title Modern Server Administrator - Build System
color 0B
cls

echo.
echo  ================================================================
echo  |                                                              |
echo  |           MODERN SERVER ADMINISTRATOR v2.0                  |
echo  |                      BUILD SYSTEM                           |
echo  |                                                              |
echo  ================================================================
echo.

REM Check if Python is available
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [ERROR] Please install Python 3.7+ and try again
    echo.
    echo [INFO] Download Python from: https://www.python.org/downloads/
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python is available
echo.

REM Install required Python packages
echo [INFO] Installing required packages...
echo [INFO] Installing Flask, Werkzeug, and psutil...
pip install flask werkzeug psutil
if errorlevel 1 (
    echo [ERROR] Failed to install required packages
    echo [ERROR] Please run: pip install flask werkzeug psutil
    pause
    exit /b 1
)
echo [OK] Packages installed successfully
echo.

REM Create necessary directories
echo [INFO] Creating directory structure...
if not exist "sites" mkdir sites
if not exist "logs" mkdir logs
if not exist "apache\bin" mkdir apache\bin
if not exist "apache\conf" mkdir apache\conf
if not exist "apache\logs" mkdir apache\logs
if not exist "apache\htdocs" mkdir apache\htdocs
echo [OK] Directories created
echo.

REM Set up Apache configuration
echo [INFO] Setting up Apache configuration...
echo # Portable Apache Configuration > apache\conf\httpd.conf
echo ServerRoot "%~dp0apache" >> apache\conf\httpd.conf
echo Listen 8080 >> apache\conf\httpd.conf
echo. >> apache\conf\httpd.conf
echo DocumentRoot "%~dp0apache\htdocs" >> apache\conf\httpd.conf
echo DirectoryIndex index.html index.php index.htm >> apache\conf\httpd.conf
echo. >> apache\conf\httpd.conf
echo ^<Directory "%~dp0apache\htdocs"^> >> apache\conf\httpd.conf
echo     Options Indexes FollowSymLinks >> apache\conf\httpd.conf
echo     AllowOverride All >> apache\conf\httpd.conf
echo     Require all granted >> apache\conf\httpd.conf
echo ^</Directory^> >> apache\conf\httpd.conf
echo [OK] Apache configuration created
echo.

REM Create test site
echo [INFO] Creating test site...
if not exist "sites\test-site" mkdir sites\test-site
echo ^<!DOCTYPE html^> > sites\test-site\index.html
echo ^<html^>^<head^>^<title^>Test Site^</title^>^</head^> >> sites\test-site\index.html
echo ^<body^>^<h1^>Apache Server Test^</h1^>^<p^>This site is working!^</p^>^</body^> >> sites\test-site\index.html
echo ^</html^> >> sites\test-site\index.html

echo ^<?php > sites\test-site\index.php
echo echo "^<!DOCTYPE html^>"; >> sites\test-site\index.php
echo echo "^<html^>^<head^>^<title^>PHP Test^</title^>^</head^>"; >> sites\test-site\index.php
echo echo "^<body^>^<h1^>PHP is working!^</h1^>"; >> sites\test-site\index.php
echo echo "^<p^>Current time: " . date('Y-m-d H:i:s') . "^</p^>"; >> sites\test-site\index.php
echo echo "^<p^>PHP Version: " . phpversion() . "^</p^>"; >> sites\test-site\index.php
echo echo "^</body^>^</html^>"; >> sites\test-site\index.php
echo ?^> >> sites\test-site\index.php
echo [OK] Test site created
echo.

echo [SUCCESS] Build complete!
echo.
echo [INFO] You can now run start.bat to start the server administrator
echo [INFO] The server will be available at: http://localhost:3000
echo.
pause