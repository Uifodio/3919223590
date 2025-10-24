#!/usr/bin/env python3
"""
Unified Server Administrator - Production Ready
===============================================

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
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  YAML not available - using JSON fallback for configurations")
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

import logging
import logging.handlers
import platform

# Optional speed: if psutil is available use it for port checks; otherwise fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except Exception:
    PSUTIL_AVAILABLE = False

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# =========================
# Configuration
# =========================
class Config:
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    
    # Paths
    ROOT = Path.cwd()
    UPLOAD_FOLDER = ROOT / 'uploads'
    SITES_FOLDER = ROOT / 'sites'
    LOGS_FOLDER = ROOT / 'logs'
    NGINX_CONFIG_DIR = ROOT / 'nginx_configs'
    PHP_FPM_CONFIG_DIR = ROOT / 'php_fpm_configs'
    PERSIST_FILE = ROOT / 'servers.json'
    PHP_LOCAL_FOLDER = ROOT / 'php'
    
    # Nginx Configuration
    NGINX_MAIN_CONFIG = '/etc/nginx/nginx.conf'
    NGINX_SITES_AVAILABLE = '/etc/nginx/sites-available'
    NGINX_SITES_ENABLED = '/etc/nginx/sites-enabled'
    
    # PHP-FPM Configuration
    PHP_FPM_POOL_DIR = '/etc/php/8.1/fpm/pool.d'
    PHP_FPM_SOCKET_DIR = '/var/run/php'
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm',
        'php', 'html', 'css', 'js', 'json', 'xml', 'md', 'py', 'sql', 'zip', 'rar', '7z'
    }
    
    # Runtime options
    AUTO_REFRESH_INTERVAL = 2.0
    MAX_WORKERS = 32
    LOG_TAIL_LINES = 200
    BIND_ALL_DEFAULT = True

# =========================
# Initialize Flask App
# =========================
app = Flask(__name__)
app.secret_key = 'unified_server_admin_2024_production'

# Create necessary directories
for directory in [Config.UPLOAD_FOLDER, Config.SITES_FOLDER, Config.LOGS_FOLDER, 
                 Config.NGINX_CONFIG_DIR, Config.PHP_FPM_CONFIG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Thread pool for concurrent operations
EXECUTOR = ThreadPoolExecutor(max_workers=Config.MAX_WORKERS)

# Global state
servers = {}           # name -> metadata (persisted)
server_processes = {}  # name -> subprocess.Popen
log_queues = {}        # name -> Queue()
nginx_configs = {}     # name -> nginx config path

LOCK = threading.RLock()

# =========================
# Logging Setup
# =========================
def setup_logging():
    app_logger = logging.getLogger('usa_app')
    app_logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.handlers.RotatingFileHandler(
        str(Config.LOGS_FOLDER / 'usa_app.log'), 
        maxBytes=5_000_000, 
        backupCount=5, 
        encoding='utf-8'
    )
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app_logger.addHandler(fh)
    app_logger.addHandler(logging.StreamHandler(sys.stdout))
    
    return app_logger

app_logger = setup_logging()

# =========================
# Utility Functions
# =========================
def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def human_size(path):
    try:
        s = os.path.getsize(path)
        for unit in ['B','KB','MB','GB','TB']:
            if s < 1024.0: 
                return f"{s:.1f} {unit}"
            s /= 1024.0
    except:
        return "Unknown"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in Config.ALLOWED_EXTENSIONS

def secure_name(n):
    return secure_filename(n) or f"site-{int(time.time())}"

def is_port_in_use(port: int, host='0.0.0.0') -> bool:
    try:
        if PSUTIL_AVAILABLE:
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port == int(port):
                    if host in ('0.0.0.0','') or (conn.laddr.ip == host) or conn.laddr.ip in ('0.0.0.0','127.0.0.1','::'):
                        return True
            return False
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.4)
                return s.connect_ex(('127.0.0.1', int(port))) == 0
    except Exception:
        return False

def tail_lines(filepath, n=200):
    try:
        with open(filepath, 'rb') as f:
            avg = 200
            to_read = n * avg
            try:
                f.seek(-to_read, os.SEEK_END)
            except OSError:
                f.seek(0)
            data = f.read().decode(errors='replace')
        return data.splitlines()[-n:]
    except Exception:
        return []

# =========================
# System Checks
# =========================
def get_php_path():
    local = str(Config.PHP_LOCAL_FOLDER / ('php.exe' if platform.system() == 'Windows' else 'php'))
    if Path(local).exists(): 
        return local
    w = shutil.which('php')
    if w: 
        return w
    if platform.system() == 'Windows':
        for p in [r'C:\php\php.exe', r'C:\xampp\php\php.exe', r'C:\wamp\bin\php\php.exe']:
            if Path(p).exists(): 
                return p
    return 'php'

def check_php_available():
    try:
        p = get_php_path()
        r = subprocess.run([p,'--version'], capture_output=True, text=True, timeout=3)
        return r.returncode == 0
    except:
        return False

def get_node_path():
    return shutil.which('node') or 'node'

def check_node_available():
    try:
        n = get_node_path()
        r = subprocess.run([n,'--version'], capture_output=True, text=True, timeout=3)
        return r.returncode == 0
    except:
        return False

def check_nginx_available():
    try:
        r = subprocess.run(['nginx', '-v'], capture_output=True, text=True, timeout=3)
        return r.returncode == 0
    except:
        return False

# =========================
# Nginx Configuration Management
# =========================
class NginxManager:
    def __init__(self):
        self.config_dir = Config.NGINX_CONFIG_DIR
        self.sites_available = Config.NGINX_SITES_AVAILABLE
        self.sites_enabled = Config.NGINX_SITES_ENABLED
    
    def generate_nginx_config(self, server_name: str, server_type: str, port: int, 
                            site_path: str, domain: str = None) -> str:
        """Generate nginx configuration for a server"""
        
        if server_type == 'PHP':
            return self._generate_php_config(server_name, port, site_path, domain)
        elif server_type == 'Node.js':
            return self._generate_nodejs_config(server_name, port, site_path, domain)
        else:  # Static files
            return self._generate_static_config(server_name, port, site_path, domain)
    
    def _generate_php_config(self, server_name: str, port: int, site_path: str, domain: str = None) -> str:
        """Generate nginx config for PHP with php-fpm"""
        server_name_config = domain or f"{server_name}.local"
        
        config = f"""
