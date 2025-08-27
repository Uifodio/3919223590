@echo off
echo Setting up Kivy Counter App for Windows...
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv kivy_env
if %errorlevel% neq 0 (
    echo Failed to create virtual environment!
    echo Make sure python3-venv is installed
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call kivy_env\Scripts\activate.bat

echo.
echo Installing Kivy...
pip install kivy>=2.3.0

echo.
echo Installing PyInstaller for compilation...
pip install pyinstaller

echo.
echo Testing installation...
python test_installation.py

echo.
echo Setup complete! To run the app:
echo 1. Activate the environment: kivy_env\Scripts\activate.bat
echo 2. Run the app: python main.py
echo 3. To compile: pyinstaller CounterApp.spec
pause