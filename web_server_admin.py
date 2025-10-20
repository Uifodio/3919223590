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
import socket
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
app.secret_key = 'modern_server_admin_2024'

# Global variables
servers = {}
server_processes = {}
log_queues = {}

def is_port_in_use(port):
    """Check if port is already in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False

def check_php_available():
    """Check if PHP is available on the system"""
    try:
        result = subprocess.run(['php', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_node_available():
    """Check if Node.js is available on the system"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def start_server_process(name, folder, port, server_type):
    """Start a server process with proper support for all types"""
    try:
        if server_type == "PHP":
            if not check_php_available():
                return False, "PHP is not installed or not in PATH. Please install PHP to use PHP servers."
            
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
            if not check_node_available():
                return False, "Node.js is not installed or not in PATH. Please install Node.js to use Node.js servers."
            
            # Create a simple Node.js server script
            node_script = f"""
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const server = http.createServer((req, res) => {{
    const parsedUrl = url.parse(req.url);
    let pathname = parsedUrl.pathname;
    
    if (pathname === '/') {{
        pathname = '/index.html';
    }}
    
    const filePath = path.join('{folder}', pathname);
    
    fs.readFile(filePath, (err, data) => {{
        if (err) {{
            res.writeHead(404, {{'Content-Type': 'text/html'}});
            res.end(`
                <html>
                    <head><title>404 Not Found</title></head>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h1>404 - File Not Found</h1>
                        <p>The requested file was not found on this server.</p>
                    </body>
                </html>
            `);
        }} else {{
            const ext = path.extname(filePath);
            const mimeTypes = {{
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.json': 'application/json',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml'
            }};
            
            const contentType = mimeTypes[ext] || 'text/plain';
            res.writeHead(200, {{'Content-Type': contentType}});
            res.end(data);
        }}
    }});
}});

server.listen({port}, 'localhost', () => {{
    console.log(`Node.js server running on http://localhost:{port}`);
}});
"""
            
            # Write the Node.js script to a temporary file
            script_path = os.path.join(folder, 'temp_server.js')
            with open(script_path, 'w') as f:
                f.write(node_script)
            
            process = subprocess.Popen([
                'node', script_path
            ], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
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
            
            # Also capture stderr for errors
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
    try:
        data = request.get_json()
        folder = data.get('folder', '').strip()
        port = data.get('port', 8000)
        server_type = data.get('type', 'HTTP')
        
        if not folder:
            return jsonify({'success': False, 'message': 'Please select a website folder'})
        
        if not os.path.exists(folder):
            return jsonify({'success': False, 'message': 'Selected folder does not exist'})
        
        try:
            port = int(port)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Port must be a valid number'})
        
        if port < 1000 or port > 65535:
            return jsonify({'success': False, 'message': 'Port must be between 1000 and 65535'})
        
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
            return jsonify({'success': True, 'message': f'Server {server_name} started successfully on port {port}'})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding server: {str(e)}'})

@app.route('/api/stop_server', methods=['POST'])
def stop_server():
    """Stop a server"""
    try:
        data = request.get_json()
        server_name = data.get('name')
        
        if not server_name or server_name not in server_processes:
            return jsonify({'success': False, 'message': 'Server not found'})
        
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
        
        # Clean up
        del server_processes[server_name]
        if server_name in log_queues:
            del log_queues[server_name]
        
        if server_name in servers:
            servers[server_name]['status'] = 'Stopped'
        
        return jsonify({'success': True, 'message': f'Server {server_name} stopped successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping server: {str(e)}'})

@app.route('/api/server_logs/<server_name>')
def get_server_logs(server_name):
    """Get server logs"""
    try:
        if server_name not in log_queues:
            return jsonify({'logs': []})
        
        logs = []
        try:
            while not log_queues[server_name].empty():
                logs.append(log_queues[server_name].get_nowait())
        except:
            pass
        
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'logs': [], 'error': str(e)})

@app.route('/api/servers')
def get_servers():
    """Get all servers"""
    return jsonify(servers)

@app.route('/api/system_info')
def get_system_info():
    """Get system information"""
    try:
        php_available = check_php_available()
        node_available = check_node_available()
        
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
            'php_version': get_php_version() if php_available else None,
            'node_available': node_available,
            'node_version': get_node_version() if node_available else None
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)})

def get_php_version():
    """Get PHP version"""
    try:
        result = subprocess.run(['php', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.split('\n')[0]
    except:
        pass
    return "Unknown"

def get_node_version():
    """Get Node.js version"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "Unknown"

@app.route('/api/open_browser/<server_name>')
def open_browser(server_name):
    """Open server in browser"""
    try:
        if server_name in servers:
            port = servers[server_name]['port']
            url = f'http://localhost:{port}'
            webbrowser.open(url)
            return jsonify({'success': True, 'message': f'Opening {url}'})
        return jsonify({'success': False, 'message': 'Server not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error opening browser: {str(e)}'})

@app.route('/api/check_php')
def check_php():
    """Check PHP availability"""
    try:
        available = check_php_available()
        version = get_php_version() if available else None
        return jsonify({'available': available, 'version': version})
    except Exception as e:
        return jsonify({'available': False, 'version': None, 'error': str(e)})

@app.route('/api/check_node')
def check_node():
    """Check Node.js availability"""
    try:
        available = check_node_available()
        version = get_node_version() if available else None
        return jsonify({'available': available, 'version': version})
    except Exception as e:
        return jsonify({'available': False, 'version': None, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Modern Server Administrator - Professional Edition")
    print("=" * 60)
    print("Starting professional web interface...")
    print("The application will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the application")
    print()
    
    # Check system requirements
    print("Checking system requirements...")
    
    if check_php_available():
        print("✓ PHP detected and ready")
    else:
        print("⚠️  PHP not detected - PHP servers will not work")
    
    if check_node_available():
        print("✓ Node.js detected and ready")
    else:
        print("⚠️  Node.js not detected - Node.js servers will not work")
    
    print("✓ Python HTTP server always available")
    print()
    
    # Start the Flask application
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        for name, process in server_processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("Goodbye!")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)