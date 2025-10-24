@echo off
echo 🚀 Starting Unified Server Administrator...
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Install required packages
echo 📦 Installing dependencies...
pip install flask psutil pyyaml

REM Create necessary directories
if not exist "sites" mkdir sites
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "nginx_configs" mkdir nginx_configs
if not exist "php_fpm_configs" mkdir php_fpm_configs

echo ✅ Directories created
echo 🌐 Starting web server...
echo 📱 Open http://localhost:5000 in your browser
echo ==================================================

REM Start the server
python web_server_admin.py

pause