#!/usr/bin/env python3
"""
Professional Web Server Manager
Manages multiple web servers with proper logging and controls
"""

import http.server
import socketserver
import threading
import time
import os
import json
import logging
import socket
import webbrowser
from pathlib import Path
from urllib.parse import unquote, urlparse
from datetime import datetime
import mimetypes

class ServerLogger:
    """Professional logging system for each server"""
    
    def __init__(self, server_id, log_dir="logs"):
        self.server_id = server_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(f"server_{server_id}")
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        log_file = self.log_dir / f"server_{server_id}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            f'[Server {server_id}] %(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)

class ProfessionalWebHandler(http.server.SimpleHTTPRequestHandler):
    """Professional HTTP handler with proper logging and features"""
    
    def __init__(self, *args, **kwargs):
        self.server_manager = kwargs.pop('server_manager', None)
        self.server_id = kwargs.pop('server_id', None)
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to use our custom logger"""
        if self.server_manager and self.server_id:
            message = format % args
            self.server_manager.log_message(self.server_id, message)
    
    def do_GET(self):
        """Handle GET requests with proper logging"""
        self.log_message(f"GET {self.path}")
        
        if self.path == '/':
            self.send_file_browser()
        elif self.path.startswith('/download/'):
            self.send_file_download()
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        self.log_message(f"POST {self.path}")
        
        if self.path == '/upload':
            self.handle_file_upload()
        else:
            self.send_error(404, "Not Found")
    
    def send_file_browser(self):
        """Send professional file browser page"""
        files = self.get_file_list()
        html = self.generate_file_browser_html(files)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_file_download(self):
        """Handle file downloads with proper logging"""
        filename = unquote(self.path[10:])  # Remove '/download/' prefix
        file_path = os.path.join(self.directory, filename)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                # Get file info
                file_size = os.path.getsize(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', mime_type or 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                
                self.log_message(f"Downloaded: {filename} ({file_size} bytes)")
                
            except Exception as e:
                self.log_message(f"Download error: {str(e)}")
                self.send_error(500, f"Error reading file: {str(e)}")
        else:
            self.log_message(f"File not found: {filename}")
            self.send_error(404, "File not found")
    
    def handle_api_request(self):
        """Handle API requests"""
        if self.path == '/api/files':
            self.send_file_list_api()
        elif self.path == '/api/status':
            self.send_status_api()
        else:
            self.send_error(404, "API endpoint not found")
    
    def send_file_list_api(self):
        """Send file list as JSON"""
        files = self.get_file_list()
        response = {
            'success': True,
            'files': files,
            'count': len(files),
            'directory': self.directory
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def send_status_api(self):
        """Send server status as JSON"""
        status = {
            'server_id': self.server_id,
            'port': self.server.server_address[1],
            'directory': self.directory,
            'uptime': time.time() - getattr(self.server, 'start_time', time.time()),
            'status': 'running'
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode('utf-8'))
    
    def handle_file_upload(self):
        """Handle file uploads with proper logging"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse multipart data
            boundary = self.headers['Content-Type'].split('boundary=')[1]
            parts = post_data.split(f'--{boundary}'.encode())
            
            uploaded_files = []
            for part in parts:
                if b'filename=' in part:
                    # Extract filename
                    filename_start = part.find(b'filename="') + 10
                    filename_end = part.find(b'"', filename_start)
                    filename = part[filename_start:filename_end].decode()
                    
                    # Extract file content
                    content_start = part.find(b'\r\n\r\n') + 4
                    file_content = part[content_start:-2]  # Remove trailing \r\n
                    
                    # Save file
                    file_path = os.path.join(self.directory, filename)
                    with open(file_path, 'wb') as f:
                        f.write(file_content)
                    
                    uploaded_files.append(filename)
                    self.log_message(f"Uploaded: {filename} ({len(file_content)} bytes)")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            response_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Upload Successful</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
                    .container {{ max-width: 600px; margin: 0 auto; text-align: center; }}
                    .success {{ background: #28a745; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                    .btn {{ background: #007acc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ Upload Successful!</h1>
                    <div class="success">
                        <h3>Uploaded {len(uploaded_files)} file(s):</h3>
                        <ul style="text-align: left;">
            """
            for filename in uploaded_files:
                response_html += f"<li>{filename}</li>"
            
            response_html += """
                        </ul>
                    </div>
                    <a href="/" class="btn">← Back to File Browser</a>
                </div>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode('utf-8'))
            
        except Exception as e:
            self.log_message(f"Upload error: {str(e)}")
            self.send_error(500, f"Upload error: {str(e)}")
    
    def get_file_list(self):
        """Get list of files in the directory"""
        files = []
        try:
            for item in os.listdir(self.directory):
                item_path = os.path.join(self.directory, item)
                if os.path.isfile(item_path):
                    stat = os.stat(item_path)
                    files.append({
                        'name': item,
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'type': mimetypes.guess_type(item_path)[0] or 'unknown'
                    })
        except Exception as e:
            self.log_message(f"Error reading directory: {str(e)}")
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def generate_file_browser_html(self, files):
        """Generate professional file browser HTML"""
        server_id = getattr(self, 'server_id', 'Unknown')
        port = self.server.server_address[1] if hasattr(self, 'server') else 'Unknown'
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Server {server_id} - Port {port}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff; 
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 40px; 
            padding: 40px 0;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        .header h1 {{ font-size: 3em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .header p {{ font-size: 1.2em; margin: 10px 0 0 0; opacity: 0.9; }}
        .server-info {{ 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .info-item {{ text-align: center; }}
        .info-label {{ font-size: 0.9em; opacity: 0.7; margin-bottom: 5px; }}
        .info-value {{ font-size: 1.2em; font-weight: bold; }}
        .upload-area {{ 
            border: 3px dashed rgba(255,255,255,0.3); 
            padding: 40px; 
            text-align: center; 
            margin-bottom: 40px; 
            border-radius: 15px;
            background: rgba(255,255,255,0.05);
            transition: all 0.3s ease;
        }}
        .upload-area:hover {{ 
            border-color: rgba(255,255,255,0.6);
            background: rgba(255,255,255,0.1);
        }}
        .file-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 25px; 
        }}
        .file-card {{ 
            background: rgba(255,255,255,0.1); 
            padding: 25px; 
            border-radius: 15px; 
            text-align: center;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .file-card:hover {{ 
            transform: translateY(-5px);
            background: rgba(255,255,255,0.2);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .file-name {{ 
            font-weight: bold; 
            margin-bottom: 10px; 
            word-break: break-word;
            font-size: 1.1em;
        }}
        .file-info {{ 
            color: rgba(255,255,255,0.7); 
            font-size: 0.9em; 
            margin-bottom: 15px; 
        }}
        .file-actions {{ 
            display: flex; 
            gap: 10px; 
            justify-content: center; 
            flex-wrap: wrap;
        }}
        .btn {{ 
            background: #007acc; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 8px; 
            cursor: pointer; 
            text-decoration: none;
            display: inline-block;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        .btn:hover {{ 
            background: #005a9e; 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        .btn-danger {{ background: #dc3545; }}
        .btn-danger:hover {{ background: #c82333; }}
        .btn-success {{ background: #28a745; }}
        .btn-success:hover {{ background: #218838; }}
        input[type="file"] {{ display: none; }}
        .upload-btn {{ background: #28a745; }}
        .upload-btn:hover {{ background: #218838; }}
        .empty-state {{ 
            grid-column: 1 / -1; 
            text-align: center; 
            padding: 60px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
        }}
        .refresh-btn {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #6c757d; 
            color: white; 
            border: none; 
            padding: 10px 15px; 
            border-radius: 50%; 
            cursor: pointer;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <button class="refresh-btn" onclick="location.reload()" title="Refresh">🔄</button>
        
        <div class="header">
            <h1>🚀 Server {server_id}</h1>
            <p>Professional File Management & Streaming</p>
        </div>
        
        <div class="server-info">
            <div class="info-item">
                <div class="info-label">Port</div>
                <div class="info-value">{port}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Directory</div>
                <div class="info-value">{os.path.basename(self.directory)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Files</div>
                <div class="info-value">{len(files)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Status</div>
                <div class="info-value" style="color: #28a745;">Running</div>
            </div>
        </div>
        
        <div class="upload-area">
            <h3>📁 Upload Files</h3>
            <p>Select files to upload to this server</p>
            <input type="file" id="fileInput" multiple>
            <button class="btn upload-btn" onclick="document.getElementById('fileInput').click()">Choose Files</button>
            <button class="btn" onclick="uploadFiles()">Upload Files</button>
        </div>
        
        <div class="file-grid">
"""
        
        if not files:
            html += """
            <div class="empty-state">
                <h3>📂 No files found</h3>
                <p>Upload some files to get started!</p>
            </div>
"""
        else:
            for file in files:
                size = self.format_file_size(file['size'])
                modified = time.strftime('%Y-%m-%d %H:%M', time.localtime(file['modified']))
                file_type = file.get('type', 'unknown')
                
                html += f"""
            <div class="file-card">
                <div class="file-name">{file['name']}</div>
                <div class="file-info">{size}</div>
                <div class="file-info">{modified}</div>
                <div class="file-info">{file_type}</div>
                <div class="file-actions">
                    <a href="/download/{file['name']}" class="btn btn-success">📥 Download</a>
                    <button class="btn btn-danger" onclick="deleteFile('{file['name']}')">🗑️ Delete</button>
                </div>
            </div>
"""
        
        html += """
        </div>
    </div>
    
    <script>
        function uploadFiles() {
            const input = document.getElementById('fileInput');
            const files = input.files;
            
            if (files.length === 0) {
                alert('Please select files to upload');
                return;
            }
            
            const formData = new FormData();
            for (let file of files) {
                formData.append('file', file);
            }
            
            // Show loading
            const uploadBtn = document.querySelector('button[onclick="uploadFiles()"]');
            const originalText = uploadBtn.textContent;
            uploadBtn.textContent = 'Uploading...';
            uploadBtn.disabled = true;
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Upload failed');
                }
            })
            .catch(error => {
                alert('Upload error: ' + error);
            })
            .finally(() => {
                uploadBtn.textContent = originalText;
                uploadBtn.disabled = false;
            });
        }
        
        function deleteFile(filename) {
            if (confirm('Are you sure you want to delete ' + filename + '?')) {
                alert('Delete functionality would be implemented here. For now, you can delete files manually from the server directory.');
            }
        }
        
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""
        return html
    
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

class WebServer:
    """Individual web server instance"""
    
    def __init__(self, server_id, port, directory, server_manager):
        self.server_id = server_id
        self.port = port
        self.directory = os.path.abspath(directory)
        self.server_manager = server_manager
        self.logger = ServerLogger(server_id)
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.start_time = None
        
        # Ensure directory exists
        os.makedirs(self.directory, exist_ok=True)
    
    def start(self):
        """Start the web server"""
        try:
            # Check if port is available
            if not self.is_port_available(self.port):
                raise Exception(f"Port {self.port} is already in use")
            
            # Create custom handler
            class CustomHandler(ProfessionalWebHandler):
                def __init__(self, *args, **kwargs):
                    kwargs['server_manager'] = self.server_manager
                    kwargs['server_id'] = self.server_id
                    super().__init__(*args, **kwargs)
            
            # Start server in separate thread
            def run_server():
                with socketserver.TCPServer(("", self.port), CustomHandler) as httpd:
                    httpd.directory = self.directory
                    httpd.start_time = time.time()
                    self.server = httpd
                    self.start_time = time.time()
                    self.is_running = True
                    
                    self.logger.info(f"Server started on port {self.port}")
                    self.logger.info(f"Serving directory: {self.directory}")
                    self.logger.info(f"Access at: http://localhost:{self.port}")
                    
                    httpd.serve_forever()
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Wait a moment to ensure server started
            time.sleep(0.5)
            
            if self.is_running:
                self.logger.info("Server started successfully")
                return True
            else:
                raise Exception("Server failed to start")
                
        except Exception as e:
            self.logger.error(f"Failed to start server: {str(e)}")
            return False
    
    def stop(self):
        """Stop the web server"""
        try:
            if self.server:
                self.server.shutdown()
                self.server = None
            
            self.is_running = False
            self.logger.info("Server stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping server: {str(e)}")
            return False
    
    def is_port_available(self, port):
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False
    
    def get_status(self):
        """Get server status"""
        uptime = time.time() - self.start_time if self.start_time else 0
        return {
            'server_id': self.server_id,
            'port': self.port,
            'directory': self.directory,
            'is_running': self.is_running,
            'uptime': uptime,
            'start_time': self.start_time
        }

class ServerManager:
    """Professional server manager for multiple servers"""
    
    def __init__(self):
        self.servers = {}
        self.next_server_id = 1
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create main logger
        self.main_logger = logging.getLogger("server_manager")
        self.main_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.main_logger.handlers.clear()
        
        # File handler
        log_file = self.log_dir / "manager.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.main_logger.addHandler(file_handler)
        self.main_logger.addHandler(console_handler)
    
    def create_server(self, port, directory):
        """Create a new server"""
        server_id = self.next_server_id
        self.next_server_id += 1
        
        server = WebServer(server_id, port, directory, self)
        self.servers[server_id] = server
        
        self.main_logger.info(f"Created server {server_id} on port {port} serving {directory}")
        return server_id
    
    def start_server(self, server_id):
        """Start a server"""
        if server_id in self.servers:
            server = self.servers[server_id]
            if server.start():
                self.main_logger.info(f"Started server {server_id}")
                return True
            else:
                self.main_logger.error(f"Failed to start server {server_id}")
                return False
        else:
            self.main_logger.error(f"Server {server_id} not found")
            return False
    
    def stop_server(self, server_id):
        """Stop a server"""
        if server_id in self.servers:
            server = self.servers[server_id]
            if server.stop():
                self.main_logger.info(f"Stopped server {server_id}")
                return True
            else:
                self.main_logger.error(f"Failed to stop server {server_id}")
                return False
        else:
            self.main_logger.error(f"Server {server_id} not found")
            return False
    
    def get_server_status(self, server_id):
        """Get server status"""
        if server_id in self.servers:
            return self.servers[server_id].get_status()
        return None
    
    def get_all_servers_status(self):
        """Get status of all servers"""
        return {server_id: server.get_status() for server_id, server in self.servers.items()}
    
    def list_servers(self):
        """List all servers"""
        return list(self.servers.keys())
    
    def log_message(self, server_id, message):
        """Log a message for a specific server"""
        if server_id in self.servers:
            self.servers[server_id].logger.info(message)
    
    def open_server_in_browser(self, server_id):
        """Open server in browser"""
        if server_id in self.servers:
            server = self.servers[server_id]
            if server.is_running:
                webbrowser.open(f"http://localhost:{server.port}")
                return True
        return False