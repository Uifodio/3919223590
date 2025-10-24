#!/bin/bash

# Professional Server Administrator - Standalone Startup Script
# GitHub-inspired professional web server management tool

echo "🚀 Starting Professional Server Administrator..."
echo "================================================"

# Check if we're in the right directory
if [ ! -f "web_server_admin.py" ]; then
    echo "❌ Error: web_server_admin.py not found. Please run this script from the project directory."
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check PHP installation
if ! command -v php &> /dev/null; then
    echo "❌ Error: PHP is not installed or not in PATH"
    exit 1
fi

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed or not in PATH"
    exit 1
fi

# Display system information
echo "📋 System Information:"
echo "  Python: $(python3 --version)"
echo "  PHP: $(php --version | head -n1)"
echo "  Node.js: $(node --version)"
echo "  OS: $(uname -s) $(uname -r)"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p sites logs uploads php templates static/css static/js static/images

# Set permissions
chmod +x web_server_admin.py
chmod 755 sites logs uploads

# Check if Flask is installed
echo "🔍 Checking dependencies..."
python3 -c "import flask, psutil, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing missing dependencies..."
    pip3 install -r requirements.txt --user
fi

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="127.0.0.1"
fi

echo ""
echo "🌐 Server will be available at:"
echo "  Local:   http://127.0.0.1:5000"
echo "  Network: http://$LOCAL_IP:5000"
echo ""
echo "📱 Features:"
echo "  ✅ GitHub-inspired professional UI"
echo "  ✅ Multi-server management (HTTP, PHP, Node.js)"
echo "  ✅ Real-time monitoring and logging"
echo "  ✅ File upload and management"
echo "  ✅ Drag-and-drop interface"
echo "  ✅ Responsive design"
echo ""

# Start the application
echo "🚀 Starting Professional Server Administrator..."
echo "   Press Ctrl+C to stop the server"
echo ""

# Run the Flask application
python3 web_server_admin.py