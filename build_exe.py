#!/usr/bin/env python3
"""
Build script for Anora Editor
Converts the Python application into a standalone executable
"""

import os
import sys
import subprocess
import shutil

def build_executable():
    """Build the Anora Editor executable using PyInstaller"""
    
    print("🚀 Building Anora Editor executable...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable file
        '--windowed',                   # No console window
        '--name=AnoraEditor',           # Executable name
        '--icon=icon.ico',              # Icon (if available)
        '--add-data=requirements.txt;.', # Include requirements
        '--hidden-import=tkinter',
        '--hidden-import=pygments',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.scrolledtext',
        '--clean',                      # Clean cache
        'anora_editor.py'
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = os.path.join('dist', 'AnoraEditor.exe')
        if os.path.exists(exe_path):
            print(f"📁 Executable created: {exe_path}")
            print(f"📏 File size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
        else:
            print("❌ Executable not found in dist folder")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it first:")
        print("pip install pyinstaller")
        return False
        
    return True

def create_installer():
    """Create a simple installer script"""
    
    installer_content = '''@echo off
echo Installing Anora Editor...
echo.

REM Create program directory
if not exist "%PROGRAMFILES%\\AnoraEditor" mkdir "%PROGRAMFILES%\\AnoraEditor"

REM Copy executable
copy "dist\\AnoraEditor.exe" "%PROGRAMFILES%\\AnoraEditor\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Anora Editor.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\AnoraEditor\\AnoraEditor.exe'; $Shortcut.Save()"

echo.
echo Installation completed!
echo Anora Editor has been installed to: %PROGRAMFILES%\\AnoraEditor\\
echo Desktop shortcut created.
pause
'''
    
    with open('install_anora.bat', 'w') as f:
        f.write(installer_content)
    
    print("📝 Installer script created: install_anora.bat")

def main():
    """Main build process"""
    
    print("=" * 50)
    print("🔧 Anora Editor Build System")
    print("=" * 50)
    
    # Check if main file exists
    if not os.path.exists('anora_editor.py'):
        print("❌ anora_editor.py not found!")
        return
    
    # Install dependencies if needed
    print("📦 Checking dependencies...")
    try:
        import pygments
        print("✅ Pygments already installed")
    except ImportError:
        print("📥 Installing Pygments...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pygments'], check=True)
    
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📥 Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Build executable
    if build_executable():
        # Create installer
        create_installer()
        
        print("\n" + "=" * 50)
        print("🎉 Build completed successfully!")
        print("=" * 50)
        print("📁 Files created:")
        print("   - dist/AnoraEditor.exe (Main executable)")
        print("   - install_anora.bat (Installer script)")
        print("\n🚀 To install:")
        print("   1. Run install_anora.bat as administrator")
        print("   2. Or manually copy AnoraEditor.exe to your desired location")
        print("\n💡 To run directly:")
        print("   ./dist/AnoraEditor.exe")
    else:
        print("\n❌ Build failed!")

if __name__ == "__main__":
    main()