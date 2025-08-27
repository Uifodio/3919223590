#!/usr/bin/env python3
"""
Anora Editor Launcher
Provides a smooth startup experience and handles dependencies
"""

import sys
import os
import subprocess
import importlib.util

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    # Check tkinter
    try:
        import tkinter
        print("✅ Tkinter available")
    except ImportError:
        missing_deps.append("tkinter")
        print("❌ Tkinter not found")
    
    # Check pygments
    try:
        import pygments
        print("✅ Pygments available")
    except ImportError:
        missing_deps.append("pygments")
        print("❌ Pygments not found")
    
    return missing_deps

def install_dependencies():
    """Install missing dependencies"""
    print("\n📦 Installing missing dependencies...")
    
    try:
        # Try to install via pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pygments'], 
                      check=True, capture_output=True)
        print("✅ Pygments installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install via pip")
        print("💡 Please install manually:")
        print("   pip install pygments")
        return False

def show_welcome():
    """Show welcome message"""
    print("=" * 60)
    print("🌟 Welcome to Anora Editor!")
    print("=" * 60)
    print("A professional code editor designed for Unity development")
    print()
    print("✨ Features:")
    print("   • Professional dark theme")
    print("   • Tabbed interface for multiple files")
    print("   • Syntax highlighting for C#, Python, JavaScript, and more")
    print("   • Search and replace functionality")
    print("   • Always on top mode for Unity workflow")
    print("   • Compact design for overlay editing")
    print()
    print("🚀 Starting Anora Editor...")
    print("=" * 60)

def main():
    """Main launcher function"""
    
    # Show welcome message
    show_welcome()
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        
        if "pygments" in missing_deps:
            if not install_dependencies():
                print("\n💡 Manual installation required:")
                print("   pip install pygments")
                print("\n   Or on Ubuntu/Debian:")
                print("   sudo apt install python3-pygments")
                return False
        
        if "tkinter" in missing_deps:
            print("\n💡 Tkinter installation required:")
            print("   On Ubuntu/Debian: sudo apt install python3-tk")
            print("   On macOS: Install Python from python.org")
            print("   On Windows: Usually included with Python")
            return False
    
    # Launch the editor
    try:
        print("\n🎯 Launching Anora Editor...")
        
        # Import and run the editor
        from anora_editor import AnoraEditor
        
        app = AnoraEditor()
        app.run()
        
    except ImportError as e:
        print(f"❌ Failed to import Anora Editor: {e}")
        print("💡 Make sure anora_editor.py is in the same directory")
        return False
    except Exception as e:
        print(f"❌ Failed to start Anora Editor: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Failed to launch Anora Editor")
        sys.exit(1)