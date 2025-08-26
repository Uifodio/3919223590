@echo off
setlocal

REM Create and activate venv, install requirements
IF NOT EXIST .venv (
  echo Creating virtual environment...
  python -m venv .venv
)

CALL .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Venv ready.
endlocal
