@echo off
setlocal

REM ============================================
REM Anora Editor Bulletproof Windows Launcher (BAT)
REM - Creates a private .venv next to this script
REM - Installs wxPython, pywin32, pygments with retries
REM - Verifies imports
REM - Launches the editor with the venv interpreter
REM - Logs to anora_launcher.log
REM ============================================

cd /d "%~dp0"
set LOG=anora_launcher.log
set VENV_DIR=.venv
set VENV_PY=%VENV_DIR%\Scripts\python.exe

echo ================================================================ >> "%LOG%"
echo [%%DATE%% %%TIME%%] Starting Launch_Anora.bat >> "%LOG%"

REM Find a system Python to create the venv if needed
set SYS_PY=
py -3 -V >nul 2>&1 && set SYS_PY=py -3
if not defined SYS_PY (
  where python >nul 2>&1 && set SYS_PY=python
)
if not defined SYS_PY (
  echo Python not found. Install Python 3.10+ and retry. >> "%LOG%"
  echo Python not found. Install Python 3.10+ and retry.
  pause
  exit /b 1
)

echo Creating virtual environment if missing... >> "%LOG%"
if not exist "%VENV_DIR%" (
  %SYS_PY% -m venv "%VENV_DIR%" >> "%LOG%" 2>&1
  if errorlevel 1 (
    echo Failed to create venv. See %LOG% for details.
    echo Failed to create venv. >> "%LOG%"
    pause
    exit /b 2
  )
)

if not exist "%VENV_PY%" (
  echo venv python not found at %VENV_PY%. >> "%LOG%"
  echo venv python not found at %VENV_PY%.
  pause
  exit /b 3
)

echo Upgrading pip/setuptools/wheel... >> "%LOG%"
"%VENV_PY%" -m pip install -U pip setuptools wheel >> "%LOG%" 2>&1

echo Installing wxPython (attempt 1, with extras wheels)... >> "%LOG%"
"%VENV_PY%" -m pip install -U "wxPython>=4.2.1" -f https://extras.wxpython.org/wxPython4/extras/index.html >> "%LOG%" 2>&1
if errorlevel 1 (
  echo Installing wxPython (attempt 2, no extras)... >> "%LOG%"
  "%VENV_PY%" -m pip install -U "wxPython>=4.2.1" >> "%LOG%" 2>&1
)

echo Installing optional packages (pywin32, pygments)... >> "%LOG%"
"%VENV_PY%" -m pip install -U pywin32 pygments >> "%LOG%" 2>&1

echo Verifying wx imports with venv... >> "%LOG%"
"%VENV_PY%" -c "import wx, wx.stc, wx.aui, wx.adv, wx.html, wx.grid, wx.richtext; print('wx OK')" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo wxPython still not importable in venv. See %LOG% for details.
  echo wxPython still not importable in venv. >> "%LOG%"
  type "%LOG%"
  pause
  exit /b 4
)

echo Launching launcher with venv interpreter... >> "%LOG%"
"%VENV_PY%" launch_anora.py %* >> "%LOG%" 2>&1
if errorlevel 1 (
  echo Launcher returned non-zero, attempting direct run... >> "%LOG%"
  "%VENV_PY%" anora_editor.py %* >> "%LOG%" 2>&1
)

echo [%%DATE%% %%TIME%%] Launch_Anora.bat finished >> "%LOG%"
endlocal