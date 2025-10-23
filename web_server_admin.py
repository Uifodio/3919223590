#!/usr/bin/env python3
"""
Modern Server Administrator - Production (final polish)

- Persistent server registry (servers.json)
- Background monitor for auto-refresh (updates UI without manual refresh)
- Fixed open_browser (returns usable URL, optional local open)
- Robust uploads (zip, multiple-files), atomic extraction & recursive import
- Per-server rotating logs + in-memory queues (UI tail + file fallback)
- ThreadPoolExecutor for async IO
- Toggleable runtime options (exposed as constants for now)
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
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

import logging
import logging.handlers
import platform

# Optional speed: if psutil is available use it for port checks; otherwise fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except Exception:
    PSUTIL_AVAILABLE = False

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# -------------------------
# Runtime options (expose these)
# -------------------------
RUNTIME_OPTIONS = {
    'AUTO_REFRESH_ON_LOAD': True,      # backend ensures fresh server states when dashboard loads
    'AUTO_REFRESH_INTERVAL': 2.0,      # seconds between background refreshes (low = faster UI updates)
    'AUTO_RESTORE_RUNNING': False,     # attempt to restart servers that were running at shutdown
    'AUTO_START_DISCOVERED': False,    # whether to auto-start discovered sites in sites/
    'BIND_ALL_DEFAULT': True,          # child servers bind to 0.0.0.0 by default for multi-device access
    'MAX_WORKERS': 32,                 # threadpool size for concurrent uploads/etc.
    'LOG_TAIL_LINES': 200,             # fallback lines read from file if in-memory queue empty
    'DELETE_SITE_ON_REMOVE': False,    # default behavior when deleting a server
    'ALLOW_REMOTE_OPEN_BROWSER': True  # allow returning remote host IP in open_browser response
}

# -------------------------
# Paths and globals
# -------------------------
app = Flask(__name__)
app.secret_key = 'modern_server_admin_2024'

ROOT = Path.cwd()
SITES_FOLDER = ROOT / 'sites'
LOGS_FOLDER = ROOT / 'logs'
PERSIST_FILE = ROOT / 'servers.json'
CADDY_FOLDER = ROOT / 'caddy'
SETTINGS_FILE = ROOT / 'settings.json'

ALLOWED_EXTENSIONS = {'txt','pdf','png','jpg','jpeg','gif','mp4','avi','mov','mkv','wmv','flv','webm',
                      'php','html','css','js','json','xml','md','py','sql','zip','rar','7z'}

for d in (SITES_FOLDER, LOGS_FOLDER, CADDY_FOLDER):
    os.makedirs(d, exist_ok=True)

EXECUTOR = ThreadPoolExecutor(max_workers=RUNTIME_OPTIONS['MAX_WORKERS'])

# in-memory state
servers = {}           # name -> metadata (persisted)
server_processes = {}  # name -> subprocess.Popen
log_queues = {}        # name -> Queue()

LOCK = threading.RLock()

# Logging
app_logger = logging.getLogger('msa_app')
app_logger.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler(str(LOGS_FOLDER / 'msa_app.log'), maxBytes=5_000_000, backupCount=5, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
app_logger.addHandler(fh)
app_logger.addHandler(logging.StreamHandler(sys.stdout))

# -------------------------
# Utility functions
# -------------------------
def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def human_size(path):
    try:
        s = os.path.getsize(path)
        for unit in ['B','KB','MB','GB','TB']:
            if s < 1024.0: return f"{s:.1f} {unit}"
            s /= 1024.0
    except:
        return "Unknown"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def secure_name(n):
    return secure_filename(n) or f"site-{int(time.time())}"

# port check: prefer psutil for faster accurate checking; fallback to socket connect
def is_port_in_use(port:int, host='0.0.0.0') -> bool:
    try:
        if PSUTIL_AVAILABLE:
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port == int(port):
                    # if host specified, check ip matches or host is wildcard
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

# -------------------------
# Caddy Web Server Management
# -------------------------
def get_caddy_path():
    """Get Caddy executable path"""
    if platform.system() == 'Windows':
        caddy_exe = CADDY_FOLDER / 'caddy.exe'
    else:
        caddy_exe = CADDY_FOLDER / 'caddy'
    
    if caddy_exe.exists():
        return str(caddy_exe)
    
    # Fallback to system caddy
    return shutil.which('caddy') or 'caddy'

def download_caddy():
    """Download and install Caddy web server"""
    try:
        if platform.system() == 'Windows':
            url = "https://caddyserver.com/api/download?os=windows&arch=amd64&p=github.com%2Fcaddyserver%2Fcaddy%2Fv2%2Fmodules%2Fstandard"
            filename = "caddy.exe"
        else:
            url = "https://caddyserver.com/api/download?os=linux&arch=amd64&p=github.com%2Fcaddyserver%2Fcaddy%2Fv2%2Fmodules%2Fstandard"
            filename = "caddy"
        
        caddy_path = CADDY_FOLDER / filename
        
        if caddy_path.exists():
            return True, "Caddy already installed"
        
        app_logger.info(f"Downloading Caddy from {url}")
        
        # Download Caddy
        import urllib.request
        urllib.request.urlretrieve(url, caddy_path)
        
        # Make executable on Unix systems
        if platform.system() != 'Windows':
            os.chmod(caddy_path, 0o755)
        
        app_logger.info(f"Caddy downloaded to {caddy_path}")
        return True, f"Caddy installed successfully"
        
    except Exception as e:
        app_logger.exception("Failed to download Caddy")
        return False, f"Failed to download Caddy: {str(e)}"

def check_caddy_available():
    """Check if Caddy is available"""
    try:
        caddy_path = get_caddy_path()
        result = subprocess.run([caddy_path, 'version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def create_caddy_config(site_name, site_path, port, server_type):
    """Create Caddy configuration for a site"""
    config_dir = CADDY_FOLDER / 'configs'
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / f"{site_name}.Caddyfile"
    
    if server_type == 'PHP':
        # Caddy with PHP support (using built-in PHP handler)
        config_content = f""":{port} {{
    root * {site_path}
    file_server
    
    # Handle PHP files with built-in PHP support
    try_files {{path}} {{path}}/ /index.php
    php_fastcgi unix//var/run/php/php-fpm.sock {{
        index index.php index.html index.htm
    }}
    
    # Fallback to static files if PHP not available
    @php {{
        path *.php
    }}
    handle @php {{
        try_files {{path}} /index.html
        file_server
    }}
    
    log {{
        output file {LOGS_FOLDER / f"{site_name}_caddy.log"}
        format json
    }}
}}"""
    else:
        # Caddy for static files
        config_content = f""":{port} {{
    root * {site_path}
    file_server
    
    # Try common index files
    try_files {{path}} {{path}}/ /index.html /index.php /index.htm
    
    log {{
        output file {LOGS_FOLDER / f"{site_name}_caddy.log"}
        format json
    }}
}}"""
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    return str(config_file)

def start_caddy_server(site_name, site_path, port, server_type):
    """Start Caddy server for a site"""
    try:
        if not check_caddy_available():
            # Try to download Caddy
            success, message = download_caddy()
            if not success:
                return False, f"Caddy not available: {message}"
        
        caddy_path = get_caddy_path()
        config_file = create_caddy_config(site_name, site_path, port, server_type)
        
        # Start Caddy process
        process = subprocess.Popen([
            caddy_path, 'run', '--config', config_file, '--adapter', 'caddyfile'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Give it a moment to start
        time.sleep(1)
        
        if process.poll() is None:
            return True, "Caddy server started"
        else:
            return False, "Caddy failed to start"
            
    except Exception as e:
        app_logger.exception("Failed to start Caddy server")
        return False, f"Failed to start Caddy: {str(e)}"

# -------------------------
# System checks
# -------------------------
# PHP functionality removed - Caddy handles all web serving

def get_node_path():
    return shutil.which('node') or 'node'

def check_node_available():
    try:
        n = get_node_path()
        r = subprocess.run([n,'--version'], capture_output=True, text=True, timeout=3)
        return r.returncode == 0
    except:
        return False

# -------------------------
# Logging helpers
# -------------------------
def get_server_logger(name):
    logger = logging.getLogger(f"msa_server_{name}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    log_file = LOGS_FOLDER / f"{name}.log"
    fh = logging.handlers.RotatingFileHandler(str(log_file), maxBytes=2_000_000, backupCount=3, encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(fh)
    return logger

# -------------------------
# Persistence helpers
# -------------------------
def save_servers_to_disk():
    try:
        with LOCK:
            minimal = {}
            for name, meta in servers.items():
                # only persist serializable fields
                minimal[name] = {
                    'name': meta.get('name'),
                    'folder': meta.get('folder'),
                    'port': meta.get('port'),
                    'type': meta.get('type'),
                    'status': meta.get('status'),
                    'start_time': meta.get('start_time')
                }
        with open(PERSIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(minimal, f, indent=2)
    except Exception:
        app_logger.exception("save_servers_to_disk failed")

def load_servers_from_disk():
    if not PERSIST_FILE.exists():
        return
    try:
        with open(PERSIST_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with LOCK:
            for name, meta in data.items():
                # only register if folder still exists
                folder = meta.get('folder')
                if folder and Path(folder).exists():
                    servers[name] = {
                        'name': meta.get('name', name),
                        'folder': folder,
                        'port': meta.get('port'),
                        'type': meta.get('type', 'HTTP'),
                        'status': meta.get('status','Stopped'),
                        'start_time': meta.get('start_time')
                    }
    except Exception:
        app_logger.exception("load_servers_from_disk failed")

# -------------------------
# Folder import / upload
# -------------------------
def import_folder_recursive(src: str, dest_basename: str = None) -> Tuple[bool,str]:
    srcp = Path(src)
    if not srcp.exists() or not srcp.is_dir():
        return False, "Source not a directory"
    if not dest_basename:
        dest_basename = f"{srcp.name}-{int(time.time())}"
    dest = SITES_FOLDER / secure_name(dest_basename)
    try:
        shutil.copytree(srcp, dest, dirs_exist_ok=True)
        app_logger.info("Imported folder %s -> %s", src, dest)
        return True, str(dest)
    except Exception:
        app_logger.exception("import_folder failed")
        return False, "Import failed"

def extract_zip_to_sites(zip_path: str, dest_basename: str = None) -> Tuple[bool,str]:
    """Extract ZIP file to sites folder with proper structure preservation"""
    tmpdir = tempfile.mkdtemp(prefix='msa_extract_')
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Get list of files and filter out system files
            file_list = [f for f in z.namelist() if not f.startswith('__MACOSX') and not f.startswith('.DS_Store')]
            
            if not file_list:
                return False, "ZIP file is empty or contains only system files"
            
            # Extract all files preserving directory structure
            z.extractall(tmpdir, members=file_list)
            
            # Find the root directory structure
            extracted_path = Path(tmpdir)
            entries = [p for p in extracted_path.iterdir() if not p.name.startswith('.')]
            
            if len(entries) == 1 and entries[0].is_dir():
                # Single directory - use it as root (this is the correct behavior)
                target_name = dest_basename or entries[0].name
                dest = SITES_FOLDER / secure_name(target_name)
                
                # Move directory atomically
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(entries[0]), str(dest))
                
            elif len(entries) > 1:
                # Multiple files/directories - create a container directory
                target_name = dest_basename or f"site-{int(time.time())}"
                dest = SITES_FOLDER / secure_name(target_name)
                os.makedirs(dest, exist_ok=True)
                
                # Move all items into the container
                for item in entries:
                    dest_item = dest / item.name
                    if item.is_dir():
                        if dest_item.exists():
                            shutil.rmtree(dest_item)
                        shutil.move(str(item), str(dest_item))
                    else:
                        shutil.move(str(item), str(dest_item))
            else:
                return False, "No valid content found in ZIP file"
            
            # Check if we have a real index file (don't create dummy ones)
            index_files = ['index.html', 'index.php', 'index.htm', 'default.html', 'index.js']
            has_real_index = any((dest / f).exists() for f in index_files)
            
            if not has_real_index:
                # Only create a minimal index if absolutely necessary
                app_logger.warning(f"No index file found in {dest}, site may not work properly")
            
            app_logger.info("Extracted zip %s -> %s", zip_path, dest)
            return True, str(dest)
            
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file format"
    except Exception as e:
        app_logger.exception("extract_zip failed")
        return False, f"Extraction failed: {str(e)}"
    finally:
        try:
            shutil.rmtree(tmpdir)
        except:
            pass

# -------------------------
# Process management
# -------------------------
def _create_node_script(folder_abs: str, port:int, bind_all:bool=True) -> str:
    bind = '0.0.0.0' if bind_all else '127.0.0.1'
    script = Path(folder_abs) / f"msa_temp_server_{port}.js"
    content = f"""
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const siteRoot = {json.dumps(folder_abs)};
const server = http.createServer((req,res) => {{
  const parsed = url.parse(req.url);
  let p = parsed.pathname;
  if (p === '/') p = '/index.html';
  const full = path.join(siteRoot, p);
  fs.readFile(full, (err, data) => {{
    if (err) {{
      res.writeHead(404, {{'Content-Type':'text/html'}});
      res.end('<h1>404</h1>');
      return;
    }}
    const ext = path.extname(full);
    const mimes = {{'.html':'text/html','.css':'text/css','.js':'application/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.gif':'image/gif','.svg':'image/svg+xml'}};
    res.writeHead(200, {{'Content-Type': mimes[ext] || 'text/plain'}});
    res.end(data);
  }});
}});
server.listen({port}, '{bind}', () => console.log('Node listening http://{bind}:{port}'));
"""
    script.write_text(content, encoding='utf-8')
    return str(script)

def start_server_process(name: str, folder: str, port: int, server_type: str, bind_all: bool = True, health_wait: float = 0.2) -> Tuple[bool,str]:
    """Start server process using Caddy for production-grade support"""
    logger = get_server_logger(name)
    try:
        folder_abs = str(Path(folder).absolute())
        
        # Use Caddy for all server types for production-grade support
        if server_type in ['PHP', 'HTTP', 'Static']:
            # Try Caddy first (production-grade)
            if check_caddy_available():
                success, msg = start_caddy_server(name, folder_abs, port, server_type)
                if success:
                    # Find the Caddy process
                    time.sleep(1)
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if 'caddy' in proc.info['name'].lower() and str(port) in ' '.join(proc.info['cmdline']):
                                proc_obj = subprocess.Popen(['echo', 'dummy'])  # Create a dummy process object
                                proc_obj.pid = proc.info['pid']
                                with LOCK:
                                    server_processes[name] = proc_obj
                                    log_queues.setdefault(name, queue.Queue())
                                logger.info("Started Caddy server successfully")
                                return True, "Caddy server started"
                        except:
                            continue
                    return False, "Caddy started but process not found"
                else:
                    logger.warning(f"Caddy failed, falling back to built-in server: {msg}")
            
            # Fallback to built-in servers
            if server_type == 'HTTP':
                cmd = [sys.executable, '-m', 'http.server', str(int(port)), '--bind', ('0.0.0.0' if bind_all else '127.0.0.1')]
        elif server_type == 'Node.js':
            nodeexec = shutil.which('node')
            if not nodeexec:
                return False, "Node.js not available"
            script = _create_node_script(folder_abs, int(port), bind_all)
            cmd = [nodeexec, script]
        else:
            return False, "Unsupported server type"

        proc = subprocess.Popen(cmd, cwd=folder_abs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        with LOCK:
            server_processes[name] = proc
            log_queues.setdefault(name, queue.Queue())
        threading.Thread(target=_monitor_process_io, args=(name, proc), daemon=True).start()

        time.sleep(health_wait)
        if proc.poll() is not None:
            try:
                err = proc.stderr.read() if proc.stderr else ''
                out = proc.stdout.read() if proc.stdout else ''
            except:
                err = out = ''
            with LOCK:
                server_processes.pop(name, None)
                log_queues.pop(name, None)
            msg = (err.strip() or out.strip() or "Exiting immediately")
            logger.error("Health-check failed: %s", msg)
            return False, msg

        logger.info("Started process successfully")
        return True, "Started"
    except Exception:
        app_logger.exception("start_server_process failed")
        return False, "Failed to start process"

def _monitor_process_io(name: str, proc: subprocess.Popen):
    logger = get_server_logger(name)
    q = log_queues.setdefault(name, queue.Queue())
    def push(m,t='info'):
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
                try:
                    rem = proc.stdout.read() if proc.stdout else ''
                    for l in rem.splitlines(): logger.info(l); push(l,'info')
                except: pass
                try:
                    rem = proc.stderr.read() if proc.stderr else ''
                    for l in rem.splitlines(): logger.error(l); push(l,'error')
                except: pass
                break
            time.sleep(0.02)
    except Exception:
        logger.exception("monitor io error")
    finally:
        with LOCK:
            if name in servers:
                servers[name]['status'] = 'Stopped'
        logger.info("Process monitor ended")

# -------------------------
# Background monitor & persistence
# -------------------------
def monitor_loop():
    """Enhanced background monitor with auto-refresh and persistence"""
    app_logger.info("Background monitor started (interval %s)", RUNTIME_OPTIONS['AUTO_REFRESH_INTERVAL'])
    interval = float(RUNTIME_OPTIONS['AUTO_REFRESH_INTERVAL'])
    last_cleanup = time.time()
    
    while True:
        try:
            with LOCK:
                # Update server statuses
                for name, meta in list(servers.items()):
                    proc = server_processes.get(name)
                    port = meta.get('port')
                    
                    if proc:
                        if proc.poll() is None:
                            # Process is running
                            if meta.get('status') != 'Running':
                                meta['status'] = 'Running'
                                meta['start_time'] = now_str()
                        else:
                            # Process has died
                            meta['status'] = 'Stopped'
                            # Clean up dead process
                            server_processes.pop(name, None)
                            log_queues.pop(name, None)
                    else:
                        # No process - check if port is in use by external process
                        if port and is_port_in_use(port, '0.0.0.0'):
                            if meta.get('status') != 'Running':
                                meta['status'] = 'Running (External)'
                        else:
                            meta['status'] = 'Stopped'
                
                # Periodic cleanup of orphaned processes
                if time.time() - last_cleanup > 300:  # Every 5 minutes
                    cleanup_orphaned_processes()
                    last_cleanup = time.time()
                
                # Auto-restart servers if enabled
                if RUNTIME_OPTIONS['AUTO_RESTORE_RUNNING']:
                    for name, meta in servers.items():
                        if meta.get('status') == 'Stopped' and meta.get('auto_restart', False):
                            port = meta.get('port')
                            if port and not is_port_in_use(port, '0.0.0.0'):
                                success, msg = start_server_process(
                                    name, meta['folder'], port, meta.get('type', 'HTTP'),
                                    bind_all=RUNTIME_OPTIONS['BIND_ALL_DEFAULT']
                                )
                                if success:
                                    meta['status'] = 'Running'
                                    meta['start_time'] = now_str()
                                    app_logger.info(f"Auto-restarted server {name}")
            
            # Persist state
            save_servers_to_disk()
            
        except Exception as e:
            app_logger.exception("monitor_loop error: %s", str(e))
        
        time.sleep(interval)

def cleanup_orphaned_processes():
    """Clean up orphaned processes that are no longer tracked"""
    try:
        with LOCK:
            # Get all tracked process PIDs
            tracked_pids = set()
            for proc in server_processes.values():
                if proc and proc.poll() is None:
                    tracked_pids.add(proc.pid)
            
            # Find orphaned log queues
            orphaned_queues = []
            for name, queue in log_queues.items():
                if name not in servers:
                    orphaned_queues.append(name)
            
            # Clean up orphaned queues
            for name in orphaned_queues:
                log_queues.pop(name, None)
                app_logger.info(f"Cleaned up orphaned log queue for {name}")
                
    except Exception as e:
        app_logger.exception("cleanup_orphaned_processes error: %s", str(e))

# Start monitor thread
t = threading.Thread(target=monitor_loop, daemon=True)
t.start()

# -------------------------
# Discover sites on boot & load persisted servers
# -------------------------
def discover_and_load():
    # load persisted
    load_servers_from_disk()
    # scan sites folder and register any non-registered folders
    for entry in SITES_FOLDER.iterdir():
        if entry.is_dir():
            name_base = secure_name(entry.name)
            with LOCK:
                if name_base not in servers:
                    # choose unique name
                    n = name_base
                    i = 1
                    while n in servers:
                        n = f"{name_base}-{i}"; i += 1
                    servers[n] = {
                        'name': n,
                        'folder': str(entry),
                        'port': None,
                        'type': 'HTTP',
                        'status': 'Stopped',
                        'start_time': None
                    }
    # optionally auto-start discovered (disabled by default)
    if RUNTIME_OPTIONS['AUTO_START_DISCOVERED']:
        with LOCK:
            to_start = [ (n,s) for n,s in servers.items() if s.get('status')!='Running' ]
        for name, meta in to_start:
            if not meta.get('port'):
                p = 8000
                while p < 65535 and (is_port_in_use(p,'0.0.0.0') or any(s.get('port')==p for s in servers.values())):
                    p += 1
                meta['port'] = p
            success,msg = start_server_process(name, meta['folder'], meta['port'], meta['type'], bind_all=RUNTIME_OPTIONS['BIND_ALL_DEFAULT'])
            with LOCK:
                if success:
                    meta['status'] = 'Running'
                    meta['start_time'] = now_str()
                else:
                    meta['status'] = 'Stopped'

# Load settings and discover sites
if SETTINGS_FILE.exists():
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            saved_settings = json.load(f)
        # Update RUNTIME_OPTIONS with saved settings
        for key, value in saved_settings.items():
            if key in RUNTIME_OPTIONS:
                RUNTIME_OPTIONS[key] = value
        app_logger.info("Settings loaded from disk")
    except Exception as e:
        app_logger.warning(f"Failed to load settings from disk: {e}")

discover_and_load()

# If AUTO_RESTORE_RUNNING True, try to start servers that were previously 'Running' on disk
if RUNTIME_OPTIONS['AUTO_RESTORE_RUNNING']:
    with LOCK:
        to_restore = [ (n,m) for n,m in servers.items() if m.get('status')=='Running' ]
    for name, meta in to_restore:
        port = meta.get('port') or 8000
        while is_port_in_use(port,'0.0.0.0') or any(s.get('port')==port for s in servers.values() if s['name']!=name):
            port += 1
            if port > 65535: break
        success, msg = start_server_process(name, meta['folder'], port, meta.get('type','HTTP'), bind_all=RUNTIME_OPTIONS['BIND_ALL_DEFAULT'])
        with LOCK:
            if success:
                meta['status'] = 'Running'
                meta['port'] = port
                meta['start_time'] = now_str()
            else:
                meta['status'] = 'Stopped'

# -------------------------
# Routes
# -------------------------
@app.route('/')
def index():
    # UI unchanged; front-end will call /api/servers automatically
    return render_template('index.html', servers=servers, current_folder=str(SITES_FOLDER))

@app.route('/api/servers')
def api_servers():
    # returns up-to-date server list (monitor loop keeps fresh)
    with LOCK:
        out = {}
        for name, s in servers.items():
            out[name] = {
                'name': s.get('name'),
                'folder': s.get('folder'),
                'port': s.get('port'),
                'type': s.get('type'),
                'status': s.get('status'),
                'start_time': s.get('start_time')
            }
    return jsonify(out)

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """Manual refresh endpoint with performance optimizations"""
    try:
        start_time = time.time()
        discover_and_load()
        
        # Update server statuses
        with LOCK:
            for name, meta in list(servers.items()):
                proc = server_processes.get(name)
                port = meta.get('port')
                
                if proc and proc.poll() is None:
                    meta['status'] = 'Running'
                elif port and is_port_in_use(port, '0.0.0.0'):
                    meta['status'] = 'Running (External)'
                else:
                    meta['status'] = 'Stopped'
        
        save_servers_to_disk()
        
        duration = time.time() - start_time
        return jsonify({
            'success': True, 
            'message': f'Refreshed in {duration:.2f}s',
            'duration': duration,
            'timestamp': now_str()
        })
    except Exception as e:
        app_logger.exception("api_refresh error")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/status')
def api_status():
    """Quick status check for auto-refresh"""
    try:
        with LOCK:
            running_count = len([s for s in servers.values() if s.get('status') == 'Running'])
            total_count = len(servers)
            
        return jsonify({
            'success': True,
            'running_servers': running_count,
            'total_servers': total_count,
            'timestamp': now_str(),
            'auto_refresh_interval': RUNTIME_OPTIONS['AUTO_REFRESH_INTERVAL']
        })
    except Exception as e:
        app_logger.exception("api_status error")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/add_server', methods=['POST'])
def api_add_server():
    try:
        data = request.get_json() or {}
        folder = data.get('folder','').strip()
        port = data.get('port', 8000)
        server_type = data.get('type','HTTP')
        auto_import = bool(data.get('auto_import', True))
        auto_start = bool(data.get('auto_start', True))
        if not folder:
            return jsonify({'success': False, 'message': 'Select folder'})

        folder_p = Path(folder)
        if folder_p.exists() and folder_p.is_dir() and SITES_FOLDER in folder_p.parents:
            final = str(folder_p)
        elif folder_p.exists() and folder_p.is_dir() and auto_import:
            ok,res = import_folder_recursive(str(folder_p), dest_basename=folder_p.name)
            if not ok: return jsonify({'success': False, 'message': f'Import failed: {res}'})
            final = res
        else:
            dest = SITES_FOLDER / secure_name(folder_p.name or f"site-{int(time.time())}")
            os.makedirs(dest, exist_ok=True)
            final = str(dest)

        try:
            port = int(port)
        except:
            return jsonify({'success': False, 'message': 'Invalid port'})
        if port<1024 or port>65535: return jsonify({'success': False, 'message':'Port out of range'})

        orig = port
        while is_port_in_use(port,'0.0.0.0') or any(s.get('port')==port for s in servers.values()):
            port += 1
            if port>65535: return jsonify({'success': False, 'message':f'No free port from {orig}'})

        base = secure_name(Path(final).name)
        with LOCK:
            server_name = base
            i=1
            while server_name in servers:
                server_name = f"{base}-{i}"; i+=1
            servers[server_name] = {
                'name': server_name,
                'folder': final,
                'port': port,
                'type': server_type,
                'status': 'Stopped',
                'start_time': None
            }
        # attempt start
        success,msg = start_server_process(server_name, final, port, server_type, bind_all=RUNTIME_OPTIONS['BIND_ALL_DEFAULT'])
        with LOCK:
            if success:
                servers[server_name]['status'] = 'Running'
                servers[server_name]['start_time'] = now_str()
            else:
                servers.pop(server_name, None)
                save_servers_to_disk()
                return jsonify({'success': False, 'message': f'Start failed: {msg}'})
        save_servers_to_disk()
        return jsonify({'success': True, 'message': f'Started {server_name} on port {port}'})
    except Exception:
        app_logger.exception("api_add_server error")
        return jsonify({'success': False, 'message': 'Error'})

@app.route('/api/stop_server', methods=['POST'])
def api_stop_server():
    try:
        data = request.get_json() or {}
        name = data.get('name')
        if not name: return jsonify({'success': False, 'message': 'Missing name'})
        with LOCK:
            proc = server_processes.get(name)
        if not proc:
            with LOCK:
                if name in servers: servers[name]['status'] = 'Stopped'
            save_servers_to_disk()
            return jsonify({'success': False, 'message': 'Not running'})
        try:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
        except: pass
        with LOCK:
            server_processes.pop(name, None)
            log_queues.pop(name, None)
            if name in servers: servers[name]['status'] = 'Stopped'
        save_servers_to_disk()
        return jsonify({'success': True, 'message': 'Stopped'})
    except Exception:
        app_logger.exception("api_stop_server error")
        return jsonify({'success': False, 'message': 'Error'})

@app.route('/api/start_server', methods=['POST'])
def api_start_server():
    try:
        data = request.get_json() or {}
        name = data.get('name')
        if not name or name not in servers:
            return jsonify({'success': False, 'message': 'Server not found'})
        with LOCK:
            meta = servers[name]
        if meta.get('status') == 'Running':
            return jsonify({'success': False, 'message': 'Already running'})
        port = meta.get('port') or 8000
        while is_port_in_use(port,'0.0.0.0') or any(s.get('port')==port for s in servers.values() if s['name']!=name):
            port += 1
            if port>65535: return jsonify({'success': False,'message':'No free port'})
        success,msg = start_server_process(name, meta['folder'], port, meta.get('type','HTTP'), bind_all=RUNTIME_OPTIONS['BIND_ALL_DEFAULT'])
        with LOCK:
            if success:
                meta['port'] = port
                meta['status'] = 'Running'
                meta['start_time'] = now_str()
                save_servers_to_disk()
                return jsonify({'success': True, 'message':'Started'})
            else:
                return jsonify({'success': False, 'message': msg})
    except Exception:
        app_logger.exception("api_start_server error")
        return jsonify({'success': False, 'message': 'Error'})

@app.route('/api/delete_server', methods=['POST'])
def api_delete_server():
    try:
        data = request.get_json() or {}
        name = data.get('name'); delete_files = bool(data.get('delete_files', RUNTIME_OPTIONS['DELETE_SITE_ON_REMOVE']))
        if not name or name not in servers:
            return jsonify({'success': False, 'message': 'Not found'})
        with LOCK:
            proc = server_processes.pop(name, None)
        if proc:
            try:
                proc.terminate(); proc.wait(timeout=3)
            except:
                try: proc.kill(); proc.wait()
                except: pass
        with LOCK:
            meta = servers.pop(name, None)
            log_queues.pop(name, None)
        if delete_files and meta and meta.get('folder'):
            try:
                shutil.rmtree(meta['folder'])
            except Exception:
                app_logger.exception("delete site files error")
                return jsonify({'success': False, 'message': 'Server deleted but failed to delete files'})
        save_servers_to_disk()
        return jsonify({'success': True, 'message': 'Deleted'})
    except Exception:
        app_logger.exception("api_delete_server error")
        return jsonify({'success': False, 'message': 'Error'})

@app.route('/api/upload_zip', methods=['POST'])
def api_upload_zip():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file'})
        f = request.files['file']
        if f.filename == '':
            return jsonify({'success': False, 'message': 'Empty filename'})
        if not (f.filename.lower().endswith('.zip') or allowed_file(f.filename)):
            return jsonify({'success': False, 'message': 'Not allowed type'})
        name = request.form.get('name')
        auto_register = request.form.get('auto_register','true').lower()!='false'
        auto_start = request.form.get('auto_start','false').lower()=='true'
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.zip')
        os.close(tmp_fd)
        f.save(tmp_path)
        ok,res = extract_zip_to_sites(tmp_path, dest_basename=name)
        os.remove(tmp_path)
        if not ok:
            return jsonify({'success': False, 'message': res})
        site_path = res
        registered = None
        if auto_register:
            base = secure_name(Path(site_path).name)
            with LOCK:
                n = base; i=1
                while n in servers: n = f"{base}-{i}"; i+=1
                servers[n] = {'name': n, 'folder': site_path, 'port': None, 'type':'HTTP', 'status':'Stopped','start_time':None}
                registered = n
            if auto_start:
                p = 8000
                while is_port_in_use(p,'0.0.0.0') or any(s.get('port')==p for s in servers.values()):
                    p+=1
                success,msg = start_server_process(registered, site_path, p, 'HTTP', bind_all=RUNTIME_OPTIONS['BIND_ALL_DEFAULT'])
                if success:
                    with LOCK:
                        servers[registered]['port'] = p; servers[registered]['status']='Running'; servers[registered]['start_time']=now_str()
                else:
                    return jsonify({'success': False, 'message': f'Imported but failed to auto-start: {msg}', 'registered': registered})
        save_servers_to_disk()
        return jsonify({'success': True, 'site_path': site_path, 'registered': registered})
    except Exception:
        app_logger.exception("api_upload_zip error")
        return jsonify({'success': False, 'message': 'Error'})

@app.route('/api/upload_folder', methods=['POST'])
def api_upload_folder():
    """Upload multiple files preserving directory structure - bulletproof for mobile"""
    try:
        files = request.files.getlist('files[]')
        folder_name = request.form.get('folder_name') or f"site-{int(time.time())}"
        auto_register = request.form.get('auto_register', 'true').lower() != 'false'
        auto_start = request.form.get('auto_start', 'false').lower() == 'true'
        
        if not files:
            return jsonify({'success': False, 'message': 'No files provided'})
        
        # Create destination directory
        dest = SITES_FOLDER / secure_name(folder_name)
        os.makedirs(dest, exist_ok=True)
        
        uploaded_files = []
        errors = []
        
        for f in files:
            if not f.filename:
                continue
                
            try:
                # Handle both webkitRelativePath (from folder selection) and regular filenames
                filename = f.filename
                
                # Check if this is from webkitdirectory (has webkitRelativePath)
                if hasattr(f, 'webkitRelativePath') and f.webkitRelativePath:
                    # Use webkitRelativePath to preserve directory structure
                    relative_path = f.webkitRelativePath
                    # Clean up the path
                    path_parts = [p for p in relative_path.split('/') if p and p != '.']
                else:
                    # Regular file upload - check for path separators
                    if '/' in filename or '\\' in filename:
                        path_parts = [p for p in Path(filename).parts if p and p != '.']
                    else:
                        path_parts = [filename]
                
                if not path_parts:
                    continue
                
                # Create the full destination path
                if len(path_parts) == 1:
                    # Single file
                    dest_file = dest / secure_name(path_parts[0])
                else:
                    # File in subdirectory
                    subdir = dest.joinpath(*[secure_name(p) for p in path_parts[:-1]])
                    subdir.mkdir(parents=True, exist_ok=True)
                    dest_file = subdir / secure_name(path_parts[-1])
                
                # Save the file
                f.save(str(dest_file))
                uploaded_files.append(str(dest_file.relative_to(dest)))
                
            except Exception as e:
                errors.append(f"Failed to save {f.filename}: {str(e)}")
                app_logger.warning("Failed to save file %s: %s", f.filename, str(e))
        
        if not uploaded_files:
            return jsonify({'success': False, 'message': 'No files were successfully uploaded'})
        
        # Check if we have a real index file (don't create dummy ones)
        index_files = ['index.html', 'index.php', 'index.htm', 'default.html', 'index.js']
        has_real_index = any((dest / f).exists() for f in index_files)
        
        if not has_real_index:
            # Only log a warning, don't create dummy files
            app_logger.warning(f"No index file found in {dest}, site may not work properly")
            # Create a simple directory listing instead
            index_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory Listing - {dest.name}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px; 
            background: #0d1117; 
            color: #f0f6fc; 
            margin: 0;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #0969da; margin-bottom: 20px; }}
        .info {{ background: #161b22; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .file-list {{ text-align: left; margin-top: 20px; }}
        .file-item {{ padding: 8px 0; color: #c9d1d9; border-bottom: 1px solid #30363d; }}
        .file-item:last-child {{ border-bottom: none; }}
        .success {{ color: #1a7f37; }}
        .error {{ color: #d1242f; }}
        a {{ color: #58a6ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Directory Listing</h1>
        <div class="info">
            <p>Files uploaded successfully. Click on any file to view it.</p>
            <p class="success">✓ {len(uploaded_files)} files uploaded successfully</p>
            {f'<p class="error">⚠ {len(errors)} files failed to upload</p>' if errors else ''}
        </div>
        <div class="file-list">
            <h3>Available Files:</h3>
            {''.join([f'<div class="file-item"><a href="{file_path}">📄 {file_path}</a></div>' for file_path in uploaded_files[:50]])}
            {f'<div class="file-item">... and {len(uploaded_files) - 50} more files</div>' if len(uploaded_files) > 50 else ''}
        </div>
    </div>
</body>
</html>'''
            
            with open(dest / 'index.html', 'w', encoding='utf-8') as f:
                f.write(index_content)
        
        registered = None
        if auto_register:
            base = secure_name(dest.name)
            with LOCK:
                n = base
                i = 1
                while n in servers:
                    n = f"{base}-{i}"
                    i += 1
                servers[n] = {
                    'name': n, 
                    'folder': str(dest), 
                    'port': None, 
                    'type': 'HTTP', 
                    'status': 'Stopped',
                    'start_time': None
                }
                registered = n
            
            if auto_start:
                # Find available port
                port = 8000
                while is_port_in_use(port, '0.0.0.0') or any(s.get('port') == port for s in servers.values()):
                    port += 1
                    if port > 65535:
                        break
                
                success, msg = start_server_process(registered, str(dest), port, 'HTTP', bind_all=RUNTIME_OPTIONS['BIND_ALL_DEFAULT'])
                if success:
                    with LOCK:
                        servers[registered]['port'] = port
                        servers[registered]['status'] = 'Running'
                        servers[registered]['start_time'] = now_str()
                else:
                    return jsonify({
                        'success': False, 
                        'message': f'Uploaded successfully but failed to auto-start: {msg}', 
                        'registered': registered
                    })
        
        save_servers_to_disk()
        
        result = {
            'success': True, 
            'site_path': str(dest),
            'uploaded_files': len(uploaded_files),
            'errors': len(errors)
        }
        if registered:
            result['registered'] = registered
        
        return jsonify(result)
        
    except Exception as e:
        app_logger.exception("api_upload_folder error")
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@app.route('/api/open_browser/<server_name>')
def api_open_browser(server_name):
    """Open server in browser - bulletproof for mobile and remote access"""
    try:
        if server_name not in servers:
            return jsonify({'success': False, 'message': 'Server not found'})
        
        meta = servers[server_name]
        port = meta.get('port')
        if not port:
            return jsonify({'success': False, 'message': 'Server not started'})
        
        # Get client information
        client_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
        
        # Determine the best URL to return
        if RUNTIME_OPTIONS['ALLOW_REMOTE_OPEN_BROWSER']:
            # Try to get the server's external IP
            try:
                # First try to get the IP from the request
                host_ip = request.host.split(':')[0]
                if host_ip in ('0.0.0.0', '', 'localhost', '127.0.0.1'):
                    # Get the actual server IP
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    host_ip = s.getsockname()[0]
                    s.close()
            except Exception:
                # Fallback to client IP or localhost
                host_ip = client_ip or '127.0.0.1'
        else:
            # Force localhost only
            host_ip = '127.0.0.1'
        
        # Build URLs for different scenarios
        urls = {
            'primary': f"http://{host_ip}:{port}",
            'localhost': f"http://127.0.0.1:{port}",
            'local_ip': f"http://{host_ip}:{port}"
        }
        
        # For mobile devices, prefer the external IP
        if is_mobile and RUNTIME_OPTIONS['ALLOW_REMOTE_OPEN_BROWSER']:
            primary_url = urls['local_ip']
        else:
            primary_url = urls['primary']
        
        # Check if server is actually running
        if not is_port_in_use(port, '0.0.0.0'):
            return jsonify({
                'success': False, 
                'message': 'Server is not actually running on the specified port',
                'url': primary_url
            })
        
        # Prepare response
        response_data = {
            'success': True,
            'url': primary_url,
            'urls': urls,
            'server_name': server_name,
            'port': port,
            'client_ip': client_ip,
            'is_mobile': is_mobile,
            'message': f'Server accessible at {primary_url}'
        }
        
        # If client specifically requests local opening
        if request.args.get('open_local', 'false').lower() == 'true':
            try:
                import webbrowser
                webbrowser.open(primary_url)
                response_data['message'] = 'Opening in local browser'
            except Exception as e:
                response_data['message'] = f'URL ready but failed to open locally: {str(e)}'
        
        return jsonify(response_data)
        
    except Exception as e:
        app_logger.exception("api_open_browser error")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/server_logs/<server_name>')
def api_server_logs(server_name):
    """Get server logs with live streaming support"""
    try:
        logs = []
        live_data = False
        
        # Get live logs from queue first
        if server_name in log_queues:
            q = log_queues[server_name]
            try:
                while not q.empty():
                    log_entry = q.get_nowait()
                    logs.append(log_entry)
                    live_data = True
            except Exception:
                pass
        
        # If no live logs, get from file
        if not logs:
            logfile = LOGS_FOLDER / f"{server_name}.log"
            if logfile.exists():
                lines = tail_lines(str(logfile), n=RUNTIME_OPTIONS['LOG_TAIL_LINES'])
                logs = [{'timestamp': None, 'message': l, 'type': 'info'} for l in lines]
        
        # Check if server is running for live indicator
        server_running = False
        if server_name in servers:
            server_running = servers[server_name].get('status') == 'Running'
        
        return jsonify({
            'logs': logs,
            'live_data': live_data,
            'server_running': server_running,
            'timestamp': now_str()
        })
    except Exception as e:
        app_logger.exception("api_server_logs error")
        return jsonify({'logs': [], 'error': str(e), 'live_data': False})

@app.route('/api/server_logs_stream/<server_name>')
def api_server_logs_stream(server_name):
    """Server-Sent Events endpoint for live log streaming"""
    def generate_logs():
        try:
            while True:
                logs = []
                live_data = False
                
                # Get live logs from queue
                if server_name in log_queues:
                    q = log_queues[server_name]
                    try:
                        while not q.empty():
                            log_entry = q.get_nowait()
                            logs.append(log_entry)
                            live_data = True
                    except Exception:
                        pass
                
                # Send logs as SSE
                if logs:
                    for log in logs:
                        yield f"data: {json.dumps(log)}\n\n"
                else:
                    # Send heartbeat
                    yield f"data: {json.dumps({'timestamp': now_str(), 'message': '', 'type': 'heartbeat'})}\n\n"
                
                time.sleep(1)  # 1 second interval
                
        except GeneratorExit:
            app_logger.info(f"Log stream closed for {server_name}")
        except Exception as e:
            app_logger.exception(f"Log stream error for {server_name}")
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
    
    return app.response_class(
        generate_logs(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

# PHP check removed - Caddy handles all web serving

@app.route('/api/check_node')
def api_check_node():
    try:
        ok = check_node_available()
        ver = subprocess.run([get_node_path(),'--version'], capture_output=True, text=True).stdout.strip() if ok else None
        return jsonify({'available': ok, 'version': ver})
    except Exception:
        app_logger.exception("api_check_node error")
        return jsonify({'available': False, 'version': None})

@app.route('/api/check_caddy')
def api_check_caddy():
    try:
        ok = check_caddy_available()
        if ok:
            caddy_path = get_caddy_path()
            ver = subprocess.run([caddy_path, 'version'], capture_output=True, text=True).stdout.strip()
        else:
            ver = None
        return jsonify({'available': ok, 'version': ver})
    except Exception:
        app_logger.exception("api_check_caddy error")
        return jsonify({'available': False, 'version': None})

@app.route('/api/install_caddy', methods=['POST'])
def api_install_caddy():
    try:
        success, message = download_caddy()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        app_logger.exception("api_install_caddy error")
        return jsonify({'success': False, 'message': str(e)})

def save_settings_to_disk():
    """Save current settings to disk"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(RUNTIME_OPTIONS, f, indent=2)
        app_logger.info("Settings saved to disk")
    except Exception as e:
        app_logger.warning(f"Failed to save settings to disk: {e}")

