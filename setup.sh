#!/bin/bash

# Anora Editor - Setup Script
# This script sets up Anora Editor for Linux/macOS

echo "Setting up Anora Editor..."

# Make scripts executable
chmod +x anora_editor.py
chmod +x run_anora.sh
chmod +x install_linux_default_editor.sh
chmod +x setup.sh

echo "Made scripts executable"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To run Anora Editor:"
echo "  ./run_anora.sh"
echo ""
echo "To install file associations:"
echo "  ./install_linux_default_editor.sh"
echo ""
echo "To run directly with Python:"
echo "  python3 anora_editor.py"