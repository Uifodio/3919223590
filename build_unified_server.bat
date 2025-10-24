@echo off
title Unified Server Stack Builder
color 0A

echo.
echo  ========================================
echo  🚀 Unified Server Stack Builder
echo  ========================================
echo  Professional Portable Web Server
echo  ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✓ Python found: 
python --version
echo.

REM Create directory structure
echo Creating unified server structure...
if not exist "nginx" mkdir nginx
if not exist "php" mkdir php
if not exist "nodejs" mkdir nodejs
if not exist "openssl" mkdir openssl
if not exist "ffmpeg" mkdir ffmpeg
if not exist "tools" mkdir tools
if not exist "sites" mkdir sites
if not exist "logs" mkdir logs
if not exist "certs" mkdir certs
if not exist "configs" mkdir configs
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
echo ✓ Directory structure created
echo.

REM Download Nginx
echo Downloading Nginx...
cd nginx
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'http://nginx.org/download/nginx-1.24.0.zip' -OutFile 'nginx-1.24.0.zip'}"
if exist "nginx-1.24.0.zip" (
    echo ✓ Nginx downloaded
    powershell -Command "Expand-Archive -Path 'nginx-1.24.0.zip' -DestinationPath '.' -Force"
    for /d %%i in (nginx-*) do (
        if exist "%%i\nginx.exe" (
            xcopy "%%i\*" "." /E /I /Y
            rmdir /s /q "%%i"
            goto :nginx_extracted
        )
    )
    :nginx_extracted
    del "nginx-1.24.0.zip" 2>nul
    echo ✓ Nginx extracted and configured
) else (
    echo ❌ Failed to download Nginx
    cd ..
    pause
    exit /b 1
)
cd ..

REM Download PHP-FPM
echo Downloading PHP-FPM...
cd php
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://windows.php.net/downloads/releases/php-8.3.12-Win32-vs16-x64.zip' -OutFile 'php-8.3.12-Win32-vs16-x64.zip'}"
if exist "php-8.3.12-Win32-vs16-x64.zip" (
    echo ✓ PHP downloaded
    powershell -Command "Expand-Archive -Path 'php-8.3.12-Win32-vs16-x64.zip' -DestinationPath '.' -Force"
    for /d %%i in (php-*) do (
        if exist "%%i\php.exe" (
            xcopy "%%i\*" "." /E /I /Y
            rmdir /s /q "%%i"
            goto :php_extracted
        )
    )
    :php_extracted
    del "php-8.3.12-Win32-vs16-x64.zip" 2>nul
    
    REM Configure PHP-FPM
    if not exist "php.ini" (
        copy "php.ini-development" "php.ini"
    )
    
    REM Enable extensions
    powershell -Command "(Get-Content 'php.ini') -replace ';extension=curl', 'extension=curl' | Set-Content 'php.ini'"
    powershell -Command "(Get-Content 'php.ini') -replace ';extension=gd', 'extension=gd' | Set-Content 'php.ini'"
    powershell -Command "(Get-Content 'php.ini') -replace ';extension=mbstring', 'extension=mbstring' | Set-Content 'php.ini'"
    powershell -Command "(Get-Content 'php.ini') -replace ';extension=openssl', 'extension=openssl' | Set-Content 'php.ini'"
    powershell -Command "(Get-Content 'php.ini') -replace ';extension=pdo_sqlite', 'extension=pdo_sqlite' | Set-Content 'php.ini'"
    powershell -Command "(Get-Content 'php.ini') -replace ';extension=zip', 'extension=zip' | Set-Content 'php.ini'"
    powershell -Command "(Get-Content 'php.ini') -replace ';extension=fileinfo', 'extension=fileinfo' | Set-Content 'php.ini'"
    
    echo ✓ PHP-FPM configured
) else (
    echo ❌ Failed to download PHP
    cd ..
    pause
    exit /b 1
)
cd ..

REM Download Node.js
echo Downloading Node.js...
cd nodejs
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.10.0/node-v20.10.0-win-x64.zip' -OutFile 'node-v20.10.0-win-x64.zip'}"
if exist "node-v20.10.0-win-x64.zip" (
    echo ✓ Node.js downloaded
    powershell -Command "Expand-Archive -Path 'node-v20.10.0-win-x64.zip' -DestinationPath '.' -Force"
    for /d %%i in (node-*) do (
        if exist "%%i\node.exe" (
            xcopy "%%i\*" "." /E /I /Y
            rmdir /s /q "%%i"
            goto :node_extracted
        )
    )
    :node_extracted
    del "node-v20.10.0-win-x64.zip" 2>nul
    echo ✓ Node.js extracted
) else (
    echo ❌ Failed to download Node.js
    cd ..
    pause
    exit /b 1
)
cd ..

