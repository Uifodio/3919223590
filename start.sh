#!/bin/bash
# Modern Server Administrator - Startup Script

echo "🚀 Modern Server Administrator - Professional Edition"
echo "======================================================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import flask, psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
fi

echo "✓ Dependencies ready"

# Check PHP availability
echo "Checking PHP availability..."
if command -v php &> /dev/null; then
    echo "✓ PHP found: $(php --version | head -n1)"
else
    echo "⚠️  PHP not found - PHP servers will not work"
    echo "   Install PHP to enable PHP server support"
fi

# Create demo folder if it doesn't exist
if [ ! -d "demo_website" ]; then
    echo "Creating demo website..."
    python3 demo.py
fi

echo ""
echo "Starting Modern Server Administrator..."
echo "The application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the application"
echo ""

# Start the application
python3 web_server_admin.py
