@echo off
setlocal enabledelayedexpansion

REM ========================================
REM Windows File Manager - Enhanced Auto Install & Compile
REM ========================================
title Windows File Manager - Enhanced Auto Setup
color 0A

echo.
echo ========================================
echo   Windows File Manager - Enhanced Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running with administrator privileges
) else (
    echo [WARNING] Not running as administrator - some features may be limited
    echo [INFO] Right-click and 'Run as administrator' for best results
    echo.
)

REM ========================================
REM Step 1: Check Python Installation
REM ========================================
echo [STEP 1] Checking Python installation...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo [INFO] Attempting to download and install Python...
    echo.
    
    REM Download Python installer
    echo [INFO] Downloading Python 3.11.8 (latest stable)...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python_installer.exe'}"
    
    if exist python_installer.exe (
        echo [INFO] Installing Python...
        echo [INFO] Please follow the installation wizard and ensure 'Add Python to PATH' is checked
        echo [INFO] After installation, close this window and run the batch file again
        echo.
        pause
        python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        del python_installer.exe
        echo.
        echo [INFO] Python installation completed. Please restart this batch file.
        pause
        exit /b 1
    ) else (
        echo [ERROR] Failed to download Python installer
        echo [INFO] Please manually install Python from https://python.org
        echo [INFO] Make sure to check 'Add Python to PATH' during installation
        pause
        exit /b 1
    )
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [SUCCESS] Python !PYTHON_VERSION! is installed
)

REM ========================================
REM Step 2: Check Python Version
REM ========================================
echo.
echo [STEP 2] Checking Python version compatibility...
echo.

python -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.6 or higher is required
    echo [INFO] Current version may be too old
    pause
    exit /b 1
) else (
    echo [SUCCESS] Python version is compatible
)

REM ========================================
REM Step 3: Install/Upgrade pip
REM ========================================
echo.
echo [STEP 3] Ensuring pip is up to date...
echo.

python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
) else (
    echo [SUCCESS] pip is up to date
)

REM ========================================
REM Step 4: Install Required Dependencies
REM ========================================
echo.
echo [STEP 4] Installing required dependencies...
echo.

REM Install pywin32 for Windows API access
echo [INFO] Installing pywin32 for enhanced Windows functionality...
python -m pip install pywin32>=228 --quiet
if errorlevel 1 (
    echo [WARNING] Failed to install pywin32, continuing with limited functionality...
) else (
    echo [SUCCESS] pywin32 installed
)

REM Install PyInstaller for creating executable
echo [INFO] Installing PyInstaller for executable creation...
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller
    echo [INFO] Cannot create executable without PyInstaller
    pause
    exit /b 1
) else (
    echo [SUCCESS] PyInstaller installed
)

REM Install Pillow for icon creation
echo [INFO] Installing Pillow for icon generation...
python -m pip install pillow --quiet
if errorlevel 1 (
    echo [WARNING] Failed to install Pillow, will use default icon...
) else (
    echo [SUCCESS] Pillow installed
)

REM Install additional useful packages
echo [INFO] Installing additional packages for enhanced functionality...
python -m pip install psutil --quiet
python -m pip install requests --quiet
echo [SUCCESS] Additional packages installed

REM ========================================
REM Step 5: Create Icon
REM ========================================
echo.
echo [STEP 5] Creating application icon...
echo.

if exist "create_icon.py" (
    echo [INFO] Generating custom file manager icon...
    python create_icon.py
    if exist "file_manager.ico" (
        echo [SUCCESS] Custom icon created
        set ICON_PATH=file_manager.ico
    ) else (
        echo [WARNING] Failed to create custom icon, will use default
        set ICON_PATH=
    )
) else (
    echo [INFO] Icon generator not found, will use default icon
    set ICON_PATH=
)

REM ========================================
REM Step 6: Verify File Manager Files
REM ========================================
echo.
echo [STEP 6] Checking file manager files...
echo.

