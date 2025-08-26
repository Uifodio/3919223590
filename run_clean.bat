@echo off
echo ========================================
echo Nova Explorer - Clean Installation
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

echo Creating clean virtual environment...
python -m venv nova_env

echo Activating virtual environment...
call nova_env\Scripts\activate.bat

echo Installing Kivy in clean environment...
python -m pip install --upgrade pip
python -m pip install kivy kivymd pillow pywin32 psutil pyperclip send2trash

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo Starting Nova Explorer...
echo.

python main.py

echo.
echo Deactivating virtual environment...
deactivate

pause