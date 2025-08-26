@echo off
title Nova Explorer - Build EXE
color 0B

echo.
echo ========================================
echo    Nova Explorer - Build EXE
echo ========================================
echo    Creating Standalone Executable
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.11 or later from https://python.org
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found - Installing build dependencies...
echo.

:: Install PyInstaller and dependencies
echo [INSTALL] Installing PyInstaller...
python -m pip install pyinstaller==6.2.0 --quiet

echo [INSTALL] Installing Kivy and dependencies...
python -m pip install kivy==2.3.1 kivymd==1.1.1 pillow==10.1.0 pywin32==306 psutil==5.9.6 pyperclip==1.8.2 send2trash==1.8.3 --quiet

if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install with specific versions
    echo [INFO] Trying alternative installation method...
    
    python -m pip install pyinstaller kivy kivymd pillow pywin32 psutil pyperclip send2trash --quiet
    
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
)

echo.
echo [BUILD] Creating executable...
echo [INFO] This may take a few minutes...
echo.

:: Build the executable
python -m PyInstaller --onefile --windowed --name "NovaExplorer" --icon=NONE main.py

if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Build completed successfully!
echo.

:: Check if EXE was created
if exist "dist\NovaExplorer.exe" (
    echo [INFO] Executable created: dist\NovaExplorer.exe
    echo [INFO] Size: 
    dir "dist\NovaExplorer.exe" | find "NovaExplorer.exe"
    echo.
    echo [SUCCESS] You can now run NovaExplorer.exe from the dist folder!
) else (
    echo [WARNING] EXE not found in dist folder
    echo [INFO] Checking other possible locations...
    
    if exist "NovaExplorer.exe" (
        echo [INFO] Found: NovaExplorer.exe (current directory)
        if not exist "dist" mkdir dist
        copy "NovaExplorer.exe" "dist\"
        echo [SUCCESS] Moved to dist folder!
    ) else (
        echo [ERROR] Could not find the executable
        echo [INFO] Please check the build output for errors
    )
)

echo.
echo [INFO] Build process completed.
echo [INFO] You can now distribute NovaExplorer.exe to other computers!
echo.
pause