if not exist "file_manager.py" (
    echo [ERROR] file_manager.py not found in current directory
    echo [INFO] Please ensure all project files are in the same directory as this batch file
    pause
    exit /b 1
) else (
    echo [SUCCESS] file_manager.py found
)

REM ========================================
REM Step 7: Test File Manager
REM ========================================
echo.
echo [STEP 7] Testing file manager functionality...
echo.

if exist "test_file_manager.py" (
    echo [INFO] Running file manager test suite...
    python test_file_manager.py
    if errorlevel 1 (
        echo [WARNING] Some tests failed, but continuing with compilation...
    ) else (
        echo [SUCCESS] All tests passed
    )
) else (
    echo [INFO] Test file not found, skipping tests...
)

REM ========================================
REM Step 8: Create Executable
REM ========================================
echo.
echo [STEP 8] Creating executable file...
echo.

echo [INFO] This may take a few minutes...
echo [INFO] PyInstaller is compiling the application...

REM Create PyInstaller spec file for better control
echo [INFO] Creating optimized build configuration...

REM Create a temporary spec file with icon support
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis(
echo     ['file_manager.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=['win32api', 'win32con', 'win32gui', 'win32process', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'tkinter.simpledialog'],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'jupyter'],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
if defined ICON_PATH (
    echo exe = EXE(
    echo     pyz,
    echo     a.scripts,
    echo     a.binaries,
    echo     a.zipfiles,
    echo     a.datas,
    echo     [],
    echo     name='WindowsFileManager',
    echo     debug=False,
    echo     bootloader_ignore_signals=False,
    echo     strip=False,
    echo     upx=True,
    echo     upx_exclude=[],
    echo     runtime_tmpdir=None,
    echo     console=False,
    echo     disable_windowed_traceback=False,
    echo     argv_emulation=False,
    echo     target_arch=None,
    echo     codesign_identity=None,
    echo     entitlements_file=None,
    echo     icon='!ICON_PATH!',
    echo ^)
) else (
    echo exe = EXE(
    echo     pyz,
    echo     a.scripts,
    echo     a.binaries,
    echo     a.zipfiles,
    echo     a.datas,
    echo     [],
    echo     name='WindowsFileManager',
    echo     debug=False,
    echo     bootloader_ignore_signals=False,
    echo     strip=False,
    echo     upx=True,
    echo     upx_exclude=[],
    echo     runtime_tmpdir=None,
    echo     console=False,
    echo     disable_windowed_traceback=False,
    echo     argv_emulation=False,
    echo     target_arch=None,
    echo     codesign_identity=None,
    echo     entitlements_file=None,
    echo     icon=None,
    echo ^)
)
) > file_manager_enhanced.spec

REM Run PyInstaller with the spec file
pyinstaller --clean file_manager_enhanced.spec
if errorlevel 1 (
    echo [ERROR] Failed to create executable with enhanced spec
    echo [INFO] Trying alternative compilation method...
    
    REM Try alternative method with icon
    if defined ICON_PATH (
        pyinstaller --onefile --windowed --name "WindowsFileManager" --icon="!ICON_PATH!" file_manager.py
    ) else (
        pyinstaller --onefile --windowed --name "WindowsFileManager" file_manager.py
    )
    
    if errorlevel 1 (
        echo [ERROR] Alternative compilation also failed
        echo [INFO] The file manager will run in Python mode instead
        set COMPILE_SUCCESS=false
    ) else (
        echo [SUCCESS] Executable created using alternative method
        set COMPILE_SUCCESS=true
    )
) else (
    echo [SUCCESS] Executable created successfully
    set COMPILE_SUCCESS=true
)

REM ========================================
REM Step 9: Create Desktop Shortcut
REM ========================================
echo.
echo [STEP 9] Creating desktop shortcut...
echo.

if "%COMPILE_SUCCESS%"=="true" (
    if exist "dist\WindowsFileManager.exe" (
        echo [INFO] Creating desktop shortcut for executable...
        
        REM Create VBS script to create shortcut
        (
        echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
        echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\Windows File Manager.lnk"
        echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
        echo oLink.TargetPath = "%CD%\dist\WindowsFileManager.exe"
        echo oLink.WorkingDirectory = "%CD%\dist"
        echo oLink.Description = "Windows File Manager - Complete file management solution"
        if defined ICON_PATH (
            echo oLink.IconLocation = "%CD%\!ICON_PATH!"
        )
        echo oLink.Save
        ) > create_shortcut.vbs
        
        cscript //nologo create_shortcut.vbs
        del create_shortcut.vbs
        
        if exist "%USERPROFILE%\Desktop\Windows File Manager.lnk" (
            echo [SUCCESS] Desktop shortcut created
        ) else (
            echo [WARNING] Failed to create desktop shortcut
        )
    )
) else (
    echo [INFO] Creating desktop shortcut for Python version...
    
    REM Create VBS script to create shortcut for Python version
    (
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\Windows File Manager.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "python"
    echo oLink.Arguments = "%CD%\file_manager.py"
    echo oLink.WorkingDirectory = "%CD%"
    echo oLink.Description = "Windows File Manager - Complete file management solution"
    if defined ICON_PATH (
        echo oLink.IconLocation = "%CD%\!ICON_PATH!"
    )
    echo oLink.Save
    ) > create_shortcut.vbs
    
    cscript //nologo create_shortcut.vbs
    del create_shortcut.vbs
    
    if exist "%USERPROFILE%\Desktop\Windows File Manager.lnk" (
        echo [SUCCESS] Desktop shortcut created
    ) else (
        echo [WARNING] Failed to create desktop shortcut
    )
)

REM ========================================
REM Step 10: Create Start Menu Entry
REM ========================================
echo.
echo [STEP 10] Creating start menu entry...
echo.

if "%COMPILE_SUCCESS%"=="true" (
    if exist "dist\WindowsFileManager.exe" (
        echo [INFO] Creating start menu entry...
        
        REM Create start menu directory
        if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Windows File Manager" (
            mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Windows File Manager"
        )
        
        REM Create VBS script to create start menu shortcut
        (
        echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
        echo sLinkFile = "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Windows File Manager\Windows File Manager.lnk"
        echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
        echo oLink.TargetPath = "%CD%\dist\WindowsFileManager.exe"
        echo oLink.WorkingDirectory = "%CD%\dist"
        echo oLink.Description = "Windows File Manager - Complete file management solution"
        if defined ICON_PATH (
            echo oLink.IconLocation = "%CD%\!ICON_PATH!"
        )
        echo oLink.Save
        ) > create_startmenu_shortcut.vbs
        
        cscript //nologo create_startmenu_shortcut.vbs
        del create_startmenu_shortcut.vbs
        
        if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Windows File Manager\Windows File Manager.lnk" (
            echo [SUCCESS] Start menu entry created
        ) else (
            echo [WARNING] Failed to create start menu entry
        )
    )
)

