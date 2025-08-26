@echo off
title Windows File Manager - One Click Install
color 0B

echo.
echo ========================================
echo   Windows File Manager - One Click Install
echo ========================================
echo.
echo This will automatically:
echo   - Install Python (if needed)
echo   - Install all dependencies
echo   - Create executable file
echo   - Create desktop shortcut
echo   - Create start menu entry
echo   - Set up everything for you
echo.
echo Estimated time: 5-10 minutes
echo.
echo [INFO] Starting automatic installation...
echo.

REM Check if enhanced installer exists
if exist "auto_install_and_compile_enhanced.bat" (
    echo [INFO] Running enhanced installer...
    call "auto_install_and_compile_enhanced.bat"
) else if exist "auto_install_and_compile.bat" (
    echo [INFO] Running standard installer...
    call "auto_install_and_compile.bat"
) else (
    echo [ERROR] Installer files not found!
    echo [INFO] Please ensure all project files are in the same directory.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Your Windows File Manager is now ready to use!
echo.
pause