@echo off
echo ========================================
echo  Creating Professional Server Manager
echo  Standalone Package for Windows
echo ========================================
echo.

:: Create package directory
if exist "ServerManager" rmdir /s /q "ServerManager"
mkdir "ServerManager"
cd "ServerManager"

:: Create subdirectories
mkdir bin
mkdir servers
mkdir config
mkdir logs
mkdir www
mkdir templates

echo [INFO] Creating package structure...

:: Copy main files
copy "..\index.html" "www\"
copy "..\styles.css" "www\"
copy "..\script.js" "www\"
copy "..\server-manager-windows.js" "server-manager.js"

:: Create Windows batch files
echo [INFO] Creating Windows batch files...

:: Main launcher
echo @echo off > start.bat
echo title Professional Server Manager >> start.bat
echo echo Starting Professional Server Manager... >> start.bat
echo node server-manager.js >> start.bat
echo pause >> start.bat

:: Web interface launcher
echo @echo off > start-web.bat
echo title Professional Server Manager - Web Interface >> start-web.bat
echo echo Opening web interface... >> start-web.bat
echo start www\index.html >> start-web.bat

:: Installer
echo @echo off > install.bat
echo title Professional Server Manager - Installer >> install.bat
echo echo Installing Professional Server Manager... >> install.bat
echo echo. >> install.bat
echo echo This will install Node.js, PHP, and Nginx for Windows >> install.bat
echo echo. >> install.bat
echo pause >> install.bat
echo. >> install.bat
echo echo [INFO] Downloading Node.js... >> install.bat
echo powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi' -OutFile 'nodejs.msi'}" >> install.bat
echo if exist "nodejs.msi" ( >> install.bat
echo     echo [INFO] Installing Node.js... >> install.bat
echo     msiexec /i nodejs.msi /quiet /norestart >> install.bat
echo     del nodejs.msi >> install.bat
echo ) else ( >> install.bat
echo     echo [ERROR] Failed to download Node.js >> install.bat
echo     pause >> install.bat
echo     exit /b 1 >> install.bat
echo ) >> install.bat
echo. >> install.bat
echo echo [INFO] Downloading PHP... >> install.bat
echo powershell -Command "& {Invoke-WebRequest -Uri 'https://windows.php.net/downloads/releases/php-8.3.2-Win32-vs16-x64.zip' -OutFile 'php.zip'}" >> install.bat
echo if exist "php.zip" ( >> install.bat
echo     echo [INFO] Extracting PHP... >> install.bat
echo     powershell -Command "& {Expand-Archive -Path 'php.zip' -DestinationPath 'bin\php' -Force}" >> install.bat
echo     del php.zip >> install.bat
echo ) else ( >> install.bat
echo     echo [ERROR] Failed to download PHP >> install.bat
echo     pause >> install.bat
echo     exit /b 1 >> install.bat
echo ) >> install.bat
echo. >> install.bat
echo echo [INFO] Downloading Nginx... >> install.bat
echo powershell -Command "& {Invoke-WebRequest -Uri 'http://nginx.org/download/nginx-1.24.0.zip' -OutFile 'nginx.zip'}" >> install.bat
echo if exist "nginx.zip" ( >> install.bat
echo     echo [INFO] Extracting Nginx... >> install.bat
echo     powershell -Command "& {Expand-Archive -Path 'nginx.zip' -DestinationPath 'bin\nginx' -Force}" >> install.bat
echo     del nginx.zip >> install.bat
echo ) else ( >> install.bat
echo     echo [ERROR] Failed to download Nginx >> install.bat
echo     pause >> install.bat
echo     exit /b 1 >> install.bat
echo ) >> install.bat
echo. >> install.bat
echo echo [INFO] Creating configuration files... >> install.bat
echo echo worker_processes 1; > config\nginx.conf >> install.bat
echo echo events { worker_connections 1024; } >> config\nginx.conf >> install.bat
echo echo http { include mime.types; default_type application/octet-stream; sendfile on; keepalive_timeout 65; server { listen 80; server_name localhost; root %CD%\www; index index.html index.php; location / { try_files $uri $uri/ =404; } location ~ \.php$ { fastcgi_pass 127.0.0.1:9000; fastcgi_index index.php; fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name; include fastcgi_params; } } } >> config\nginx.conf >> install.bat
echo. >> install.bat
echo echo [INFO] Creating server templates... >> install.bat
echo echo const http = require('http'); > templates\node-template.js >> install.bat
echo echo const fs = require('fs'); >> templates\node-template.js >> install.bat
echo echo const path = require('path'); >> templates\node-template.js >> install.bat
echo echo const PORT = process.env.PORT ^|^| 3000; >> templates\node-template.js >> install.bat
echo echo const server = http.createServer((req, res) =^> { >> templates\node-template.js >> install.bat
echo echo     let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url); >> templates\node-template.js >> install.bat
echo echo     filePath = path.resolve(filePath); >> templates\node-template.js >> install.bat
echo echo     if (!filePath.startsWith(__dirname)) { res.writeHead(403); res.end('Forbidden'); return; } >> templates\node-template.js >> install.bat
echo echo     fs.readFile(filePath, (err, data) =^> { >> templates\node-template.js >> install.bat
echo echo         if (err) { res.writeHead(404); res.end('File not found'); } else { res.writeHead(200, {'Content-Type': 'text/html'}); res.end(data); } >> templates\node-template.js >> install.bat
echo echo     }); >> templates\node-template.js >> install.bat
echo echo }); >> templates\node-template.js >> install.bat
echo echo server.listen(PORT, () =^> { console.log(`Server running on http://localhost:${PORT}`); }); >> templates\node-template.js >> install.bat
echo. >> install.bat
echo echo [INFO] Installation complete! >> install.bat
echo echo. >> install.bat
echo echo Professional Server Manager has been installed successfully! >> install.bat
echo echo. >> install.bat
echo echo To start the application: >> install.bat
echo echo 1. Run: start.bat >> install.bat
echo echo 2. Or run: start-web.bat for web interface >> install.bat
echo echo. >> install.bat
echo pause >> install.bat

