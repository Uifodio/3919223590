#!/usr/bin/env python3
"""
Build script for Unity File Manager Pro
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller if not available"""
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

def create_executable():
    """Create the executable using PyInstaller"""
    print("Creating executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window
        "--name=UnityFileManagerPro",   # Executable name
        "--add-data=resources;resources",  # Include resources
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets", 
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=pygments",
        "--hidden-import=psutil",
        "--hidden-import=winreg",
        "main.py"
    ]
    
    # Add icon if available
    icon_path = "resources/icons/app.ico"
    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Run PyInstaller
    subprocess.run(cmd, check=True)
    
    print("Executable created successfully!")
    print("Location: dist/UnityFileManagerPro.exe")

def create_installer():
    """Create installer using NSIS (if available)"""
    print("Creating installer...")
    
    # Create NSIS script
    nsis_script = """
!include "MUI2.nsh"

Name "Unity File Manager Pro"
OutFile "UnityFileManagerPro-Setup.exe"
InstallDir "$PROGRAMFILES\\Unity File Manager Pro"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    File "dist\\UnityFileManagerPro.exe"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\\Unity File Manager Pro"
    CreateShortCut "$SMPROGRAMS\\Unity File Manager Pro\\Unity File Manager Pro.lnk" "$INSTDIR\\UnityFileManagerPro.exe"
    CreateShortCut "$DESKTOP\\Unity File Manager Pro.lnk" "$INSTDIR\\UnityFileManagerPro.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\UnityFileManagerPro" "DisplayName" "Unity File Manager Pro"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\UnityFileManagerPro" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\UnityFileManagerPro" "DisplayIcon" "$INSTDIR\\UnityFileManagerPro.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\UnityFileManagerPro" "Publisher" "Unity File Manager Team"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\UnityFileManagerPro" "DisplayVersion" "1.0.0"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\UnityFileManagerPro.exe"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\Unity File Manager Pro\\Unity File Manager Pro.lnk"
    RMDir "$SMPROGRAMS\\Unity File Manager Pro"
    Delete "$DESKTOP\\Unity File Manager Pro.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\UnityFileManagerPro"
SectionEnd
"""
    
    # Write NSIS script
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Check if NSIS is available
    try:
        subprocess.run(["makensis", "installer.nsi"], check=True)
        print("Installer created: UnityFileManagerPro-Setup.exe")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("NSIS not found. Installer creation skipped.")
        print("You can manually run: makensis installer.nsi")

def clean_build():
    """Clean build artifacts"""
    print("Cleaning build artifacts...")
    
    # Remove PyInstaller directories
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    if os.path.exists("dist"):
        # Keep the executable, remove other files
        for item in os.listdir("dist"):
            if not item.endswith(".exe"):
                item_path = os.path.join("dist", item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
    
    # Remove spec file
    if os.path.exists("UnityFileManagerPro.spec"):
        os.remove("UnityFileManagerPro.spec")

def main():
    """Main build process"""
    print("Unity File Manager Pro - Build Script")
    print("=" * 40)
    
    try:
        # Check and install PyInstaller
        if not check_pyinstaller():
            install_pyinstaller()
        
        # Clean previous build
        clean_build()
        
        # Create executable
        create_executable()
        
        # Create installer (optional)
        create_installer = input("Create installer? (y/n): ").lower().startswith('y')
        if create_installer:
            create_installer()
        
        print("\nBuild completed successfully!")
        print("Executable: dist/UnityFileManagerPro.exe")
        
    except Exception as e:
        print(f"Build failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())