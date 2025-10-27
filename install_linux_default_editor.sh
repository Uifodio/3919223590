#!/bin/bash

# Anora Editor - Linux Default Editor Installation Script
# This script sets Anora Editor as the default editor for various file types

echo "Installing Anora Editor as default editor..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

# Create desktop entry
DESKTOP_ENTRY="$HOME/.local/share/applications/anora-editor.desktop"

cat > "$DESKTOP_ENTRY" << EOF
[Desktop Entry]
Name=Anora Editor
Comment=Professional Unity Code Editor
Exec=$APP_DIR/dist_electron/linux-unpacked/anora-editor %F
Icon=$APP_DIR/public/icon.svg
Terminal=false
Type=Application
Categories=Development;TextEditor;IDE;
MimeType=text/plain;text/x-python;text/x-csharp;text/x-javascript;text/x-typescript;text/html;text/css;application/json;text/x-c;text/x-c++;
StartupNotify=true
StartupWMClass=anora-editor
EOF

# Make the desktop entry executable
chmod +x "$DESKTOP_ENTRY"

# Update desktop database
update-desktop-database "$HOME/.local/share/applications"

# Set as default for various file types
echo "Setting file associations..."

# Python files
xdg-mime default anora-editor.desktop text/x-python
xdg-mime default anora-editor.desktop application/x-python

# C# files
xdg-mime default anora-editor.desktop text/x-csharp

# JavaScript files
xdg-mime default anora-editor.desktop text/x-javascript
xdg-mime default anora-editor.desktop application/javascript

# TypeScript files
xdg-mime default anora-editor.desktop text/x-typescript
xdg-mime default anora-editor.desktop application/typescript

# HTML files
xdg-mime default anora-editor.desktop text/html

# CSS files
xdg-mime default anora-editor.desktop text/css

# JSON files
xdg-mime default anora-editor.desktop application/json

# C/C++ files
xdg-mime default anora-editor.desktop text/x-c
xdg-mime default anora-editor.desktop text/x-c++

# Text files
xdg-mime default anora-editor.desktop text/plain

echo "Installation complete!"
echo "Anora Editor is now set as the default editor for:"
echo "  - Python (.py)"
echo "  - C# (.cs)"
echo "  - JavaScript (.js, .jsx)"
echo "  - TypeScript (.ts, .tsx)"
echo "  - HTML (.html, .htm)"
echo "  - CSS (.css)"
echo "  - JSON (.json)"
echo "  - C/C++ (.c, .cpp, .h, .hpp)"
echo "  - Text files (.txt)"
echo ""
echo "You may need to restart your file manager for changes to take effect."
echo "Desktop entry created at: $DESKTOP_ENTRY"