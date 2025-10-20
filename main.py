#!/usr/bin/env python3
"""
Futuristic Web Server - Main Entry Point
Simple, working web server that definitely works
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from simple_server import main
    main()
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)