@app.route('/api/settings')
def api_get_settings():
    """Get current runtime settings"""
    try:
        return jsonify({
            'success': True,
            'settings': RUNTIME_OPTIONS.copy()
        })
    except Exception as e:
        app_logger.exception("api_get_settings error")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    """Update runtime settings with proper validation and persistence"""
    try:
        data = request.get_json() or {}
        updated = {}
        
        # Validate and update settings
        for key, value in data.items():
            if key in RUNTIME_OPTIONS:
                # Type validation and bounds checking
                if key in ['AUTO_REFRESH_ON_LOAD', 'AUTO_RESTORE_RUNNING', 'AUTO_START_DISCOVERED', 
                          'BIND_ALL_DEFAULT', 'DELETE_SITE_ON_REMOVE', 'ALLOW_REMOTE_OPEN_BROWSER']:
                    RUNTIME_OPTIONS[key] = bool(value)
                    updated[key] = bool(value)
                elif key == 'AUTO_REFRESH_INTERVAL':
                    RUNTIME_OPTIONS[key] = max(0.5, min(60.0, float(value)))
                    updated[key] = RUNTIME_OPTIONS[key]
                elif key == 'MAX_WORKERS':
                    RUNTIME_OPTIONS[key] = max(1, min(100, int(value)))
                    updated[key] = RUNTIME_OPTIONS[key]
                elif key == 'LOG_TAIL_LINES':
                    RUNTIME_OPTIONS[key] = max(10, min(1000, int(value)))
                    updated[key] = RUNTIME_OPTIONS[key]
        
        # Save settings to disk
        save_settings_to_disk()
        
        # Apply settings immediately
        if 'AUTO_REFRESH_INTERVAL' in updated:
            # Restart monitor with new interval
            global monitor_thread
            if 'monitor_thread' in globals():
                monitor_thread.cancel()
            start_monitor_thread()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated and saved successfully',
            'updated': updated,
            'current_settings': RUNTIME_OPTIONS.copy()
        })
    except Exception as e:
        app_logger.exception("api_update_settings error")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/system_info')