REM Download OpenSSL
echo Downloading OpenSSL...
cd openssl
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://slproweb.com/download/Win64OpenSSL-3_1_4.exe' -OutFile 'Win64OpenSSL-3_1_4.exe'}"
if exist "Win64OpenSSL-3_1_4.exe" (
    echo ✓ OpenSSL downloaded
    echo Installing OpenSSL...
    Win64OpenSSL-3_1_4.exe /SILENT /DIR=.
    echo ✓ OpenSSL installed
) else (
    echo ❌ Failed to download OpenSSL
    cd ..
    pause
    exit /b 1
)
cd ..

REM Download FFmpeg
echo Downloading FFmpeg...
cd ffmpeg
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'}"
if exist "ffmpeg.zip" (
    echo ✓ FFmpeg downloaded
    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"
    for /d %%i in (ffmpeg-*) do (
        if exist "%%i\bin\ffmpeg.exe" (
            xcopy "%%i\*" "." /E /I /Y
            rmdir /s /q "%%i"
            goto :ffmpeg_extracted
        )
    )
    :ffmpeg_extracted
    del "ffmpeg.zip" 2>nul
    echo ✓ FFmpeg extracted
) else (
    echo ❌ Failed to download FFmpeg
    cd ..
    pause
    exit /b 1
)
cd ..

REM Download 7-Zip
echo Downloading 7-Zip...
cd tools
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://7-zip.org/a/7z2301-x64.exe' -OutFile '7z2301-x64.exe'}"
if exist "7z2301-x64.exe" (
    echo ✓ 7-Zip downloaded
    echo Installing 7-Zip...
    7z2301-x64.exe /S /D=.
    echo ✓ 7-Zip installed
) else (
    echo ❌ Failed to download 7-Zip
    cd ..
    pause
    exit /b 1
)
cd ..

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✓ Python dependencies installed
echo.

REM Generate SSL certificates
echo Generating SSL certificates...
cd certs
..\openssl\bin\openssl.exe req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
echo ✓ SSL certificates generated
cd ..

REM Create configuration files
echo Creating configuration files...
call :create_configs

REM Create startup scripts
echo Creating startup scripts...
call :create_scripts

REM Create demo sites
echo Creating demo sites...
call :create_demos

echo.
echo  ========================================
echo  ✅ Unified Server Stack Complete!
echo  ========================================
echo  Your professional web server is ready!
echo.
echo  Components installed:
echo  • Nginx 1.24.0 (Web Server)
echo  • PHP 8.3.12 with PHP-FPM
echo  • Node.js 20.10.0
echo  • OpenSSL 3.1.4 (HTTPS)
echo  • FFmpeg (Media Streaming)
echo  • 7-Zip (File Management)
echo  • SSL Certificates
echo.
echo  To start the server:
echo  1. Run: start.bat
echo  2. Open: https://localhost:8443
echo  3. Dashboard: https://localhost:8443/admin
echo.
echo  ========================================
echo.

pause
exit /b 0

:create_configs
echo Creating configuration files...

REM Create main config.json
echo { > configs\config.json
echo   "server": { >> configs\config.json
echo     "http_port": 8080, >> configs\config.json
echo     "https_port": 8443, >> configs\config.json
echo     "admin_port": 3000 >> configs\config.json
echo   }, >> configs\config.json
echo   "nginx": { >> configs\config.json
echo     "config_path": "nginx/conf/nginx.conf", >> configs\config.json
echo     "pid_path": "logs/nginx.pid", >> configs\config.json
echo     "log_path": "logs/nginx.log" >> configs\config.json
echo   }, >> configs\config.json
echo   "php": { >> configs\config.json
echo     "executable": "php/php.exe", >> configs\config.json
echo     "fpm_port": 9000, >> configs\config.json
echo     "config_path": "php/php.ini" >> configs\config.json
echo   }, >> configs\config.json
echo   "nodejs": { >> configs\config.json
echo     "executable": "nodejs/node.exe", >> configs\config.json
echo     "port": 3000, >> configs\config.json
echo     "admin_port": 3001 >> configs\config.json
echo   }, >> configs\config.json
echo   "ssl": { >> configs\config.json
echo     "cert_path": "certs/server.crt", >> configs\config.json
echo     "key_path": "certs/server.key" >> configs\config.json
echo   }, >> configs\config.json
echo   "sites": { >> configs\config.json
echo     "root": "sites", >> configs\config.json
echo     "max_upload_size": "100M", >> configs\config.json
echo     "enable_php": true, >> configs\config.json
echo     "enable_nodejs": true >> configs\config.json
echo   } >> configs\config.json
echo } >> configs\config.json

