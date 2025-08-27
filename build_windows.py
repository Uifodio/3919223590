#!/usr/bin/env python3
"""
Windows-specific build script for Anora Editor
Handles DLL dependency issues common on Windows
"""

import os
import sys
import subprocess
import shutil
import platform

def check_windows():
    """Check if we're on Windows"""
    if platform.system() != 'Windows':
        print("❌ This script is designed for Windows systems")
        print(f"   Current system: {platform.system()}")
        return False
    return True

def install_vcredist():
    """Provide instructions for installing Visual C++ Redistributable"""
    print("📋 Visual C++ Redistributable Installation")
    print("=" * 50)
    print("Many DLL errors on Windows are caused by missing Visual C++ Redistributable.")
    print("Please install the appropriate version for your system:")
    print()
    print("🔗 Download links:")
    print("   - Visual C++ 2015-2022 Redistributable (x64):")
    print("     https://aka.ms/vs/17/release/vc_redist.x64.exe")
    print("   - Visual C++ 2015-2022 Redistributable (x86):")
    print("     https://aka.ms/vs/17/release/vc_redist.x86.exe")
    print()
    print("💡 Install both x64 and x86 versions for maximum compatibility")
    print()

def build_windows_compatible():
    """Build with Windows-specific optimizations"""
    
    print("🚀 Building Windows-compatible executable...")
    
    # Windows-optimized PyInstaller command
    cmd = [
        'pyinstaller',
        '--onedir',                     # Directory mode (more reliable than onefile)
        '--windowed',                   # No console window
        '--name=AnoraEditor_Windows',   # Windows-specific name
        '--distpath=dist_windows',      # Windows output directory
        '--workpath=build_windows',     # Windows build directory
        '--specpath=build_windows',     # Windows spec directory
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=tkinter.font',
        '--hidden-import=pygments',
        '--hidden-import=pygments.lexers',
        '--hidden-import=pygments.formatters',
        '--hidden-import=pygments.lexers.python',
        '--hidden-import=pygments.lexers.csharp',
        '--hidden-import=pygments.lexers.javascript',
        '--hidden-import=pygments.lexers.html',
        '--hidden-import=pygments.lexers.css',
        '--hidden-import=pygments.lexers.json',
        '--hidden-import=pygments.lexers.xml',
        '--collect-all=tkinter',
        '--collect-all=pygments',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=PIL',
        '--exclude-module=cv2',
        '--exclude-module=PyQt5',
        '--exclude-module=PyQt6',
        '--exclude-module=PySide2',
        '--exclude-module=PySide6',
        '--exclude-module=wx',
        '--exclude-module=gtk',
        '--exclude-module=tkinter.test',
        '--exclude-module=test',
        '--exclude-module=unittest',
        '--exclude-module=doctest',
        '--exclude-module=pdb',
        '--exclude-module=profile',
        '--exclude-module=cProfile',
        '--exclude-module=pstats',
        '--exclude-module=timeit',
        '--exclude-module=trace',
        '--exclude-module=dis',
        '--exclude-module=pickletools',
        '--exclude-module=tabnanny',
        '--exclude-module=py_compile',
        '--exclude-module=compileall',
        '--exclude-module=ensurepip',
        '--exclude-module=venv',
        '--exclude-module=distutils',
        '--exclude-module=setuptools',
        '--exclude-module=pip',
        '--exclude-module=wheel',
        '--exclude-module=email',
        '--exclude-module=html',
        '--exclude-module=http',
        '--exclude-module=urllib',
        '--exclude-module=xml',
        '--exclude-module=xmlrpc',
        '--exclude-module=multiprocessing',
        '--exclude-module=concurrent',
        '--exclude-module=asyncio',
        '--exclude-module=threading',
        '--exclude-module=subprocess',
        '--exclude-module=socket',
        '--exclude-module=ssl',
        '--exclude-module=cryptography',
        '--exclude-module=hashlib',
        '--exclude-module=hmac',
        '--exclude-module=secrets',
        '--exclude-module=base64',
        '--exclude-module=binascii',
        '--exclude-module=quopri',
        '--exclude-module=uu',
        '--exclude-module=encodings',
        '--exclude-module=codecs',
        '--exclude-module=locale',
        '--exclude-module=gettext',
        '--exclude-module=unicodedata',
        '--exclude-module=stringprep',
        '--exclude-module=readline',
        '--exclude-module=rlcompleter',
        '--exclude-module=cmd',
        '--exclude-module=shlex',
        '--exclude-module=configparser',
        '--exclude-module=netrc',
        '--exclude-module=xdrlib',
        '--exclude-module=plistlib',
        '--exclude-module=platform',
        '--exclude-module=sysconfig',
        '--exclude-module=site',
        '--exclude-module=os',
        '--exclude-module=posixpath',
        '--exclude-module=ntpath',
        '--exclude-module=stat',
        '--exclude-module=filecmp',
        '--exclude-module=tempfile',
        '--exclude-module=glob',
        '--exclude-module=fnmatch',
        '--exclude-module=linecache',
        '--exclude-module=shutil',
        '--exclude-module=pathlib',
        '--exclude-module=pathlib2',
        '--exclude-module=zipfile',
        '--exclude-module=tarfile',
        '--clean',
        'anora_editor.py'
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Windows build completed successfully!")
        
        # Check if executable was created
        exe_path = os.path.join('dist_windows', 'AnoraEditor_Windows', 'AnoraEditor_Windows.exe')
        if os.path.exists(exe_path):
            print(f"📁 Windows executable created: {exe_path}")
            print(f"📏 Directory size: {get_dir_size('dist_windows/AnoraEditor_Windows') / (1024*1024):.1f} MB")
            
            # Create Windows launcher
            create_windows_launcher()
            
        else:
            print("❌ Windows executable not found")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Windows build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it first:")
        print("pip install pyinstaller")
        return False
        
    return True

def get_dir_size(path):
    """Get directory size in bytes"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total += os.path.getsize(filepath)
    return total

def create_windows_launcher():
    """Create a Windows-specific launcher"""
    
    launcher_content = '''@echo off
title Anora Editor - Professional Code Editor for Unity
echo.
echo ========================================
echo    Anora Editor - Starting...
echo ========================================
echo.
echo Professional code editor for Unity development
echo.
echo Features:
echo   - Professional dark theme
echo   - Tabbed interface for multiple files
echo   - C# syntax highlighting for Unity
echo   - Always on top mode for Unity workflow
echo   - Search and replace functionality
echo.
echo ========================================
echo.

cd /d "%~dp0"
AnoraEditor_Windows.exe

if errorlevel 1 (
    echo.
    echo ========================================
    echo    ERROR: Anora Editor failed to start
    echo ========================================
    echo.
    echo Possible solutions:
    echo   1. Install Visual C++ Redistributable 2015-2022
    echo   2. Run as Administrator
    echo   3. Check Windows Defender/Firewall settings
    echo   4. Ensure all files are present in this directory
    echo.
    echo Download Visual C++ Redistributable:
    echo   https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    pause
) else (
    echo.
    echo Anora Editor closed successfully.
)
'''
    
    launcher_path = os.path.join('dist_windows', 'AnoraEditor_Windows', 'launch_anora.bat')
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    print(f"📝 Windows launcher created: {launcher_path}")

def create_windows_package():
    """Create a Windows-specific package"""
    
    print("📦 Creating Windows package...")
    
    if not os.path.exists('dist_windows/AnoraEditor_Windows'):
        print("❌ Windows build not found. Please run Windows build first.")
        return False
    
    # Create Windows package directory
    package_dir = 'AnoraEditor_Windows_Package'
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    
    # Copy the entire AnoraEditor_Windows directory
    shutil.copytree('dist_windows/AnoraEditor_Windows', package_dir)
    
    # Create Windows-specific README
    readme_content = '''# Anora Editor - Windows Package

Professional code editor designed for Unity development on Windows.

## Quick Start:
1. Extract this folder anywhere on your Windows computer
2. Run "launch_anora.bat" or "AnoraEditor_Windows.exe" directly
3. No installation required!

## Features:
- Professional dark theme with syntax highlighting
- Tabbed interface for multiple files
- C# support for Unity scripts
- Always on top mode for Unity workflow
- Search and replace functionality
- Compact design for overlay editing

## System Requirements:
- Windows 7, 8, 10, or 11
- Visual C++ Redistributable 2015-2022 (if not already installed)

## Troubleshooting:
If you get DLL errors:
1. Install Visual C++ Redistributable 2015-2022:
   https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Run as Administrator
3. Check Windows Defender/Firewall settings

## Unity Workflow:
1. Launch Anora Editor
2. Click "📌 Pin" to keep it always on top
3. Resize to overlay Unity viewport
4. Open your C# scripts with Ctrl+O
5. Edit quickly while keeping Unity visible

Enjoy coding with Anora Editor!
'''
    
    with open(os.path.join(package_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Windows package created: {package_dir}")
    print(f"📏 Package size: {get_dir_size(package_dir) / (1024*1024):.1f} MB")
    
    return True

def main():
    """Main Windows build process"""
    
    print("=" * 60)
    print("🔧 Anora Editor - Windows Build System")
    print("=" * 60)
    
    # Check if we're on Windows
    if not check_windows():
        return
    
    # Show Visual C++ Redistributable info
    install_vcredist()
    
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
    
    print("\n🔧 Building Windows-compatible executable...")
    
    # Build Windows version
    if build_windows_compatible():
        create_windows_package()
    
    print("\n" + "=" * 60)
    print("🎉 Windows build completed!")
    print("=" * 60)
    print("📁 Files created:")
    
    if os.path.exists('dist_windows/AnoraEditor_Windows'):
        print("   - dist_windows/AnoraEditor_Windows/ (Windows executable)")
        print("   - AnoraEditor_Windows_Package/ (Windows package)")
    
    print("\n💡 To run:")
    if os.path.exists('AnoraEditor_Windows_Package'):
        print("   ./AnoraEditor_Windows_Package/launch_anora.bat")
    
    print("\n⚠️  If you get DLL errors:")
    print("   1. Install Visual C++ Redistributable 2015-2022")
    print("   2. Run as Administrator")
    print("   3. Check Windows Defender/Firewall settings")

if __name__ == "__main__":
    main()