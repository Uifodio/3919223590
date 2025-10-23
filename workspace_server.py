#!/usr/bin/env python3
"""
Windows-Compatible Workspace Server
A production-style local development server that can run PHP, Node.js, and static sites
simultaneously through a central Python reverse proxy.

Features:
- Central reverse proxy on localhost:8000
- Support for PHP, Node.js, and static sites
- Windows + Linux compatible
- Self-contained and production-style
- Multiple project management
- Auto-detection of PHP and Node.js
- Professional web interface
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
import logging
import platform
import webbrowser
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import mimetypes

# Optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from flask import Flask, render_template, request, jsonify, Response, send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.serving import WSGIRequestHandler

# ============================================================================
# Configuration
# ============================================================================

class Config:
    # Server settings
    PROXY_PORT = 8000
    PROXY_HOST = '0.0.0.0'
    
    # Project settings
    MAX_PROJECTS = 20
    MAX_WORKERS = 32
    LOG_TAIL_LINES = 200
    
    # Paths
    ROOT = Path.cwd()
    PROJECTS_FOLDER = ROOT / 'projects'
    LOGS_FOLDER = ROOT / 'logs'
    CONFIG_FILE = ROOT / 'workspace_config.json'
    TEMPLATES_FOLDER = ROOT / 'templates'
    STATIC_FOLDER = ROOT / 'static'
    
    # File upload settings
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico',
        'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm',
        'php', 'html', 'htm', 'css', 'js', 'json', 'xml', 'md',
        'py', 'sql', 'zip', 'rar', '7z', 'tar', 'gz'
    }
    
    # Server types
    SERVER_TYPES = ['static', 'php', 'nodejs', 'python']
    
    # Windows-specific settings
    WINDOWS_PHP_PATHS = [
        r'C:\php\php.exe',
        r'C:\xampp\php\php.exe',
        r'C:\wamp\bin\php\php.exe',
        r'C:\laragon\bin\php\php.exe',
        r'C:\Program Files\PHP\php.exe',
        r'C:\Program Files (x86)\PHP\php.exe'
    ]
    
    WINDOWS_NODE_PATHS = [
        r'C:\Program Files\nodejs\node.exe',
        r'C:\Program Files (x86)\nodejs\node.exe',
        r'C:\Users\{}\AppData\Roaming\npm\node.exe'.format(os.getenv('USERNAME', '')),
        r'C:\Users\{}\AppData\Local\Programs\nodejs\node.exe'.format(os.getenv('USERNAME', ''))
    ]

# ============================================================================
# Global State
# ============================================================================

app = Flask(__name__, 
           template_folder=str(Config.TEMPLATES_FOLDER),
           static_folder=str(Config.STATIC_FOLDER))
app.secret_key = 'workspace_server_2024'

# Global state
projects: Dict[str, Dict] = {}
project_processes: Dict[str, subprocess.Popen] = {}
log_queues: Dict[str, queue.Queue] = {}
proxy_routes: Dict[str, Dict] = {}  # route -> project info

# Threading
LOCK = threading.RLock()
EXECUTOR = ThreadPoolExecutor(max_workers=Config.MAX_WORKERS)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOGS_FOLDER / 'workspace_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('workspace_server')

# ============================================================================
# Utility Functions
# ============================================================================

def ensure_directories():
    """Create necessary directories"""
    for folder in [Config.PROJECTS_FOLDER, Config.LOGS_FOLDER, Config.TEMPLATES_FOLDER, Config.STATIC_FOLDER]:
        folder.mkdir(exist_ok=True)

def is_port_in_use(port: int, host: str = '0.0.0.0') -> bool:
    """Check if a port is in use"""
    try:
        if PSUTIL_AVAILABLE:
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port == port:
                    if host in ('0.0.0.0', '') or conn.laddr.ip == host:
                        return True
            return False
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def find_free_port(start_port: int = 8001) -> int:
    """Find a free port starting from start_port"""
    port = start_port
    while port < 65535:
        if not is_port_in_use(port):
            return port
        port += 1
    raise RuntimeError("No free ports available")

def get_php_executable() -> Optional[str]:
    """Find PHP executable"""
    if platform.system() == 'Windows':
        # Check Windows-specific paths
        for path in Config.WINDOWS_PHP_PATHS:
            if Path(path).exists():
                return path
        # Check PATH
        return shutil.which('php')
    else:
        return shutil.which('php')

def get_node_executable() -> Optional[str]:
    """Find Node.js executable"""
    if platform.system() == 'Windows':
        # Check Windows-specific paths
        for path in Config.WINDOWS_NODE_PATHS:
            if Path(path).exists():
                return path
        # Check PATH
        return shutil.which('node')
    else:
        return shutil.which('node')

def check_php_available() -> Tuple[bool, str]:
    """Check if PHP is available and get version"""
    php_exe = get_php_executable()
    if not php_exe:
        return False, "PHP not found"
    
    try:
        result = subprocess.run([php_exe, '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            return True, version
        return False, "PHP execution failed"
    except Exception as e:
        return False, f"PHP check failed: {e}"

def check_node_available() -> Tuple[bool, str]:
    """Check if Node.js is available and get version"""
    node_exe = get_node_executable()
    if not node_exe:
        return False, "Node.js not found"
    
    try:
        result = subprocess.run([node_exe, '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        return False, "Node.js execution failed"
    except Exception as e:
        return False, f"Node.js check failed: {e}"

def get_mime_type(file_path: str) -> str:
    """Get MIME type for a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def secure_filename_custom(name: str) -> str:
    """Create a secure filename"""
    return secure_filename(name) or f"project-{int(time.time())}"

