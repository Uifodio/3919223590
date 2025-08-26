#!/usr/bin/env python3
"""
Quick Start Script for Unity File Manager Pro
Automatically installs dependencies and runs the application
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_os():
    """Check if operating system is supported"""
    if platform.system() != 'Windows':
        print("Warning: This application is designed for Windows.")
        print("Some features may not work on other operating systems.")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def run_application():
    """Run the main application"""
    print("Starting Unity File Manager Pro...")
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        return False
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        return True
    
    return True

def main():
    """Main quick start process"""
    print("Unity File Manager Pro - Quick Start")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check OS
    check_os()
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Run application
    if not run_application():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())