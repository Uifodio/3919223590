@echo off
setlocal enabledelayedexpansion

:: Set console title
title Super File Manager - Build Script

:: Set colors for output
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "MAGENTA=[95m"
set "CYAN=[96m"
set "WHITE=[97m"
set "RESET=[0m"

:: Create log file
set "LOG_FILE=build_log_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt"
set "LOG_FILE=%LOG_FILE: =0%"

echo %BLUE%========================================%RESET%
echo %BLUE%  Super File Manager - Build Script%RESET%
echo %BLUE%========================================%RESET%
echo %CYAN%Build started at: %date% %time%%RESET%
echo %CYAN%Log file: %LOG_FILE%%RESET%
echo.

:: Function to log messages
:log
echo [%date% %time%] %~1 >> "%LOG_FILE%"
echo %~1
goto :eof

:: Function to check if command succeeded
:check_error
if %errorlevel% neq 0 (
    echo %RED%ERROR: %~1 failed with exit code %errorlevel%%RESET%
    echo [%date% %time%] ERROR: %~1 failed with exit code %errorlevel% >> "%LOG_FILE%"
    pause
    exit /b %errorlevel%
)
goto :eof

:: Check if Node.js is installed
echo %YELLOW%[1/8] Checking Node.js installation...%RESET%
call :log "[1/8] Checking Node.js installation..."
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%ERROR: Node.js is not installed or not in PATH%RESET%
    echo %YELLOW%Please install Node.js from https://nodejs.org/%RESET%
    echo [%date% %time%] ERROR: Node.js not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version 2^>^&1') do set "NODE_VERSION=%%i"
echo %GREEN%✓ Node.js version: %NODE_VERSION%%RESET%
call :log "✓ Node.js version: %NODE_VERSION%"

:: Check if npm is available
echo %YELLOW%[1/8] Checking npm installation...%RESET%
call :log "[1/8] Checking npm installation..."
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%ERROR: npm is not available%RESET%
    echo [%date% %time%] ERROR: npm not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm --version 2^>^&1') do set "NPM_VERSION=%%i"
echo %GREEN%✓ npm version: %NPM_VERSION%%RESET%
call :log "✓ npm version: %NPM_VERSION%"

:: Check if Git is available (optional)
echo %YELLOW%[1/8] Checking Git installation...%RESET%
call :log "[1/8] Checking Git installation..."
git --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('git --version 2^>^&1') do set "GIT_VERSION=%%i"
    echo %GREEN%✓ Git version: %GIT_VERSION%%RESET%
    call :log "✓ Git version: %GIT_VERSION%"
) else (
    echo %YELLOW%⚠ Git not found (optional)%RESET%
    call :log "⚠ Git not found (optional)"
)

