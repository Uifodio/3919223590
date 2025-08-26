@echo off
setlocal
CALL %~dp0setup_venv.bat
CALL .venv\Scripts\activate.bat

REM Build portable single-folder distribution
pyinstaller --noconfirm --clean ^
  --name "NovaExplorer" ^
  --windowed ^
  --icon assets\icon.ico ^
  --add-data "assets;assets" ^
  main.py

echo Build complete. See dist\NovaExplorer\
endlocal
