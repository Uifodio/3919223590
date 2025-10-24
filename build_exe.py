#!/usr/bin/env python3
"""
Build script for creating standalone EXE
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['web_server_admin.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('demo_website', 'demo_website'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'flask',
        'psutil',
        'PIL',
        'werkzeug',
        'jinja2',
        'markupsafe',
        'itsdangerous',
        'click',
        'blinker',
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
    name='ModernServerAdministrator',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('ModernServerAdministrator.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ Created PyInstaller spec file")

def create_icon():
    """Create a simple icon file"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a server icon
        draw.rectangle([16, 8, 48, 56], fill=(9, 105, 218, 255), outline=(255, 255, 255, 255))
        draw.rectangle([20, 12, 44, 20], fill=(255, 255, 255, 255))
        draw.rectangle([20, 24, 44, 32], fill=(255, 255, 255, 255))
        draw.rectangle([20, 36, 44, 44], fill=(255, 255, 255, 255))
        
        img.save('icon.ico', format='ICO')
        print("✓ Created icon file")
    except ImportError:
        print("⚠️  Pillow not available, skipping icon creation")

def build_exe():
    """Build the EXE file"""
    print("Building EXE file...")
    
    try:
        subprocess.check_call([
            'pyinstaller',
            '--clean',
            '--noconfirm',
            'ModernServerAdministrator.spec'
        ])
        print("✓ EXE built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error building EXE: {e}")
        return False

def create_installer():
    """Create a simple installer script"""
    installer_content = '''@echo off
title Modern Server Administrator Installer
color 0A

echo.
echo  ========================================
echo  Modern Server Administrator Installer
echo  ========================================
echo.

echo Installing Modern Server Administrator...
echo.

REM Create installation directory
if not exist "C:\\Program Files\\Modern Server Administrator" (
    mkdir "C:\\Program Files\\Modern Server Administrator"
)

REM Copy files
copy "ModernServerAdministrator.exe" "C:\\Program Files\\Modern Server Administrator\\"
copy "README.md" "C:\\Program Files\\Modern Server Administrator\\"
copy "requirements.txt" "C:\\Program Files\\Modern Server Administrator\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Modern Server Administrator.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\Modern Server Administrator\\ModernServerAdministrator.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo You can now run Modern Server Administrator from your desktop.
echo.
pause
'''
    
    with open('install.bat', 'w') as f:
        f.write(installer_content)
    
    print("✓ Created installer script")

def main():
    """Main build process"""
    print("🚀 Building Modern Server Administrator EXE")
    print("=" * 50)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("❌ This build script is designed for Windows")
        print("   For other platforms, use: python web_server_admin.py")
        return
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Create icon
    create_icon()
    
    # Build EXE
    if build_exe():
        print("\n✅ Build completed successfully!")
        print("📁 EXE file location: dist/ModernServerAdministrator.exe")
        
        # Create installer
        create_installer()
        print("📁 Installer created: install.bat")
        
        print("\n🎉 Modern Server Administrator is ready!")
        print("   Run 'install.bat' to install the application")
        print("   Or run 'dist/ModernServerAdministrator.exe' directly")
    else:
        print("\n❌ Build failed!")
        print("   Please check the error messages above")

if __name__ == "__main__":
    main()