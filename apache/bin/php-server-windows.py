#!/usr/bin/env python3
"""
Windows-Compatible PHP Server - Apache Alternative
Provides PHP support using Python's built-in server with PHP-CGI
Optimized for Windows compatibility
"""

import os
import sys
import subprocess
import threading
import time
import socket
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import mimetypes
import platform

class PHPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.php_cgi_path = kwargs.pop('php_cgi_path', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path.endswith('.php'):
            self.handle_php_request()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.endswith('.php'):
            self.handle_php_request()
        else:
            super().do_POST()
    
    def handle_php_request(self):
        try:
            # Get the file path
            file_path = self.translate_path(self.path)
            
            if not os.path.exists(file_path):
                self.send_error(404, "File not found")
                return
            
            # Set up environment variables for PHP
            env = os.environ.copy()
            env['REQUEST_METHOD'] = self.command
            env['SCRIPT_FILENAME'] = file_path
            env['QUERY_STRING'] = urllib.parse.urlparse(self.path).query
            env['SERVER_NAME'] = 'localhost'
            env['SERVER_PORT'] = str(self.server.server_port)
            env['CONTENT_TYPE'] = self.headers.get('Content-Type', '')
            env['CONTENT_LENGTH'] = self.headers.get('Content-Length', '0')
            env['SERVER_SOFTWARE'] = 'Apache-like Server/1.0'
            env['DOCUMENT_ROOT'] = str(Path(file_path).parent)
            
            # Read POST data if any
            post_data = b''
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
            
            # Use PHP-CGI if available, otherwise use built-in PHP
            if self.php_cgi_path and os.path.exists(self.php_cgi_path):
                cmd = [self.php_cgi_path, file_path]
            else:
                # Try to find PHP in system
                php_cmd = 'php'
                if platform.system() == 'nt':  # Windows
                    php_cmd = 'php.exe'
                cmd = [php_cmd, file_path]
            
            # Execute PHP
            if platform.system() == 'nt':  # Windows
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    cwd=os.path.dirname(file_path),
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    cwd=os.path.dirname(file_path)
                )
            
            stdout, stderr = process.communicate(input=post_data)
            
            if process.returncode != 0:
                self.send_error(500, f"PHP Error: {stderr.decode()}")
                return
            
            # Parse headers from PHP output
            output = stdout.decode('utf-8', errors='ignore')
            if '\r\n\r\n' in output:
                headers, content = output.split('\r\n\r\n', 1)
                self.send_response(200)
                
                # Parse and set headers
                for line in headers.split('\r\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        self.send_header(key.strip(), value.strip())
                
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                # No headers, send as plain text
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(stdout)
                
        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")

def find_available_port(start_port=8080):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def start_server(port, document_root, php_cgi_path=None):
    """Start the PHP-enabled server"""
    os.chdir(document_root)
    
    handler = lambda *args, **kwargs: PHPRequestHandler(*args, php_cgi_path=php_cgi_path, **kwargs)
    
    try:
        server = HTTPServer(('0.0.0.0', port), handler)
        print(f"Apache-like Server running on http://localhost:{port}")
        print(f"Document root: {document_root}")
        print("Press Ctrl+C to stop")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python php-server-windows.py <port> <document_root> [php_cgi_path]")
        sys.exit(1)
    
    port = int(sys.argv[1])
    document_root = sys.argv[2]
    php_cgi_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    start_server(port, document_root, php_cgi_path)