@echo off
echo Building Modern Server Administrator...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Install required Python packages
echo Installing required packages...
pip install flask werkzeug psutil

REM Create necessary directories
echo Creating directories...
if not exist "sites" mkdir sites
if not exist "logs" mkdir logs
if not exist "apache\bin" mkdir apache\bin
if not exist "apache\conf" mkdir apache\conf
if not exist "apache\logs" mkdir apache\logs
if not exist "apache\htdocs" mkdir apache\htdocs

REM Set up Apache configuration
echo Setting up Apache configuration...
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

echo.
echo Build complete! You can now run start.bat to start the server administrator.
echo.
pause