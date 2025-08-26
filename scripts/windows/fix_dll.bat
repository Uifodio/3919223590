@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Nova Explorer - DLL Fix Script
echo ========================================
echo.

:: Check if dist directory exists
if not exist "dist" (
  echo ERROR: dist directory not found.
  echo Please run the build script first.
  pause
  exit /b 1
)

:: Find Python DLL
echo Looking for Python DLL...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

:: Extract version numbers
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
  set PYTHON_MAJOR=%%a
  set PYTHON_MINOR=%%b
)

set DLL_NAME=python%PYTHON_MAJOR%%PYTHON_MINOR%.dll
echo Looking for: %DLL_NAME%

:: Try to find the DLL
set DLL_FOUND=
for %%p in (
  "%PYTHON_HOME%\%DLL_NAME%"
  "%PYTHON_HOME%\DLLs\%DLL_NAME%"
  "C:\Python%PYTHON_MAJOR%%PYTHON_MINOR%\%DLL_NAME%"
  "C:\Python%PYTHON_MAJOR%%PYTHON_MINOR%\DLLs\%DLL_NAME%"
  "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%PYTHON_MAJOR%%PYTHON_MINOR%\%DLL_NAME%"
  "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%PYTHON_MAJOR%%PYTHON_MINOR%\DLLs\%DLL_NAME%"
) do (
  if exist %%p (
    echo Found DLL: %%p
    set DLL_FOUND=%%p
    goto :found_dll
  )
)

echo ERROR: Could not find %DLL_NAME%
echo.
echo Please manually copy the Python DLL to the dist directory.
echo Look for %DLL_NAME% in your Python installation directory.
pause
exit /b 1

:found_dll
echo.
echo Copying DLL to dist directory...

:: Copy to dist root
copy "%DLL_FOUND%" "dist\%DLL_NAME%" >nul
if %errorlevel% equ 0 (
  echo ✓ Copied to dist\%DLL_NAME%
) else (
  echo ✗ Failed to copy to dist\%DLL_NAME%
)

:: Copy to _internal if it exists
if exist "dist\NovaExplorer\_internal" (
  copy "%DLL_FOUND%" "dist\NovaExplorer\_internal\%DLL_NAME%" >nul
  if %errorlevel% equ 0 (
    echo ✓ Copied to dist\NovaExplorer\_internal\%DLL_NAME%
  ) else (
    echo ✗ Failed to copy to dist\NovaExplorer\_internal\%DLL_NAME%
  )
)

echo.
echo DLL fix completed.
echo Try running the application now.
pause