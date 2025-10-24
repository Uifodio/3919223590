# Professional Server Manager - PowerShell Installer
# Run as Administrator

param(
    [switch]$SkipDependencies,
    [string]$InstallPath = "C:\ServerManager"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Professional Server Manager Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Installing Professional Server Manager..." -ForegroundColor Green

# Create installation directory
if (Test-Path $InstallPath) {
    Write-Host "[INFO] Removing existing installation..." -ForegroundColor Yellow
    Remove-Item -Path $InstallPath -Recurse -Force
}

Write-Host "[INFO] Creating directory structure..." -ForegroundColor Green
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\bin" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\servers" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\config" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\www" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\templates" -Force | Out-Null

# Copy application files
Write-Host "[INFO] Copying application files..." -ForegroundColor Green
Copy-Item "index.html" "$InstallPath\www\" -Force
Copy-Item "styles.css" "$InstallPath\www\" -Force
Copy-Item "script.js" "$InstallPath\www\" -Force
Copy-Item "server-manager-windows.js" "$InstallPath\server-manager.js" -Force

# Create package.json
$packageJson = @{
    name = "professional-server-manager"
    version = "1.0.0"
    description = "Professional local development server manager for Windows"
    main = "server-manager.js"
    scripts = @{
        start = "node server-manager.js"
        web = "start www\\index.html"
    }
    keywords = @("server", "development", "nodejs", "php", "windows", "local")
    author = "Professional Server Manager"
    license = "MIT"
} | ConvertTo-Json -Depth 3

$packageJson | Out-File -FilePath "$InstallPath\package.json" -Encoding UTF8

# Create launcher scripts
Write-Host "[INFO] Creating launcher scripts..." -ForegroundColor Green

# Main launcher
$startBat = @"
@echo off
title Professional Server Manager
echo Starting Professional Server Manager...
node server-manager.js
pause
"@
$startBat | Out-File -FilePath "$InstallPath\start.bat" -Encoding ASCII

# Web interface launcher
$startWebBat = @"
@echo off
title Professional Server Manager - Web Interface
echo Opening web interface...
start www\index.html
"@
$startWebBat | Out-File -FilePath "$InstallPath\start-web.bat" -Encoding ASCII

# PowerShell launcher
$startPs1 = @"
# Professional Server Manager - PowerShell Launcher
Write-Host "Starting Professional Server Manager..." -ForegroundColor Green
Set-Location "$InstallPath"
node server-manager.js
"@
$startPs1 | Out-File -FilePath "$InstallPath\start.ps1" -Encoding UTF8

# Create server templates
Write-Host "[INFO] Creating server templates..." -ForegroundColor Green

# Node.js template
$nodeTemplate = @"
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
"@
$nodeTemplate | Out-File -FilePath "$InstallPath\templates\node-template.js" -Encoding UTF8

# PHP template
$phpTemplate = @"
<?php
echo "<!DOCTYPE html>";
echo "<html><head><title>PHP Server</title></head><body>";
echo "<h1>PHP Server Running</h1>";
echo "<p>Server started at: " . date('Y-m-d H:i:s') . "</p>";
echo "<p>PHP Version: " . phpversion() . "</p>";
echo "<p>Document Root: " . __DIR__ . "</p>";
echo "<p>Request URI: " . ($_SERVER['REQUEST_URI'] ?? '/') . "</p>";
echo "</body></html>";
?>
"@
$phpTemplate | Out-File -FilePath "$InstallPath\templates\php-template.php" -Encoding UTF8

# Create sample servers
Write-Host "[INFO] Creating sample servers..." -ForegroundColor Green

# Node.js sample
New-Item -ItemType Directory -Path "$InstallPath\servers\node-sample" -Force | Out-Null
$nodeSampleHtml = @"
<!DOCTYPE html>
<html>
<head>
    <title>Node.js Sample Server</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin: 0; min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
        h1 { text-align: center; margin-bottom: 30px; }
        .info { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Node.js Sample Server</h1>
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
"@
$nodeSampleHtml | Out-File -FilePath "$InstallPath\servers\node-sample\index.html" -Encoding UTF8

# PHP sample
New-Item -ItemType Directory -Path "$InstallPath\servers\php-sample" -Force | Out-Null
$phpSample = @"
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
<html>
<head>
    <title>PHP Sample Server</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; margin: 0; min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
        h1 { text-align: center; margin-bottom: 30px; }
        .info { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
        .php-info { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐘 PHP Sample Server</h1>
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
                <li>PHP 8.3+ support</li>
                <li>Built-in development server</li>
                <li>All major extensions loaded</li>
                <li>Error reporting enabled</li>
            </ul>
        </div>
    </div>
</body>
</html>
"@
$phpSample | Out-File -FilePath "$InstallPath\servers\php-sample\index.php" -Encoding UTF8

# Create README
Write-Host "[INFO] Creating documentation..." -ForegroundColor Green
$readme = @"
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

1. **Start Application**: Run `start.bat` or `start-web.bat`
2. **Create Servers**: Use the web interface or command line
3. **Manage**: Start, stop, and monitor your servers

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
├── start.ps1              # PowerShell launcher
├── server-manager.js      # Main application
├── www/                   # Web interface files
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── servers/               # Server directories
├── config/                # Configuration files
├── templates/             # Server templates
└── logs/                  # Log files
```

## Requirements

- Windows 10 or later
- Node.js (will be installed automatically)
- Internet connection for initial setup

## Troubleshooting

### Common Issues

1. **Port already in use**: Choose a different port or stop the conflicting server
2. **Permission denied**: Run as Administrator
3. **Server won't start**: Check logs and ensure dependencies are installed

## License

MIT License - Free for personal and commercial use
"@
$readme | Out-File -FilePath "$InstallPath\README.md" -Encoding UTF8

# Install dependencies if not skipped
if (-not $SkipDependencies) {
    Write-Host "[INFO] Installing dependencies..." -ForegroundColor Green
    
    # Check if Node.js is installed
    try {
        $nodeVersion = node --version 2>$null
        Write-Host "[INFO] Node.js found: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "[INFO] Node.js not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
        Write-Host "[INFO] Or run this installer with -SkipDependencies to skip dependency installation" -ForegroundColor Yellow
    }
}

# Create desktop shortcut
Write-Host "[INFO] Creating desktop shortcut..." -ForegroundColor Green
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Professional Server Manager.lnk")
$Shortcut.TargetPath = "$InstallPath\start-web.bat"
$Shortcut.WorkingDirectory = $InstallPath
$Shortcut.Description = "Professional Server Manager - Local Development Server Manager"
$Shortcut.Save()

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Professional Server Manager has been installed to: $InstallPath" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "1. Run: $InstallPath\start.bat" -ForegroundColor White
Write-Host "2. Or run: $InstallPath\start-web.bat" -ForegroundColor White
Write-Host "3. Or double-click the desktop shortcut" -ForegroundColor White
Write-Host ""
Write-Host "Sample servers are available in: $InstallPath\servers\" -ForegroundColor Green
Write-Host ""

# Ask if user wants to start the application
$response = Read-Host "Would you like to start the web interface now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "Starting web interface..." -ForegroundColor Green
    Start-Process "$InstallPath\start-web.bat"
}

Write-Host "Installation completed successfully!" -ForegroundColor Green
Read-Host "Press Enter to exit"