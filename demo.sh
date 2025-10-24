#!/bin/bash

echo "🚀 Professional Server Manager - Demo"
echo "======================================"
echo ""

# Check installations
echo "📋 Checking installations..."
echo "Node.js version: $(node --version)"
echo "NPM version: $(npm --version)"
echo "PHP version: $(php --version | head -1)"
echo "Nginx version: $(nginx -v 2>&1)"
echo ""

# Show directory structure
echo "📁 Directory structure:"
ls -la /workspace/
echo ""

echo "📁 Server directories:"
ls -la /workspace/servers/
echo ""

echo "📁 Configuration files:"
ls -la /workspace/config/
echo ""

# Test Node.js server
echo "🧪 Testing Node.js server..."
cd /workspace/servers/node-server-1
echo "Starting Node.js server on port 3000..."
node server.js &
NODE_PID=$!
sleep 2

# Test if server is responding
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Node.js server is running and responding"
else
    echo "❌ Node.js server test failed"
fi

# Kill the test server
kill $NODE_PID 2>/dev/null
echo ""

# Test PHP server
echo "🧪 Testing PHP server..."
cd /workspace/servers/php-server-1
echo "Starting PHP server on port 3001..."
php -S localhost:3001 -t . &
PHP_PID=$!
sleep 2

# Test if server is responding
if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ PHP server is running and responding"
else
    echo "❌ PHP server test failed"
fi

# Kill the test server
kill $PHP_PID 2>/dev/null
echo ""

# Show available commands
echo "🎯 Available commands:"
echo "1. Start web interface: Open web-interface.html in your browser"
echo "2. Start CLI manager: node server-manager.js"
echo "3. Quick start: ./start.sh"
echo "4. Start Node.js server: cd /workspace/servers/node-server-1 && node server.js"
echo "5. Start PHP server: cd /workspace/servers/php-server-1 && php -S localhost:3001 -t ."
echo ""

echo "📖 Documentation:"
echo "Read README.md for detailed usage instructions"
echo ""

echo "🎉 Professional Server Manager is ready for use!"
echo "You can now run up to 10 servers simultaneously on ports 3000-3009"