:: Create README
echo [INFO] Creating documentation...
echo Professional Server Manager for Windows > README.md
echo ====================================== >> README.md
echo. >> README.md
echo A professional local development server manager that allows you to run up to 10 servers simultaneously. >> README.md
echo. >> README.md
echo ## Features >> README.md
echo. >> README.md
echo - **Node.js Servers**: Full HTTP server with static file serving >> README.md
echo - **PHP Servers**: PHP 8.3+ with all major extensions >> README.md
echo - **Web Interface**: Beautiful dark theme GitHub-style interface >> README.md
echo - **Command Line Interface**: Full-featured CLI for power users >> README.md
echo - **Multiple Servers**: Run up to 10 servers simultaneously on ports 3000-3009 >> README.md
echo - **Windows Compatible**: Designed specifically for Windows >> README.md
echo. >> README.md
echo ## Quick Start >> README.md
echo. >> README.md
echo 1. **Install Dependencies**: Run `install.bat` as Administrator >> README.md
echo 2. **Start Application**: Run `start.bat` or `start-web.bat` >> README.md
echo 3. **Create Servers**: Use the web interface or command line >> README.md
echo. >> README.md
echo ## Usage >> README.md
echo. >> README.md
echo ### Web Interface >> README.md
echo - Run `start-web.bat` to open the web interface >> README.md
echo - Create, start, stop, and manage servers through the beautiful UI >> README.md
echo - Monitor server status, logs, and performance >> README.md
echo. >> README.md
echo ### Command Line Interface >> README.md
echo - Run `start.bat` to start the CLI >> README.md
echo - Follow the interactive menu to manage servers >> README.md
echo - Perfect for automation and scripting >> README.md
echo. >> README.md
echo ## Server Types >> README.md
echo. >> README.md
echo ### Node.js Server >> README.md
echo - Full HTTP server implementation >> README.md
echo - Static file serving with MIME type detection >> README.md
echo - Security protection against directory traversal >> README.md
echo - Supports HTML, CSS, JS, images, and JSON >> README.md
echo. >> README.md
echo ### PHP Server >> README.md
echo - PHP 8.3+ with all major extensions >> README.md
echo - Built-in development server >> README.md
echo - MySQL, GD, cURL, XML, and more >> README.md
echo - Perfect for web applications >> README.md
echo. >> README.md
echo ## Directory Structure >> README.md
echo. >> README.md
echo ``` >> README.md
echo ServerManager/ >> README.md
echo ├── start.bat              # Main launcher >> README.md
echo ├── start-web.bat          # Web interface launcher >> README.md
echo ├── install.bat            # Dependency installer >> README.md
echo ├── server-manager.js      # Main application >> README.md
echo ├── www/                   # Web interface files >> README.md
echo │   ├── index.html >> README.md
echo │   ├── styles.css >> README.md
echo │   └── script.js >> README.md
echo ├── bin/                   # Dependencies >> README.md
echo │   ├── php/ >> README.md
echo │   └── nginx/ >> README.md
echo ├── servers/               # Server directories >> README.md
echo ├── config/                # Configuration files >> README.md
echo ├── templates/             # Server templates >> README.md
echo └── logs/                  # Log files >> README.md
echo ``` >> README.md
echo. >> README.md
echo ## Requirements >> README.md
echo. >> README.md
echo - Windows 10 or later >> README.md
echo - Administrator privileges for installation >> README.md
echo - Internet connection for initial setup >> README.md
echo. >> README.md
echo ## Troubleshooting >> README.md
echo. >> README.md
echo ### Common Issues >> README.md
echo. >> README.md
echo 1. **Port already in use**: Choose a different port or stop the conflicting server >> README.md
echo 2. **Permission denied**: Run as Administrator >> README.md
echo 3. **Server won't start**: Check logs and ensure dependencies are installed >> README.md
echo. >> README.md
echo ### Support >> README.md
echo. >> README.md
echo This is a professional development environment designed for: >> README.md
echo - Web development >> README.md
echo - API development >> README.md
echo - Testing and debugging >> README.md
echo - Local development workflows >> README.md
echo. >> README.md
echo ## License >> README.md
echo. >> README.md
echo MIT License - Free for personal and commercial use >> README.md

