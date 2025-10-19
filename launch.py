#!/usr/bin/env python3
"""
Futuristic Web Server Launcher
Automatically detects the best mode to run the application
"""

import sys
import os
import subprocess
from pathlib import Path

def check_gui_support():
    """Check if GUI is supported"""
    try:
        # Try to import PyQt6
        import PyQt6
        return True
    except ImportError:
        return False

def check_display():
    """Check if display is available"""
    return os.environ.get('DISPLAY') is not None

def run_gui_version():
    """Run the GUI version"""
    print("🖥️  Starting GUI version...")
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ GUI version failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  GUI version stopped by user")
        return True

def run_headless_version():
    """Run the headless version"""
    print("🖥️  Starting headless version...")
    try:
        subprocess.run([sys.executable, 'test_server.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Headless version failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Headless version stopped by user")
        return True

def main():
    """Main launcher logic"""
    print("🚀 Futuristic Web Server Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('main.py').exists():
        print("❌ Error: main.py not found. Please run from the project directory.")
        return False
    
    # Check GUI support
    gui_supported = check_gui_support()
    display_available = check_display()
    
    print(f"GUI Support: {'✅ Yes' if gui_supported else '❌ No'}")
    print(f"Display Available: {'✅ Yes' if display_available else '❌ No'}")
    
    # Choose the best mode
    if gui_supported and display_available:
        print("\n🎨 Starting in GUI mode...")
        return run_gui_version()
    else:
        print("\n🖥️  Starting in headless mode...")
        print("   (GUI not available or no display)")
        return run_headless_version()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)