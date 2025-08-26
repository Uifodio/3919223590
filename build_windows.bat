@echo off
setlocal ENABLEDELAYEDEXPANSION

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Checking python.exe...
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python not found. Attempting to install via winget...
    where winget >nul 2>nul
    if errorlevel 1 (
      echo winget not found. Please install Python manually from https://www.python.org/downloads/windows/
      pause
      exit /b 1
    ) else (
      winget install -e --id Python.Python.3.11 --source winget --silent
    )
  )
)

if not exist .venv (
  echo Creating virtual environment...
  py -3 -m venv .venv 2>nul
  if errorlevel 1 (
    python -m venv .venv
  )
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

pyinstaller --noconfirm --name "AuroraFileManager" --windowed --add-data "app\themes.json;app" app\main.py

echo Build complete. Find the EXE in the dist\AuroraFileManager folder.
pause

endlocal