:: Create package info
echo [INFO] Creating package information...
echo { > package.json
echo   "name": "professional-server-manager", >> package.json
echo   "version": "1.0.0", >> package.json
echo   "description": "Professional local development server manager for Windows", >> package.json
echo   "main": "server-manager.js", >> package.json
echo   "scripts": { >> package.json
echo     "start": "node server-manager.js", >> package.json
echo     "web": "start www\\index.html" >> package.json
echo   }, >> package.json
echo   "keywords": ["server", "development", "nodejs", "php", "windows", "local"], >> package.json
echo   "author": "Professional Server Manager", >> package.json
echo   "license": "MIT" >> package.json
echo } >> package.json

:: Create sample servers
echo [INFO] Creating sample servers...
mkdir "servers\node-sample"
mkdir "servers\php-sample"

:: Node.js sample
echo ^<!DOCTYPE html^> > "servers\node-sample\index.html"
echo ^<html^> >> "servers\node-sample\index.html"
echo ^<head^> >> "servers\node-sample\index.html"
echo     ^<title^>Node.js Sample Server^</title^> >> "servers\node-sample\index.html"
echo     ^<style^>body{font-family:Arial;padding:20px;background:#f0f0f0;}^</style^> >> "servers\node-sample\index.html"
echo ^</head^> >> "servers\node-sample\index.html"
echo ^<body^> >> "servers\node-sample\index.html"
echo     ^<h1^>Node.js Sample Server^</h1^> >> "servers\node-sample\index.html"
echo     ^<p^>This is a sample Node.js server running through Professional Server Manager.^</p^> >> "servers\node-sample\index.html"
echo     ^<p^>Server started at: ^<span id="time"^>^</span^>^</p^> >> "servers\node-sample\index.html"
echo     ^<script^>document.getElementById('time').textContent = new Date().toLocaleString();^</script^> >> "servers\node-sample\index.html"
echo ^</body^> >> "servers\node-sample\index.html"
echo ^</html^> >> "servers\node-sample\index.html"

:: PHP sample
echo ^<?php > "servers\php-sample\index.php"
echo echo "^<!DOCTYPE html^>"; >> "servers\php-sample\index.php"
echo echo "^<html^>^<head^>^<title^>PHP Sample Server^</title^>^</head^>^<body^>"; >> "servers\php-sample\index.php"
echo echo "^<h1^>PHP Sample Server^</h1^>"; >> "servers\php-sample\index.php"
echo echo "^<p^>This is a sample PHP server running through Professional Server Manager.^</p^>"; >> "servers\php-sample\index.php"
echo echo "^<p^>Server started at: " . date('Y-m-d H:i:s') . "^</p^>"; >> "servers\php-sample\index.php"
echo echo "^<p^>PHP Version: " . phpversion() . "^</p^>"; >> "servers\php-sample\index.php"
echo echo "^</body^>^</html^>"; >> "servers\php-sample\index.php"
echo ?^> >> "servers\php-sample\index.php"

echo [INFO] Package created successfully!
echo.
echo Professional Server Manager package is ready in the 'ServerManager' directory.
echo.
echo To distribute:
echo 1. Zip the 'ServerManager' folder
echo 2. Share the zip file
echo 3. Users can extract and run install.bat
echo.
echo Package contents:
dir /b
echo.
pause