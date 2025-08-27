#!/usr/bin/env python3
"""
Anora Editor Launcher
Professional Code Editor with Native Windows Integration
"""

import os
import sys
import subprocess
import platform

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        'wx',
        'wx.stc',
        'wx.aui',
        'wx.adv',
        'wx.html',
        'wx.grid',
        'wx.richtext'
    ]
    
    optional_modules = [
        'winreg',
        'win32gui',
        'win32con',
        'win32api',
        'win32clipboard',
        'ctypes',
        'pygments'
    ]
    
    missing_modules = []
    missing_optional = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} not found")
    
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            missing_optional.append(module)
            print(f"⚠️ {module} not found (optional)")
    
    return missing_modules, missing_optional

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing dependencies...")
    
    # Install wxPython first
    try:
        print("📦 Installing wxPython...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'wxPython'])
        print("✅ wxPython installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install wxPython via pip")
        
        # Try alternative installation methods
        if platform.system() == "Windows":
            print("💡 Trying alternative Windows installation...")
            try:
                # Try installing with --user flag
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', 'wxPython'])
                print("✅ wxPython installed with --user flag")
            except subprocess.CalledProcessError:
                print("❌ Failed to install with --user flag")
                
            try:
                # Try installing from wheel
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'wxPython'])
                print("✅ wxPython installed after pip upgrade")
            except subprocess.CalledProcessError:
                print("❌ Failed to install after pip upgrade")
        else:
            print("💡 Trying system package manager...")
            try:
                # Try system package manager
                subprocess.check_call(['sudo', 'apt', 'update'])
                subprocess.check_call(['sudo', 'apt', 'install', '-y', 'python3-wxgtk4.0'])
                print("✅ wxPython installed via system package manager")
            except subprocess.CalledProcessError:
                print("❌ Failed to install via system package manager")
                return False
    
    # Install pywin32 for Windows features
    if platform.system() == "Windows":
        try:
            print("📦 Installing pywin32...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32'])
            print("✅ pywin32 installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️ Failed to install pywin32 - Windows features will be limited")
    
    # Install pygments for advanced syntax highlighting
    try:
        print("📦 Installing pygments...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygments'])
        print("✅ pygments installed successfully")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to install pygments - using built-in highlighting")
    
    return True

def show_welcome():
    """Show welcome message"""
    print("=" * 70)
    print("🌟 Welcome to Anora Editor - Professional Code Editor!")
    print("=" * 70)
    print("A professional code editor with native Windows integration")
    print()
    print("✨ ALL Features Included:")
    print("   • Native Windows drag and drop")
    print("   • Professional dark theme")
    print("   • Advanced syntax highlighting (8+ languages)")
    print("   • Tabbed interface for multiple files")
    print("   • Search and replace functionality")
    print("   • Professional window behavior")
    print("   • Auto-save and file monitoring")
    print("   • Advanced keyboard shortcuts")
    print("   • Windows registry integration")
    print("   • Clipboard monitoring")
    print("   • File associations")
    print("   • Professional menus and toolbars")
    print("   • Line operations (delete, duplicate, move)")
    print("   • Multiple cursors and selections")
    print("   • Code folding and bracket matching")
    print("   • Settings persistence")
    print()
    print("🚀 Starting Anora Editor...")
    print("=" * 70)

def launch_anora():
    """Launch Anora Editor"""
    print("🚀 Launching Anora Editor...")
    
    # Check if anora_editor.py exists
    if not os.path.exists('anora_editor.py'):
        print("❌ anora_editor.py not found!")
        print("💡 Make sure anora_editor.py is in the same directory")
        return False
    
    try:
        # Launch Anora Editor
        subprocess.run([sys.executable, 'anora_editor.py'] + sys.argv[1:])
        return True
    except Exception as e:
        print(f"❌ Failed to launch Anora Editor: {e}")
        return False

def show_error_dialog(message):
    """Show error dialog"""
    try:
        import wx
        app = wx.App()
        dlg = wx.MessageDialog(None, message, "Anora Editor Launcher", 
                              wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        app.Destroy()
    except:
        print(f"❌ Error: {message}")

def main():
    """Main launcher function"""
    show_welcome()
    
    # Check dependencies
    missing_modules, missing_optional = check_dependencies()
    
    if missing_modules:
        print(f"\n❌ Missing required modules: {', '.join(missing_modules)}")
        
        if 'wx' in missing_modules:
            print("\n📦 Installing dependencies...")
            if not install_dependencies():
                print("\n💡 Manual installation required:")
                if platform.system() == "Windows":
                    print("   On Windows:")
                    print("   1. Open Command Prompt as Administrator")
                    print("   2. Run: pip install wxPython")
                    print("   3. Run: pip install pywin32")
                    print("   4. Run: pip install pygments")
                    print("   5. If that fails, try: pip install --user wxPython")
                    print("   6. Or download from: https://www.wxpython.org/download.php")
                else:
                    print("   On Ubuntu/Debian: sudo apt install python3-wxgtk4.0")
                    print("   On macOS: pip install wxPython")
                return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional modules: {', '.join(missing_optional)}")
        print("   Some advanced features may be limited")
        
        # Try to install optional modules
        if platform.system() == "Windows" and 'win32gui' in missing_optional:
            try:
                print("📦 Installing pywin32 for Windows features...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32'])
                print("✅ pywin32 installed successfully")
            except:
                print("⚠️ Failed to install pywin32 - Windows features will be limited")
        
        if 'pygments' in missing_optional:
            try:
                print("📦 Installing pygments for advanced highlighting...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygments'])
                print("✅ pygments installed successfully")
            except:
                print("⚠️ Failed to install pygments - using built-in highlighting")
    
    # Launch Anora Editor
    if not launch_anora():
        show_error_dialog("Failed to launch Anora Editor.\nPlease check the console for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())