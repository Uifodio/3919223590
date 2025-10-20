#!/usr/bin/env python3
"""
Test the Professional Web Server Manager
"""

import sys
import os
import time
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from server_manager import ServerManager, WebServer, ServerLogger
        print("✅ ServerManager imported successfully")
        print("✅ WebServer imported successfully")
        print("✅ ServerLogger imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False

def test_server_creation():
    """Test server creation"""
    print("\n🔧 Testing server creation...")
    
    try:
        from server_manager import ServerManager
        
        # Create manager
        manager = ServerManager()
        print("✅ ServerManager created successfully")
        
        # Create test directory
        test_dir = Path("test_server_dir")
        test_dir.mkdir(exist_ok=True)
        (test_dir / "test.txt").write_text("Hello, World!")
        
        # Create server
        server_id = manager.create_server(9999, str(test_dir))
        print(f"✅ Server {server_id} created successfully")
        
        # Check server exists
        if server_id in manager.servers:
            print("✅ Server added to manager")
        else:
            print("❌ Server not found in manager")
            return False
        
        # Test server status
        status = manager.get_server_status(server_id)
        if status:
            print(f"✅ Server status retrieved: Port {status['port']}")
        else:
            print("❌ Failed to get server status")
            return False
        
        # Cleanup
        manager.stop_server(server_id)
        (test_dir / "test.txt").unlink()
        test_dir.rmdir()
        
        return True
    except Exception as e:
        print(f"❌ Server creation failed: {e}")
        return False

def test_logging():
    """Test logging system"""
    print("\n📝 Testing logging system...")
    
    try:
        from server_manager import ServerLogger
        
        # Create logger
        logger = ServerLogger(1)
        print("✅ ServerLogger created successfully")
        
        # Test logging
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        print("✅ Logging functions work")
        
        # Check log file exists
        log_file = Path("logs/server_1.log")
        if log_file.exists():
            print("✅ Log file created successfully")
        else:
            print("❌ Log file not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("\n📁 Testing file operations...")
    
    try:
        # Test directory creation
        test_dir = Path("test_operations")
        test_dir.mkdir(exist_ok=True)
        print("✅ Directory creation works")
        
        # Test file creation
        test_file = test_dir / "test.txt"
        test_file.write_text("Hello, World!")
        print("✅ File creation works")
        
        # Test file reading
        content = test_file.read_text()
        if content == "Hello, World!":
            print("✅ File reading works")
        else:
            print("❌ File reading failed")
            return False
        
        # Test file listing
        files = list(test_dir.iterdir())
        if len(files) > 0:
            print("✅ File listing works")
        else:
            print("❌ File listing failed")
            return False
        
        # Cleanup
        test_file.unlink()
        test_dir.rmdir()
        print("✅ File cleanup works")
        
        return True
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return False

def test_port_availability():
    """Test port availability checking"""
    print("\n🔌 Testing port availability...")
    
    try:
        from server_manager import WebServer, ServerManager
        
        manager = ServerManager()
        
        # Test port availability
        server = WebServer(1, 9998, "/tmp", manager)
        if server.is_port_available(9998):
            print("✅ Port availability checking works")
        else:
            print("❌ Port availability checking failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Port availability test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PROFESSIONAL WEB SERVER MANAGER - TESTS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_server_creation,
        test_logging,
        test_file_operations,
        test_port_availability
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Professional Web Server Manager is ready!")
        print("\nTo use the system:")
        print("  python3 quick_start.py  # Quick start with test servers")
        print("  python3 main.py         # Full management interface")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)