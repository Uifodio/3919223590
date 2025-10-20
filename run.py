#!/usr/bin/env python3
"""
Modern Server Administrator Launcher
Quick launcher with dependency checking
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['psutil', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstalling missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install dependencies. Please run:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def main():
    """Main launcher function"""
    print("🚀 Modern Server Administrator")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return
    
    print(f"Python version: {sys.version}")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Import and run the main application
    try:
        from main import main as run_app
        print("Starting Modern Server Administrator...")
        run_app()
    except ImportError as e:
        print(f"Error importing application: {e}")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()