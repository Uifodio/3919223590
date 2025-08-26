#!/usr/bin/env python3
"""
File Manager Launcher
A simple launcher script for the Windows File Manager application.
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        return True
    except ImportError:
        print("Error: tkinter is not available.")
        print("Please install tkinter for your Python distribution.")
        return False

def install_optional_dependencies():
    """Install optional dependencies if needed"""
    try:
        import win32api
        return True
    except ImportError:
        print("Note: pywin32 not found. Installing for enhanced Windows functionality...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32>=228"])
            print("pywin32 installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("Warning: Could not install pywin32. File manager will work with limited functionality.")
            return False

def main():
    """Main launcher function"""
    print("Windows File Manager Launcher")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return 1
    
    # Check tkinter
    if not check_tkinter():
        input("Press Enter to exit...")
        return 1
    
    # Install optional dependencies on Windows
    if sys.platform.startswith('win'):
        install_optional_dependencies()
    
    # Import and run the file manager
    try:
        from file_manager import main as run_file_manager
        print("Starting File Manager...")
        run_file_manager()
    except ImportError as e:
        print(f"Error: Could not import file manager: {e}")
        print("Make sure file_manager.py is in the same directory as this launcher.")
        input("Press Enter to exit...")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())