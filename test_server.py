#!/usr/bin/env python3
"""
Test version of the Futuristic Web Server - Headless mode for testing
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from server_manager import WebServerManager
import logging

def test_server():
    """Test the server functionality without GUI"""
    print("🚀 Testing Futuristic Web Server - Headless Mode")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/server.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Create server manager
    server_manager = WebServerManager()
    
    # Test server 1
    print("\n📡 Starting Server 1 on port 8080...")
    if server_manager.start_server(1, 8080, str(Path.home())):
        print("✅ Server 1 started successfully!")
        print("   Access at: http://localhost:8080")
    else:
        print("❌ Failed to start Server 1")
        return False
    
    # Test server 2
    print("\n📡 Starting Server 2 on port 8081...")
    if server_manager.start_server(2, 8081, str(Path.home() / "Documents")):
        print("✅ Server 2 started successfully!")
        print("   Access at: http://localhost:8081")
    else:
        print("❌ Failed to start Server 2")
        return False
    
    print("\n🎉 Both servers are running!")
    print("\nServer Status:")
    print(f"  Server 1: {'Running' if server_manager.get_server_status(1) else 'Stopped'}")
    print(f"  Server 2: {'Running' if server_manager.get_server_status(2) else 'Stopped'}")
    
    print("\n📋 Available Features:")
    print("  - File upload and download")
    print("  - Media streaming")
    print("  - QR code generation")
    print("  - Thumbnail generation")
    print("  - File search")
    print("  - Real-time logs")
    
    print("\n🌐 Web Interface:")
    print("  - Server 1: http://localhost:8080")
    print("  - Server 2: http://localhost:8081")
    
    print("\n📁 API Endpoints:")
    print("  - GET /api/files - List files")
    print("  - POST /api/upload - Upload files")
    print("  - GET /api/download/<filename> - Download file")
    print("  - GET /api/stream/<filename> - Stream file")
    print("  - GET /api/qr/<filename> - Generate QR code")
    print("  - GET /api/thumbnail/<filename> - Get thumbnail")
    print("  - DELETE /api/delete/<filename> - Delete file")
    
    print("\n⏹️  Press Ctrl+C to stop servers...")
    
    try:
        # Keep servers running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        server_manager.stop_server(1)
        server_manager.stop_server(2)
        print("✅ Servers stopped successfully!")
        return True

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)