# ============================================================================
# Project Management
# ============================================================================

def load_projects():
    """Load projects from config file"""
    if Config.CONFIG_FILE.exists():
        try:
            with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                projects.update(data.get('projects', {}))
                proxy_routes.update(data.get('routes', {}))
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")

def save_projects():
    """Save projects to config file"""
    try:
        data = {
            'projects': projects,
            'routes': proxy_routes,
            'last_updated': datetime.now().isoformat()
        }
        with open(Config.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save projects: {e}")

def create_project(name: str, project_type: str, source_path: str, 
                  port: Optional[int] = None, route: str = None) -> Dict:
    """Create a new project"""
    if port is None:
        port = find_free_port()
    
    if route is None:
        route = f"/{name}"
    
    project = {
        'name': name,
        'type': project_type,
        'source_path': str(Path(source_path).absolute()),
        'port': port,
        'route': route,
        'status': 'stopped',
        'created_at': datetime.now().isoformat(),
        'last_started': None
    }
    
    projects[name] = project
    proxy_routes[route] = {
        'project_name': name,
        'port': port,
        'type': project_type
    }
    
    save_projects()
    return project

def start_project(project_name: str) -> Tuple[bool, str]:
    """Start a project server"""
    if project_name not in projects:
        return False, "Project not found"
    
    project = projects[project_name]
    
    if project['status'] == 'running':
        return False, "Project already running"
    
    try:
        if project['type'] == 'static':
            success, msg = start_static_server(project)
        elif project['type'] == 'php':
            success, msg = start_php_server(project)
        elif project['type'] == 'nodejs':
            success, msg = start_nodejs_server(project)
        elif project['type'] == 'python':
            success, msg = start_python_server(project)
        else:
            return False, f"Unsupported project type: {project['type']}"
        
        if success:
            project['status'] = 'running'
            project['last_started'] = datetime.now().isoformat()
            save_projects()
            logger.info(f"Started project {project_name} on port {project['port']}")
        
        return success, msg
        
    except Exception as e:
        logger.error(f"Failed to start project {project_name}: {e}")
        return False, str(e)

def stop_project(project_name: str) -> Tuple[bool, str]:
    """Stop a project server"""
    if project_name not in projects:
        return False, "Project not found"
    
    project = projects[project_name]
    
    if project['status'] != 'running':
        return False, "Project not running"
    
    try:
        if project_name in project_processes:
            proc = project_processes[project_name]
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            
            del project_processes[project_name]
            if project_name in log_queues:
                del log_queues[project_name]
        
        project['status'] = 'stopped'
        save_projects()
        logger.info(f"Stopped project {project_name}")
        return True, "Project stopped"
        
    except Exception as e:
        logger.error(f"Failed to stop project {project_name}: {e}")
        return False, str(e)

# ============================================================================
# Server Implementations
# ============================================================================

def start_static_server(project: Dict) -> Tuple[bool, str]:
    """Start a static file server"""
    try:
        source_path = project['source_path']
        port = project['port']
        
        if not Path(source_path).exists():
            return False, "Source path does not exist"
        
        # Use Python's built-in HTTP server
        cmd = [sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1']
        proc = subprocess.Popen(cmd, cwd=source_path, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, bufsize=1)
        
        project_processes[project['name']] = proc
        log_queues[project['name']] = queue.Queue()
        
        # Start log monitoring
        threading.Thread(target=monitor_process_logs, 
                        args=(project['name'], proc), daemon=True).start()
        
        # Wait a moment to check if it started successfully
        time.sleep(0.5)
        if proc.poll() is not None:
            return False, "Static server failed to start"
        
        return True, f"Static server started on port {port}"
        
    except Exception as e:
        return False, f"Failed to start static server: {e}"

def start_php_server(project: Dict) -> Tuple[bool, str]:
    """Start a PHP development server"""
    try:
        php_exe = get_php_executable()
        if not php_exe:
            return False, "PHP not found. Please install PHP."
        
        source_path = project['source_path']
        port = project['port']
        
        if not Path(source_path).exists():
            return False, "Source path does not exist"
        
        cmd = [php_exe, '-S', f'127.0.0.1:{port}', '-t', source_path,
               '-d', 'display_errors=1', '-d', 'log_errors=1']
        
        proc = subprocess.Popen(cmd, cwd=source_path,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, bufsize=1)
        
        project_processes[project['name']] = proc
        log_queues[project['name']] = queue.Queue()
        
        # Start log monitoring
        threading.Thread(target=monitor_process_logs, 
                        args=(project['name'], proc), daemon=True).start()
        
        # Wait a moment to check if it started successfully
        time.sleep(0.5)
        if proc.poll() is not None:
            return False, "PHP server failed to start"
        
        return True, f"PHP server started on port {port}"
        
    except Exception as e:
        return False, f"Failed to start PHP server: {e}"

def start_nodejs_server(project: Dict) -> Tuple[bool, str]:
    """Start a Node.js server"""
    try:
        node_exe = get_node_executable()
        if not node_exe:
            return False, "Node.js not found. Please install Node.js."
        
        source_path = project['source_path']
        port = project['port']
        
        if not Path(source_path).exists():
            return False, "Source path does not exist"
        
        # Look for package.json or server.js
        package_json = Path(source_path) / 'package.json'
        server_js = Path(source_path) / 'server.js'
        index_js = Path(source_path) / 'index.js'
        
        if package_json.exists():
            # Try to run npm start or node server
            cmd = [node_exe, 'server.js'] if server_js.exists() else [node_exe, 'index.js']
        elif server_js.exists():
            cmd = [node_exe, 'server.js']
        elif index_js.exists():
            cmd = [node_exe, 'index.js']
        else:
            # Create a simple static server
            cmd = create_nodejs_static_server(source_path, port)
        
        proc = subprocess.Popen(cmd, cwd=source_path,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, bufsize=1)
        
        project_processes[project['name']] = proc
        log_queues[project['name']] = queue.Queue()
        
        # Start log monitoring
        threading.Thread(target=monitor_process_logs, 
                        args=(project['name'], proc), daemon=True).start()
        
        # Wait a moment to check if it started successfully
        time.sleep(0.5)
        if proc.poll() is not None:
            return False, "Node.js server failed to start"
        
        return True, f"Node.js server started on port {port}"
        
    except Exception as e:
        return False, f"Failed to start Node.js server: {e}"

def create_nodejs_static_server(source_path: str, port: int) -> List[str]:
    """Create a simple Node.js static server script"""
    script_path = Path(source_path) / 'temp_server.js'
    
    script_content = f"""
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
    
    const filePath = path.join('{source_path}', pathname);
    
    fs.readFile(filePath, (err, data) => {{
        if (err) {{
            res.writeHead(404, {{'Content-Type': 'text/html'}});
            res.end('<h1>404 Not Found</h1>');
            return;
        }}
        
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
    }});
}});

server.listen({port}, '127.0.0.1', () => {{
    console.log(`Node.js static server running on http://127.0.0.1:{port}`);
}});
"""
    
    script_path.write_text(script_content)
    return [get_node_executable(), str(script_path)]

def start_python_server(project: Dict) -> Tuple[bool, str]:
    """Start a Python server (Flask/Django/etc.)"""
    try:
        source_path = project['source_path']
        port = project['port']
        
        if not Path(source_path).exists():
            return False, "Source path does not exist"
        
        # Look for common Python web app files
        app_py = Path(source_path) / 'app.py'
        main_py = Path(source_path) / 'main.py'
        manage_py = Path(source_path) / 'manage.py'  # Django
        
        if manage_py.exists():
            # Django project
            cmd = [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}']
        elif app_py.exists():
            # Flask app
            cmd = [sys.executable, 'app.py']
        elif main_py.exists():
            # Generic Python app
            cmd = [sys.executable, 'main.py']
        else:
            # Fallback to static server
            cmd = [sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1']
        
        proc = subprocess.Popen(cmd, cwd=source_path,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, bufsize=1)
        
        project_processes[project['name']] = proc
        log_queues[project['name']] = queue.Queue()
        
        # Start log monitoring
        threading.Thread(target=monitor_process_logs, 
                        args=(project['name'], proc), daemon=True).start()
        
        # Wait a moment to check if it started successfully
        time.sleep(0.5)
        if proc.poll() is not None:
            return False, "Python server failed to start"
        
        return True, f"Python server started on port {port}"
        
    except Exception as e:
        return False, f"Failed to start Python server: {e}"

def monitor_process_logs(project_name: str, proc: subprocess.Popen):
    """Monitor process output and add to log queue"""
    log_queue = log_queues.get(project_name)
    if not log_queue:
        return
    
    try:
        while True:
            if proc.stdout:
                line = proc.stdout.readline()
                if line:
                    log_queue.put({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': line.strip(),
                        'type': 'info'
                    })
            
            if proc.stderr:
                line = proc.stderr.readline()
                if line:
                    log_queue.put({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': line.strip(),
                        'type': 'error'
                    })
            
            if proc.poll() is not None:
                break
            
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error monitoring logs for {project_name}: {e}")

# ============================================================================
# Reverse Proxy
# ============================================================================

def proxy_request(route: str, path: str) -> Response:
    """Proxy a request to the appropriate backend server"""
    if route not in proxy_routes:
        abort(404)
    
    project_info = proxy_routes[route]
    project_name = project_info['project_name']
    backend_port = project_info['port']
    
    if project_name not in projects or projects[project_name]['status'] != 'running':
        abort(503)
    
    try:
        # Make request to backend server
        import requests
        backend_url = f"http://127.0.0.1:{backend_port}{path}"
        
        # Forward the request
        response = requests.get(backend_url, stream=True, timeout=30)
        
        # Create Flask response
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk
        
        return Response(generate(), 
                       status=response.status_code,
                       headers=dict(response.headers))
        
    except Exception as e:
        logger.error(f"Proxy error for {route}{path}: {e}")
        abort(502)

# ============================================================================
# Flask Routes
# ============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html', 
                         projects=projects,
                         php_available=check_php_available()[0],
                         node_available=check_node_available()[0])

@app.route('/api/projects')
def api_projects():
    """Get all projects"""
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
def api_create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        name = data.get('name')
        project_type = data.get('type', 'static')
        source_path = data.get('source_path')
        port = data.get('port')
        route = data.get('route')
        
        if not name or not source_path:
            return jsonify({'success': False, 'message': 'Name and source_path required'})
        
        if project_type not in Config.SERVER_TYPES:
            return jsonify({'success': False, 'message': f'Invalid project type: {project_type}'})
        
        # Check if project already exists
        if name in projects:
            return jsonify({'success': False, 'message': 'Project already exists'})
        
        # Create project
        project = create_project(name, project_type, source_path, port, route)
        
        return jsonify({'success': True, 'project': project})
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/projects/<project_name>/start', methods=['POST'])
def api_start_project(project_name):
    """Start a project"""
    success, message = start_project(project_name)
    return jsonify({'success': success, 'message': message})

@app.route('/api/projects/<project_name>/stop', methods=['POST'])
def api_stop_project(project_name):
    """Stop a project"""
    success, message = stop_project(project_name)
    return jsonify({'success': success, 'message': message})

@app.route('/api/projects/<project_name>', methods=['DELETE'])
def api_delete_project(project_name):
    """Delete a project"""
    try:
        if project_name not in projects:
            return jsonify({'success': False, 'message': 'Project not found'})
        
        # Stop if running
        if projects[project_name]['status'] == 'running':
            stop_project(project_name)
        
        # Remove from routes
        route = projects[project_name]['route']
        if route in proxy_routes:
            del proxy_routes[route]
        
        # Remove project
        del projects[project_name]
        save_projects()
        
        return jsonify({'success': True, 'message': 'Project deleted'})
        
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/check-php')
def api_check_php():
    """Check PHP availability"""
    available, version = check_php_available()
    return jsonify({'available': available, 'version': version})

@app.route('/api/check-node')
def api_check_node():
    """Check Node.js availability"""
    available, version = check_node_available()
    return jsonify({'available': available, 'version': version})

# Proxy routes - catch all
@app.route('/<path:path>')
def proxy_route(path):
    """Proxy requests to backend servers"""
    # Find matching route
    for route, project_info in proxy_routes.items():
        if path.startswith(route.lstrip('/')):
            remaining_path = '/' + path[len(route.lstrip('/')):]
            return proxy_request(route, remaining_path)
    
    # No matching route found
    abort(404)

# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point"""
    print("🚀 Starting Windows-Compatible Workspace Server...")
    print(f"📁 Projects folder: {Config.PROJECTS_FOLDER}")
    print(f"🌐 Proxy server: http://{Config.PROXY_HOST}:{Config.PROXY_PORT}")
    
    # Ensure directories exist
    ensure_directories()
    
    # Load existing projects
    load_projects()
    
    # Check dependencies
    php_available, php_version = check_php_available()
    node_available, node_version = check_node_available()
    
    print(f"🐘 PHP: {'✓' if php_available else '✗'} {php_version if php_available else 'Not found'}")
    print(f"🟢 Node.js: {'✓' if node_available else '✗'} {node_version if node_available else 'Not found'}")
    
    # Start the server
    try:
        print(f"\n🌐 Server starting on http://{Config.PROXY_HOST}:{Config.PROXY_PORT}")
        print("Press Ctrl+C to stop")
        
        # Open browser on Windows
        if platform.system() == 'Windows':
            threading.Timer(2.0, lambda: webbrowser.open(f'http://localhost:{Config.PROXY_PORT}')).start()
        
        app.run(host=Config.PROXY_HOST, port=Config.PROXY_PORT, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        # Stop all running projects
        for project_name in list(projects.keys()):
            if projects[project_name]['status'] == 'running':
                stop_project(project_name)
        print("✅ Shutdown complete")

if __name__ == '__main__':
    main()