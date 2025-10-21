#!/usr/bin/env python3
"""
Modern Server Administrator - Professional Edition
A bulletproof, professional server management tool with all features
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
import mimetypes
import tempfile
import zipfile
import urllib.request
import ssl

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'modern_server_admin_2024'

# Global variables
servers = {}
server_processes = {}
log_queues = {}
current_folder = None

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'php', 'html', 'css', 'js', 'json', 'xml', 'md', 'py', 'sql', 'zip', 'rar', '7z'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def is_windows():
    """Check if running on Windows"""
    return platform.system() == 'Windows'

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

def install_php_windows():
    """Install PHP on Windows with fallback options"""
    try:
        print("Installing PHP for Windows...")
        
        # Try multiple PHP versions and sources
        php_urls = [
            "https://windows.php.net/downloads/releases/php-8.3.0-Win32-vs16-x64.zip",
            "https://windows.php.net/downloads/releases/php-8.2.12-Win32-vs16-x64.zip",
            "https://windows.php.net/downloads/releases/php-8.1.25-Win32-vs16-x64.zip"
        ]
        
        for i, php_url in enumerate(php_urls):
            try:
                print(f"Trying PHP source {i+1}/{len(php_urls)}: {php_url}")
                
                # Create temp directory
                temp_dir = tempfile.mkdtemp()
                php_zip = os.path.join(temp_dir, 'php.zip')
                
                # Create SSL context to ignore certificate errors
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                # Download with progress
                try:
                    with urllib.request.urlopen(php_url, context=ssl_context, timeout=30) as response:
                        total_size = int(response.headers.get('Content-Length', 0))
                        downloaded = 0
                        
                        with open(php_zip, 'wb') as f:
                            while True:
                                chunk = response.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    print(f"Downloaded {percent:.1f}%")
                except Exception as e:
                    print(f"Failed to download from {php_url}: {str(e)}")
                    continue
                
                # Extract PHP
                try:
                    with zipfile.ZipFile(php_zip, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                except Exception as e:
                    print(f"Failed to extract PHP: {str(e)}")
                    continue
                
                # Find PHP directory
                php_dir = None
                for item in os.listdir(temp_dir):
                    if item.startswith('php-'):
                        php_dir = os.path.join(temp_dir, item)
                        break
                
                if not php_dir:
                    print("Could not find PHP directory in downloaded files")
                    continue
                
                # Copy PHP to application directory
                app_php_dir = os.path.join(os.getcwd(), 'php')
                if os.path.exists(app_php_dir):
                    shutil.rmtree(app_php_dir)
                
                try:
                    shutil.copytree(php_dir, app_php_dir)
                except Exception as e:
                    print(f"Failed to copy PHP files: {str(e)}")
                    continue
                
                # Add PHP to PATH for this session
                php_exe = os.path.join(app_php_dir, 'php.exe')
                if os.path.exists(php_exe):
                    os.environ['PATH'] = app_php_dir + os.pathsep + os.environ['PATH']
                    # Test PHP installation
                    try:
                        result = subprocess.run([php_exe, '--version'], capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            return True, f"PHP installed successfully: {result.stdout.split()[1]}"
                        else:
                            print("PHP installed but not working properly")
                            continue
                    except Exception as e:
                        print(f"PHP installed but test failed: {str(e)}")
                        continue
                else:
                    print("PHP executable not found after installation")
                    continue
                    
            except Exception as e:
                print(f"Error with PHP source {i+1}: {str(e)}")
                continue
        
        # If all automatic downloads failed, provide manual installation instructions
        return False, """Automatic PHP installation failed. Please install PHP manually:

1. Download PHP from: https://windows.php.net/download/
2. Extract to C:\\php\\ or any folder
3. Add PHP folder to your system PATH
4. Or place php.exe in the application folder

Alternatively, you can:
- Install XAMPP: https://www.apachefriends.org/
- Install WAMP: https://www.wampserver.com/
- Install Laragon: https://laragon.org/

