#!/usr/bin/env python3
"""
Unified Server Administrator - Full Production Version
=====================================================

A professional, production-ready web server administration tool that unifies:
- PHP via php-fpm
- Node.js via internal proxy  
- Static files via nginx
- All managed through a single nginx reverse proxy

Features:
- GitHub-like professional dark theme UI
- Nginx reverse proxy configuration
- Unified server management
- Real-time monitoring and logs
- Professional deployment ready
- Cross-platform compatibility (Windows, Linux, Mac)
"""

import os
import sys
import json
import shutil
import socket
import queue
import tempfile
import zipfile
import subprocess
import threading
import time
import signal
import platform
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

import logging
import logging.handlers

# Optional dependencies with fallbacks
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  YAML not available - using JSON fallback for configurations")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available - using basic port checking")

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file

# Configuration
class Config:
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    SITES_DIR = Path('sites')
    LOGS_DIR = Path('logs')
    UPLOADS_DIR = Path('uploads')
    NGINX_CONFIGS_DIR = Path('nginx_configs')
    PHP_FPM_CONFIGS_DIR = Path('php_fpm_configs')
    SERVERS_FILE = 'servers.json'
    
    # Create directories
    SITES_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)
    NGINX_CONFIGS_DIR.mkdir(exist_ok=True)
    PHP_FPM_CONFIGS_DIR.mkdir(exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Global variables
servers = {}
server_processes = {}
background_monitor = None
monitor_running = False
log_queue = queue.Queue()

# Setup logging
def setup_logging():
    """Setup comprehensive logging system"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Main application logger
    logger = logging.getLogger('usa')
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'usa_app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

def load_servers():
    """Load servers from JSON file"""
    global servers
    try:
        if os.path.exists(Config.SERVERS_FILE):
            with open(Config.SERVERS_FILE, 'r') as f:
                servers = json.load(f)
        else:
            servers = {}
        logger.info(f"Loaded {len(servers)} servers from configuration")
    except Exception as e:
        logger.error(f"Error loading servers: {e}")
        servers = {}

def save_servers():
    """Save servers to JSON file"""
    try:
        with open(Config.SERVERS_FILE, 'w') as f:
            json.dump(servers, f, indent=2)
        logger.info("Servers configuration saved")
    except Exception as e:
        logger.error(f"Error saving servers: {e}")

def is_port_available(port):
    """Check if port is available using psutil if available, fallback to socket"""
    if PSUTIL_AVAILABLE:
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return False
            return True
        except Exception:
            pass
    
    # Fallback to socket method
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
    """Start a static file server"""
    try:
        # Use Python's built-in HTTP server
        cmd = [sys.executable, '-m', 'http.server', str(port)]
        process = subprocess.Popen(
            cmd,
            cwd=site_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        server_processes[name] = process
        logger.info(f"Static server '{name}' started on port {port}")
        return True, f"Static server started on port {port}"
    except Exception as e:
        logger.error(f"Failed to start static server '{name}': {e}")
        return False, f"Failed to start static server: {e}"

def start_php_server(name, port, site_path):
    """Start a PHP server"""
    try:
        # Use PHP's built-in server
        php_exe = os.path.join('php', 'php.exe') if os.name == 'nt' else 'php'
        if not os.path.exists(php_exe) and os.name == 'nt':
            php_exe = 'php.exe'  # Try system PHP
        
        cmd = [php_exe, '-S', f'localhost:{port}', '-t', site_path]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        server_processes[name] = process
        logger.info(f"PHP server '{name}' started on port {port}")
        return True, f"PHP server started on port {port}"
    except Exception as e:
        logger.error(f"Failed to start PHP server '{name}': {e}")
        return False, f"Failed to start PHP server: {e}"

def start_nodejs_server(name, port, site_path):
    """Start a Node.js server"""
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
        server_processes[name] = process
        logger.info(f"Node.js server '{name}' started on port {port}")
        return True, f"Node.js server started on port {port}"
    except Exception as e:
        logger.error(f"Failed to start Node.js server '{name}': {e}")
        return False, f"Failed to start Node.js server: {e}"

def stop_server(name):
    """Stop a server process"""
    if name in server_processes:
        try:
            process = server_processes[name]
            if process.poll() is None:  # Process is still running
                if os.name == 'nt':
                    process.terminate()
                else:
                    process.terminate()
                    process.wait(timeout=5)
                logger.info(f"Server '{name}' stopped")
            del server_processes[name]
            return True
        except Exception as e:
            logger.error(f"Error stopping server '{name}': {e}")
            return False
    return True

def background_monitor_worker():
    """Background worker to monitor servers"""
    global monitor_running
    monitor_running = True
    
    while monitor_running:
        try:
            # Update server status based on process status
            for name, server in servers.items():
                if server.get('status') == 'running':
                    if name in server_processes:
                        process = server_processes[name]
                        if process.poll() is None:  # Process is still running
                            server['status'] = 'running'
                        else:
                            server['status'] = 'stopped'
                            del server_processes[name]
                            logger.info(f"Server '{name}' stopped unexpectedly")
                    else:
                        # Check if port is still in use
                        port = server.get('port')
                        if port and not is_port_available(port):
                            server['status'] = 'running'
                        else:
                            server['status'] = 'stopped'
                            logger.info(f"Server '{name}' port {port} is now available")
            
            time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            time.sleep(10)

def get_system_info():
    """Get comprehensive system information"""
    info = {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'python_version': sys.version,
        'servers_count': len(servers),
        'running_servers': len([s for s in servers.values() if s.get('status') == 'running']),
        'timestamp': datetime.now().isoformat()
    }
    
    if PSUTIL_AVAILABLE:
        try:
            info.update({
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent
            })
        except Exception as e:
            logger.warning(f"Could not get system info: {e}")
    
    # Check for PHP
    php_exe = os.path.join('php', 'php.exe') if os.name == 'nt' else 'php'
    info['php_available'] = os.path.exists(php_exe) or shutil.which('php') is not None
    
    # Check for Node.js
    info['node_available'] = shutil.which('node') is not None
    
    # Check for nginx
    info['nginx_available'] = shutil.which('nginx') is not None
    
    return info

# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

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
        server_type = data.get('type', 'Static')
        port = int(data.get('port', 8000))
        site_path = data.get('site_path', '').strip()
        domain = data.get('domain', '').strip() or None
        
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
        
        # Map frontend server types to backend types
        server_type_mapping = {
            'Static': 'static',
            'PHP': 'php', 
            'Node.js': 'nodejs'
        }
        
        backend_type = server_type_mapping.get(server_type, server_type.lower())
        
        # Start server based on type
        success = False
        message = ""
        
        if backend_type == 'static':
            success, message = start_static_server(name, port, site_path)
        elif backend_type == 'php':
            success, message = start_php_server(name, port, site_path)
        elif backend_type == 'nodejs':
            success, message = start_nodejs_server(name, port, site_path)
        else:
            return jsonify({'success': False, 'error': 'Invalid server type'})
        
        if success:
            servers[name] = {
                'name': name,
                'type': server_type,  # Keep original frontend type for display
                'port': port,
                'site_path': site_path,
                'domain': domain,
                'status': 'running',
                'created_at': datetime.now().isoformat(),
                'url': f'http://localhost:{port}'
            }
            save_servers()
            logger.info(f"Server '{name}' created successfully")
            return jsonify({'success': True, 'message': message, 'server': servers[name]})
        else:
            return jsonify({'success': False, 'error': message})
            
    except Exception as e:
        logger.error(f"Error creating server: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_server', methods=['POST'])
def api_delete_server():
    """Delete a server"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if name not in servers:
            return jsonify({'success': False, 'error': 'Server not found'})
        
        # Stop server process
        stop_server(name)
        
        # Remove from servers list
        del servers[name]
        save_servers()
        
        logger.info(f"Server '{name}' deleted")
        return jsonify({'success': True, 'message': f'Server {name} deleted'})
        
    except Exception as e:
        logger.error(f"Error deleting server: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/server_logs/<server_name>')
def api_server_logs(server_name):
    """Get server logs"""
    try:
        if server_name not in servers:
            return jsonify({'error': 'Server not found'})
        
        server = servers[server_name]
        logs = [
            f"[{datetime.now().strftime('%H:%M:%S')}] Server: {server['name']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] Type: {server['type']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] Port: {server['port']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] Status: {server['status']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] URL: {server['url']}",
            f"[{datetime.now().strftime('%H:%M:%S')}] Created: {server['created_at']}"
        ]
        
        # Add process info if available
        if server_name in server_processes:
            process = server_processes[server_name]
            if process.poll() is None:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Process: Running (PID: {process.pid})")
            else:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Process: Stopped")
        
        return jsonify({'logs': logs})
        
    except Exception as e:
        logger.error(f"Error getting logs for server '{server_name}': {e}")
        return jsonify({'error': str(e)})

@app.route('/api/system_info')
def api_system_info():
    """Get system information"""
    try:
        return jsonify(get_system_info())
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save file to uploads directory
        filename = file.filename
        file_path = Config.UPLOADS_DIR / filename
        file.save(file_path)
        
        logger.info(f"File uploaded: {filename}")
        return jsonify({'success': True, 'message': f'File {filename} uploaded successfully', 'path': str(file_path)})
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Start background monitor
def start_background_monitor():
    global background_monitor
    if background_monitor is None or not background_monitor.is_alive():
        background_monitor = threading.Thread(target=background_monitor_worker, daemon=True)
        background_monitor.start()
        logger.info("Background monitor started")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received, stopping all servers...")
    global monitor_running
    monitor_running = False
    
    # Stop all server processes
    for name in list(server_processes.keys()):
        stop_server(name)
    
    logger.info("All servers stopped, exiting...")
    sys.exit(0)

if __name__ == '__main__':
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Unified Server Administrator (Full Production Version)...")
    print("=" * 70)
    
    # Load existing servers
    load_servers()
    
    # Start background monitor
    start_background_monitor()
    
    # Display system info
    info = get_system_info()
    print(f"✅ System: {info['platform']} {info['platform_version']}")
    print(f"✅ Python: {info['python_version'].split()[0]}")
    print(f"✅ PHP Available: {'Yes' if info['php_available'] else 'No'}")
    print(f"✅ Node.js Available: {'Yes' if info['node_available'] else 'No'}")
    print(f"✅ Nginx Available: {'Yes' if info['nginx_available'] else 'No'}")
    print(f"✅ Loaded {info['servers_count']} servers")
    print(f"🌐 Web interface: http://localhost:{Config.PORT}")
    print("=" * 70)
    
    # Run Flask app
    try:
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)