#!/usr/bin/env python3
"""
Build script to create standalone EXE from the Futuristic Web Server application
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_directories():
    """Clean previous build directories"""
    print("🧹 Cleaning previous build directories...")
    directories_to_clean = ['build', 'dist', '__pycache__']
    for directory in directories_to_clean:
        if Path(directory).exists():
            shutil.rmtree(directory)
            print(f"   Removed {directory}/")

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('config', 'config'),
        ('logs', 'logs'),
        ('uploads', 'uploads'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineWidgets',
        'flask',
        'flask_cors',
        'werkzeug',
        'PIL',
        'cv2',
        'qrcode',
        'magic',
        'psutil',
        'requests',
        'aiohttp',
        'watchdog',
        'cryptography',
        'bcrypt',
        'python_dotenv',
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
    name='FuturisticWebServer',
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
    icon='static/images/icon.ico' if os.path.exists('static/images/icon.ico') else None,
)
'''
    
    with open('FuturisticWebServer.spec', 'w') as f:
        f.write(spec_content)
    print("📝 Created PyInstaller spec file")

def create_icon():
    """Create application icon if it doesn't exist"""
    icon_path = Path('static/images/icon.ico')
    if not icon_path.exists():
        icon_path.parent.mkdir(parents=True, exist_ok=True)
        # Create a simple icon placeholder
        print("🎨 Creating application icon...")
        # You can replace this with a proper icon file
        print("   Note: Add a proper icon.ico file to static/images/ for better branding")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Use the spec file for building
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'FuturisticWebServer.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo Installing Futuristic Web Server...
echo.

REM Create application directory
if not exist "%PROGRAMFILES%\\FuturisticWebServer" mkdir "%PROGRAMFILES%\\FuturisticWebServer"

REM Copy executable
copy "FuturisticWebServer.exe" "%PROGRAMFILES%\\FuturisticWebServer\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Futuristic Web Server.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\FuturisticWebServer\\FuturisticWebServer.exe'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Futuristic Web Server" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Futuristic Web Server"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Futuristic Web Server\\Futuristic Web Server.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\FuturisticWebServer\\FuturisticWebServer.exe'; $Shortcut.Save()"

echo.
echo Installation completed!
echo You can now run Futuristic Web Server from the desktop or start menu.
pause
'''
    
    with open('install.bat', 'w') as f:
        f.write(installer_content)
    print("📦 Created installer script (install.bat)")

def create_readme():
    """Create README for the built application"""
    readme_content = '''# Futuristic Web Server - Professional Edition

A modern, professional web server application with a sleek UI and advanced features.

## Features

- 🚀 **Dual Server Support**: Run two servers simultaneously on different ports
- 📁 **Advanced File Management**: Upload, download, and manage files with ease
- 🎬 **Media Streaming**: Stream videos and audio files directly in browser
- 📱 **QR Code Generation**: Generate QR codes for easy file sharing
- 🖼️ **Thumbnail Generation**: Automatic thumbnails for images and videos
- 🔍 **Search Functionality**: Find files quickly with built-in search
- 🌙 **Dark Theme**: Professional dark theme with modern UI
- 📊 **Real-time Logs**: Monitor server activity with live logs
- 🔒 **Security Features**: File type validation and secure uploads

## Installation

1. Run `install.bat` as administrator
2. The application will be installed to Program Files
3. Desktop and Start Menu shortcuts will be created

## Usage

1. Launch the application from desktop or start menu
2. Configure server ports and directories
3. Start your servers
4. Access files through the web interface

## System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum
- 100MB free disk space

## Support

For support and updates, visit the project repository.

---
© 2024 Futuristic Software. All rights reserved.
'''
    
    with open('README.txt', 'w') as f:
        f.write(readme_content)
    print("📖 Created README.txt")

def main():
    """Main build process"""
    print("🚀 Building Futuristic Web Server Executable")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('main.py').exists():
        print("❌ Error: main.py not found. Please run this script from the project root.")
        return False
    
    # Clean previous builds
    clean_build_directories()
    
    # Create necessary files
    create_spec_file()
    create_icon()
    create_installer_script()
    create_readme()
    
    # Build the executable
    if build_executable():
        print("\n🎉 Build completed successfully!")
        print("\nFiles created:")
        print("  - dist/FuturisticWebServer.exe (Main executable)")
        print("  - install.bat (Installer script)")
        print("  - README.txt (User documentation)")
        print("\nTo distribute:")
        print("  1. Copy the entire 'dist' folder")
        print("  2. Include install.bat and README.txt")
        print("  3. Users can run install.bat to install the application")
        return True
    else:
        print("\n❌ Build failed. Check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)