server {{
    listen {port};
    server_name {server_name_config};
    root {site_path};
    index index.php index.html index.htm;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # PHP processing
    location ~ \\.php$ {{
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\\.php)(/.+)$;
        fastcgi_pass unix:/var/run/php/php8.1-fpm-{server_name}.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        
        # Security
        fastcgi_hide_header X-Powered-By;
        fastcgi_read_timeout 300;
        fastcgi_connect_timeout 300;
        fastcgi_send_timeout 300;
    }}
    
    # Static files
    location / {{
        try_files $uri $uri/ /index.php?$query_string;
        
        # Cache static files
        location ~* \\.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
    
    # Deny access to hidden files
    location ~ /\\. {{
        deny all;
    }}
    
    # Logging
    access_log /var/log/nginx/{server_name}_access.log;
    error_log /var/log/nginx/{server_name}_error.log;
}}
"""
        return config.strip()
    
    def _generate_nodejs_config(self, server_name: str, port: int, site_path: str, domain: str = None) -> str:
        """Generate nginx config for Node.js reverse proxy"""
        server_name_config = domain or f"{server_name}.local"
        
        config = f"""
upstream {server_name}_backend {{
    server 127.0.0.1:{port + 1000};
    keepalive 32;
}}

server {{
    listen {port};
    server_name {server_name_config};
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # Proxy to Node.js
    location / {{
        proxy_pass http://{server_name}_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Static files (if any)
    location ~* \\.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {{
        root {site_path};
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Logging
    access_log /var/log/nginx/{server_name}_access.log;
    error_log /var/log/nginx/{server_name}_error.log;
}}
"""
        return config.strip()
    
    def _generate_static_config(self, server_name: str, port: int, site_path: str, domain: str = None) -> str:
        """Generate nginx config for static files"""
        server_name_config = domain or f"{server_name}.local"
        
        config = f"""
server {{
    listen {port};
    server_name {server_name_config};
    root {site_path};
    index index.html index.htm;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # Static files
    location / {{
        try_files $uri $uri/ =404;
        
        # Cache static files
        location ~* \\.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
    
    # Deny access to hidden files
    location ~ /\\. {{
        deny all;
    }}
    
    # Logging
    access_log /var/log/nginx/{server_name}_access.log;
    error_log /var/log/nginx/{server_name}_error.log;
}}
"""
        return config.strip()
    
    def save_nginx_config(self, server_name: str, config: str) -> str:
        """Save nginx configuration to file"""
        config_path = self.config_dir / f"{server_name}.conf"
        config_path.write_text(config, encoding='utf-8')
        return str(config_path)
    
    def enable_site(self, server_name: str) -> bool:
        """Enable nginx site by creating symlink"""
        try:
            source = self.config_dir / f"{server_name}.conf"
            target = Path(self.sites_enabled) / f"{server_name}.conf"
            
            if target.exists():
                target.unlink()
            
            target.symlink_to(source)
            return True
        except Exception as e:
            app_logger.error(f"Failed to enable nginx site {server_name}: {e}")
            return False
    
    def disable_site(self, server_name: str) -> bool:
        """Disable nginx site by removing symlink"""
        try:
            target = Path(self.sites_enabled) / f"{server_name}.conf"
            if target.exists():
                target.unlink()
            return True
        except Exception as e:
            app_logger.error(f"Failed to disable nginx site {server_name}: {e}")
            return False
    
    def reload_nginx(self) -> bool:
        """Reload nginx configuration"""
        try:
            result = subprocess.run(['sudo', 'nginx', '-t'], capture_output=True, text=True)
            if result.returncode != 0:
                app_logger.error(f"Nginx config test failed: {result.stderr}")
                return False
            
            result = subprocess.run(['sudo', 'systemctl', 'reload', 'nginx'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                # Fallback to nginx -s reload
                result = subprocess.run(['sudo', 'nginx', '-s', 'reload'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    app_logger.error(f"Failed to reload nginx: {result.stderr}")
                    return False
            
            return True
        except Exception as e:
            app_logger.error(f"Failed to reload nginx: {e}")
            return False

# =========================
# PHP-FPM Configuration Management
# =========================
class PHPFPMManager:
    def __init__(self):
        self.pool_dir = Config.PHP_FPM_POOL_DIR
        self.socket_dir = Config.PHP_FPM_SOCKET_DIR
    
    def generate_pool_config(self, server_name: str, site_path: str) -> str:
        """Generate PHP-FPM pool configuration"""
        config = f"""[{server_name}]
user = www-data
group = www-data
listen = /var/run/php/php8.1-fpm-{server_name}.sock
listen.owner = www-data
listen.group = www-data
listen.mode = 0660

pm = dynamic
pm.max_children = 20
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
pm.max_requests = 1000

chdir = {site_path}

php_admin_value[error_log] = /var/log/php8.1-fpm-{server_name}.log
php_admin_flag[log_errors] = on
php_value[session.save_handler] = files
php_value[session.save_path] = /var/lib/php/sessions
php_value[soap.wsdl_cache_dir] = /var/lib/php/wsdlcache
"""
        return config.strip()
    
    def save_pool_config(self, server_name: str, config: str) -> str:
        """Save PHP-FPM pool configuration"""
        config_path = Config.PHP_FPM_CONFIG_DIR / f"{server_name}.conf"
        config_path.write_text(config, encoding='utf-8')
        return str(config_path)
    
    def enable_pool(self, server_name: str) -> bool:
        """Enable PHP-FPM pool by creating symlink"""
        try:
            source = Config.PHP_FPM_CONFIG_DIR / f"{server_name}.conf"
            target = Path(self.pool_dir) / f"{server_name}.conf"
            
            if target.exists():
                target.unlink()
            
            target.symlink_to(source)
            return True
        except Exception as e:
            app_logger.error(f"Failed to enable PHP-FPM pool {server_name}: {e}")
            return False
    
    def disable_pool(self, server_name: str) -> bool:
        """Disable PHP-FPM pool by removing symlink"""
        try:
            target = Path(self.pool_dir) / f"{server_name}.conf"
            if target.exists():
                target.unlink()
            return True
        except Exception as e:
            app_logger.error(f"Failed to disable PHP-FPM pool {server_name}: {e}")
            return False
    
    def reload_php_fpm(self) -> bool:
        """Reload PHP-FPM configuration"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'reload', 'php8.1-fpm'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                app_logger.error(f"Failed to reload PHP-FPM: {result.stderr}")
                return False
            return True
        except Exception as e:
            app_logger.error(f"Failed to reload PHP-FPM: {e}")
            return False

# =========================
# Server Management
# =========================
class ServerManager:
    def __init__(self):
        self.nginx = NginxManager()
        self.php_fpm = PHPFPMManager()
    
    def create_server(self, name: str, server_type: str, port: int, site_path: str, domain: str = None) -> Tuple[bool, str]:
        """Create a new server with nginx configuration"""
        try:
            # Generate nginx configuration
            nginx_config = self.nginx.generate_nginx_config(name, server_type, port, site_path, domain)
            nginx_config_path = self.nginx.save_nginx_config(name, nginx_config)
            
            # Enable nginx site
            if not self.nginx.enable_site(name):
                return False, "Failed to enable nginx site"
            
            # For PHP servers, create PHP-FPM pool
            if server_type == 'PHP':
                php_fpm_config = self.php_fpm.generate_pool_config(name, site_path)
                php_fpm_config_path = self.php_fpm.save_pool_config(name, php_fpm_config)
                
                if not self.php_fpm.enable_pool(name):
                    return False, "Failed to enable PHP-FPM pool"
                
                if not self.php_fpm.reload_php_fpm():
                    return False, "Failed to reload PHP-FPM"
            
            # Reload nginx
            if not self.nginx.reload_nginx():
                return False, "Failed to reload nginx"
            
            # Start backend process for Node.js
            if server_type == 'Node.js':
                success, msg = self._start_nodejs_backend(name, site_path, port + 1000)
                if not success:
                    return False, f"Failed to start Node.js backend: {msg}"
            
            return True, "Server created successfully"
            
        except Exception as e:
            app_logger.error(f"Failed to create server {name}: {e}")
            return False, f"Error creating server: {e}"
    
    def _start_nodejs_backend(self, name: str, site_path: str, port: int) -> Tuple[bool, str]:
        """Start Node.js backend process"""
        try:
            # Create Node.js server script
            script_path = self._create_nodejs_script(name, site_path, port)
            
            # Start process
            cmd = [get_node_path(), script_path]
            proc = subprocess.Popen(cmd, cwd=site_path, stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, text=True, bufsize=1)
            
            with LOCK:
                server_processes[name] = proc
                log_queues.setdefault(name, queue.Queue())
            
            # Start monitoring thread
            threading.Thread(target=self._monitor_process_io, args=(name, proc), daemon=True).start()
            
            return True, "Node.js backend started"
            
        except Exception as e:
            app_logger.error(f"Failed to start Node.js backend for {name}: {e}")
            return False, str(e)
    
    def _create_nodejs_script(self, name: str, site_path: str, port: int) -> str:
        """Create Node.js server script"""
        script_path = Path(site_path) / f"server_{name}.js"
        
        script_content = f"""
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const siteRoot = '{site_path}';
const port = {port};

const server = http.createServer((req, res) => {{
    const parsed = url.parse(req.url);
    let filePath = parsed.pathname;
    
    if (filePath === '/') filePath = '/index.html';
    
    const fullPath = path.join(siteRoot, filePath);
    
    // Security check
    if (!fullPath.startsWith(siteRoot)) {{
        res.writeHead(403, {{'Content-Type': 'text/plain'}});
        res.end('Forbidden');
        return;
    }}
    
    fs.readFile(fullPath, (err, data) => {{
        if (err) {{
            res.writeHead(404, {{'Content-Type': 'text/html'}});
            res.end('<h1>404 - File Not Found</h1>');
            return;
        }}
        
        const ext = path.extname(fullPath);
        const mimeTypes = {{
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon'
        }};
        
        const contentType = mimeTypes[ext] || 'text/plain';
        res.writeHead(200, {{'Content-Type': contentType}});
        res.end(data);
    }});
}});

server.listen(port, '127.0.0.1', () => {{
    console.log(`Node.js server for {name} listening on port ${{port}}`);
}});

// Graceful shutdown
process.on('SIGTERM', () => {{
    console.log('Received SIGTERM, shutting down gracefully');
    server.close(() => {{
        process.exit(0);
    }});
}});

process.on('SIGINT', () => {{
    console.log('Received SIGINT, shutting down gracefully');
    server.close(() => {{
        process.exit(0);
    }});
}});
"""
        
        script_path.write_text(script_content, encoding='utf-8')
        return str(script_path)
    
    def _monitor_process_io(self, name: str, proc: subprocess.Popen):
        """Monitor process output"""
        logger = logging.getLogger(f"usa_server_{name}")
        q = log_queues.setdefault(name, queue.Queue())
        
        def push(m, t='info'):
            try:
                q.put({'timestamp': now_str(), 'message': m, 'type': t})
            except:
                pass
        
        try:
            while True:
                out = proc.stdout.readline() if proc.stdout else ''
                err = proc.stderr.readline() if proc.stderr else ''
                
                if out:
                    logger.info(out.rstrip('\n'))
                    push(out.rstrip('\n'), 'info')
                
                if err:
                    logger.error(err.rstrip('\n'))
                    push(err.rstrip('\n'), 'error')
                
                if proc.poll() is not None:
                    break
                
                time.sleep(0.02)
        except Exception as e:
            logger.error(f"Monitor error: {e}")
        finally:
            with LOCK:
                if name in servers:
                    servers[name]['status'] = 'Stopped'
            logger.info("Process monitor ended")
    
    def delete_server(self, name: str) -> Tuple[bool, str]:
        """Delete a server and clean up configurations"""
        try:
            # Stop process if running
            if name in server_processes:
                proc = server_processes[name]
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except:
                    try:
                        proc.kill()
                        proc.wait()
                    except:
                        pass
                
                with LOCK:
                    server_processes.pop(name, None)
                    log_queues.pop(name, None)
            
            # Disable nginx site
            self.nginx.disable_site(name)
            
            # Disable PHP-FPM pool if exists
            if name in servers and servers[name].get('type') == 'PHP':
                self.php_fpm.disable_pool(name)
                self.php_fpm.reload_php_fpm()
            
            # Remove configuration files
            nginx_config = Config.NGINX_CONFIG_DIR / f"{name}.conf"
            if nginx_config.exists():
                nginx_config.unlink()
            
            php_fpm_config = Config.PHP_FPM_CONFIG_DIR / f"{name}.conf"
            if php_fpm_config.exists():
                php_fpm_config.unlink()
            
            # Reload nginx
            self.nginx.reload_nginx()
            
            return True, "Server deleted successfully"
            
        except Exception as e:
            app_logger.error(f"Failed to delete server {name}: {e}")
            return False, f"Error deleting server: {e}"

# =========================
# Persistence
# =========================
def save_servers_to_disk():
    try:
        with LOCK:
            minimal = {}
            for name, meta in servers.items():
                minimal[name] = {
                    'name': meta.get('name'),
                    'folder': meta.get('folder'),
                    'port': meta.get('port'),
                    'type': meta.get('type'),
                    'status': meta.get('status'),
                    'start_time': meta.get('start_time'),
                    'domain': meta.get('domain')
                }
        
        with open(Config.PERSIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(minimal, f, indent=2)
    except Exception as e:
        app_logger.exception("save_servers_to_disk failed")

def load_servers_from_disk():
    if not Config.PERSIST_FILE.exists():
        return
    
    try:
        with open(Config.PERSIST_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with LOCK:
            for name, meta in data.items():
                folder = meta.get('folder')
                if folder and Path(folder).exists():
                    servers[name] = {
                        'name': meta.get('name', name),
                        'folder': folder,
                        'port': meta.get('port'),
                        'type': meta.get('type', 'Static'),
                        'status': meta.get('status', 'Stopped'),
                        'start_time': meta.get('start_time'),
                        'domain': meta.get('domain')
                    }
    except Exception as e:
        app_logger.exception("load_servers_from_disk failed")

# =========================
# Background Monitor
# =========================
def monitor_loop():
    app_logger.info("Background monitor started")
    while True:
        try:
            with LOCK:
                for name, meta in list(servers.items()):
                    proc = server_processes.get(name)
                    port = meta.get('port')
                    
                    if proc:
                        if proc.poll() is None:
                            meta['status'] = 'Running'
                        else:
                            meta['status'] = 'Stopped'
                    else:
                        if port and is_port_in_use(port, '0.0.0.0'):
                            meta['status'] = 'Running'
                        else:
                            meta['status'] = 'Stopped'
            
            save_servers_to_disk()
        except Exception as e:
            app_logger.exception("monitor_loop error")
        
        time.sleep(Config.AUTO_REFRESH_INTERVAL)

# Start monitor thread
monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
monitor_thread.start()

# =========================
# Flask Routes
# =========================
@app.route('/')
def index():
    return render_template('unified_index.html', servers=servers)

@app.route('/api/servers')
def api_servers():
    with LOCK:
        out = {}
        for name, s in servers.items():
            out[name] = {
                'name': s.get('name'),
                'folder': s.get('folder'),
                'port': s.get('port'),
                'type': s.get('type'),
                'status': s.get('status'),
                'start_time': s.get('start_time'),
                'domain': s.get('domain')
            }
    return jsonify(out)

@app.route('/api/add_server', methods=['POST'])
def api_add_server():
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        server_type = data.get('type', 'Static')
        port = int(data.get('port', 8000))
        site_path = data.get('site_path', '').strip()
        domain = data.get('domain', '').strip() or None
        
        if not name:
            return jsonify({'success': False, 'message': 'Server name is required'})
        
        if not site_path or not Path(site_path).exists():
            return jsonify({'success': False, 'message': 'Valid site path is required'})
        
        if port < 1000 or port > 65535:
            return jsonify({'success': False, 'message': 'Port must be between 1000 and 65535'})
        
        if is_port_in_use(port):
            return jsonify({'success': False, 'message': f'Port {port} is already in use'})
        
        # Create server
        server_manager = ServerManager()
        success, message = server_manager.create_server(name, server_type, port, site_path, domain)
        
        if success:
            with LOCK:
                servers[name] = {
                    'name': name,
                    'folder': site_path,
                    'port': port,
                    'type': server_type,
                    'status': 'Running',
                    'start_time': now_str(),
                    'domain': domain
                }
            save_servers_to_disk()
            return jsonify({'success': True, 'message': f'Server {name} created successfully'})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        app_logger.exception("api_add_server error")
        return jsonify({'success': False, 'message': f'Error: {e}'})

@app.route('/api/delete_server', methods=['POST'])
def api_delete_server():
    try:
        data = request.get_json() or {}
        name = data.get('name')
        
        if not name or name not in servers:
            return jsonify({'success': False, 'message': 'Server not found'})
        
        server_manager = ServerManager()
        success, message = server_manager.delete_server(name)
        
        if success:
            with LOCK:
                servers.pop(name, None)
            save_servers_to_disk()
            return jsonify({'success': True, 'message': f'Server {name} deleted successfully'})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        app_logger.exception("api_delete_server error")
        return jsonify({'success': False, 'message': f'Error: {e}'})

@app.route('/api/server_logs/<server_name>')
def api_server_logs(server_name):
    try:
        logs = []
        if server_name in log_queues:
            q = log_queues[server_name]
            try:
                while not q.empty():
                    logs.append(q.get_nowait())
            except:
                pass
        
        if not logs:
            logfile = Config.LOGS_FOLDER / f"{server_name}.log"
            if logfile.exists():
                lines = tail_lines(str(logfile), n=Config.LOG_TAIL_LINES)
                logs = [{'timestamp': None, 'message': l, 'type': 'info'} for l in lines]
        
        return jsonify({'logs': logs})
    except Exception as e:
        app_logger.exception("api_server_logs error")
        return jsonify({'logs': [], 'error': 'Error'})

@app.route('/api/system_info')
def api_system_info():
    try:
        info = {
            'os': f"{platform.system()} {platform.release()}",
            'cpu_cores': psutil.cpu_count() if PSUTIL_AVAILABLE else None,
            'python_version': platform.python_version(),
            'active_servers': len([s for s in servers.values() if s.get('status') == 'Running']),
            'sites_folder': str(Config.SITES_FOLDER),
            'php_available': check_php_available(),
            'node_available': check_node_available(),
            'nginx_available': check_nginx_available()
        }
        return jsonify(info)
    except Exception as e:
        app_logger.exception("api_system_info error")
        return jsonify({})

# =========================
# Main Application
# =========================
if __name__ == '__main__':
    app_logger.info("Unified Server Administrator - Production Ready")
    app_logger.info("Nginx: %s, PHP: %s, Node.js: %s", 
                   check_nginx_available(), check_php_available(), check_node_available())
    
    # Load persisted servers
    load_servers_from_disk()
    
    try:
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
    except KeyboardInterrupt:
        app_logger.info("Shutting down...")
    except Exception as e:
        app_logger.exception("Fatal app error")
        sys.exit(1)