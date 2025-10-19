"""
Web Server Manager
Handles multiple web servers with advanced features
"""

import threading
import time
import os
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, redirect, url_for
from flask_cors import CORS
import mimetypes
try:
    import magic
except ImportError:
    magic = None
from werkzeug.utils import secure_filename
import qrcode
import io
import base64
from PIL import Image
try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

class WebServerManager:
    """Manages multiple web servers with advanced features"""
    
    def __init__(self):
        self.servers = {}
        self.server_threads = {}
        self.running = {}
        self.config = self.load_config()
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['uploads', 'logs', 'static', 'templates', 'static/css', 'static/js', 'static/images']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def load_config(self):
        """Load server configuration"""
        config_path = Path('config/server_config.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'allowed_extensions': {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.avi', '.mov', '.mp3', '.wav'},
            'enable_upload': True,
            'enable_download': True,
            'enable_streaming': True
        }
    
    def save_config(self):
        """Save server configuration"""
        config_path = Path('config/server_config.json')
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def create_app(self, server_id, port, directory):
        """Create Flask application for a server"""
        app = Flask(__name__, 
                   static_folder=directory,
                   template_folder='templates')
        CORS(app)
        
        # Configure upload settings
        app.config['MAX_CONTENT_LENGTH'] = self.config['max_file_size']
        upload_folder = Path(directory) / 'uploads'
        upload_folder.mkdir(parents=True, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = upload_folder
        
        @app.route('/')
        def index():
            """Main page with file browser"""
            return self.render_file_browser(directory, server_id)
        
        @app.route('/api/files')
        def api_files():
            """API endpoint for file listing"""
            return jsonify(self.get_file_list(directory))
        
        @app.route('/api/upload', methods=['POST'])
        def api_upload():
            """API endpoint for file upload"""
            if not self.config['enable_upload']:
                return jsonify({'error': 'Upload disabled'}), 403
            
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if self.is_allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = app.config['UPLOAD_FOLDER'] / filename
                file.save(file_path)
                return jsonify({'message': 'File uploaded successfully', 'filename': filename})
            
            return jsonify({'error': 'File type not allowed'}), 400
        
        @app.route('/api/download/<path:filename>')
        def api_download(filename):
            """API endpoint for file download"""
            if not self.config['enable_download']:
                return jsonify({'error': 'Download disabled'}), 403
            
            file_path = Path(directory) / filename
            if file_path.exists() and file_path.is_file():
                return send_file(file_path, as_attachment=True)
            return jsonify({'error': 'File not found'}), 404
        
        @app.route('/api/stream/<path:filename>')
        def api_stream(filename):
            """API endpoint for media streaming"""
            if not self.config['enable_streaming']:
                return jsonify({'error': 'Streaming disabled'}), 403
            
            file_path = Path(directory) / filename
            if file_path.exists() and file_path.is_file():
                return send_file(file_path)
            return jsonify({'error': 'File not found'}), 404
        
        @app.route('/api/qr/<path:filename>')
        def api_qr(filename):
            """Generate QR code for file access"""
            url = f"http://localhost:{port}/api/stream/{filename}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return send_file(img_buffer, mimetype='image/png')
        
        @app.route('/api/thumbnail/<path:filename>')
        def api_thumbnail(filename):
            """Generate thumbnail for images/videos"""
            file_path = Path(directory) / filename
            if not file_path.exists():
                return jsonify({'error': 'File not found'}), 404
            
            try:
                if self.is_image_file(filename):
                    thumbnail = self.generate_image_thumbnail(file_path)
                elif self.is_video_file(filename):
                    thumbnail = self.generate_video_thumbnail(file_path)
                else:
                    return jsonify({'error': 'File type not supported for thumbnails'}), 400
                
                return send_file(thumbnail, mimetype='image/png')
            except Exception as e:
                return jsonify({'error': f'Failed to generate thumbnail: {str(e)}'}), 500
        
        @app.route('/api/info/<path:filename>')
        def api_info(filename):
            """Get file information"""
            file_path = Path(directory) / filename
            if not file_path.exists():
                return jsonify({'error': 'File not found'}), 404
            
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            info = {
                'name': filename,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'mime_type': mime_type,
                'is_image': self.is_image_file(filename),
                'is_video': self.is_video_file(filename),
                'is_audio': self.is_audio_file(filename)
            }
            
            return jsonify(info)
        
        @app.route('/api/delete/<path:filename>', methods=['DELETE'])
        def api_delete(filename):
            """Delete a file"""
            file_path = Path(directory) / filename
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return jsonify({'message': 'File deleted successfully'})
            return jsonify({'error': 'File not found'}), 404
        
        return app
    
    def render_file_browser(self, directory, server_id):
        """Render the file browser HTML"""
        files = self.get_file_list(directory)
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Futuristic Web Server - Server {server_id}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #fff;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                
                .header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                
                .upload-area {{
                    background: rgba(255,255,255,0.1);
                    border: 2px dashed rgba(255,255,255,0.3);
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    margin-bottom: 30px;
                    transition: all 0.3s ease;
                }}
                
                .upload-area:hover {{
                    background: rgba(255,255,255,0.2);
                    border-color: rgba(255,255,255,0.5);
                }}
                
                .upload-area.dragover {{
                    background: rgba(255,255,255,0.3);
                    border-color: #4CAF50;
                }}
                
                .file-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }}
                
                .file-card {{
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(10px);
                }}
                
                .file-card:hover {{
                    transform: translateY(-5px);
                    background: rgba(255,255,255,0.2);
                }}
                
                .file-icon {{
                    font-size: 3em;
                    margin-bottom: 10px;
                }}
                
                .file-name {{
                    font-weight: bold;
                    margin-bottom: 5px;
                    word-break: break-word;
                }}
                
                .file-size {{
                    color: rgba(255,255,255,0.7);
                    font-size: 0.9em;
                }}
                
                .file-actions {{
                    margin-top: 15px;
                }}
                
                .btn {{
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 0 5px;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                }}
                
                .btn:hover {{
                    background: #45a049;
                    transform: scale(1.05);
                }}
                
                .btn-danger {{
                    background: #f44336;
                }}
                
                .btn-danger:hover {{
                    background: #da190b;
                }}
                
                .btn-info {{
                    background: #2196F3;
                }}
                
                .btn-info:hover {{
                    background: #1976D2;
                }}
                
                .search-box {{
                    width: 100%;
                    padding: 15px;
                    border: none;
                    border-radius: 25px;
                    background: rgba(255,255,255,0.1);
                    color: white;
                    font-size: 16px;
                    margin-bottom: 20px;
                }}
                
                .search-box::placeholder {{
                    color: rgba(255,255,255,0.7);
                }}
                
                .search-box:focus {{
                    outline: none;
                    background: rgba(255,255,255,0.2);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Futuristic Web Server</h1>
                    <p>Server {server_id} - Professional File Management</p>
                </div>
                
                <div class="upload-area" id="uploadArea">
                    <h3>📁 Drag & Drop Files Here</h3>
                    <p>or click to select files</p>
                    <input type="file" id="fileInput" multiple style="display: none;">
                </div>
                
                <input type="text" class="search-box" placeholder="🔍 Search files..." id="searchBox">
                
                <div class="file-grid" id="fileGrid">
                    {self.generate_file_cards(files)}
                </div>
            </div>
            
            <script>
                const uploadArea = document.getElementById('uploadArea');
                const fileInput = document.getElementById('fileInput');
                const searchBox = document.getElementById('searchBox');
                const fileGrid = document.getElementById('fileGrid');
                
                // File upload handling
                uploadArea.addEventListener('click', () => fileInput.click());
                
                uploadArea.addEventListener('dragover', (e) => {{
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                }});
                
                uploadArea.addEventListener('dragleave', () => {{
                    uploadArea.classList.remove('dragover');
                }});
                
                uploadArea.addEventListener('drop', (e) => {{
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    uploadFiles(e.dataTransfer.files);
                }});
                
                fileInput.addEventListener('change', (e) => {{
                    uploadFiles(e.target.files);
                }});
                
                function uploadFiles(files) {{
                    const formData = new FormData();
                    for (let file of files) {{
                        formData.append('file', file);
                    }}
                    
                    fetch('/api/upload', {{
                        method: 'POST',
                        body: formData
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.error) {{
                            alert('Error: ' + data.error);
                        }} else {{
                            location.reload();
                        }}
                    }});
                }}
                
                // Search functionality
                searchBox.addEventListener('input', (e) => {{
                    const searchTerm = e.target.value.toLowerCase();
                    const cards = fileGrid.querySelectorAll('.file-card');
                    
                    cards.forEach(card => {{
                        const fileName = card.querySelector('.file-name').textContent.toLowerCase();
                        if (fileName.includes(searchTerm)) {{
                            card.style.display = 'block';
                        }} else {{
                            card.style.display = 'none';
                        }}
                    }});
                }});
                
                // Delete file function
                function deleteFile(filename) {{
                    if (confirm('Are you sure you want to delete this file?')) {{
                        fetch(`/api/delete/${{filename}}`, {{
                            method: 'DELETE'
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.message) {{
                                location.reload();
                            }} else {{
                                alert('Error: ' + data.error);
                            }}
                        }});
                    }}
                }}
            </script>
        </body>
        </html>
        """
    
    def generate_file_cards(self, files):
        """Generate HTML for file cards"""
        cards = []
        for file in files:
            icon = self.get_file_icon(file['name'])
            size = self.format_file_size(file['size'])
            modified = time.strftime('%Y-%m-%d %H:%M', time.localtime(file['modified']))
            
            card = f"""
            <div class="file-card">
                <div class="file-icon">{icon}</div>
                <div class="file-name">{file['name']}</div>
                <div class="file-size">{size}</div>
                <div class="file-actions">
                    <a href="/api/stream/{file['name']}" class="btn btn-info" target="_blank">View</a>
                    <a href="/api/download/{file['name']}" class="btn">Download</a>
                    <a href="/api/qr/{file['name']}" class="btn btn-info">QR Code</a>
                    <button onclick="deleteFile('{file['name']}')" class="btn btn-danger">Delete</button>
                </div>
            </div>
            """
            cards.append(card)
        return ''.join(cards)
    
    def get_file_icon(self, filename):
        """Get appropriate icon for file type"""
        ext = Path(filename).suffix.lower()
        icon_map = {
            '.txt': '📄', '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
            '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬', '.mkv': '🎬',
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵',
            '.zip': '📦', '.rar': '📦', '.7z': '📦',
            '.exe': '⚙️', '.msi': '⚙️',
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨'
        }
        return icon_map.get(ext, '📁')
    
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_file_list(self, directory):
        """Get list of files in directory"""
        files = []
        try:
            for item in Path(directory).iterdir():
                if item.is_file():
                    stat = item.stat()
                    files.append({
                        'name': item.name,
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
        except PermissionError:
            pass
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def is_allowed_file(self, filename):
        """Check if file type is allowed"""
        return Path(filename).suffix.lower() in self.config['allowed_extensions']
    
    def is_image_file(self, filename):
        """Check if file is an image"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        return Path(filename).suffix.lower() in image_extensions
    
    def is_video_file(self, filename):
        """Check if file is a video"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        return Path(filename).suffix.lower() in video_extensions
    
    def is_audio_file(self, filename):
        """Check if file is audio"""
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        return Path(filename).suffix.lower() in audio_extensions
    
    def generate_image_thumbnail(self, file_path, size=(200, 200)):
        """Generate thumbnail for image files"""
        try:
            with Image.open(file_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                thumbnail_buffer = io.BytesIO()
                img.save(thumbnail_buffer, format='PNG')
                thumbnail_buffer.seek(0)
                return thumbnail_buffer
        except Exception as e:
            logging.error(f"Failed to generate image thumbnail: {e}")
            return None
    
    def generate_video_thumbnail(self, file_path, size=(200, 200)):
        """Generate thumbnail for video files"""
        if cv2 is None:
            logging.warning("OpenCV not available, cannot generate video thumbnails")
            return None
            
        try:
            cap = cv2.VideoCapture(str(file_path))
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                thumbnail_buffer = io.BytesIO()
                img.save(thumbnail_buffer, format='PNG')
                thumbnail_buffer.seek(0)
                return thumbnail_buffer
        except Exception as e:
            logging.error(f"Failed to generate video thumbnail: {e}")
            return None
    
    def start_server(self, server_id, port, directory):
        """Start a web server"""
        if server_id in self.running and self.running[server_id]:
            return False
        
        try:
            app = self.create_app(server_id, port, directory)
            self.servers[server_id] = app
            
            def run_server():
                app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
            
            thread = threading.Thread(target=run_server, daemon=True)
            thread.start()
            self.server_threads[server_id] = thread
            self.running[server_id] = True
            
            logging.info(f"Server {server_id} started on port {port} serving {directory}")
            return True
        except Exception as e:
            logging.error(f"Failed to start server {server_id}: {e}")
            return False
    
    def stop_server(self, server_id):
        """Stop a web server"""
        if server_id in self.running:
            self.running[server_id] = False
            if server_id in self.servers:
                del self.servers[server_id]
            if server_id in self.server_threads:
                del self.server_threads[server_id]
            logging.info(f"Server {server_id} stopped")
            return True
        return False
    
    def get_server_status(self, server_id):
        """Get status of a server"""
        return self.running.get(server_id, False)
    
    def get_all_servers_status(self):
        """Get status of all servers"""
        return dict(self.running)