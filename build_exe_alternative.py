#!/usr/bin/env python3
"""
Alternative build script for Anora Editor
Uses a different approach to avoid DLL dependency issues
"""

import os
import sys
import subprocess
import shutil

def build_executable_alternative():
    """Build the Anora Editor executable using alternative PyInstaller settings"""
    
    print("🚀 Building Nexus Code executable (Alternative Method)...")
    
    # Alternative PyInstaller command - more compatible
    cmd = [
        'pyinstaller',
        '--onedir',                     # Directory mode instead of onefile
        '--windowed',                   # No console window
        '--name=NexusCode',           # Executable name
        '--distpath=dist_alt',          # Different output directory
        '--workpath=build_alt',         # Different build directory
        '--specpath=build_alt',         # Different spec directory
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
        '--clean',
        'nexus_code.py'
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = os.path.join('dist_alt', 'NexusCode', 'NexusCode.exe')
        if os.path.exists(exe_path):
            print(f"📁 Executable created: {exe_path}")
            print(f"📏 Directory size: {get_dir_size('dist_alt/NexusCode') / (1024*1024):.1f} MB")
            
            # Create a simple launcher batch file
            create_launcher_bat()
            
        else:
            print("❌ Executable not found in dist_alt folder")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it first:")
        print("pip install pyinstaller")
        return False
        
    return True

def build_executable_simple():
    """Build using the simplest possible PyInstaller command"""
    
    print("🚀 Building Nexus Code executable (Simple Method)...")
    
    # Simple PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=NexusCode_Simple',
        '--distpath=dist_simple',
        'nexus_code.py'
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Simple build completed successfully!")
        
        # Check if executable was created
        exe_path = os.path.join('dist_simple', 'NexusCode_Simple.exe')
        if os.path.exists(exe_path):
            print(f"📁 Simple executable created: {exe_path}")
            print(f"📏 File size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
            
        else:
            print("❌ Simple executable not found")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Simple build failed: {e}")
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

def create_launcher_bat():
    """Create a launcher batch file for the directory version"""
    
    launcher_content = '''@echo off
echo Starting Nexus Code...
cd /d "%~dp0"
NexusCode.exe
if errorlevel 1 (
    echo.
    echo Error: Nexus Code failed to start.
    echo Please check if all files are present in this directory.
    pause
)
'''
    
    launcher_path = os.path.join('dist_alt', 'NexusCode', 'launch_nexus.bat')
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    print(f"📝 Launcher batch file created: {launcher_path}")

def create_portable_package():
    """Create a portable package with all dependencies"""
    
    print("📦 Creating portable package...")
    
    if not os.path.exists('dist_alt/AnoraEditor'):
        print("❌ Alternative build not found. Please run alternative build first.")
        return False
    
    # Create portable directory
    portable_dir = 'AnoraEditor_Portable'
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    # Copy the entire AnoraEditor directory
    shutil.copytree('dist_alt/AnoraEditor', portable_dir)
    
    # Create a README for the portable version
    readme_content = '''# Anora Editor - Portable Version

This is a portable version of Anora Editor that includes all necessary dependencies.

## How to Use:
1. Extract this folder anywhere on your computer
2. Run "launch_anora.bat" or "AnoraEditor.exe" directly
3. No installation required!

## Features:
- Professional code editor for Unity development
- Dark theme with syntax highlighting
- Tabbed interface for multiple files
- Always on top mode for Unity workflow
- Search and replace functionality
- C# support for Unity scripts

## System Requirements:
- Windows 7 or later
- No additional software required

Enjoy coding with Anora Editor!
'''
    
    with open(os.path.join(portable_dir, 'README.txt'), 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Portable package created: {portable_dir}")
    print(f"📏 Package size: {get_dir_size(portable_dir) / (1024*1024):.1f} MB")
    
    return True

def main():
    """Main build process with multiple options"""
    
    print("=" * 60)
    print("🔧 Anora Editor Build System - Alternative Methods")
    print("=" * 60)
    
    # Check if main file exists
    if not os.path.exists('nexus_code.py'):
    print("❌ nexus_code.py not found!")
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
    
    print("\n🔧 Building with multiple methods to avoid DLL issues...")
    
    # Method 1: Alternative build (directory mode)
    print("\n1️⃣ Method 1: Directory Mode (Most Compatible)")
    if build_executable_alternative():
        create_portable_package()
    
    # Method 2: Simple build
    print("\n2️⃣ Method 2: Simple Build (Minimal Dependencies)")
    build_executable_simple()
    
    print("\n" + "=" * 60)
    print("🎉 Build completed!")
    print("=" * 60)
    print("📁 Files created:")
    
    if os.path.exists('dist_alt/AnoraEditor'):
        print("   - dist_alt/AnoraEditor/ (Directory version - Most compatible)")
        print("   - AnoraEditor_Portable/ (Portable package)")
    
    if os.path.exists('dist_simple/AnoraEditor_Simple.exe'):
        print("   - dist_simple/AnoraEditor_Simple.exe (Simple version)")
    
    print("\n💡 Recommendations:")
    print("   1. Try the portable package first (most compatible)")
    print("   2. If that works, you can distribute the entire folder")
    print("   3. The simple version might work on some systems")
    print("\n🚀 To run:")
    if os.path.exists('AnoraEditor_Portable'):
        print("   ./AnoraEditor_Portable/launch_anora.bat")
    if os.path.exists('dist_simple/AnoraEditor_Simple.exe'):
        print("   ./dist_simple/AnoraEditor_Simple.exe")

if __name__ == "__main__":
    main()