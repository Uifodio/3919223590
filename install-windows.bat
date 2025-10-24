@echo off
echo ========================================
echo  Professional Server Manager - Windows
echo ========================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running as Administrator
) else (
    echo [ERROR] Please run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [INFO] Installing Professional Server Manager for Windows...

:: Create main directory
if not exist "C:\ServerManager" mkdir "C:\ServerManager"
cd /d "C:\ServerManager"

:: Create subdirectories
mkdir bin 2>nul
mkdir servers 2>nul
mkdir config 2>nul
mkdir logs 2>nul
mkdir www 2>nul

echo [INFO] Downloading Node.js...
:: Download Node.js LTS for Windows
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

echo [INFO] Downloading PHP...
:: Download PHP for Windows
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

echo [INFO] Downloading Nginx...
:: Download Nginx for Windows
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

echo [INFO] Setting up environment...
:: Add to PATH
setx PATH "%PATH%;C:\ServerManager\bin\php;C:\ServerManager\bin\nginx" /M

echo [INFO] Creating configuration files...

:: Create nginx.conf
echo worker_processes 1; > config\nginx.conf
echo. >> config\nginx.conf
echo events { >> config\nginx.conf
echo     worker_connections 1024; >> config\nginx.conf
echo } >> config\nginx.conf
echo. >> config\nginx.conf
echo http { >> config\nginx.conf
echo     include       mime.types; >> config\nginx.conf
echo     default_type  application/octet-stream; >> config\nginx.conf
echo     sendfile        on; >> config\nginx.conf
echo     keepalive_timeout  65; >> config\nginx.conf
echo. >> config\nginx.conf
echo     server { >> config\nginx.conf
echo         listen       80; >> config\nginx.conf
echo         server_name  localhost; >> config\nginx.conf
echo         root         C:\ServerManager\www; >> config\nginx.conf
echo         index        index.html index.php; >> config\nginx.conf
echo. >> config\nginx.conf
echo         location / { >> config\nginx.conf
echo             try_files $uri $uri/ =404; >> config\nginx.conf
echo         } >> config\nginx.conf
echo. >> config\nginx.conf
echo         location ~ \.php$ { >> config\nginx.conf
echo             fastcgi_pass   127.0.0.1:9000; >> config\nginx.conf
echo             fastcgi_index  index.php; >> config\nginx.conf
echo             fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name; >> config\nginx.conf
echo             include        fastcgi_params; >> config\nginx.conf
echo         } >> config\nginx.conf
echo     } >> config\nginx.conf
echo } >> config\nginx.conf

:: Create PHP configuration
echo [PHP] > bin\php\php.ini
echo engine = On >> bin\php\php.ini
echo short_open_tag = Off >> bin\php\php.ini
echo precision = 14 >> bin\php\php.ini
echo output_buffering = 4096 >> bin\php\php.ini
echo zlib.output_compression = Off >> bin\php\php.ini
echo implicit_flush = Off >> bin\php\php.ini
echo unserialize_callback_func = >> bin\php\php.ini
echo serialize_precision = -1 >> bin\php\php.ini
echo disable_functions = >> bin\php\php.ini
echo disable_classes = >> bin\php\php.ini
echo zend.enable_gc = On >> bin\php\php.ini
echo expose_php = On >> bin\php\php.ini
echo. >> bin\php\php.ini
echo ; Extensions >> bin\php\php.ini
echo extension_dir = "ext" >> bin\php\php.ini
echo extension=curl >> bin\php\php.ini
echo extension=gd >> bin\php\php.ini
echo extension=mbstring >> bin\php\php.ini
echo extension=mysqli >> bin\php\php.ini
echo extension=pdo_mysql >> bin\php\php.ini
echo extension=zip >> bin\php\php.ini
echo extension=json >> bin\php\php.ini
echo extension=xml >> bin\php\php.ini

echo [INFO] Creating server templates...

:: Create Node.js server template
echo const http = require('http'); > servers\node-template.js
echo const fs = require('fs'); >> servers\node-template.js
echo const path = require('path'); >> servers\node-template.js
echo. >> servers\node-template.js
echo const PORT = process.env.PORT ^|^| 3000; >> servers\node-template.js
echo. >> servers\node-template.js
echo const server = http.createServer((req, res) =^> { >> servers\node-template.js
echo     let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url); >> servers\node-template.js
echo     filePath = path.resolve(filePath); >> servers\node-template.js
echo     if (!filePath.startsWith(__dirname)) { >> servers\node-template.js
echo         res.writeHead(403); >> servers\node-template.js
echo         res.end('Forbidden'); >> servers\node-template.js
echo         return; >> servers\node-template.js
echo     } >> servers\node-template.js
echo     fs.readFile(filePath, (err, data) =^> { >> servers\node-template.js
echo         if (err) { >> servers\node-template.js
echo             res.writeHead(404); >> servers\node-template.js
echo             res.end('File not found'); >> servers\node-template.js
echo         } else { >> servers\node-template.js
echo             res.writeHead(200, {'Content-Type': 'text/html'}); >> servers\node-template.js
echo             res.end(data); >> servers\node-template.js
echo         } >> servers\node-template.js
echo     }); >> servers\node-template.js
echo }); >> servers\node-template.js
echo. >> servers\node-template.js
echo server.listen(PORT, () =^> { >> servers\node-template.js
echo     console.log(`Server running on http://localhost:${PORT}`); >> servers\node-template.js
echo }); >> servers\node-template.js

:: Create PHP server template
echo ^<?php > servers\php-template.php
echo echo "PHP Server Running"; >> servers\php-template.php
echo echo "PHP Version: " . phpversion(); >> servers\php-template.php
echo ?^> >> servers\php-template.php

echo [INFO] Installation complete!
echo.
echo Professional Server Manager has been installed to C:\ServerManager
echo.
echo To start the application:
echo 1. Run: C:\ServerManager\ServerManager.exe
echo 2. Or open: C:\ServerManager\www\index.html
echo.
echo Press any key to exit...
pause >nul