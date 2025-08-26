@echo off
echo Testing build script...
echo.

echo Checking if build.bat exists...
if exist "build.bat" (
    echo ✓ build.bat found
) else (
    echo ✗ build.bat not found
    exit /b 1
)

echo.
echo Checking if build.sh exists...
if exist "build.sh" (
    echo ✓ build.sh found
) else (
    echo ✗ build.sh not found
    exit /b 1
)

echo.
echo Checking if package.json exists...
if exist "package.json" (
    echo ✓ package.json found
) else (
    echo ✗ package.json not found
    exit /b 1
)

echo.
echo Checking if src directory exists...
if exist "src" (
    echo ✓ src directory found
) else (
    echo ✗ src directory not found
    exit /b 1
)

echo.
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo ✓ Node.js: %%i
) else (
    echo ✗ Node.js not found
    exit /b 1
)

echo.
echo Checking npm installation...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('npm --version 2^>^&1') do echo ✓ npm: %%i
) else (
    echo ✗ npm not found
    exit /b 1
)

echo.
echo ========================================
echo ✓ All prerequisites are met!
echo ✓ Build scripts are ready to use!
echo ========================================
echo.
echo To build the application:
echo - Windows: Double-click build.bat
echo - Linux/macOS: Run ./build.sh
echo.
pause