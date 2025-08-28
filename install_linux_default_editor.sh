#!/bin/bash

# Nexus Editor Linux Installation Script
# This script creates a .desktop entry and registers file associations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Nexus Editor Linux Installation${NC}"
echo "=================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR"

# Check if the app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}Error: App directory not found at $APP_DIR${NC}"
    exit 1
fi

# Check if the executable exists
if [ ! -f "$APP_DIR/nexus-editor" ] && [ ! -f "$APP_DIR/nexus-editor.AppImage" ]; then
    echo -e "${YELLOW}Warning: Nexus Editor executable not found. Please build the app first.${NC}"
    echo "Run: npm run dist"
fi

# Create .desktop file
DESKTOP_FILE="$HOME/.local/share/applications/nexus-editor.desktop"

echo "Creating .desktop file..."

# Determine the executable path
if [ -f "$APP_DIR/nexus-editor" ]; then
    EXEC_PATH="$APP_DIR/nexus-editor"
elif [ -f "$APP_DIR/nexus-editor.AppImage" ]; then
    EXEC_PATH="$APP_DIR/nexus-editor.AppImage"
else
    EXEC_PATH="$APP_DIR/nexus-editor"
fi

# Create the .desktop file
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Nexus Editor
Comment=Professional code editor for Unity development
Exec=$EXEC_PATH %F
Icon=$APP_DIR/icon.png
Terminal=false
Categories=Development;TextEditor;IDE;
MimeType=text/plain;text/x-c;text/x-c++;text/x-csharp;text/x-java;text/x-javascript;text/x-python;text/x-php;text/x-html;text/x-css;text/xml;application/json;application/x-yaml;
Keywords=editor;code;programming;unity;csharp;javascript;python;
StartupWMClass=nexus-editor
EOF

# Make the .desktop file executable
chmod +x "$DESKTOP_FILE"

# Create icon directory if it doesn't exist
mkdir -p "$HOME/.local/share/icons"

# Copy icon if it exists
if [ -f "$APP_DIR/icon.png" ]; then
    cp "$APP_DIR/icon.png" "$HOME/.local/share/icons/nexus-editor.png"
    echo "Icon copied to $HOME/.local/share/icons/nexus-editor.png"
fi

# Register MIME types
echo "Registering MIME types..."

# Create MIME type associations
mkdir -p "$HOME/.local/share/mime/packages"

cat > "$HOME/.local/share/mime/packages/nexus-editor.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="text/x-c">
    <glob pattern="*.c"/>
    <glob pattern="*.h"/>
  </mime-type>
  <mime-type type="text/x-c++">
    <glob pattern="*.cpp"/>
    <glob pattern="*.cc"/>
    <glob pattern="*.cxx"/>
    <glob pattern="*.hpp"/>
    <glob pattern="*.hh"/>
    <glob pattern="*.hxx"/>
  </mime-type>
  <mime-type type="text/x-csharp">
    <glob pattern="*.cs"/>
  </mime-type>
  <mime-type type="text/x-javascript">
    <glob pattern="*.js"/>
    <glob pattern="*.jsx"/>
    <glob pattern="*.ts"/>
    <glob pattern="*.tsx"/>
  </mime-type>
  <mime-type type="text/x-python">
    <glob pattern="*.py"/>
    <glob pattern="*.pyw"/>
  </mime-type>
  <mime-type type="text/x-html">
    <glob pattern="*.html"/>
    <glob pattern="*.htm"/>
  </mime-type>
  <mime-type type="text/x-css">
    <glob pattern="*.css"/>
  </mime-type>
  <mime-type type="application/json">
    <glob pattern="*.json"/>
  </mime-type>
  <mime-type type="text/xml">
    <glob pattern="*.xml"/>
    <glob pattern="*.xhtml"/>
  </mime-type>
</mime-info>
EOF

# Update MIME database
update-mime-database "$HOME/.local/share/mime"

# Set default applications for common file types
echo "Setting default applications..."

# Function to set default app for a MIME type
set_default_app() {
    local mime_type="$1"
    local desktop_file="nexus-editor.desktop"
    
    if command -v xdg-mime >/dev/null 2>&1; then
        xdg-mime default "$desktop_file" "$mime_type" 2>/dev/null || true
    fi
}

# Set defaults for common development file types
set_default_app "text/x-c"
set_default_app "text/x-c++"
set_default_app "text/x-csharp"
set_default_app "text/x-javascript"
set_default_app "text/x-python"
set_default_app "text/x-html"
set_default_app "text/x-css"
set_default_app "application/json"
set_default_app "text/xml"

echo -e "${GREEN}Installation completed successfully!${NC}"
echo ""
echo "Nexus Editor has been installed with the following features:"
echo "✓ Desktop entry created at $DESKTOP_FILE"
echo "✓ File associations registered for common development file types"
echo "✓ Icon installed (if available)"
echo ""
echo "You can now:"
echo "- Launch Nexus Editor from your applications menu"
echo "- Double-click on code files to open them in Nexus Editor"
echo "- Right-click on files and select 'Open with > Nexus Editor'"
echo ""
echo "To uninstall, run:"
echo "rm $DESKTOP_FILE"
echo "rm $HOME/.local/share/icons/nexus-editor.png"
echo "rm $HOME/.local/share/mime/packages/nexus-editor.xml"
echo "update-mime-database $HOME/.local/share/mime"