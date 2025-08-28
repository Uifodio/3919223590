#!/usr/bin/env python3
"""
Anora Editor - Dependency Installer
Automatically installs required dependencies for the Anora code editor
"""

import subprocess
import sys
import os
import platform

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Anora Editor - Installing Dependencies")
    print("=" * 40)
    
    # Check if we're on Windows
    if platform.system() != "Windows":
        print("This installer is designed for Windows systems.")
        print("For other platforms, please install dependencies manually:")
        print("pip install -r requirements.txt")
        return
    
    # Install Pygments for syntax highlighting
    print("Installing Pygments for syntax highlighting...")
    if install_package("pygments==2.17.2"):
        print("✓ Pygments installed successfully")
    else:
        print("✗ Failed to install Pygments")
        print("You can try installing manually with: pip install pygments")
    
    print("\nInstallation complete!")
    print("You can now run the Anora editor with: python anora_editor.py")

if __name__ == "__main__":
    main()