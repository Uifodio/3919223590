#!/usr/bin/env python3
"""
Build Script for Anora Editor (wxPython Version)
Creates professional executable with native Windows integration
"""

import os
import sys
import subprocess
import shutil

def build_executable():
    """Build the Anora Editor executable using PyInstaller"""
    
    print("🚀 Building Anora Editor (wxPython) executable...")
    
    # PyInstaller command for wxPython
    cmd = [
        'pyinstaller',
        '--onedir',                     # Directory mode for better compatibility
        '--windowed',                   # No console window
        '--name=AnoraEditor_WX',        # Executable name
        '--distpath=dist_wx',           # Output directory
        '--workpath=build_wx',          # Build directory
        '--specpath=build_wx',          # Spec directory
        '--hidden-import=wx',
        '--hidden-import=wx.stc',
        '--hidden-import=wx.aui',
        '--hidden-import=wx.adv',
        '--hidden-import=wx.html',
        '--hidden-import=wx.grid',
        '--hidden-import=wx.richtext',
        '--collect-all=wx',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=PIL',
        '--exclude-module=cv2',
        '--clean',
        'anora_editor_wx.py'
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = os.path.join('dist_wx', 'AnoraEditor_WX', 'anora_editor_wx')
        if os.path.exists(exe_path):
            print(f"📁 Executable created: {exe_path}")
            print(f"📏 Directory size: {get_dir_size('dist_wx/AnoraEditor_WX') / (1024*1024):.1f} MB")
            
            # Create a launcher script
            create_launcher_script()
            
        else:
            print("❌ Executable not found in dist_wx folder")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it first:")
        print("pip install pyinstaller")
        return False
        
    return True

def build_simple_executable():
    """Build using the simplest possible PyInstaller command"""
    
    print("🚀 Building Anora Editor (wxPython) simple executable...")
    
    # Simple PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=AnoraEditor_WX_Simple',
        '--distpath=dist_wx_simple',
        'anora_editor_wx.py'
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Simple build completed successfully!")
        
        # Check if executable was created
        exe_path = os.path.join('dist_wx_simple', 'anora_editor_wx')
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

def create_launcher_script():
    """Create a launcher script for the directory version"""
    
    launcher_content = '''#!/bin/bash
echo "Starting Anora Editor (wxPython)..."
cd "$(dirname "$0")"
./anora_editor_wx
if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Anora Editor failed to start."
    echo "Please check if all files are present in this directory."
    read -p "Press Enter to continue..."
fi
'''
    
    launcher_path = os.path.join('dist_wx', 'AnoraEditor_WX', 'launch_anora_wx.sh')
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    # Make it executable
    os.chmod(launcher_path, 0o755)
    
    print(f"📄 Launcher script created: {launcher_path}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check if main file exists
    if not os.path.exists('anora_editor_wx.py'):
        print("❌ anora_editor_wx.py not found!")
        return False
    
    # Check if wxPython is available
    try:
        import wx
        print("✅ wxPython available")
    except ImportError:
        print("❌ wxPython not found")
        print("💡 Please install wxPython first:")
        print("   pip install wxPython")
        print("   or")
        print("   sudo apt install python3-wxgtk4.0")
        return False
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print("✅ PyInstaller available")
    except ImportError:
        print("❌ PyInstaller not found")
        print("💡 Please install PyInstaller first:")
        print("   pip install pyinstaller")
        return False
    
    return True

def main():
    """Main build function"""
    print("🔥 Anora Editor (wxPython) Build Script")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Install dependencies if needed
    print("\n📦 Installing dependencies if needed...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                      check=True, capture_output=True)
        print("✅ PyInstaller installed/updated")
    except:
        print("⚠️ PyInstaller installation failed (may already be installed)")
    
    print("\n" + "=" * 60)
    
    # Build executable
    if build_executable():
        print("\n✅ Build completed successfully!")
        print(f"📁 Executable location: dist_wx/AnoraEditor_WX/")
        print(f"🚀 Run: ./dist_wx/AnoraEditor_WX/anora_editor_wx")
    else:
        print("\n❌ Build failed!")
        print("💡 Trying simple build method...")
        
        if build_simple_executable():
            print("\n✅ Simple build completed!")
            print(f"📁 Executable location: dist_wx_simple/")
            print(f"🚀 Run: ./dist_wx_simple/anora_editor_wx")
        else:
            print("\n❌ All build methods failed!")
            return 1
    
    print("\n🎉 Anora Editor (wxPython) build complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())