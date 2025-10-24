#!/usr/bin/env python3
"""
Unified Server Administrator - Startup Script
============================================

This script starts the unified server administrator with all necessary components.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Check if all required components are available"""
    print("Checking system requirements...")
    
    # Check Python packages
    try:
        import flask
        import psutil
        import yaml
        print("✓ Python packages available")
    except ImportError as e:
        print(f"✗ Missing Python package: {e}")
        return False
    
    # Check nginx
    try:
        result = subprocess.run(['nginx', '-v'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Nginx available")
        else:
            print("✗ Nginx not available")
            return False
    except FileNotFoundError:
        print("✗ Nginx not found")
        return False
    
    # Check PHP
    try:
        result = subprocess.run(['php', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ PHP available")
        else:
            print("⚠ PHP not available (PHP servers will not work)")
    except FileNotFoundError:
        print("⚠ PHP not found (PHP servers will not work)")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Node.js available")
        else:
            print("⚠ Node.js not available (Node.js servers will not work)")
    except FileNotFoundError:
        print("⚠ Node.js not found (Node.js servers will not work)")
    
    return True

def start_nginx():
    """Start nginx if not running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'active' in result.stdout:
            print("✓ Nginx already running")
            return True
    except:
        pass
    
    try:
        print("Starting nginx...")
        result = subprocess.run(['sudo', 'nginx'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Nginx started successfully")
            return True
        else:
            print(f"✗ Failed to start nginx: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error starting nginx: {e}")
        return False

def start_php_fpm():
    """Start PHP-FPM if not running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'php8.1-fpm'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'active' in result.stdout:
            print("✓ PHP-FPM already running")
            return True
    except:
        pass
    
    try:
        print("Starting PHP-FPM...")
        result = subprocess.run(['sudo', 'systemctl', 'start', 'php8.1-fpm'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ PHP-FPM started successfully")
            return True
        else:
            print(f"⚠ PHP-FPM not available: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠ PHP-FPM not available: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'sites',
        'logs',
        'uploads',
        'nginx_configs',
        'php_fpm_configs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✓ Directories created")

def main():
    """Main startup function"""
    print("Unified Server Administrator - Starting...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ System requirements not met. Please install missing components.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Start nginx
    if not start_nginx():
        print("\n❌ Failed to start nginx. Please check nginx installation.")
        sys.exit(1)
    
    # Start PHP-FPM (optional)
    start_php_fpm()
    
    print("\n✓ All services started successfully!")
    print("\nStarting Unified Server Administrator...")
    print("=" * 50)
    
    # Start the unified server
    try:
        from unified_server_admin import app, Config
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()