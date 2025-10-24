#!/bin/bash

# Professional Server Manager Setup Script
# This script sets up the complete development environment

echo "🚀 Setting up Professional Server Manager Environment..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /workspace/servers
mkdir -p /workspace/servers/node-server-1
mkdir -p /workspace/servers/php-server-1
mkdir -p /workspace/servers/static-server-1
mkdir -p /workspace/logs
mkdir -p /workspace/config

# Set up Node.js server template
echo "📝 Creating Node.js server template..."
cat > /workspace/servers/node-server-1/server.js << 'EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
    let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
    
    // Security: prevent directory traversal
    filePath = path.resolve(filePath);
    if (!filePath.startsWith(__dirname)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404);
                res.end('File not found');
            } else {
                res.writeHead(500);
                res.end('Server error');
            }
        } else {
            const ext = path.extname(filePath);
            const contentType = {
                '.html': 'text/html',
                '.js': 'text/javascript',
                '.css': 'text/css',
                '.json': 'application/json',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml'
            }[ext] || 'text/plain';
            
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(data);
        }
    });
});

server.listen(PORT, () => {
    console.log(`Node.js server running on http://localhost:${PORT}`);
});
EOF

# Create sample HTML file for Node.js server
cat > /workspace/servers/node-server-1/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Node.js Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { text-align: center; margin-bottom: 30px; }
        .info { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Node.js Server Running!</h1>
        <div class="info">
            <h3>Server Information</h3>
            <p><strong>Type:</strong> Node.js HTTP Server</p>
            <p><strong>Status:</strong> Running</p>
            <p><strong>Started:</strong> <span id="startTime"></span></p>
        </div>
        <div class="info">
            <h3>Features</h3>
            <ul>
                <li>Static file serving</li>
                <li>MIME type detection</li>
                <li>Security protection</li>
                <li>Error handling</li>
            </ul>
        </div>
    </div>
    <script>
        document.getElementById('startTime').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
EOF

# Create PHP server template
echo "📝 Creating PHP server template..."
cat > /workspace/servers/php-server-1/index.php << 'EOF'
<?php
$serverInfo = [
    'type' => 'PHP Built-in Server',
    'version' => phpversion(),
    'status' => 'Running',
    'started' => date('Y-m-d H:i:s'),
    'document_root' => __DIR__,
    'request_uri' => $_SERVER['REQUEST_URI'] ?? '/',
    'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'PHP Built-in Server'
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { text-align: center; margin-bottom: 30px; }
        .info { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
        .php-info { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐘 PHP Server Running!</h1>
        <div class="info">
            <h3>Server Information</h3>
            <?php foreach($serverInfo as $key => $value): ?>
                <p><strong><?= ucfirst(str_replace('_', ' ', $key)) ?>:</strong> <?= htmlspecialchars($value) ?></p>
            <?php endforeach; ?>
        </div>
        <div class="php-info">
            <h3>PHP Extensions</h3>
            <p><?= implode(', ', get_loaded_extensions()) ?></p>
        </div>
        <div class="info">
            <h3>Features</h3>
            <ul>
                <li>PHP 8.4+ support</li>
                <li>Built-in development server</li>
                <li>All major extensions loaded</li>
                <li>Error reporting enabled</li>
            </ul>
        </div>
    </div>
</body>
</html>
EOF

# Create static server template
echo "📝 Creating static server template..."
cat > /workspace/servers/static-server-1/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Static Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { text-align: center; margin-bottom: 30px; }
        .info { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Static Server Running!</h1>
        <div class="info">
            <h3>Server Information</h3>
            <p><strong>Type:</strong> Static File Server</p>
            <p><strong>Status:</strong> Running</p>
            <p><strong>Started:</strong> <span id="startTime"></span></p>
        </div>
        <div class="info">
            <h3>Features</h3>
            <ul>
                <li>HTML, CSS, JS file serving</li>
                <li>Image support (PNG, JPG, GIF, SVG)</li>
                <li>JSON file serving</li>
                <li>Directory browsing</li>
            </ul>
        </div>
    </div>
    <script>
        document.getElementById('startTime').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
EOF

# Create Nginx configuration
echo "📝 Creating Nginx configuration..."
cat > /workspace/config/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Logging
    access_log /workspace/logs/nginx_access.log;
    error_log /workspace/logs/nginx_error.log;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Default server
    server {
        listen 80 default_server;
        server_name localhost;
        root /workspace;
        index index.html index.php;
        
        location / {
            try_files $uri $uri/ =404;
        }
        
        location ~ \.php$ {
            fastcgi_pass unix:/run/php/php8.4-fpm.sock;
            fastcgi_index index.php;
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        }
    }
    
    # Proxy servers for Node.js applications
    server {
        listen 8080;
        server_name localhost;
        
        location / {
            proxy_pass http://127.0.0.1:3000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }
    }
}
EOF

# Create PHP-FPM configuration
echo "📝 Creating PHP-FPM configuration..."
cat > /workspace/config/www.conf << 'EOF'
[www]
user = www-data
group = www-data
listen = /run/php/php8.4-fpm.sock
listen.owner = www-data
listen.group = www-data
listen.mode = 0660
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
pm.max_requests = 500
EOF

# Create a comprehensive README
echo "📝 Creating documentation..."
cat > /workspace/README.md << 'EOF'
# Professional Server Manager

A comprehensive local development environment that allows you to run up to 10 servers simultaneously.

## Features

- **Node.js Servers**: Full HTTP server with static file serving
- **PHP Servers**: PHP 8.4+ with all major extensions
- **Nginx**: High-performance web server and reverse proxy
- **Web Interface**: Beautiful, responsive web UI for server management
- **Command Line Interface**: Full-featured CLI for power users
- **Multiple Servers**: Run up to 10 servers simultaneously on ports 3000-3009

## Quick Start

### Using the Web Interface
1. Open `web-interface.html` in your browser
2. Fill in the server details
3. Click "Start Server"

### Using the Command Line
```bash
# Make the server manager executable
chmod +x server-manager.js

# Run the server manager
node server-manager.js
```

### Direct Server Commands

#### Node.js Server
```bash
# Start a Node.js server
cd /workspace/servers/node-server-1
node server.js

# Or with custom port
PORT=3001 node server.js
```

#### PHP Server
```bash
# Start a PHP server
cd /workspace/servers/php-server-1
php -S localhost:3001 -t .
```

#### Nginx Server
```bash
# Start Nginx (if systemd is available)
sudo systemctl start nginx

# Or manually
sudo nginx -c /workspace/config/nginx.conf
```

## Directory Structure

```
/workspace/
├── server-manager.js          # Main server management script
├── web-interface.html         # Web-based management interface
├── setup.sh                   # Setup script
├── config/                    # Configuration files
│   ├── nginx.conf
│   └── www.conf
├── servers/                   # Server directories
│   ├── node-server-1/
│   ├── php-server-1/
│   └── static-server-1/
└── logs/                      # Log files
```

## Server Types

### Node.js Server
- Full HTTP server implementation
- Static file serving with MIME type detection
- Security protection against directory traversal
- Error handling and logging
- Supports HTML, CSS, JS, images, and JSON

### PHP Server
- PHP 8.4+ with all major extensions
- Built-in development server
- MySQL, GD, cURL, XML, and more
- Error reporting enabled
- FastCGI support

### Static Server
- Pure static file serving
- No server-side processing
- Perfect for frontend development
- Supports all web file types

## Configuration

### Port Management
- Default ports: 3000-3009
- Automatic port assignment
- Port conflict detection
- Easy port switching

### Security Features
- Directory traversal protection
- MIME type validation
- Error message sanitization
- Process isolation

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Check if another server is running on the same port
   - Use a different port or stop the conflicting server

2. **Permission denied**
   - Ensure proper file permissions
   - Run with appropriate user privileges

3. **Server won't start**
   - Check the logs in `/workspace/logs/`
   - Verify all dependencies are installed
   - Ensure the directory exists and is accessible

### Logs
- Nginx logs: `/workspace/logs/nginx_access.log` and `/workspace/logs/nginx_error.log`
- Server logs: Displayed in the terminal/console

## Advanced Usage

### Custom Server Templates
Create your own server templates by modifying the files in `/workspace/servers/`.

### Nginx Configuration
Modify `/workspace/config/nginx.conf` for custom Nginx settings.

### PHP Configuration
Edit `/workspace/config/www.conf` for PHP-FPM settings.

## Support

This is a professional development environment designed for:
- Web development
- API development
- Testing and debugging
- Local development workflows
- Educational purposes

For issues or questions, check the logs and ensure all dependencies are properly installed.
EOF

# Set permissions
echo "🔐 Setting permissions..."
chmod +x /workspace/server-manager.js
chmod +x /workspace/setup.sh

# Create a quick start script
echo "📝 Creating quick start script..."
cat > /workspace/start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Professional Server Manager..."
echo "Choose your interface:"
echo "1. Web Interface (open web-interface.html in browser)"
echo "2. Command Line Interface"
echo "3. Start sample servers"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Opening web interface..."
        echo "Please open web-interface.html in your browser"
        ;;
    2)
        echo "Starting CLI..."
        node server-manager.js
        ;;
    3)
        echo "Starting sample servers..."
        echo "Starting Node.js server on port 3000..."
        cd /workspace/servers/node-server-1 && node server.js &
        echo "Starting PHP server on port 3001..."
        cd /workspace/servers/php-server-1 && php -S localhost:3001 -t . &
        echo "Sample servers started!"
        echo "Node.js: http://localhost:3000"
        echo "PHP: http://localhost:3001"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
EOF

chmod +x /workspace/start.sh

echo "✅ Setup complete!"
echo ""
echo "🎉 Professional Server Manager is ready!"
echo ""
echo "Quick start options:"
echo "1. Run: ./start.sh"
echo "2. Open: web-interface.html in your browser"
echo "3. Run: node server-manager.js"
echo ""
echo "Sample servers are available in /workspace/servers/"
echo "Configuration files are in /workspace/config/"
echo "Logs will be stored in /workspace/logs/"