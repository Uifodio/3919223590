#!/usr/bin/env python3
"""
Anora Editor - Universal Launcher
=================================

This script launches Anora Editor with comprehensive dependency checking
and installation instructions.
"""

import sys
import os
import subprocess
import platform

def print_banner():
    """Print the Anora Editor banner"""
    print("=" * 60)
    print("    ANORA EDITOR - Professional Code Editor for Unity")
    print("=" * 60)
    print("    Fast, lightweight, and designed for Unity developers")
    print("    who need a professional editing experience without the bloat.")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required.")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please install Python 3.7+ from https://python.org")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        print("✅ tkinter - Available")
        return True
    except ImportError:
        print("❌ tkinter - Not available")
        print("\n   Installation instructions:")
        system = platform.system().lower()
        if system == "linux":
            print("   Ubuntu/Debian: sudo apt install python3-tk")
            print("   CentOS/RHEL: sudo yum install python3-tkinter")
            print("   Arch: sudo pacman -S tk")
        elif system == "darwin":  # macOS
            print("   macOS: brew install python-tk")
        elif system == "windows":
            print("   Windows: Usually included with Python")
            print("   Try reinstalling Python from https://python.org")
        return False

def check_pygments():
    """Check if pygments is available"""
    try:
        import pygments
        print("✅ pygments - Available")
        return True
    except ImportError:
        print("❌ pygments - Not available")
        print("\n   Installation:")
        print("   pip install pygments")
        print("   or")
        print("   pip install -r requirements.txt")
        return False

def install_dependencies():
    """Attempt to install missing dependencies"""
    print("\n🔧 Attempting to install missing dependencies...")
    
    # Try to install pygments
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygments"])
        print("✅ Successfully installed pygments")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install pygments automatically")
        print("   Please install manually: pip install pygments")
        return False

def launch_editor():
    """Launch the main editor"""
    try:
        # Import and run the main editor
        from anora_editor import main
        print("\n🚀 Launching Anora Editor...")
        main()
    except ImportError as e:
        print(f"❌ Error importing main editor: {e}")
        print("   Make sure anora_editor.py is in the same directory.")
        return False
    except Exception as e:
        print(f"❌ Error launching editor: {e}")
        return False

def main():
    """Main launcher function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    tkinter_ok = check_tkinter()
    pygments_ok = check_pygments()
    
    # If pygments is missing, try to install it
    if not pygments_ok:
        install_dependencies()
        # Check again
        try:
            import pygments
            pygments_ok = True
            print("✅ pygments - Now available")
        except ImportError:
            pass
    
    # If dependencies are missing, show instructions
    if not tkinter_ok or not pygments_ok:
        print("\n❌ Missing dependencies detected.")
        print("\nPlease install the missing dependencies and try again.")
        print("\nQuick fix commands:")
        print("  pip install pygments")
        print("  # For tkinter, see installation instructions above")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # All dependencies available, launch editor
    print("\n✅ All dependencies available!")
    launch_editor()

if __name__ == "__main__":
    main()