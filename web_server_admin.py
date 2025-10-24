#!/usr/bin/env python3
"""
Windows-Compatible Workspace Server - Enhanced Multi-Project Development Server

Features:
- Central reverse proxy on localhost:8000 (configurable)
- Support for PHP, Node.js, Python, and static sites simultaneously
- Windows + Linux compatible with auto-detection
- Self-contained and production-style
- Multiple project management through one interface
- Professional web dashboard with GitHub-themed UI
- Auto-installation of PHP and Node.js on Windows
- Real-time project monitoring and logging
- File upload and project import capabilities
- Route-based project access through central proxy

Enhanced from original Modern Server Administrator with:
- Reverse proxy functionality for unified access
- Better Windows compatibility and auto-setup
- Multi-project workspace management
- Enhanced UI with project routing
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

from flask import Flask, render_template, request, jsonify, Response, send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.serving import WSGIRequestHandler
import webbrowser
import mimetypes
from urllib.parse import urlparse, parse_qs

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
    'ALLOW_REMOTE_OPEN_BROWSER': True, # allow returning remote host IP in open_browser response
    'ENABLE_REVERSE_PROXY': True,      # enable reverse proxy functionality
    'PROXY_PORT': 8000,                # main proxy port
    'PROXY_HOST': '0.0.0.0',          # main proxy host
    'AUTO_OPEN_BROWSER': True,         # auto-open browser on Windows
    'WINDOWS_AUTO_INSTALL': True       # auto-install PHP/Node.js on Windows
}

# -------------------------
# Paths and globals
# -------------------------
app = Flask(__name__)
app.secret_key = 'modern_server_admin_2024'

ROOT = Path.cwd()
UPLOAD_FOLDER = ROOT / 'uploads'
SITES_FOLDER = ROOT / 'sites'
LOGS_FOLDER = ROOT / 'logs'
PERSIST_FILE = ROOT / 'servers.json'
PHP_LOCAL_FOLDER = ROOT / 'php'

# Windows-specific paths for auto-detection
WINDOWS_PHP_PATHS = [
    r'php_standalone\php.exe',  # Portable PHP
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

# Reverse proxy routes
proxy_routes = {}  # route -> server info

ALLOWED_EXTENSIONS = {'txt','pdf','png','jpg','jpeg','gif','mp4','avi','mov','mkv','wmv','flv','webm',
                      'php','html','css','js','json','xml','md','py','sql','zip','rar','7z'}

for d in (UPLOAD_FOLDER, SITES_FOLDER, LOGS_FOLDER, PHP_LOCAL_FOLDER):
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
# System checks
# -------------------------
def get_php_path():
    local = str(PHP_LOCAL_FOLDER / ('php.exe' if platform.system() == 'Windows' else 'php'))
    if Path(local).exists(): return local
    w = shutil.which('php')
    if w: return w
    if platform.system() == 'Windows':
        for p in [r'C:\php\php.exe', r'C:\xampp\php\php.exe', r'C:\wamp\bin\php\php.exe']:
            if Path(p).exists(): return p
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
    tmpdir = tempfile.mkdtemp(prefix='msa_extract_')
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmpdir)
        entries = [p for p in Path(tmpdir).iterdir() if not p.name.startswith('__MACOSX')]
        if len(entries) == 1 and entries[0].is_dir():
            target_name = dest_basename or entries[0].name
            dest = SITES_FOLDER / secure_name(target_name)
            shutil.move(str(entries[0]), str(dest))
        else:
            target_name = dest_basename or f"site-{int(time.time())}"
            dest = SITES_FOLDER / secure_name(target_name)
            os.makedirs(dest, exist_ok=True)
            for item in Path(tmpdir).iterdir():
                shutil.move(str(item), str(dest / item.name))
        app_logger.info("Extracted zip %s -> %s", zip_path, dest)
        return True, str(dest)
    except Exception:
        app_logger.exception("extract_zip failed")
        return False, "Extraction failed"
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
    logger = get_server_logger(name)
    try:
        folder_abs = str(Path(folder).absolute())
        if server_type == 'PHP':
            php = get_php_path()
            if not check_php_available():
                return False, "PHP not available"
            cmd = [php, '-S', f"{'0.0.0.0' if bind_all else '127.0.0.1'}:{int(port)}", '-t', folder_abs, '-d', 'display_errors=1', '-d', 'log_errors=1']
        elif server_type == 'HTTP':
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
    app_logger.info("Background monitor started (interval %s)", RUNTIME_OPTIONS['AUTO_REFRESH_INTERVAL'])
    interval = float(RUNTIME_OPTIONS['AUTO_REFRESH_INTERVAL'])
    while True:
        try:
            # update server entries: mark Running if process exists & listening; else Stopped
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
                        # if no process, but port is in use by some other program, consider it 'Running (external)'
                        if port and is_port_in_use(port, '0.0.0.0'):
                            meta['status'] = 'Running'
                        else:
                            meta['status'] = 'Stopped'
            # persist every cycle
            save_servers_to_disk()
        except Exception:
            app_logger.exception("monitor_loop error")
        time.sleep(interval)

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

# call discovery/load
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
    # manual refresh endpoint (UI can call)
    try:
        discover_and_load()
        return jsonify({'success': True, 'message': 'Refreshed'})
    except Exception as e:
        app_logger.exception("api_refresh error")
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
    try:
        # clients should prefer zip. But support multiple files with folder_name
        files = request.files.getlist('files[]')
        folder_name = request.form.get('folder_name') or f"site-{int(time.time())}"
        if not files:
            return jsonify({'success': False, 'message': 'No files'})
        dest = SITES_FOLDER / secure_name(folder_name)
        os.makedirs(dest, exist_ok=True)
        for f in files:
            filename = f.filename
            if '/' in filename or '\\' in filename:
                parts = Path(filename).parts
                subdir = dest.joinpath(*parts[:-1])
                subdir.mkdir(parents=True, exist_ok=True)
                f.save(str(subdir / secure_name(parts[-1])))
            else:
                f.save(str(dest / secure_name(filename)))
        # register
        base = secure_name(dest.name)
        with LOCK:
            n = base; i=1
            while n in servers: n = f"{base}-{i}"; i+=1
            servers[n] = {'name': n, 'folder': str(dest), 'port': None, 'type':'HTTP', 'status':'Stopped','start_time':None}
        save_servers_to_disk()
        return jsonify({'success': True, 'registered': n, 'site_path': str(dest)})
    except Exception:
        app_logger.exception("api_upload_folder error")
        return jsonify({'success': False, 'message': 'Error'})

@app.route('/api/open_browser/<server_name>')
def api_open_browser(server_name):
    try:
        if server_name not in servers:
            return jsonify({'success': False, 'message': 'Server not found'})
        meta = servers[server_name]
        port = meta.get('port')
        if not port:
            return jsonify({'success': False, 'message': 'Server not started'})
        # Determine host IP to return (so remote clients can open it)
        host_ip = request.host.split(':')[0]
        if host_ip in ('0.0.0.0', ''):
            # try to find machine IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                host_ip = s.getsockname()[0]
                s.close()
            except Exception:
                host_ip = request.remote_addr or '127.0.0.1'
        # if remote open not allowed, return localhost/127.0.0.1
        if not RUNTIME_OPTIONS['ALLOW_REMOTE_OPEN_BROWSER']:
            host_ip = '127.0.0.1'
        url = f"http://{host_ip}:{port}"
        # if client wants local host to open
        if request.args.get('open_local','false').lower() == 'true':
            try:
                import webbrowser
                webbrowser.open(url)
                return jsonify({'success': True, 'url': url, 'message': 'Opening locally'})
            except Exception as e:
                return jsonify({'success': False, 'url': url, 'message': f'Failed to open local: {e}'})
        return jsonify({'success': True, 'url': url})
    except Exception:
        app_logger.exception("api_open_browser error")
        return jsonify({'success': False, 'message': 'Error'})

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
            logfile = LOGS_FOLDER / f"{server_name}.log"
            if logfile.exists():
                lines = tail_lines(str(logfile), n=RUNTIME_OPTIONS['LOG_TAIL_LINES'])
                logs = [{'timestamp': None, 'message': l, 'type': 'info'} for l in lines]
        return jsonify({'logs': logs})
    except Exception:
        app_logger.exception("api_server_logs error")
        return jsonify({'logs': [], 'error':'Error'})

@app.route('/api/check_php')
def api_check_php():
    try:
        ok = check_php_available()
        ver = subprocess.run([get_php_path(),'--version'], capture_output=True, text=True).stdout.splitlines()[0] if ok else None
        return jsonify({'available': ok, 'version': ver})
    except Exception:
        app_logger.exception("api_check_php error")
        return jsonify({'available': False, 'version': None})

@app.route('/api/check_node')
def api_check_node():
    try:
        ok = check_node_available()
        ver = subprocess.run([get_node_path(),'--version'], capture_output=True, text=True).stdout.strip() if ok else None
        return jsonify({'available': ok, 'version': ver})
    except Exception:
        app_logger.exception("api_check_node error")
        return jsonify({'available': False, 'version': None})

@app.route('/api/system_info')
def api_system_info():
    try:
        os_name = platform.system(); os_ver = platform.release()
        info = {
            'os': f"{os_name} {os_ver}",
            'cpu_cores': (psutil.cpu_count() if PSUTIL_AVAILABLE else None),
            'python_version': platform.python_version(),
            'active_servers': len([s for s in servers.values() if s.get('status')=='Running']),
            'sites_folder': str(SITES_FOLDER)
        }
        return jsonify(info)
    except Exception:
        app_logger.exception("api_system_info error")
        return jsonify({})

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
# Reverse Proxy Functionality
# -------------------------
def setup_reverse_proxy():
    """Setup reverse proxy routes for unified access"""
    global proxy_routes
    proxy_routes = {}
    
    with LOCK:
        for name, server in servers.items():
            if server.get('status') == 'Running' and server.get('port'):
                # Create route based on server name
                route = f"/{name}"
                proxy_routes[route] = {
                    'server_name': name,
                    'port': server['port'],
                    'type': server.get('type', 'HTTP')
                }

def proxy_request(route: str, path: str) -> Response:
    """Proxy a request to the appropriate backend server"""
    if route not in proxy_routes:
        abort(404)
    
    server_info = proxy_routes[route]
    server_name = server_info['server_name']
    backend_port = server_info['port']
    
    if server_name not in servers or servers[server_name]['status'] != 'Running':
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
        app_logger.error(f"Proxy error for {route}{path}: {e}")
        abort(502)

# Add reverse proxy routes
@app.route('/<path:path>')
def proxy_route(path):
    """Proxy requests to backend servers"""
    if not RUNTIME_OPTIONS['ENABLE_REVERSE_PROXY']:
        abort(404)
    
    # Find matching route
    for route, server_info in proxy_routes.items():
        if path.startswith(route.lstrip('/')):
            remaining_path = '/' + path[len(route.lstrip('/')):]
            return proxy_request(route, remaining_path)
    
    # No matching route found
    abort(404)

# -------------------------
# Run app
# -------------------------
if __name__ == '__main__':
    app_logger.info("Windows-Compatible Workspace Server - Enhanced Multi-Project Development")
    app_logger.info("Sites: %s, Logs: %s", SITES_FOLDER, LOGS_FOLDER)
    
    # Check dependencies
    php_available, php_version = check_php_available(), "Unknown"
    node_available, node_version = check_node_available(), "Unknown"
    
    if php_available:
        try:
            result = subprocess.run([get_php_path(), '--version'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                php_version = result.stdout.split('\n')[0]
        except:
            pass
    
    if node_available:
        try:
            result = subprocess.run([get_node_path(), '--version'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                node_version = result.stdout.strip()
        except:
            pass
    
    app_logger.info("PHP: %s (%s)", "Available" if php_available else "Not found", php_version)
    app_logger.info("Node.js: %s (%s)", "Available" if node_available else "Not found", node_version)
    
    # Setup reverse proxy
    if RUNTIME_OPTIONS['ENABLE_REVERSE_PROXY']:
        setup_reverse_proxy()
        app_logger.info("Reverse proxy enabled on port %s", RUNTIME_OPTIONS['PROXY_PORT'])
    
    # persist and ensure discovered sites are registered
    save_servers_to_disk()
    
    # Auto-open browser on Windows
    if platform.system() == 'Windows' and RUNTIME_OPTIONS['AUTO_OPEN_BROWSER']:
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{RUNTIME_OPTIONS["PROXY_PORT"]}')
        threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Flask with binding so UI is reachable from devices
    try:
        port = RUNTIME_OPTIONS['PROXY_PORT'] if RUNTIME_OPTIONS['ENABLE_REVERSE_PROXY'] else 5000
        app_logger.info("Starting server on http://0.0.0.0:%s", port)
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        shutdown_all()
        app_logger.info("Goodbye")
    except Exception:
        app_logger.exception("Fatal app error")
        shutdown_all()
        sys.exit(1)