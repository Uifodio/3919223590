#!/usr/bin/env python3
"""
Simple Web Server with Tkinter GUI
A working web server application using only tkinter and basic Python libraries
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import http.server
import socketserver
import threading
import os
import webbrowser
import mimetypes
import json
from pathlib import Path
import time
import socket
from urllib.parse import unquote

class WebServerHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for file serving and uploads"""
    
    def __init__(self, *args, **kwargs):
        self.server_instance = kwargs.pop('server_instance', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_file_browser()
        elif self.path.startswith('/download/'):
            self.send_file_download()
        elif self.path.startswith('/upload'):
            self.send_upload_page()
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
    
    def send_upload_page(self):
        """Send the upload page"""
        html = self.generate_upload_page_html()
        
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
                    
                    # Notify the GUI
                    if self.server_instance:
                        self.server_instance.on_file_uploaded(filename)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Upload successful!</h1><a href="/">Back to file browser</a></body></html>')
            
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
    <title>Web Server - {os.path.basename(self.directory)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .upload-area {{ 
            border: 2px dashed #555; 
            padding: 40px; 
            text-align: center; 
            margin-bottom: 30px; 
            border-radius: 10px;
            background: #2a2a2a;
        }}
        .file-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
        .file-item {{ 
            background: #333; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center;
            transition: background 0.3s;
        }}
        .file-item:hover {{ background: #444; }}
        .file-name {{ font-weight: bold; margin-bottom: 10px; word-break: break-word; }}
        .file-size {{ color: #aaa; font-size: 0.9em; margin-bottom: 15px; }}
        .file-actions {{ display: flex; gap: 10px; justify-content: center; }}
        .btn {{ 
            background: #007acc; 
            color: white; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 4px; 
            cursor: pointer; 
            text-decoration: none;
            display: inline-block;
        }}
        .btn:hover {{ background: #005a9e; }}
        .btn-danger {{ background: #dc3545; }}
        .btn-danger:hover {{ background: #c82333; }}
        input[type="file"] {{ display: none; }}
        .upload-btn {{ background: #28a745; }}
        .upload-btn:hover {{ background: #218838; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Web Server</h1>
        <p>Directory: {self.directory}</p>
    </div>
    
    <div class="upload-area">
        <h3>Upload Files</h3>
        <input type="file" id="fileInput" multiple>
        <button class="btn upload-btn" onclick="document.getElementById('fileInput').click()">Choose Files</button>
        <button class="btn" onclick="uploadFiles()">Upload</button>
    </div>
    
    <div class="file-list">
"""
        
        for file in files:
            size = self.format_file_size(file['size'])
            modified = time.strftime('%Y-%m-%d %H:%M', time.localtime(file['modified']))
            
            html += f"""
        <div class="file-item">
            <div class="file-name">{file['name']}</div>
            <div class="file-size">{size} - {modified}</div>
            <div class="file-actions">
                <a href="/download/{file['name']}" class="btn">Download</a>
                <button class="btn btn-danger" onclick="deleteFile('{file['name']}')">Delete</button>
            </div>
        </div>
"""
        
        html += """
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
            });
        }
        
        function deleteFile(filename) {
            if (confirm('Are you sure you want to delete ' + filename + '?')) {
                // For now, just reload - in a real implementation, you'd call a delete API
                alert('Delete functionality would be implemented here');
            }
        }
    </script>
</body>
</html>
"""
        return html
    
    def generate_upload_page_html(self):
        """Generate HTML for upload page"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Files</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .upload-area { 
            border: 2px dashed #555; 
            padding: 40px; 
            text-align: center; 
            margin: 20px;
            border-radius: 10px;
            background: #2a2a2a;
        }
        .btn { 
            background: #007acc; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 4px; 
            cursor: pointer; 
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="upload-area">
        <h2>Upload Files</h2>
        <input type="file" id="fileInput" multiple>
        <br>
        <button class="btn" onclick="uploadFiles()">Upload Files</button>
        <a href="/" class="btn">Back to File Browser</a>
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
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    alert('Upload successful!');
                    window.location.href = '/';
                } else {
                    alert('Upload failed');
                }
            });
        }
    </script>
</body>
</html>
"""
    
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

class WebServerApp:
    """Main application class with tkinter GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Futuristic Web Server")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Server variables
        self.server = None
        self.server_thread = None
        self.port = tk.StringVar(value="8080")
        self.directory = tk.StringVar(value=str(Path.home()))
        self.is_running = False
        
        # Create GUI
        self.create_gui()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_gui(self):
        """Create the main GUI"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🚀 Futuristic Web Server", 
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1a1a1a"
        )
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Server configuration
        config_frame = tk.LabelFrame(
            main_frame, 
            text="Server Configuration", 
            fg="white", 
            bg="#2a2a2a",
            font=("Arial", 12, "bold")
        )
        config_frame.pack(fill=tk.X, pady=10)
        
        # Port configuration
        port_frame = tk.Frame(config_frame, bg="#2a2a2a")
        port_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(port_frame, text="Port:", fg="white", bg="#2a2a2a").pack(side=tk.LEFT)
        port_entry = tk.Entry(port_frame, textvariable=self.port, width=10)
        port_entry.pack(side=tk.LEFT, padx=10)
        
        # Directory configuration
        dir_frame = tk.Frame(config_frame, bg="#2a2a2a")
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(dir_frame, text="Directory:", fg="white", bg="#2a2a2a").pack(side=tk.LEFT)
        dir_entry = tk.Entry(dir_frame, textvariable=self.directory, width=50)
        dir_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(
            dir_frame, 
            text="Browse", 
            command=self.browse_directory,
            bg="#007acc",
            fg="white",
            relief=tk.FLAT
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg="#1a1a1a")
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = tk.Button(
            button_frame,
            text="Start Server",
            command=self.start_server,
            bg="#28a745",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="Stop Server",
            command=self.stop_server,
            bg="#dc3545",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_btn = tk.Button(
            button_frame,
            text="Open in Browser",
            command=self.open_browser,
            bg="#17a2b8",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        status_frame = tk.Frame(main_frame, bg="#1a1a1a")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: Stopped",
            fg="#dc3545",
            bg="#1a1a1a",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Log area
        log_frame = tk.LabelFrame(
            main_frame,
            text="Server Logs",
            fg="white",
            bg="#2a2a2a",
            font=("Arial", 12, "bold")
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            bg="#1a1a1a",
            fg="white",
            font=("Consolas", 10),
            insertbackground="white"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File list
        file_frame = tk.LabelFrame(
            main_frame,
            text="Files in Directory",
            fg="white",
            bg="#2a2a2a",
            font=("Arial", 12, "bold")
        )
        file_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for files
        columns = ("Name", "Size", "Modified")
        self.file_tree = ttk.Treeview(file_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=200)
        
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh button
        refresh_btn = tk.Button(
            file_frame,
            text="Refresh File List",
            command=self.refresh_file_list,
            bg="#6c757d",
            fg="white",
            relief=tk.FLAT
        )
        refresh_btn.pack(pady=5)
        
        # Load initial file list
        self.refresh_file_list()
    
    def browse_directory(self):
        """Browse for directory"""
        directory = filedialog.askdirectory(initialdir=self.directory.get())
        if directory:
            self.directory.set(directory)
            self.refresh_file_list()
    
    def start_server(self):
        """Start the web server"""
        try:
            port = int(self.port.get())
            directory = self.directory.get()
            
            if not os.path.exists(directory):
                messagebox.showerror("Error", "Directory does not exist!")
                return
            
            # Create custom handler class with server instance
            class CustomHandler(WebServerHandler):
                def __init__(self, *args, **kwargs):
                    kwargs['server_instance'] = self
                    super().__init__(*args, **kwargs)
            
            # Start server in a separate thread
            def run_server():
                with socketserver.TCPServer(("", port), CustomHandler) as httpd:
                    httpd.directory = directory
                    self.server = httpd
                    self.log_message(f"Server started on port {port}")
                    self.log_message(f"Serving directory: {directory}")
                    self.log_message(f"Access at: http://localhost:{port}")
                    httpd.serve_forever()
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.open_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Running", fg="#28a745")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid port number!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
            self.server = None
        
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", fg="#dc3545")
        self.log_message("Server stopped")
    
    def open_browser(self):
        """Open the web server in browser"""
        if self.is_running:
            webbrowser.open(f"http://localhost:{self.port.get()}")
        else:
            messagebox.showwarning("Warning", "Server is not running!")
    
    def refresh_file_list(self):
        """Refresh the file list"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Add files
        directory = self.directory.get()
        if os.path.exists(directory):
            try:
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        stat = os.stat(item_path)
                        size = self.format_file_size(stat.st_size)
                        modified = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
                        self.file_tree.insert("", "end", values=(item, size, modified))
            except Exception as e:
                self.log_message(f"Error reading directory: {str(e)}")
    
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def on_file_uploaded(self, filename):
        """Called when a file is uploaded"""
        self.log_message(f"File uploaded: {filename}")
        self.refresh_file_list()
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_running:
            self.stop_server()
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = WebServerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()