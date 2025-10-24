#!/usr/bin/env python3
"""
Unified Server Administrator - Quick Start
==========================================

Simple startup script for the unified server administrator.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting Unified Server Administrator...")
    print("=" * 50)
    
    # Check if nginx is running
    try:
        result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Nginx configuration is valid")
        else:
            print("⚠️  Nginx configuration issues detected")
    except FileNotFoundError:
        print("❌ Nginx not found - some features may not work")
    
    # Create necessary directories
    directories = ['sites', 'logs', 'uploads', 'nginx_configs', 'php_fpm_configs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")
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