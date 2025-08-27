#!/usr/bin/env python3
"""
Build Windows Executable for Anora Editor
This creates a proper .exe that Windows recognizes as a real application
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    print("🔨 Building Anora Editor Windows Executable...")
    print("=" * 50)
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Create spec file for professional build
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['anora_editor.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.font',
        'pygments',
        'pygments.lexers',
        'pygments.formatters',
        'json',
        'pathlib',
        'threading',
        'time',
        're',
        'typing'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AnoraEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='anora_icon.ico' if os.path.exists('anora_icon.ico') else None,
    version_file=None,
)
'''
    
    # Write spec file
    with open('anora_editor.spec', 'w') as f:
        f.write(spec_content)
    
    print("📝 Created PyInstaller spec file")
    
    # Build executable
    print("🔨 Building executable...")
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "anora_editor.spec"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        
        # Move executable to current directory
        exe_path = Path("dist/AnoraEditor.exe")
        if exe_path.exists():
            shutil.copy2(exe_path, "AnoraEditor.exe")
            print("✅ AnoraEditor.exe created in current directory")
            
            # Create professional installer
            create_installer()
        else:
            print("❌ Executable not found in dist folder")
    else:
        print("❌ Build failed:")
        print(result.stderr)

def create_installer():
    """Create a professional Windows installer"""
    print("\n🔧 Creating professional installer...")
    
    installer_content = '''@echo off
title Anora Editor - Professional Installation
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    ANORA EDITOR INSTALLER                   ║
echo ║              Professional Code Editor for Unity             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ⚠️  Warning: Not running as Administrator
    echo    Some features may not work properly
    echo.
)

echo 🔍 Detecting AnoraEditor.exe...
if exist "AnoraEditor.exe" (
    echo ✅ AnoraEditor.exe found
) else (
    echo ❌ AnoraEditor.exe not found
    echo    Please run build_windows_executable.py first
    pause
    exit /b 1
)

echo.
echo 📝 Registering Anora Editor as Windows application...

REM Create registry entries
reg add "HKCU\\Software\\Classes\\Anora.Editor" /ve /d "Anora Editor - Professional Code Editor for Unity" /f
reg add "HKCU\\Software\\Classes\\Anora.Editor\\shell\\open\\command" /ve /d "\\"%~dp0AnoraEditor.exe\\" \\"%%1\\"" /f

REM Add application info
reg add "HKCU\\Software\\Classes\\Anora.Editor\\shell\\open" /v "FriendlyAppName" /d "Anora Editor" /f

REM Add icon if available
if exist "anora_icon.ico" (
    reg add "HKCU\\Software\\Classes\\Anora.Editor\\DefaultIcon" /ve /d "%~dp0anora_icon.ico" /f
    echo ✅ Custom icon registered
)

echo 📁 Registering file associations...

REM File associations
for %%e in (.txt .py .cs .js .html .css .json .c .cpp .h .xml .md .php .java .rb .sql .sh .bat .ps1) do (
    reg add "HKCU\\Software\\Classes\\%%e" /ve /d "Anora.Editor" /f
    reg add "HKCU\\Software\\Classes\\%%e" /v "Content Type" /d "text/plain" /f
    echo   Registered %%e
)

echo 🖱️ Adding context menu integration...

REM "Open with Anora Editor" for all files
reg add "HKCU\\Software\\Classes\\*\\shell\\OpenWithAnora" /ve /d "Open with Anora Editor" /f
reg add "HKCU\\Software\\Classes\\*\\shell\\OpenWithAnora\\command" /ve /d "\\"%~dp0AnoraEditor.exe\\" \\"%%1\\"" /f

REM "Edit with Anora Editor" for text files
reg add "HKCU\\Software\\Classes\\*\\shell\\EditWithAnora" /ve /d "Edit with Anora Editor" /f
reg add "HKCU\\Software\\Classes\\*\\shell\\EditWithAnora\\command" /ve /d "\\"%~dp0AnoraEditor.exe\\" \\"%%1\\"" /f

echo ⭐ Setting as default editor...

REM Set as default for common text files
for %%e in (.txt .py .cs .js .html .css .json) do (
    reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\%%e\\UserChoice" /v "Progid" /d "Anora.Editor" /f 2>nul
    echo   Set as default for %%e
)

echo 🖥️ Creating desktop shortcut...

REM Create desktop shortcut
set "desktop=%USERPROFILE%\\Desktop"
set "shortcut=%desktop%\\Anora Editor.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut%'); $Shortcut.TargetPath = '%~dp0AnoraEditor.exe'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Anora Editor - Professional Code Editor for Unity'; if (Test-Path '%~dp0anora_icon.ico') { $Shortcut.IconLocation = '%~dp0anora_icon.ico' }; $Shortcut.Save()"

if exist "%shortcut%" (
    echo ✅ Desktop shortcut created
) else (
    echo ⚠️ Could not create desktop shortcut
)

echo 🔄 Refreshing Windows shell...

REM Refresh shell
powershell -Command "try { $shell = New-Object -ComObject Shell.Application; $shell.RefreshDesktop(); Write-Host '✅ Desktop refreshed' } catch { Write-Host '⚠️ Could not refresh desktop (this is normal)' }"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    INSTALLATION COMPLETE!                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🎉 Anora Editor is now registered as a professional Windows application!
echo.

echo 📋 What you can now do:
echo   • Double-click any code file to open in Anora Editor
echo   • Right-click files → 'Open with Anora Editor'
echo   • Use 'Anora Editor' desktop shortcut
echo   • Command line: AnoraEditor.exe file.py
echo.

echo ⚠️ Important:
echo   • Restart File Explorer or log out/in for all changes to take effect
echo   • If files don't open, right-click → 'Open with' → 'Choose another app' → 'Anora Editor'
echo.

pause
'''
    
    with open('install_anora_editor.bat', 'w') as f:
        f.write(installer_content)
    
    print("✅ Professional installer created: install_anora_editor.bat")

if __name__ == "__main__":
    build_executable()