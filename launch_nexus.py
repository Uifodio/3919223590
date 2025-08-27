#!/usr/bin/env python3
"""
Nexus Code Launcher
Professional Dark Code Editor
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Install tkinterdnd2 for drag and drop
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tkinterdnd2'])
        print("✅ tkinterdnd2 installed")
    except:
        print("⚠️ tkinterdnd2 installation failed (optional)")
    
    try:
        # Install pywin32 for Windows API
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32'])
        print("✅ pywin32 installed")
    except:
        print("⚠️ pywin32 installation failed (optional)")
    
    try:
        # Install pygments for syntax highlighting
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygments'])
        print("✅ pygments installed")
    except:
        print("⚠️ pygments installation failed (optional)")

def launch_nexus_code():
    """Launch Nexus Code"""
    print("🚀 Launching Nexus Code...")
    
    # Check if nexus_code.py exists
    if not os.path.exists('nexus_code.py'):
        print("❌ nexus_code.py not found!")
        print("💡 Make sure nexus_code.py is in the same directory")
        return False
    
    try:
        # Launch Nexus Code
        subprocess.run([sys.executable, 'nexus_code.py'] + sys.argv[1:])
        return True
    except Exception as e:
        print(f"❌ Failed to launch Nexus Code: {e}")
        return False

def show_error_dialog(message):
    """Show error dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror("Nexus Code Launcher", message)
    root.destroy()

def main():
    """Main launcher function"""
    print("🔥 Nexus Code Launcher")
    print("=" * 40)
    
    # Check dependencies
    missing_modules = check_dependencies()
    
    if missing_modules:
        print(f"⚠️ Missing modules: {missing_modules}")
        print("📦 Installing dependencies...")
        install_dependencies()
    
    # Launch Nexus Code
    if not launch_nexus_code():
        show_error_dialog("Failed to launch Nexus Code.\nPlease check the console for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())