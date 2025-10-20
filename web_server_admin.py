#!/usr/bin/env python3
"""
Modern Server Administrator - Professional Web Server Management
A sleek, professional server management tool with full PHP support
"""

import os
import json
import subprocess
import threading
import time
import webbrowser
from datetime import datetime
import psutil
import platform
import shutil
import queue
import signal
import sys

from flask import Flask, render_template, request, jsonify, redirect, url_for
import socket

app = Flask(__name__)
app.secret_key = 'modern_server_admin_2024'

# Global variables
servers = {}
server_processes = {}
log_queues = {}

def is_port_in_use(port):
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_php_available():
    """Check if PHP is available on the system"""
    try:
        result = subprocess.run(['php', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def start_server_process(name, folder, port, server_type):
    """Start a server process with proper PHP support"""
    try:
        if server_type == "PHP":
            if not check_php_available():
                return False, "PHP is not installed or not in PATH"
            
            # Use PHP built-in server with proper configuration
            process = subprocess.Popen([
                'php', '-S', f'localhost:{port}', '-t', folder,
                '-d', 'display_errors=1',
                '-d', 'log_errors=1',
                '-d', 'error_log=php_errors.log'
            ], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        elif server_type == "HTTP":
            # Use Python's built-in HTTP server
            process = subprocess.Popen([
                'python3', '-m', 'http.server', str(port)
            ], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        elif server_type == "Node.js":
            # Check if Node.js is available
            try:
                subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            except:
                return False, "Node.js is not installed or not in PATH"
            
            # Use Node.js HTTP server
            process = subprocess.Popen([
                'node', '-e', f'''
                const http = require("http");
                const fs = require("fs");
                const path = require("path");
                const { exec } = require("child_process");
                
                const server = http.createServer((req, res) => {{
                    let filePath = path.join("{folder}", req.url === "/" ? "index.html" : req.url);
                    
                    fs.readFile(filePath, (err, data) => {{
                        if (err) {{
                            res.writeHead(404);
                            res.end("File not found");
                        }} else {{
                            res.writeHead(200);
                            res.end(data);
                        }}
                    }});
                }});
                
                server.listen({port}, () => {{
                    console.log("Node.js server running on port {port}");
                }});
                '''
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        else:
            return False, "Unsupported server type"
        
        server_processes[name] = process
        log_queues[name] = queue.Queue()
        
        # Start log monitoring thread
        log_thread = threading.Thread(target=monitor_server_logs, args=(name, process))
        log_thread.daemon = True
        log_thread.start()
        
        return True, "Server started successfully"
        
    except Exception as e:
        return False, f"Error starting server: {str(e)}"

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
            
            # Also capture stderr for PHP errors
            error_output = process.stderr.readline()
            if error_output:
                log_queues[name].put({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': error_output.strip(),
                    'type': 'error'
                })
        except:
            break

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', servers=servers)

@app.route('/api/add_server', methods=['POST'])
def add_server():
    """Add a new server"""
    data = request.get_json()
    folder = data.get('folder')
    port = int(data.get('port', 8000))
    server_type = data.get('type', 'PHP')
    
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
    
    success, message = start_server_process(server_name, folder, port, server_type)
    
    if success:
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
        return jsonify({'success': False, 'message': message})

@app.route('/api/stop_server', methods=['POST'])
def stop_server():
    """Stop a server"""
    data = request.get_json()
    server_name = data.get('name')
    
    if server_name in server_processes:
        try:
            # Gracefully terminate the process
            server_processes[server_name].terminate()
            
            # Wait for graceful shutdown
            try:
                server_processes[server_name].wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't stop gracefully
                server_processes[server_name].kill()
                server_processes[server_name].wait()
        except:
            pass
        
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

@app.route('/api/servers')
def get_servers():
    """Get all servers"""
    return jsonify(servers)

@app.route('/api/system_info')
def get_system_info():
    """Get system information"""
    php_available = check_php_available()
    
    info = {
        'os': f"{platform.system()} {platform.release()}",
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'cpu_cores': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total // (1024**3),
        'memory_available': psutil.virtual_memory().available // (1024**3),
        'disk_free': psutil.disk_usage('/').free // (1024**3),
        'active_servers': len([s for s in servers.values() if s['status'] == 'Running']),
        'php_available': php_available,
        'php_version': get_php_version() if php_available else None
    }
    return jsonify(info)

def get_php_version():
    """Get PHP version"""
    try:
        result = subprocess.run(['php', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.split('\n')[0]
    except:
        pass
    return "Unknown"

@app.route('/api/open_browser/<server_name>')
def open_browser(server_name):
    """Open server in browser"""
    if server_name in servers:
        port = servers[server_name]['port']
        webbrowser.open(f'http://localhost:{port}')
        return jsonify({'success': True, 'message': f'Opening http://localhost:{port}'})
    return jsonify({'success': False, 'message': 'Server not found'})

@app.route('/api/check_php')
def check_php():
    """Check PHP availability"""
    available = check_php_available()
    version = get_php_version() if available else None
    return jsonify({'available': available, 'version': version})

if __name__ == '__main__':
    print("🚀 Modern Server Administrator - Professional Edition")
    print("=" * 60)
    print("Starting professional web interface...")
    print("The application will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the application")
    
    # Check PHP availability
    if check_php_available():
        print("✓ PHP detected and ready")
    else:
        print("⚠️  PHP not detected - PHP servers will not work")
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)