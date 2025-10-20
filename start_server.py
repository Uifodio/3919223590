#!/usr/bin/env python3
"""
Futuristic Web Server - Auto Port Finder
Automatically finds an available port and starts the server
"""

import socket
import sys
import os
from pathlib import Path

def find_free_port(start_port=8080, max_attempts=100):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def main():
    """Main function with auto port finding"""
    print("🚀 Futuristic Web Server - Starting...")
    print("=" * 50)
    
    # Find a free port
    port = find_free_port()
    if port is None:
        print("❌ Could not find an available port")
        return 1
    
    # Set directory
    directory = "/workspace"
    if not os.path.exists(directory):
        directory = str(Path.home())
    
    print(f"📡 Found free port: {port}")
    print(f"📁 Serving directory: {directory}")
    print(f"🌐 Will open: http://localhost:{port}")
    print()
    
    # Import and run the server
    try:
        from simple_server import SimpleWebServer
        server = SimpleWebServer(port, directory)
        server.start()
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())