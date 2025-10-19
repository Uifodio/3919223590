#!/bin/bash

echo "🚀 Setting up Futuristic Web Server Application..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python 3.8+ is required. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p config
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p templates

# Set permissions
echo "🔐 Setting permissions..."
chmod +x main.py
chmod +x server_manager.py
chmod +x build_exe.py

echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: python main.py"
echo ""
echo "To build EXE:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run build script: python build_exe.py"