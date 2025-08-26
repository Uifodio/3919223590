@echo off
echo ========================================
echo    Nova Explorer - File Manager
echo ========================================
echo.
echo This will launch Nova Explorer using Godot Engine.
echo.
echo If you don't have Godot installed:
echo 1. Download from: https://godotengine.org/download
echo 2. Extract to any folder
echo 3. Run godot.exe and import this project
echo.
echo Press any key to continue...
pause >nul

REM Try to find Godot in common locations
set GODOT_PATH=

REM Check if Godot is in PATH
where godot >nul 2>&1
if %errorlevel% == 0 (
    set GODOT_PATH=godot
    goto :run
)

REM Check common installation paths
if exist "C:\Program Files\Godot\godot.exe" (
    set GODOT_PATH="C:\Program Files\Godot\godot.exe"
    goto :run
)

if exist "C:\Program Files (x86)\Godot\godot.exe" (
    set GODOT_PATH="C:\Program Files (x86)\Godot\godot.exe"
    goto :run
)

REM Check if Godot is in the same directory
if exist "godot.exe" (
    set GODOT_PATH=godot.exe
    goto :run
)

REM Check if Godot is in a subdirectory
for /d %%i in (godot*) do (
    if exist "%%i\godot.exe" (
        set GODOT_PATH="%%i\godot.exe"
        goto :run
    )
)

echo.
echo ERROR: Godot Engine not found!
echo.
echo Please download Godot from: https://godotengine.org/download
echo Extract it to this folder or install it to Program Files
echo.
echo Then run this batch file again.
echo.
pause
exit /b 1

:run
echo.
echo Found Godot at: %GODOT_PATH%
echo Launching Nova Explorer...
echo.
%GODOT_PATH% --path "%~dp0" --main-pack "%~dp0project.godot"