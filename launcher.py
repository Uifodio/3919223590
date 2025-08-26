#!/usr/bin/env python3
"""
Launcher script for Unity File Manager Pro
Handles import errors gracefully and provides helpful error messages
"""

import sys
import os
import traceback

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
    
    try:
        import pygments
    except ImportError:
        missing_deps.append("pygments")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install them using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("Unity File Manager Pro - Launcher")
    print("=" * 40)
    
    # Check dependencies first
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return 1
    
    # Add src to path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    try:
        print("✓ Starting application...")
        from src.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Unity File Manager Pro")
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        print("✓ Application started successfully!")
        
        # Start event loop
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nThis might be due to:")
        print("1. Missing dependencies - run: pip install -r requirements.txt")
        print("2. Python version - requires Python 3.8 or higher")
        print("3. Corrupted installation - try reinstalling")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\nFull error details:")
        traceback.print_exc()
        
    input("\nPress Enter to exit...")
    return 1

if __name__ == "__main__":
    sys.exit(main())