#!/usr/bin/env python3
"""
Unified Server Administrator - Windows Compatible
=================================================

A simplified version that works on Windows without external dependencies.
"""

import os
import sys
import json
import time
import socket
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

# Configuration
class Config:
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    SITES_DIR = Path('sites')
    LOGS_DIR = Path('logs')
    UPLOADS_DIR = Path('uploads')
    SERVERS_FILE = 'servers.json'
    
    # Create directories
    SITES_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Global variables
servers = {}
background_monitor = None
monitor_running = False

def load_servers():
    """Load servers from JSON file"""
    global servers
    try:
        if os.path.exists(Config.SERVERS_FILE):
            with open(Config.SERVERS_FILE, 'r') as f:
                servers = json.load(f)
        else:
            servers = {}
    except Exception as e:
        print(f"Error loading servers: {e}")
        servers = {}

def save_servers():
    """Save servers to JSON file"""
    try:
        with open(Config.SERVERS_FILE, 'w') as f:
            json.dump(servers, f, indent=2)
    except Exception as e:
        print(f"Error saving servers: {e}")

def is_port_available(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def get_available_port(start_port=8000):
    """Find an available port starting from start_port"""
    port = start_port
    while port < 65535:
        if is_port_available(port):
            return port
        port += 1
    return None

def start_static_server(name, port, site_path):
    """Start a static file server (simplified)"""
    try:
        # For Windows, we'll use Python's built-in HTTP server
        cmd = [sys.executable, '-m', 'http.server', str(port)]
        process = subprocess.Popen(
            cmd,
            cwd=site_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        return True, f"Static server started on port {port}"
    except Exception as e:
        return False, f"Failed to start static server: {e}"

def start_php_server(name, port, site_path):
    """Start a PHP server (simplified)"""
    try:
        # Use PHP's built-in server
        php_exe = os.path.join('php', 'php.exe') if os.name == 'nt' else 'php'
        cmd = [php_exe, '-S', f'localhost:{port}', '-t', site_path]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        return True, f"PHP server started on port {port}"
    except Exception as e:
        return False, f"Failed to start PHP server: {e}"

def start_nodejs_server(name, port, site_path):
    """Start a Node.js server (simplified)"""
    try:
        # Look for package.json and start with npm/node
        package_json = os.path.join(site_path, 'package.json')
        if os.path.exists(package_json):
            cmd = ['npm', 'start']
        else:
            # Look for main JS file
            main_files = ['app.js', 'server.js', 'index.js', 'main.js']
            main_file = None
            for file in main_files:
                if os.path.exists(os.path.join(site_path, file)):
                    main_file = file
                    break
            
            if main_file:
                cmd = ['node', main_file]
            else:
                return False, "No package.json or main JS file found"
        
        process = subprocess.Popen(
            cmd,
            cwd=site_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        return True, f"Node.js server started on port {port}"
    except Exception as e:
        return False, f"Failed to start Node.js server: {e}"

def background_monitor_worker():
    """Background worker to monitor servers"""
    global monitor_running
    monitor_running = True
    
    while monitor_running:
        try:
            # Update server status
            for name, server in servers.items():
                if server.get('status') == 'running':
                    # Check if process is still running (simplified check)
                    port = server.get('port')
                    if port and not is_port_available(port):
                        server['status'] = 'running'
                    else:
                        server['status'] = 'stopped'
            
            time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(10)

# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/servers')
def api_servers():
    """Get all servers"""
    return jsonify(servers)

@app.route('/api/add_server', methods=['POST'])
def api_add_server():
    """Add a new server"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        server_type = data.get('type', 'static')
        port = int(data.get('port', 8000))
        site_path = data.get('site_path', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Server name is required'})
        
        if not site_path or not os.path.exists(site_path):
            return jsonify({'success': False, 'error': 'Valid site path is required'})
        
        if name in servers:
            return jsonify({'success': False, 'error': 'Server name already exists'})
        
        # Find available port if specified port is taken
        if not is_port_available(port):
            port = get_available_port(port)
            if not port:
                return jsonify({'success': False, 'error': 'No available ports found'})
        
        # Start server based on type
        success = False
        message = ""
        
        if server_type == 'static':
            success, message = start_static_server(name, port, site_path)
        elif server_type == 'php':
            success, message = start_php_server(name, port, site_path)
        elif server_type == 'nodejs':
            success, message = start_nodejs_server(name, port, site_path)
        else:
            return jsonify({'success': False, 'error': 'Invalid server type'})
        
        if success:
            servers[name] = {
                'name': name,
                'type': server_type,
                'port': port,
                'site_path': site_path,
                'status': 'running',
                'created_at': datetime.now().isoformat(),
                'url': f'http://localhost:{port}'
            }
            save_servers()
            return jsonify({'success': True, 'message': message, 'server': servers[name]})
        else:
            return jsonify({'success': False, 'error': message})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_server', methods=['POST'])
def api_delete_server():
    """Delete a server"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if name not in servers:
            return jsonify({'success': False, 'error': 'Server not found'})
        
        # Stop server (simplified - just remove from list)
        del servers[name]
        save_servers()
        
        return jsonify({'success': True, 'message': f'Server {name} deleted'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/server_logs/<server_name>')
def api_server_logs(server_name):
    """Get server logs"""
    try:
        if server_name not in servers:
            return jsonify({'error': 'Server not found'})
        
        # Simplified logs - just return basic info
        server = servers[server_name]
        logs = [
            f"[{datetime.now().strftime('%H:%M:%S')}] Server: {server['name']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] Type: {server['type']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] Port: {server['port']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] Status: {server['status']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] URL: {server['url']}"
        ]
        
        return jsonify({'logs': logs})
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/system_info')
def api_system_info():
    """Get system information"""
    try:
        info = {
            'platform': os.name,
            'python_version': sys.version,
            'servers_count': len(servers),
            'running_servers': len([s for s in servers.values() if s.get('status') == 'running']),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)})

# Start background monitor
def start_background_monitor():
    global background_monitor
    if background_monitor is None or not background_monitor.is_alive():
        background_monitor = threading.Thread(target=background_monitor_worker, daemon=True)
        background_monitor.start()
        print("Background monitor started")

if __name__ == '__main__':
    print("🚀 Starting Unified Server Administrator (Windows Compatible)...")
    print("=" * 60)
    
    # Load existing servers
    load_servers()
    
    # Start background monitor
    start_background_monitor()
    
    print("✅ System ready")
    print(f"🌐 Web interface: http://localhost:{Config.PORT}")
    print("=" * 60)
    
    # Run Flask app
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)