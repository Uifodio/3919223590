#!/usr/bin/env python3
"""
Unified Server Administrator - Startup Script
============================================

Quick start script for the unified server administrator.
Handles dependencies, system checks, and graceful startup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['flask', 'psutil']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '--user', '--upgrade'
            ] + missing_packages)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def check_system_requirements():
    """Check system requirements and available tools"""
    print("\n🔧 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"  ✅ Python {sys.version.split()[0]}")
    
    # Check for PHP
    php_exe = os.path.join('php', 'php.exe') if os.name == 'nt' else 'php'
    if os.path.exists(php_exe) or subprocess.run(['which', 'php'], capture_output=True).returncode == 0:
        print("  ✅ PHP available")
    else:
        print("  ⚠️  PHP not found - PHP servers will not work")
    
    # Check for Node.js
    if subprocess.run(['which', 'node'], capture_output=True).returncode == 0:
        print("  ✅ Node.js available")
    else:
        print("  ⚠️  Node.js not found - Node.js servers will not work")
    
    # Check for nginx
    if subprocess.run(['which', 'nginx'], capture_output=True).returncode == 0:
        print("  ✅ Nginx available")
    else:
        print("  ⚠️  Nginx not found - advanced features will be limited")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ['sites', 'logs', 'uploads', 'nginx_configs', 'php_fpm_configs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    return True

def main():
    """Main startup function"""
    print("🚀 Unified Server Administrator - Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install required packages manually:")
        print("pip install flask psutil")
        sys.exit(1)
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create directories")
        sys.exit(1)
    
    print("\n✅ All checks passed!")
    print("🌐 Starting web server...")
    print("📱 Open http://localhost:5000 in your browser")
    print("=" * 50)
    
    # Import and run the unified server
    try:
        from web_server_admin import app, Config
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()