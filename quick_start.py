#!/usr/bin/env python3
"""
Quick Start - Professional Web Server Manager
Automatically creates and starts multiple servers for testing
"""

import sys
import os
from pathlib import Path
from server_manager import ServerManager

def create_test_directories():
    """Create test directories"""
    base_dir = Path("test_servers")
    base_dir.mkdir(exist_ok=True)
    
    directories = [
        "server1_files",
        "server2_files", 
        "server3_files"
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(exist_ok=True)
        
        # Create some test files
        (dir_path / "readme.txt").write_text(f"Welcome to {directory}!\nThis is a test file.")
        (dir_path / "test.txt").write_text(f"Test content for {directory}")
    
    return base_dir

def main():
    """Quick start with multiple servers"""
    print("🚀 PROFESSIONAL WEB SERVER MANAGER - QUICK START")
    print("=" * 60)
    print()
    
    # Create test directories
    print("📁 Creating test directories...")
    base_dir = create_test_directories()
    print(f"✅ Created test directories in {base_dir}")
    
    # Create server manager
    manager = ServerManager()
    
    # Create multiple servers
    print("\n🔧 Creating servers...")
    
    servers = [
        (8080, base_dir / "server1_files"),
        (8081, base_dir / "server2_files"),
        (8082, base_dir / "server3_files")
    ]
    
    created_servers = []
    for port, directory in servers:
        try:
            server_id = manager.create_server(port, str(directory))
            created_servers.append(server_id)
            print(f"✅ Created server {server_id} on port {port}")
        except Exception as e:
            print(f"❌ Failed to create server on port {port}: {e}")
    
    if not created_servers:
        print("❌ No servers created successfully")
        return 1
    
    # Start all servers
    print("\n▶️  Starting servers...")
    for server_id in created_servers:
        if manager.start_server(server_id):
            status = manager.get_server_status(server_id)
            print(f"✅ Server {server_id} started on port {status['port']}")
            print(f"   🌐 http://localhost:{status['port']}")
        else:
            print(f"❌ Failed to start server {server_id}")
    
    # Show status
    print("\n📊 SERVER STATUS:")
    print("-" * 40)
    all_status = manager.get_all_servers_status()
    for server_id, status in all_status.items():
        print(f"Server {server_id}: Port {status['port']} - {'Running' if status['is_running'] else 'Stopped'}")
        if status['is_running']:
            print(f"  🌐 http://localhost:{status['port']}")
    
    print("\n✨ FEATURES AVAILABLE:")
    print("  - Multiple servers running simultaneously")
    print("  - Professional web interface for each server")
    print("  - File upload and download")
    print("  - Real-time logging for each server")
    print("  - Independent directory serving")
    
    print("\n🎯 NEXT STEPS:")
    print("  1. Open the URLs above in your browser")
    print("  2. Upload files to test the functionality")
    print("  3. Check logs in the 'logs' directory")
    print("  4. Run 'python3 main.py' for full management interface")
    
    print("\n⏹️  Press Ctrl+C to stop all servers")
    
    try:
        # Keep running until interrupted
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all servers...")
        for server_id in created_servers:
            manager.stop_server(server_id)
        print("✅ All servers stopped. Goodbye!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())