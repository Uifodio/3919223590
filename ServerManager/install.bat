@echo off
title Professional Server Manager - Installer
echo Installing Professional Server Manager...
echo.
echo This will install Node.js, PHP, and Nginx for Windows
echo.
pause
echo.
echo [INFO] Downloading Node.js...
powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi' -OutFile 'nodejs.msi'}"
if exist "nodejs.msi" (
    echo [INFO] Installing Node.js...
    msiexec /i nodejs.msi /quiet /norestart
    del nodejs.msi
) else (
    echo [ERROR] Failed to download Node.js
    pause
    exit /b 1
)
echo.
echo [INFO] Downloading PHP...
powershell -Command "& {Invoke-WebRequest -Uri 'https://windows.php.net/downloads/releases/php-8.3.2-Win32-vs16-x64.zip' -OutFile 'php.zip'}"
if exist "php.zip" (
    echo [INFO] Extracting PHP...
    powershell -Command "& {Expand-Archive -Path 'php.zip' -DestinationPath 'bin\php' -Force}"
    del php.zip
) else (
    echo [ERROR] Failed to download PHP
    pause
    exit /b 1
)
echo.
echo [INFO] Downloading Nginx...
powershell -Command "& {Invoke-WebRequest -Uri 'http://nginx.org/download/nginx-1.24.0.zip' -OutFile 'nginx.zip'}"
if exist "nginx.zip" (
    echo [INFO] Extracting Nginx...
    powershell -Command "& {Expand-Archive -Path 'nginx.zip' -DestinationPath 'bin\nginx' -Force}"
    del nginx.zip
) else (
    echo [ERROR] Failed to download Nginx
    pause
    exit /b 1
)
echo.
echo [INFO] Creating configuration files...
echo worker_processes 1; > config\nginx.conf
echo events { worker_connections 1024; } >> config\nginx.conf
echo http { include mime.types; default_type application/octet-stream; sendfile on; keepalive_timeout 65; server { listen 80; server_name localhost; root %CD%\www; index index.html index.php; location / { try_files $uri $uri/ =404; } location ~ \.php$ { fastcgi_pass 127.0.0.1:9000; fastcgi_index index.php; fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name; include fastcgi_params; } } } >> config\nginx.conf
echo.
echo [INFO] Creating server templates...
echo const http = require('http'); > templates\node-template.js
echo const fs = require('fs'); >> templates\node-template.js
echo const path = require('path'); >> templates\node-template.js
echo const PORT = process.env.PORT ^|^| 3000; >> templates\node-template.js
echo const server = http.createServer((req, res) =^> { >> templates\node-template.js
echo     let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url); >> templates\node-template.js
echo     filePath = path.resolve(filePath); >> templates\node-template.js
echo     if (!filePath.startsWith(__dirname)) { res.writeHead(403); res.end('Forbidden'); return; } >> templates\node-template.js
echo     fs.readFile(filePath, (err, data) =^> { >> templates\node-template.js
echo         if (err) { res.writeHead(404); res.end('File not found'); } else { res.writeHead(200, {'Content-Type': 'text/html'}); res.end(data); } >> templates\node-template.js
echo     }); >> templates\node-template.js
echo }); >> templates\node-template.js
echo server.listen(PORT, () =^> { console.log(`Server running on http://localhost:${PORT}`); }); >> templates\node-template.js
echo.
echo [INFO] Installation complete!
echo.
echo Professional Server Manager has been installed successfully!
echo.
echo To start the application:
echo 1. Run: start.bat
echo 2. Or run: start-web.bat for web interface
echo.
pause