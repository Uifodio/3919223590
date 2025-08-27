@echo off
echo Building Kivy Counter App...
echo.

echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Compiling to executable...
pyinstaller CounterApp.spec

echo.
echo Build complete! Check the dist/ folder for CounterApp.exe
pause