def api_system_info():
    try:
        os_name = platform.system()
        os_ver = platform.release()
        
        # Enhanced system info
        info = {
            'os': f"{os_name} {os_ver}",
            'architecture': platform.architecture()[0] if platform.architecture() else 'Unknown',
            'cpu_cores': (psutil.cpu_count() if PSUTIL_AVAILABLE else None),
            'python_version': platform.python_version(),
            'active_servers': len([s for s in servers.values() if s.get('status')=='Running']),
            'total_servers': len(servers),
            'sites_folder': str(SITES_FOLDER),
            'caddy_available': check_caddy_available(),
            'node_available': check_node_available(),
            'memory_total': (psutil.virtual_memory().total // (1024**3) if PSUTIL_AVAILABLE else None),
            'memory_available': (psutil.virtual_memory().available // (1024**3) if PSUTIL_AVAILABLE else None),
            'disk_free': (psutil.disk_usage('/').free // (1024**3) if PSUTIL_AVAILABLE else None)
        }
        
        # Add Caddy version if available
        if info['caddy_available']:
            try:
                caddy_path = get_caddy_path()
                caddy_ver = subprocess.run([caddy_path, 'version'], capture_output=True, text=True, timeout=3)
                if caddy_ver.returncode == 0:
                    info['caddy_version'] = caddy_ver.stdout.splitlines()[0] if caddy_ver.stdout else 'Unknown'
            except:
                info['caddy_version'] = 'Unknown'
        
        # Add Node.js version if available
        if info['node_available']:
            try:
                node_ver = subprocess.run([get_node_path(), '--version'], capture_output=True, text=True, timeout=3)
                if node_ver.returncode == 0:
                    info['node_version'] = node_ver.stdout.strip()
            except:
                info['node_version'] = 'Unknown'
        
        return jsonify(info)
    except Exception as e:
        app_logger.exception("api_system_info error")
        return jsonify({'error': str(e)})

# -------------------------
# Graceful shutdown
# -------------------------
def shutdown_all():
    app_logger.info("Shutting down child servers")
    with LOCK:
        items = list(server_processes.items())
    for name, proc in items:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except:
            try:
                proc.kill()
            except:
                pass
        with LOCK:
            server_processes.pop(name, None)
            log_queues.pop(name, None)
            if name in servers:
                servers[name]['status'] = 'Stopped'
    save_servers_to_disk()

# -------------------------
# Run app
# -------------------------
if __name__ == '__main__':
    app_logger.info("Modern Server Administrator - production-ready (final)")
    app_logger.info("Sites: %s, Logs: %s", SITES_FOLDER, LOGS_FOLDER)
    app_logger.info("Caddy available: %s, Node available: %s", check_caddy_available(), check_node_available())
    # persist and ensure discovered sites are registered
    save_servers_to_disk()
    # Start Flask with binding so UI is reachable from devices
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        shutdown_all()
        app_logger.info("Goodbye")
    except Exception:
        app_logger.exception("Fatal app error")
        shutdown_all()
        sys.exit(1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
