@echo off
setlocal
cd /d "%~dp0"
set VENV=.venv
set VPY=%VENV%\Scripts\python.exe
set LOG=aegis_launcher.log

echo [%%DATE%% %%TIME%%] Start >> "%LOG%"

set PY=
py -3 -V >nul 2>&1 && set PY=py -3
if not defined PY where python >nul 2>&1 && set PY=python
if not defined PY echo Python not found. Install Python 3.10+ & pause & exit /b 1

if not exist "%VENV%" %PY% -m venv "%VENV%" >> "%LOG%" 2>&1
if not exist "%VPY%" echo venv missing & pause & exit /b 2

"%VPY%" -m pip install -U pip setuptools wheel >> "%LOG%" 2>&1
"%VPY%" -m pip install -U dearpygui pygments >> "%LOG%" 2>&1

"%VPY%" run_aegis.py %* >> "%LOG%" 2>&1
endlocal