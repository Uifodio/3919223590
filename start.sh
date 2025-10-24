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
