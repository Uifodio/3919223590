@echo off
echo 🚀 Starting Unified Server Administrator (Windows)...
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Install basic dependencies (skip YAML for Windows)
echo 📦 Installing dependencies...
pip install flask psutil

REM Create necessary directories
if not exist "sites" mkdir sites
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads

echo ✅ Directories created
echo 🌐 Starting web server...
echo 📱 Open http://localhost:5000 in your browser
echo ==================================================

REM Start the simplified server (Windows compatible)
python web_server_admin_simple.py

pause