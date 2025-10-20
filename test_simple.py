#!/usr/bin/env python3
"""
Test the simple web server components
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import http.server
        print("✅ http.server imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import http.server: {e}")
        return False
    
    try:
        import socketserver
        print("✅ socketserver imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import socketserver: {e}")
        return False
    
    try:
        import webbrowser
        print("✅ webbrowser imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import webbrowser: {e}")
        return False
    
    try:
        from simple_server import SimpleWebServer
        print("✅ SimpleWebServer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SimpleWebServer: {e}")
        return False
    
    return True

def test_server_creation():
    """Test server creation"""
    print("\n🔧 Testing server creation...")
    
    try:
        from simple_server import SimpleWebServer
        server = SimpleWebServer(port=9999, directory="/tmp")
        print("✅ SimpleWebServer created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create SimpleWebServer: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("\n📁 Testing file operations...")
    
    try:
        # Test directory creation
        test_dir = Path("/tmp/web_server_test")
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
        
        # Cleanup
        test_file.unlink()
        test_dir.rmdir()
        print("✅ File cleanup works")
        
        return True
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Futuristic Web Server - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_server_creation,
        test_file_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The server is ready to use.")
        print("\nTo run the server:")
        print("  python3 start_server.py")
        print("  python3 main.py --port 8080 --directory /path/to/directory")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)