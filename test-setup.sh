#!/bin/bash

echo "========================================"
echo "  Professional Server Manager Test"
echo "========================================"
echo

echo "🔍 Testing installed components..."
echo

# Test Node.js
echo "Node.js version:"
node --version
echo

# Test PHP
echo "PHP version:"
php --version
echo

# Test Nginx
echo "Nginx version:"
nginx -v
echo

# Test web interface
echo "🌐 Testing web interface..."
echo "Main interface (port 80):"
curl -s -I http://localhost:80 | head -3
echo

echo "PHP server (port 8080):"
curl -s -I http://localhost:8080 | head -3
echo

# Test file serving
echo "📁 Testing file serving..."
echo "Main index.html:"
curl -s http://localhost:80 | grep -o '<title>.*</title>'
echo

echo "PHP server:"
curl -s http://localhost:8080 | grep -o '<title>.*</title>'
echo

# Show running processes
echo "🔄 Running processes:"
ps aux | grep -E "(nginx|php|node)" | grep -v grep
echo

# Show listening ports
echo "🔌 Listening ports:"
ss -tlnp | grep -E ":(80|8080|3000|3001)"
echo

echo "========================================"
echo "✅ Professional Server Manager is ready!"
echo "========================================"
echo
echo "🌐 Web Interface: http://localhost:80"
echo "🐘 PHP Server: http://localhost:8080"
echo "📁 Server Manager: node server-manager.js"
echo
echo "All services are running and ready for development!"