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
