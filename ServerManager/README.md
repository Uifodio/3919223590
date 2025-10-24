# Professional Server Manager for Windows

A professional local development server manager that allows you to run up to 10 servers simultaneously.

## Features

- **Node.js Servers**: Full HTTP server with static file serving
- **PHP Servers**: PHP 8.3+ with all major extensions  
- **Web Interface**: Beautiful dark theme GitHub-style interface
- **Command Line Interface**: Full-featured CLI for power users
- **Multiple Servers**: Run up to 10 servers simultaneously on ports 3000-3009
- **Windows Compatible**: Designed specifically for Windows

## Quick Start

1. **Install Dependencies**: Run `install.bat` as Administrator
2. **Start Application**: Run `start.bat` or `start-web.bat`
3. **Create Servers**: Use the web interface or command line

## Usage

### Web Interface
- Run `start-web.bat` to open the web interface
- Create, start, stop, and manage servers through the beautiful UI
- Monitor server status, logs, and performance

### Command Line Interface  
- Run `start.bat` to start the CLI
- Follow the interactive menu to manage servers
- Perfect for automation and scripting

## Server Types

### Node.js Server
- Full HTTP server implementation
- Static file serving with MIME type detection
- Security protection against directory traversal
- Supports HTML, CSS, JS, images, and JSON

### PHP Server
- PHP 8.3+ with all major extensions
- Built-in development server
- MySQL, GD, cURL, XML, and more
- Perfect for web applications

## Directory Structure

```
ServerManager/
├── start.bat              # Main launcher
├── start-web.bat          # Web interface launcher
├── install.bat            # Dependency installer
├── server-manager.js      # Main application
├── www/                   # Web interface files
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── bin/                   # Dependencies
│   ├── php/
│   └── nginx/
├── servers/               # Server directories
├── config/                # Configuration files
├── templates/             # Server templates
└── logs/                  # Log files
```

## Requirements

- Windows 10 or later
- Administrator privileges for installation
- Internet connection for initial setup

## Troubleshooting

### Common Issues

1. **Port already in use**: Choose a different port or stop the conflicting server
2. **Permission denied**: Run as Administrator
3. **Server won't start**: Check logs and ensure dependencies are installed

## Support

This is a professional development environment designed for:
- Web development
- API development
- Testing and debugging
- Local development workflows

## License

MIT License - Free for personal and commercial use