:: Check current directory
echo %YELLOW%[2/8] Checking project structure...%RESET%
call :log "[2/8] Checking project structure..."
if not exist "package.json" (
    echo %RED%ERROR: package.json not found. Please run this script from the project root directory.%RESET%
    echo [%date% %time%] ERROR: package.json not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

if not exist "src" (
    echo %RED%ERROR: src directory not found. Please run this script from the project root directory.%RESET%
    echo [%date% %time%] ERROR: src directory not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo %GREEN%✓ Project structure verified%RESET%
call :log "✓ Project structure verified"

:: Clean previous builds
echo %YELLOW%[3/8] Cleaning previous builds...%RESET%
call :log "[3/8] Cleaning previous builds..."
if exist "dist" (
    echo %CYAN%Removing dist directory...%RESET%
    rmdir /s /q "dist" 2>nul
    call :log "Removed dist directory"
)

if exist "node_modules" (
    echo %CYAN%Removing node_modules directory...%RESET%
    rmdir /s /q "node_modules" 2>nul
    call :log "Removed node_modules directory"
)

if exist "package-lock.json" (
    echo %CYAN%Removing package-lock.json...%RESET%
    del "package-lock.json" 2>nul
    call :log "Removed package-lock.json"
)

echo %GREEN%✓ Cleanup completed%RESET%
call :log "✓ Cleanup completed"

:: Install dependencies
echo %YELLOW%[4/8] Installing dependencies...%RESET%
call :log "[4/8] Installing dependencies..."
echo %CYAN%Running: npm install%RESET%
call :log "Running: npm install"
npm install --verbose >> "%LOG_FILE%" 2>&1
call :check_error "npm install"

echo %GREEN%✓ Dependencies installed successfully%RESET%
call :log "✓ Dependencies installed successfully"

:: Verify critical dependencies
echo %YELLOW%[5/8] Verifying critical dependencies...%RESET%
call :log "[5/8] Verifying critical dependencies..."

if not exist "node_modules\electron" (
    echo %RED%ERROR: Electron not found in node_modules%RESET%
    echo [%date% %time%] ERROR: Electron not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

if not exist "node_modules\react" (
    echo %RED%ERROR: React not found in node_modules%RESET%
    echo [%date% %time%] ERROR: React not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

if not exist "node_modules\@monaco-editor\react" (
    echo %RED%ERROR: Monaco Editor not found in node_modules%RESET%
    echo [%date% %time%] ERROR: Monaco Editor not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo %GREEN%✓ Critical dependencies verified%RESET%
call :log "✓ Critical dependencies verified"

:: Build React application
echo %YELLOW%[6/8] Building React application...%RESET%
call :log "[6/8] Building React application..."
echo %CYAN%Running: npm run build%RESET%
call :log "Running: npm run build"
npm run build >> "%LOG_FILE%" 2>&1
call :check_error "npm run build"

if not exist "dist\index.html" (
    echo %RED%ERROR: Build output not found. Check the log file for details.%RESET%
    echo [%date% %time%] ERROR: Build output not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo %GREEN%✓ React application built successfully%RESET%
call :log "✓ React application built successfully"

:: Build Electron application
echo %YELLOW%[7/8] Building Electron application...%RESET%
call :log "[7/8] Building Electron application..."
echo %CYAN%Running: npm run build:electron%RESET%
call :log "Running: npm run build:electron"
npm run build:electron >> "%LOG_FILE%" 2>&1
call :check_error "npm run build:electron"

:: Check for build output
echo %YELLOW%[8/8] Verifying build output...%RESET%
call :log "[8/8] Verifying build output..."

set "BUILD_FOUND=0"
if exist "dist\Super File Manager Setup *.exe" (
    echo %GREEN%✓ Windows installer found%RESET%
    call :log "✓ Windows installer found"
    set "BUILD_FOUND=1"
)

if exist "dist\Super File Manager-*.AppImage" (
    echo %GREEN%✓ Linux AppImage found%RESET%
    call :log "✓ Linux AppImage found"
    set "BUILD_FOUND=1"
)

if exist "dist\Super File Manager-*.dmg" (
    echo %GREEN%✓ macOS DMG found%RESET%
    call :log "✓ macOS DMG found"
    set "BUILD_FOUND=1"
)

if exist "dist\win-unpacked" (
    echo %GREEN%✓ Windows unpacked build found%RESET%
    call :log "✓ Windows unpacked build found"
    set "BUILD_FOUND=1"
)

if exist "dist\linux-unpacked" (
    echo %GREEN%✓ Linux unpacked build found%RESET%
    call :log "✓ Linux unpacked build found"
    set "BUILD_FOUND=1"
)

if exist "dist\mac" (
    echo %GREEN%✓ macOS unpacked build found%RESET%
    call :log "✓ macOS unpacked build found"
    set "BUILD_FOUND=1"
)

if %BUILD_FOUND% equ 0 (
    echo %RED%ERROR: No build output found. Check the log file for details.%RESET%
    echo [%date% %time%] ERROR: No build output found >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Display build summary
echo.
echo %BLUE%========================================%RESET%
echo %BLUE%  BUILD COMPLETED SUCCESSFULLY!%RESET%
echo %BLUE%========================================%RESET%
echo.
echo %GREEN%✓ Node.js: %NODE_VERSION%%RESET%
echo %GREEN%✓ npm: %NPM_VERSION%%RESET%
echo %GREEN%✓ Dependencies: Installed%RESET%
echo %GREEN%✓ React Build: Completed%RESET%
echo %GREEN%✓ Electron Build: Completed%RESET%
echo %GREEN%✓ Build Output: Found%RESET%
echo.
echo %CYAN%Build artifacts are in the 'dist' directory%RESET%
echo %CYAN%Log file: %LOG_FILE%%RESET%
echo.

:: List build outputs
echo %YELLOW%Build outputs found:%RESET%
dir /b "dist\*" 2>nul | findstr /v "^$" >nul && (
    for /f "tokens=*" %%i in ('dir /b "dist\*" 2^>nul') do (
        echo %WHITE%  - %%i%RESET%
    )
) || echo %WHITE%  (No files found)%RESET%

echo.
echo %MAGENTA%Press any key to open the dist folder...%RESET%
pause >nul

:: Open dist folder
if exist "dist" (
    echo %CYAN%Opening dist folder...%RESET%
    start "" "dist"
)

echo %GREEN%Build script completed successfully!%RESET%
call :log "Build script completed successfully!"
echo %CYAN%Log file saved as: %LOG_FILE%%RESET%
echo.
pause