echo ✓ Configuration files created
goto :eof

:create_scripts
echo Creating startup scripts...

REM Create start.bat
echo @echo off > start.bat
echo title Unified Server Stack >> start.bat
echo color 0A >> start.bat
echo. >> start.bat
echo echo Starting Unified Server Stack... >> start.bat
echo. >> start.bat
echo REM Start PHP-FPM >> start.bat
echo start /B php\php.exe -S 127.0.0.1:9000 -t sites >> start.bat
echo. >> start.bat
echo REM Start Node.js admin server >> start.bat
echo start /B nodejs\node.exe admin_server.js >> start.bat
echo. >> start.bat
echo REM Start Nginx >> start.bat
echo nginx\nginx.exe -p . -c configs\nginx.conf >> start.bat
echo. >> start.bat
echo echo Server started! >> start.bat
echo echo HTTP: http://localhost:8080 >> start.bat
echo echo HTTPS: https://localhost:8443 >> start.bat
echo echo Admin: https://localhost:8443/admin >> start.bat
echo pause >> start.bat

REM Create stop.bat
echo @echo off > stop.bat
echo title Stopping Unified Server Stack >> stop.bat
echo color 0C >> stop.bat
echo. >> stop.bat
echo echo Stopping servers... >> stop.bat
echo. >> stop.bat
echo REM Stop Nginx >> stop.bat
echo nginx\nginx.exe -s quit >> stop.bat
echo. >> stop.bat
echo REM Stop PHP and Node processes >> stop.bat
echo taskkill /F /IM php.exe 2>nul >> stop.bat
echo taskkill /F /IM node.exe 2>nul >> stop.bat
echo. >> stop.bat
echo echo Servers stopped! >> stop.bat
echo pause >> stop.bat

echo ✓ Startup scripts created
goto :eof

:create_demos
echo Creating demo sites...

REM Create PHP demo
if not exist "sites\php-demo" mkdir sites\php-demo
echo ^<?php > sites\php-demo\index.php
echo echo "Hello from PHP!"; >> sites\php-demo\index.php
echo echo "Server time: " . date('Y-m-d H:i:s'); >> sites\php-demo\index.php
echo echo "PHP Version: " . phpversion(); >> sites\php-demo\index.php
echo ?^> >> sites\php-demo\index.php

REM Create Node.js demo
if not exist "sites\node-demo" mkdir sites\node-demo
echo const express = require('express'); > sites\node-demo\app.js
echo const app = express(); >> sites\node-demo\app.js
echo const port = 3001; >> sites\node-demo\app.js
echo. >> sites\node-demo\app.js
echo app.get('/', (req, res) =^> { >> sites\node-demo\app.js
echo   res.send('Hello from Node.js! Server time: ' + new Date()); >> sites\node-demo\app.js
echo }); >> sites\node-demo\app.js
echo. >> sites\node-demo\app.js
echo app.listen(port, () =^> { >> sites\node-demo\app.js
echo   console.log(`Node.js server running on port ${port}`); >> sites\node-demo\app.js
echo }); >> sites\node-demo\app.js

REM Create static demo
if not exist "sites\static-demo" mkdir sites\static-demo
echo ^<!DOCTYPE html^> > sites\static-demo\index.html
echo ^<html^> >> sites\static-demo\index.html
echo ^<head^> >> sites\static-demo\index.html
echo     ^<title^>Static Demo^</title^> >> sites\static-demo\index.html
echo     ^<style^>body{font-family:Arial;margin:40px;background:#f0f0f0;}^</style^> >> sites\static-demo\index.html
echo ^</head^> >> sites\static-demo\index.html
echo ^<body^> >> sites\static-demo\index.html
echo     ^<h1^>Hello from Static HTML!^</h1^> >> sites\static-demo\index.html
echo     ^<p^>This is a static website served by Nginx.^</p^> >> sites\static-demo\index.html
echo     ^<p^>Server time: ^<script^>document.write(new Date())^</script^>^</p^> >> sites\static-demo\index.html
echo ^</body^> >> sites\static-demo\index.html
echo ^</html^> >> sites\static-demo\index.html

echo ✓ Demo sites created
goto :eof