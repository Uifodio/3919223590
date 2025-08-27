@echo off
setlocal

REM Change to this script's directory
cd /d "%~dp0"

set LOG=anora_launcher.log

echo ================================================================ >> "%LOG%"
echo [%%DATE%% %%TIME%%] Starting Launch_Anora.bat >> "%LOG%"

REM Detect Python launcher or python.exe
set PYRUN=
py -3 -V >nul 2>&1 && set PYRUN=py -3
if not defined PYRUN (
  py -V >nul 2>&1 && set PYRUN=py
)
if not defined PYRUN (
  where python >nul 2>&1 && set PYRUN=python
)
if not defined PYRUN (
  echo Python not found. Please install Python 3.10+ from https://www.python.org/ >> "%LOG%"
  echo Python not found. Please install Python 3.10+.
  pause
  exit /b 1
)

echo Using interpreter: %PYRUN% >> "%LOG%"
echo.
echo Ensuring pip is up to date...
%PYRUN% -m pip install -U pip setuptools wheel >> "%LOG%" 2>&1

echo Installing/validating wxPython (this may take a few minutes)...
%PYRUN% -m pip install -U "wxPython>=4.2.1" -f https://extras.wxpython.org/wxPython4/extras/index.html >> "%LOG%" 2>&1
if errorlevel 1 (
  echo Retry wxPython without extras index... >> "%LOG%"
  %PYRUN% -m pip install -U "wxPython>=4.2.1" >> "%LOG%" 2>&1
)

echo Installing optional packages (pywin32, pygments)...
%PYRUN% -m pip install -U pywin32 pygments >> "%LOG%" 2>&1

echo Verifying wx imports...
%PYRUN% -c "import wx, wx.stc, wx.aui, wx.adv, wx.html, wx.grid, wx.richtext; print('wx OK')" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo wxPython still not importable. See %LOG% for details.
  echo wxPython still not importable. See %LOG% for details. >> "%LOG%"
  pause
  exit /b 2
)

echo Launching editor via launcher...
%PYRUN% launch_anora.py %* >> "%LOG%" 2>&1
if errorlevel 1 (
  echo Launcher returned non-zero. Falling back to direct run... >> "%LOG%"
  %PYRUN% anora_editor.py %* >> "%LOG%" 2>&1
)

echo [%%DATE%% %%TIME%%] Launch_Anora.bat finished >> "%LOG%"
endlocal