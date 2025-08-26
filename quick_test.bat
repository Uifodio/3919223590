@echo off
echo ========================================
echo Nova Explorer - Quick Test
echo ========================================
echo.

echo Testing Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo.
echo Running installation test...
python test_install.py

echo.
echo Test completed. Press any key to exit...
pause >nul