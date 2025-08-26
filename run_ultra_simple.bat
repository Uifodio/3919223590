@echo off
echo ========================================
echo Nova Explorer - Ultra Simple Version
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python first.
    pause
    exit /b 1
)

echo Installing Kivy dependencies...
echo.

:: Install Kivy with specific versions to avoid conflicts
echo Installing Kivy 2.3.1...
python -m pip install kivy==2.3.1

echo Installing other dependencies...
python -m pip install kivymd==1.1.1 pillow==10.1.0 pywin32==306 psutil==5.9.6 pyperclip==1.8.2 send2trash==1.8.3

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Trying alternative installation method...
    
    :: Try installing without version constraints
    python -m pip install kivy kivymd pillow pywin32 psutil pyperclip send2trash
    
    if %errorlevel% neq 0 (
        echo ERROR: Installation failed
        pause
        exit /b 1
    )
)

echo.
echo Dependencies installed successfully!
echo Starting Nova Explorer (Ultra Simple Version)...
echo.

python main_ultra_simple.py

pause