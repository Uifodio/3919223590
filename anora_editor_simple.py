#!/usr/bin/env python3
"""
ANORA EDITOR - Professional Code Editor for Unity (Simplified Version)
======================================================================

A lightweight, fast, professional code editor designed specifically for Unity development.
This is a simplified version that works with minimal dependencies.

Features:
- Dark theme with VS Code-style colors
- Syntax highlighting for multiple languages
- Tab management
- Search and replace functionality
- Session persistence
- Professional appearance

Requirements:
- Python 3.7+
- tkinter (usually included with Python)
- pygments (for syntax highlighting)

Installation:
- Ubuntu/Debian: sudo apt install python3-tk
- CentOS/RHEL: sudo yum install python3-tkinter
- macOS: brew install python-tk
- Windows: Usually included with Python
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    # Check tkinter
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter")
    
    # Check pygments
    try:
        import pygments
    except ImportError:
        missing.append("pygments")
    
    if missing:
        print("❌ Missing dependencies:", ", ".join(missing))
        print("\nInstallation instructions:")
        print("1. Install Python 3.7+ from https://python.org")
        print("2. Install tkinter:")
        print("   Ubuntu/Debian: sudo apt install python3-tk")
        print("   CentOS/RHEL: sudo yum install python3-tkinter")
        print("   macOS: brew install python-tk")
        print("   Windows: Usually included with Python")
        print("3. Install pygments: pip install pygments")
        print("\nOr run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function with dependency check"""
    print("Anora Editor - Professional Code Editor for Unity")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("\nPlease install the missing dependencies and try again.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Import the main editor
    try:
        from anora_editor import main as run_editor
        print("✅ All dependencies available!")
        print("🚀 Starting Anora Editor...")
        run_editor()
    except ImportError as e:
        print(f"❌ Error importing main editor: {e}")
        print("Make sure anora_editor.py is in the same directory.")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running editor: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()