Then restart this application."""
            
    except Exception as e:
        return False, f"Error installing PHP: {str(e)}"

def get_php_path():
    """Get PHP executable path"""
    if is_windows():
        # Check if we have local PHP installation
        local_php = os.path.join(os.getcwd(), 'php', 'php.exe')
        if os.path.exists(local_php):
            return local_php
        
        # Check system PATH
        try:
            result = subprocess.run(['where', 'php'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        # Try common PHP installation paths
        common_paths = [
            r'C:\php\php.exe',
            r'C:\xampp\php\php.exe',
            r'C:\wamp\bin\php\php.exe',
            r'C:\laragon\bin\php\php.exe'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
    
    return 'php'

def start_server_process(name, folder, port, server_type):
    """Start a server process with proper support for all types"""
    try:
        if server_type == "PHP":
            php_path = get_php_path()
            
            # Check if PHP is available
            if not check_php_available() and not os.path.exists(php_path):
                return False, "PHP is not installed. Please install PHP or use the auto-installer button."
            
            # Use PHP built-in server with proper configuration
            try:
                process = subprocess.Popen([
                    php_path, '-S', f'localhost:{port}', '-t', folder,
                    '-d', 'display_errors=1',
                    '-d', 'log_errors=1',
                    '-d', 'error_log=php_errors.log',
                    '-d', 'error_reporting=E_ALL'
                ], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except FileNotFoundError:
                return False, f"PHP executable not found at {php_path}. Please install PHP or use the auto-installer."
            except Exception as e:
                return False, f"Error starting PHP server: {str(e)}"
            
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
                '.svg': 'image/svg+xml',
                '.php': 'text/html'
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

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(filepath):
    """Get human readable file size"""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"

# Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', servers=servers, current_folder=current_folder)

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
        
        # Check if folder exists, if not try to create it or use demo folder
        if not os.path.exists(folder):
            # If it's a relative path, try to create it
            if not os.path.isabs(folder):
                try:
                    os.makedirs(folder, exist_ok=True)
                    # Create a simple index.html if folder is empty
                    index_file = os.path.join(folder, 'index.html')
                    if not os.path.exists(index_file):
                        with open(index_file, 'w') as f:
                            f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Your Server</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #0d1117; color: #f0f6fc; }
        h1 { color: #0969da; }
    </style>
</head>
<body>
    <h1>🚀 Server Running Successfully!</h1>
    <p>Your server is now running on this port.</p>
    <p>Add your website files to this folder.</p>
</body>
</html>''')
                except Exception as e:
                    return jsonify({'success': False, 'message': f'Could not create folder: {str(e)}'})
            else:
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

@app.route('/api/start_server', methods=['POST'])
def start_server():
    """Start a stopped server"""
    try:
        data = request.get_json()
        server_name = data.get('name')
        
        if server_name not in servers:
            return jsonify({'success': False, 'message': 'Server not found'})
        
        server = servers[server_name]
        
        if server['status'] == 'Running':
            return jsonify({'success': False, 'message': 'Server is already running'})
        
        # Check if port is still available
        if is_port_in_use(server['port']):
            return jsonify({'success': False, 'message': f'Port {server["port"]} is now in use by another process'})
        
        # Start the server process
        success, message = start_server_process(server_name, server['folder'], server['port'], server['type'])
        
        if success:
            server['status'] = 'Running'
            server['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return jsonify({'success': True, 'message': f'Server {server_name} started successfully'})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting server: {str(e)}'})

@app.route('/api/delete_server', methods=['POST'])
def delete_server():
    """Delete a server completely"""
    try:
        data = request.get_json()
        server_name = data.get('name')
        
        if server_name not in servers:
            return jsonify({'success': False, 'message': 'Server not found'})
        
        server = servers[server_name]
        
        # Stop the server if it's running
        if server['status'] == 'Running' and server_name in server_processes:
            try:
                server_processes[server_name].terminate()
                server_processes[server_name].wait(timeout=5)
            except:
                try:
                    server_processes[server_name].kill()
                    server_processes[server_name].wait()
                except:
                    pass
            del server_processes[server_name]
        
        # Clean up logs
        if server_name in log_queues:
            del log_queues[server_name]
        
        # Remove from servers dictionary
        del servers[server_name]
        
        return jsonify({'success': True, 'message': f'Server {server_name} deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting server: {str(e)}'})

@app.route('/api/open_browser/<server_name>')
def open_browser(server_name):
    """Open server in browser"""
    try:
        if server_name not in servers:
            return jsonify({'success': False, 'message': 'Server not found'})
        
        server = servers[server_name]
        url = f"http://localhost:{server['port']}"
        
        # Open in default browser
        if is_windows():
            os.system(f'start {url}')
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open {url}')
        else:  # Linux
            os.system(f'xdg-open {url}')
        
        return jsonify({'success': True, 'message': f'Opening {url} in browser'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error opening browser: {str(e)}'})

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


@app.route('/api/set_folder', methods=['POST'])
def set_folder():
    """Set current folder"""
    global current_folder
    try:
        data = request.get_json()
        folder = data.get('folder')
        
        if folder and os.path.exists(folder):
            current_folder = folder
            return jsonify({'success': True, 'message': f'Folder set to {folder}'})
        else:
            return jsonify({'success': False, 'message': 'Invalid folder path'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error setting folder: {str(e)}'})

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
            'node_version': get_node_version() if node_available else None,
            'current_folder': current_folder
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)})

def get_php_version():
    """Get PHP version"""
    try:
        result = subprocess.run([get_php_path(), '--version'], capture_output=True, text=True, timeout=5)
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


@app.route('/api/install_php', methods=['POST'])
def install_php():
    """Install PHP"""
    try:
        if not is_windows():
            return jsonify({'success': False, 'message': 'PHP auto-installation is only available on Windows'})
        
        success, message = install_php_windows()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error installing PHP: {str(e)}'})

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
        if is_windows():
            print("   Use the 'Install PHP' button in the application to auto-install PHP")
    
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