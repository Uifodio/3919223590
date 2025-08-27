#!/bin/bash

# Anora Editor - Linux/macOS Launcher
# This file launches Anora Editor

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

# Launch Anora Editor
python3 anora_editor.py "$@"

# If a file was passed as argument, it will be opened automatically