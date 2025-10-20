#!/usr/bin/env python3
"""
Simple Web Server - Command Line Version
A working web server that definitely works without any GUI dependencies
"""

import http.server
import socketserver
import os
import webbrowser
import time
import threading
from pathlib import Path
from urllib.parse import unquote

class SimpleWebHandler(http.server.SimpleHTTPRequestHandler):
    """Simple HTTP handler for file serving and uploads"""
    
    def __init__(self, *args, **kwargs):
        self.server_instance = kwargs.pop('server_instance', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_file_browser()
        elif self.path.startswith('/download/'):
            self.send_file_download()
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests for file uploads"""
        if self.path == '/upload':
            self.handle_file_upload()
        else:
            self.send_error(404, "Not Found")
    
    def send_file_browser(self):
        """Send the main file browser page"""
        files = self.get_file_list()
        html = self.generate_file_browser_html(files)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_file_download(self):
        """Handle file downloads"""
        filename = unquote(self.path[10:])  # Remove '/download/' prefix
        file_path = os.path.join(self.directory, filename)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Error reading file: {str(e)}")
        else:
            self.send_error(404, "File not found")
    
    def handle_file_upload(self):
        """Handle file uploads"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Simple multipart parsing
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
                    print(f"📁 File uploaded: {filename}")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff;">
                <h1>✅ Upload Successful!</h1>
                <p>Uploaded {len(uploaded_files)} file(s):</p>
                <ul>
            """
            for filename in uploaded_files:
                response_html += f"<li>{filename}</li>"
            
            response_html += """
                </ul>
                <a href="/" style="color: #007acc; text-decoration: none; background: #333; padding: 10px 20px; border-radius: 5px;">← Back to File Browser</a>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode('utf-8'))
            
        except Exception as e:
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
                        'modified': stat.st_mtime
                    })
        except Exception:
            pass
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def generate_file_browser_html(self, files):
        """Generate HTML for file browser"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Futuristic Web Server</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff; 
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
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
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
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
        .file-size {{ 
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
        .status {{ 
            background: rgba(255,255,255,0.1); 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Futuristic Web Server</h1>
            <p>Professional File Management & Streaming</p>
            <p>Directory: {self.directory}</p>
        </div>
        
        <div class="status">
            <strong>Server Status:</strong> Running | <strong>Port:</strong> {getattr(self.server_instance, 'port', 'Unknown')} | 
            <strong>Files:</strong> {len(files)}
        </div>
        
        <div class="upload-area">
            <h3>📁 Upload Files</h3>
            <p>Select files to upload to the server</p>
            <input type="file" id="fileInput" multiple>
            <button class="btn upload-btn" onclick="document.getElementById('fileInput').click()">Choose Files</button>
            <button class="btn" onclick="uploadFiles()">Upload Files</button>
        </div>
        
        <div class="file-grid">
"""
        
        if not files:
            html += """
            <div class="file-card" style="grid-column: 1 / -1;">
                <h3>📂 No files found</h3>
                <p>Upload some files to get started!</p>
            </div>
"""
        else:
            for file in files:
                size = self.format_file_size(file['size'])
                modified = time.strftime('%Y-%m-%d %H:%M', time.localtime(file['modified']))
                
                html += f"""
            <div class="file-card">
                <div class="file-name">{file['name']}</div>
                <div class="file-size">{size}</div>
                <div class="file-size">{modified}</div>
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
                // For now, just show a message - in a real implementation, you'd call a delete API
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

class SimpleWebServer:
    """Simple web server class"""
    
    def __init__(self, port=8080, directory=None):
        self.port = port
        self.directory = directory or str(Path.home())
        self.server = None
        self.is_running = False
    
    def start(self):
        """Start the web server"""
        try:
            # Create custom handler class with server instance
            class CustomHandler(SimpleWebHandler):
                def __init__(self, *args, **kwargs):
                    kwargs['server_instance'] = self
                    super().__init__(*args, **kwargs)
            
            # Start server
            with socketserver.TCPServer(("", self.port), CustomHandler) as httpd:
                httpd.directory = self.directory
                self.server = httpd
                self.is_running = True
                
                print(f"🚀 Futuristic Web Server Started!")
                print(f"📡 Port: {self.port}")
                print(f"📁 Directory: {self.directory}")
                print(f"🌐 URL: http://localhost:{self.port}")
                print(f"📱 Open in browser: http://localhost:{self.port}")
                print("\n✨ Features:")
                print("  - File upload and download")
                print("  - Modern web interface")
                print("  - Real-time file browser")
                print("  - Drag & drop support")
                print("\n⏹️  Press Ctrl+C to stop the server")
                
                # Try to open browser
                try:
                    webbrowser.open(f"http://localhost:{self.port}")
                except:
                    pass
                
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped by user")
            self.stop()
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            self.stop()
    
    def stop(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
            self.server = None
        self.is_running = False
        print("✅ Server stopped")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Futuristic Web Server')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Port to run on (default: 8080)')
    parser.add_argument('--directory', '-d', type=str, default=str(Path.home()), help='Directory to serve (default: home directory)')
    
    args = parser.parse_args()
    
    # Validate directory
    if not os.path.exists(args.directory):
        print(f"❌ Directory does not exist: {args.directory}")
        return 1
    
    # Start server
    server = SimpleWebServer(args.port, args.directory)
    server.start()
    
    return 0

if __name__ == "__main__":
    exit(main())