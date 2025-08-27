#!/usr/bin/env python3
"""
Anora Editor Launcher (wxPython Version)
Professional Code Editor with Native Windows Integration
"""

import os
import sys
import subprocess
import wx

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        'wx',
        'wx.stc',
        'wx.aui'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} not found")
    
    return missing_modules

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing wxPython...")
    
    try:
        # Try to install wxPython
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'wxPython'])
        print("✅ wxPython installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install wxPython via pip")
        print("💡 Trying system package manager...")
        
        try:
            # Try system package manager
            subprocess.check_call(['sudo', 'apt', 'update'])
            subprocess.check_call(['sudo', 'apt', 'install', '-y', 'python3-wxgtk4.0'])
            print("✅ wxPython installed via system package manager")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install wxPython")
            return False

def show_welcome():
    """Show welcome message"""
    print("=" * 60)
    print("🌟 Welcome to Anora Editor (wxPython)!")
    print("=" * 60)
    print("A professional code editor with native Windows integration")
    print()
    print("✨ Features:")
    print("   • Native Windows drag and drop")
    print("   • Professional dark theme")
    print("   • Advanced syntax highlighting")
    print("   • Tabbed interface for multiple files")
    print("   • Search and replace functionality")
    print("   • Professional window behavior")
    print("   • wxPython native integration")
    print()
    print("🚀 Starting Anora Editor...")
    print("=" * 60)

def launch_anora_wx():
    """Launch Anora Editor (wxPython version)"""
    print("🚀 Launching Anora Editor (wxPython)...")
    
    # Check if anora_editor_wx.py exists
    if not os.path.exists('anora_editor_wx.py'):
        print("❌ anora_editor_wx.py not found!")
        print("💡 Make sure anora_editor_wx.py is in the same directory")
        return False
    
    try:
        # Launch Anora Editor
        subprocess.run([sys.executable, 'anora_editor_wx.py'] + sys.argv[1:])
        return True
    except Exception as e:
        print(f"❌ Failed to launch Anora Editor: {e}")
        return False

def show_error_dialog(message):
    """Show error dialog"""
    app = wx.App()
    dlg = wx.MessageDialog(None, message, "Anora Editor Launcher", 
                          wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()
    app.Destroy()

def main():
    """Main launcher function"""
    show_welcome()
    
    # Check dependencies
    missing_modules = check_dependencies()
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        
        if 'wx' in missing_modules:
            print("\n📦 Installing wxPython...")
            if not install_dependencies():
                print("\n💡 Manual installation required:")
                print("   On Ubuntu/Debian: sudo apt install python3-wxgtk4.0")
                print("   On Windows: pip install wxPython")
                print("   On macOS: pip install wxPython")
                return False
    
    # Launch Anora Editor
    if not launch_anora_wx():
        show_error_dialog("Failed to launch Anora Editor.\nPlease check the console for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())