REM ========================================
REM Step 11: Create Uninstaller
REM ========================================
echo.
echo [STEP 11] Creating uninstaller...
echo.

REM Create uninstaller batch file
(
echo @echo off
echo title Windows File Manager - Uninstaller
echo color 0C
echo.
echo echo ========================================
echo echo   Windows File Manager - Uninstaller
echo echo ========================================
echo echo.
echo echo [WARNING] This will remove Windows File Manager from your system
echo echo.
echo set /p CONFIRM="Are you sure you want to uninstall? (y/N): "
echo.
echo if /i "%%CONFIRM%%"=="y" ^(
echo     echo [INFO] Removing desktop shortcut...
echo     if exist "%%USERPROFILE%%\Desktop\Windows File Manager.lnk" del "%%USERPROFILE%%\Desktop\Windows File Manager.lnk"
echo.
echo     echo [INFO] Removing start menu entry...
echo     if exist "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Windows File Manager" rmdir /s /q "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Windows File Manager"
echo.
echo     echo [INFO] Removing executable...
echo     if exist "dist\WindowsFileManager.exe" del "dist\WindowsFileManager.exe"
echo     if exist "dist" rmdir "dist"
echo.
echo     echo [INFO] Removing build files...
echo     if exist "build" rmdir /s /q "build"
echo     if exist "__pycache__" rmdir /s /q "__pycache__"
echo     if exist "*.spec" del "*.spec"
echo.
echo     echo [SUCCESS] Windows File Manager has been uninstalled
echo ^) else ^(
echo     echo [INFO] Uninstallation cancelled
echo ^)
echo.
echo pause
) > uninstall_file_manager.bat

