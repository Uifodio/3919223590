@echo off
setlocal ENABLEDELAYEDEXPANSION

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist .venv (
  echo Creating virtual environment...
  py -3.12 -m venv .venv 2>nul
  if errorlevel 1 (
    echo Python launcher not found. Trying python directly...
    python -m venv .venv
  )
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip >nul
pip install -r requirements.txt

python app\main.py

endlocal