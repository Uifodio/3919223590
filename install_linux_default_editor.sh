#!/bin/bash

# Anora Editor - Linux File Association Installer
# Run this script to register Anora Editor as default editor

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANORA_PATH="$SCRIPT_DIR/anora_editor.py"
PYTHON_PATH="python3"

# Check if Python is available
if ! command -v $PYTHON_PATH &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH. Please install Python 3.7+ and try again."
    exit 1
fi

# Check if Anora Editor exists
if [ ! -f "$ANORA_PATH" ]; then
    echo "Error: Anora Editor not found at: $ANORA_PATH"
    exit 1
fi

# Make the script executable
chmod +x "$ANORA_PATH"

# File extensions to register
EXTENSIONS=(".py" ".cs" ".js" ".html" ".css" ".json" ".txt" ".c" ".cpp" ".h")

# Create desktop entry
DESKTOP_ENTRY="[Desktop Entry]
Name=Anora Editor
Comment=Professional Code Editor for Unity
Exec=$PYTHON_PATH $ANORA_PATH %F
Icon=text-editor
Terminal=false
Type=Application
Categories=Development;TextEditor;
MimeType=text/plain;text/x-python;text/x-csharp;text/javascript;text/html;text/css;application/json;text/x-c;text/x-c++;
StartupNotify=true
"

# Write desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/anora-editor.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"
echo "$DESKTOP_ENTRY" > "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"

echo "Created desktop entry: $DESKTOP_FILE"

# Register MIME types
for ext in "${EXTENSIONS[@]}"; do
    case $ext in
        ".py")
            MIME_TYPE="text/x-python"
            ;;
        ".cs")
            MIME_TYPE="text/x-csharp"
            ;;
        ".js")
            MIME_TYPE="text/javascript"
            ;;
        ".html")
            MIME_TYPE="text/html"
            ;;
        ".css")
            MIME_TYPE="text/css"
            ;;
        ".json")
            MIME_TYPE="application/json"
            ;;
        ".c"|".cpp"|".h")
            MIME_TYPE="text/x-c"
            ;;
        *)
            MIME_TYPE="text/plain"
            ;;
    esac
    
    # Add MIME type association
    xdg-mime default anora-editor.desktop "$MIME_TYPE" 2>/dev/null || true
    echo "Registered $ext ($MIME_TYPE) with Anora Editor"
done

# Update desktop database
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo ""
echo "Installation complete!"
echo "You can now double-click files to open them in Anora Editor."
echo ""
echo "To uninstall, run: rm '$DESKTOP_FILE'"