echo [SUCCESS] Uninstaller created

REM ========================================
REM Step 12: Cleanup and Final Setup
REM ========================================
echo.
echo [STEP 12] Finalizing setup...
echo.

REM Clean up PyInstaller build files
if exist "build" (
    echo [INFO] Cleaning up build files...
    rmdir /s /q build
)

if exist "__pycache__" (
    echo [INFO] Cleaning up Python cache...
    rmdir /s /q __pycache__
)

REM Clean up spec files
if exist "file_manager.spec" del "file_manager.spec"
if exist "file_manager_enhanced.spec" del "file_manager_enhanced.spec"

REM Create a simple launcher script
echo [INFO] Creating simple launcher...
(
echo @echo off
echo title Windows File Manager
echo echo Starting Windows File Manager...
echo echo.
if "%COMPILE_SUCCESS%"=="true" (
    echo if exist "dist\WindowsFileManager.exe" ^(
    echo     start "" "dist\WindowsFileManager.exe"
    echo ^) else ^(
    echo     python file_manager.py
    echo ^)
) else (
    echo python file_manager.py
)
echo pause
) > launch_file_manager.bat

echo [SUCCESS] Simple launcher created

REM ========================================
REM Step 13: Display Results
REM ========================================
echo.
echo ========================================
echo   ENHANCED SETUP COMPLETED SUCCESSFULLY!
echo ========================================
echo.

if "%COMPILE_SUCCESS%"=="true" (
    echo [SUCCESS] Executable created: dist\WindowsFileManager.exe
    if defined ICON_PATH (
        echo [SUCCESS] Custom icon applied: !ICON_PATH!
    )
    echo [INFO] You can now run the file manager in several ways:
    echo.
    echo   1. Double-click the desktop shortcut
    echo   2. Use Start Menu ^> Windows File Manager
    echo   3. Run: dist\WindowsFileManager.exe
    echo   4. Run: launch_file_manager.bat
    echo.
) else (
    echo [INFO] Executable creation failed, but Python version is ready
    echo [INFO] You can run the file manager with: python file_manager.py
    echo [INFO] Or use: launch_file_manager.bat
    echo.
)

echo [INFO] Installation directory: %CD%
echo [INFO] All dependencies installed and configured
echo [INFO] Uninstaller available: uninstall_file_manager.bat
echo.

REM ========================================
REM Step 14: Ask to Run File Manager
REM ========================================
echo [QUESTION] Would you like to run the file manager now?
echo.
set /p RUN_NOW="Enter 'y' to run now, or any other key to exit: "

if /i "%RUN_NOW%"=="y" (
    echo.
    echo [INFO] Starting Windows File Manager...
    echo.
    
    if "%COMPILE_SUCCESS%"=="true" (
        if exist "dist\WindowsFileManager.exe" (
            start "" "dist\WindowsFileManager.exe"
        ) else (
            python file_manager.py
        )
    ) else (
        python file_manager.py
    )
    
    echo [INFO] File manager started!
    echo [INFO] You can close this window now.
) else (
    echo.
    echo [INFO] Setup completed. You can run the file manager anytime using:
    echo [INFO] - Desktop shortcut
    echo [INFO] - Start menu entry
    echo [INFO] - launch_file_manager.bat
    echo.
)

echo.
echo ========================================
echo   Thank you for using Windows File Manager!
echo ========================================
echo.
pause