@echo off
setlocal ENABLEDELAYEDEXPANSION

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

where py >nul 2>nul
if errorlevel 1 goto :install_py312
py -3.12 -V >nul 2>nul
if errorlevel 1 goto :install_py312
goto :have_py312

:install_py312
echo Ensuring Python 3.12 is installed...
where winget >nul 2>nul
if errorlevel 1 (
  echo winget not found. Downloading Python 3.12 installer...
  set PYVER=3.12.7
  set PYURL=https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-amd64.exe
  set PYEXE=%TEMP%\python-%PYVER%-amd64.exe
  powershell -Command "try { Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYEXE%' -UseBasicParsing } catch { exit 1 }" || (
    echo Failed to download Python installer. Please install Python 3.12 manually.
    pause
    exit /b 1
  )
  echo Running silent installer...
  "%PYEXE%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_pip=1 TargetDir="%LOCALAPPDATA%\Programs\Python\Python312" || (
    echo Python installer failed.
    pause
    exit /b 1
  )
) else (
  winget install -e --id Python.Python.3.12 --source winget --silent
)

:have_py312
if not exist .venv (
  echo Creating virtual environment with Python 3.12...
  py -3.12 -m venv .venv 2>nul
  if errorlevel 1 (
    echo Python 3.12 not available via py launcher. Trying python.exe...
    where python >nul 2>nul && python -m venv .venv
  )
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

pyinstaller --noconfirm --name "AuroraFileManager" --windowed --add-data "app\themes.json;app" app\main.py

echo Build complete. Find the EXE in the dist\AuroraFileManager folder.
pause

endlocal