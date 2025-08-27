@echo off
echo ========================================
echo Unity Code Editor - Build Script
echo ========================================
echo.

echo [1/5] Running system diagnostic...
node diagnostic.js
if %errorlevel% neq 0 (
    echo.
    echo ❌ Diagnostic failed! Please fix the errors above.
    pause
    exit /b 1
)
echo ✅ Diagnostic passed!
echo.

echo [2/5] Installing dependencies...
npm install
if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)
echo ✅ Dependencies installed!
echo.

echo [3/5] Testing the application...
echo Starting the app in test mode...
start /wait npm start
if %errorlevel% neq 0 (
    echo.
    echo ❌ Application test failed!
    pause
    exit /b 1
)
echo ✅ Application test passed!
echo.

echo [4/5] Building Windows executable...
echo This may take a few minutes...
npm run build-win
if %errorlevel% neq 0 (
    echo.
    echo ❌ Build failed!
    pause
    exit /b 1
)
echo ✅ Build completed!
echo.

echo [5/5] Checking output...
if exist "dist\Unity Code Editor Setup.exe" (
    echo ✅ Executable created successfully!
    echo.
    echo 📁 Your executable is located at:
    echo    dist\Unity Code Editor Setup.exe
    echo.
    echo 🎉 Build process completed successfully!
    echo.
    echo To install the app:
    echo 1. Double-click "Unity Code Editor Setup.exe"
    echo 2. Follow the installation wizard
    echo 3. Launch from Start Menu or Desktop shortcut
    echo.
) else (
    echo ❌ Executable not found in dist folder!
    echo Please check the build output above for errors.
)

pause