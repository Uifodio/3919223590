#!/usr/bin/env python3
"""
Modern Server Administrator - Web Version
A professional web-based server management tool with modern UI
"""

import os
import json
import subprocess
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
import mimetypes
import shutil
import queue
import psutil
import platform

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import socket

app = Flask(__name__)
app.secret_key = 'modern_server_admin_2024'

# Global variables
servers = {}
server_processes = {}
log_queues = {}
current_folder = None

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'php', 'html', 'css', 'js', 'json', 'xml'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(filepath):
    """Get human readable file size"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def is_port_in_use(port):
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_server_process(name, folder, port, server_type):
    """Start a server process"""
    try:
        if server_type == "HTTP":
            process = subprocess.Popen([
                'python3', '-m', 'http.server', str(port)
            ], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif server_type == "PHP":
            process = subprocess.Popen([
                'php', '-S', f'localhost:{port}', '-t', folder
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            process = subprocess.Popen([
                'python3', '-m', 'http.server', str(port)
            ], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        server_processes[name] = process
        log_queues[name] = queue.Queue()
        
        # Start log monitoring thread
        log_thread = threading.Thread(target=monitor_server_logs, args=(name, process))
        log_thread.daemon = True
        log_thread.start()
        
        return True
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

def monitor_server_logs(name, process):
    """Monitor server logs in a separate thread"""
    while process.poll() is None:
        try:
            output = process.stdout.readline()
            if output:
                log_queues[name].put({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': output.strip(),
                    'type': 'info'
                })
        except:
            break

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', servers=servers, current_folder=current_folder)

@app.route('/api/add_server', methods=['POST'])
def add_server():
    """Add a new server"""
    data = request.get_json()
    folder = data.get('folder')
    port = int(data.get('port', 8000))
    server_type = data.get('type', 'HTTP')
    
    if not folder or not os.path.exists(folder):
        return jsonify({'success': False, 'message': 'Invalid folder path'})
    
    if is_port_in_use(port):
        return jsonify({'success': False, 'message': f'Port {port} is already in use'})
    
    # Generate server name
    server_name = f"Server-{port}"
    counter = 1
    while server_name in servers:
        server_name = f"Server-{port}-{counter}"
        counter += 1
    
    if start_server_process(server_name, folder, port, server_type):
        servers[server_name] = {
            'name': server_name,
            'folder': folder,
            'port': port,
            'type': server_type,
            'status': 'Running',
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify({'success': True, 'message': f'Server {server_name} started successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to start server'})

@app.route('/api/stop_server', methods=['POST'])
def stop_server():
    """Stop a server"""
    data = request.get_json()
    server_name = data.get('name')
    
    if server_name in server_processes:
        try:
            server_processes[server_name].terminate()
            server_processes[server_name].wait(timeout=5)
        except:
            server_processes[server_name].kill()
        
        del server_processes[server_name]
        if server_name in log_queues:
            del log_queues[server_name]
        
        if server_name in servers:
            servers[server_name]['status'] = 'Stopped'
        
        return jsonify({'success': True, 'message': f'Server {server_name} stopped'})
    
    return jsonify({'success': False, 'message': 'Server not found'})

@app.route('/api/server_logs/<server_name>')
def get_server_logs(server_name):
    """Get server logs"""
    if server_name not in log_queues:
        return jsonify({'logs': []})
    
    logs = []
    try:
        while not log_queues[server_name].empty():
            logs.append(log_queues[server_name].get_nowait())
    except:
        pass
    
    return jsonify({'logs': logs})

@app.route('/api/files')
def get_files():
    """Get files in current folder"""
    if not current_folder or not os.path.exists(current_folder):
        return jsonify({'files': []})
    
    files = []
    try:
        for filename in os.listdir(current_folder):
            file_path = os.path.join(current_folder, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                file_type = mimetypes.guess_type(filename)[0] or "Unknown"
                
                files.append({
                    'name': filename,
                    'size': get_file_size(file_path),
                    'type': file_type,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'path': file_path
                })
    except Exception as e:
        print(f"Error getting files: {e}")
    
    return jsonify({'files': files})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if current_folder:
            file_path = os.path.join(current_folder, filename)
        else:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(file_path)
        return jsonify({'success': True, 'message': f'File {filename} uploaded successfully'})
    
    return jsonify({'success': False, 'message': 'Invalid file type'})

@app.route('/api/delete_file', methods=['POST'])
def delete_file():
    """Delete a file"""
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'success': False, 'message': 'No filename provided'})
    
    if current_folder:
        file_path = os.path.join(current_folder, filename)
    else:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True, 'message': f'File {filename} deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting file: {e}'})

@app.route('/api/set_folder', methods=['POST'])
def set_folder():
    """Set current folder"""
    global current_folder
    data = request.get_json()
    folder = data.get('folder')
    
    if folder and os.path.exists(folder):
        current_folder = folder
        return jsonify({'success': True, 'message': f'Folder set to {folder}'})
    else:
        return jsonify({'success': False, 'message': 'Invalid folder path'})

@app.route('/api/system_info')
def get_system_info():
    """Get system information"""
    info = {
        'os': f"{platform.system()} {platform.release()}",
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'cpu_cores': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total // (1024**3),
        'memory_available': psutil.virtual_memory().available // (1024**3),
        'disk_free': psutil.disk_usage('/').free // (1024**3),
        'active_servers': len([s for s in servers.values() if s['status'] == 'Running'])
    }
    return jsonify(info)

@app.route('/api/open_browser/<server_name>')
def open_browser(server_name):
    """Open server in browser"""
    if server_name in servers:
        port = servers[server_name]['port']
        webbrowser.open(f'http://localhost:{port}')
        return jsonify({'success': True, 'message': f'Opening http://localhost:{port}'})
    return jsonify({'success': False, 'message': 'Server not found'})

if __name__ == '__main__':
    print("🚀 Modern Server Administrator - Web Version")
    print("=" * 50)
    print("Starting web interface...")
    print("The application will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the application")
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)