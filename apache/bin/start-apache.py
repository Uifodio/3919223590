#!/usr/bin/env python3
"""
Apache-like Server Starter
Starts a web server with PHP support for a specific site
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def start_apache_server(site_name, site_path, port, server_type):
    """Start Apache-like server for a site"""
    try:
        # Get the directory containing this script
        script_dir = Path(__file__).parent
        php_server_script = script_dir / "php-server.py"
        
        if not php_server_script.exists():
            return False, "PHP server script not found"
        
        # Start the PHP-enabled server
        cmd = [
            sys.executable,
            str(php_server_script),
            str(port),
            str(site_path)
        ]
        
        # Start process in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(site_path)
        )
        
        # Give it a moment to start
        time.sleep(0.5)
        
        if process.poll() is None:
            return True, f"Apache-like server started on port {port}"
        else:
            stdout, stderr = process.communicate()
            return False, f"Failed to start server: {stderr or stdout}"
            
    except Exception as e:
        return False, f"Error starting Apache-like server: {str(e)}"

def stop_apache_server(process):
    """Stop Apache-like server"""
    try:
        if process and process.poll() is None:
            process.terminate()
            time.sleep(0.5)
            if process.poll() is None:
                process.kill()
            return True
    except Exception:
        pass
    return False

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python start-apache.py <site_name> <site_path> <port> [server_type]")
        sys.exit(1)
    
    site_name = sys.argv[1]
    site_path = sys.argv[2]
    port = int(sys.argv[3])
    server_type = sys.argv[4] if len(sys.argv) > 4 else 'PHP'
    
    success, message = start_apache_server(site_name, site_path, port, server_type)
    print(f"Success: {success}")
    print(f"Message: {message}")
    
    if success:
        try:
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Server stopped")