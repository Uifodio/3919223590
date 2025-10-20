#!/usr/bin/env python3
"""
Setup script for Futuristic Web Server
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygments"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ['uploads', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up Futuristic Web Server...")
    print("=" * 40)
    
    if install_requirements():
        create_directories()
        print("\n✅ Setup complete!")
        print("\nTo run the application:")
        print("  python3 main.py")
        return True
    else:
        print("\n❌ Setup failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)