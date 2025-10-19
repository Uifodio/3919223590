#!/usr/bin/env python3
"""
Simple test to verify the server components work
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from server_manager import WebServerManager
        print("✅ WebServerManager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import WebServerManager: {e}")
        return False
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Flask: {e}")
        return False
    
    try:
        import qrcode
        print("✅ QRCode imported successfully")
    except Exception as e:
        print(f"❌ Failed to import QRCode: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL imported successfully")
    except Exception as e:
        print(f"❌ Failed to import PIL: {e}")
        return False
    
    return True

def test_server_creation():
    """Test server manager creation"""
    print("\n🔧 Testing server creation...")
    
    try:
        from server_manager import WebServerManager
        server_manager = WebServerManager()
        print("✅ WebServerManager created successfully")
        
        # Test configuration loading
        config = server_manager.config
        print(f"✅ Configuration loaded: {len(config)} settings")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create WebServerManager: {e}")
        return False

def test_directories():
    """Test directory creation"""
    print("\n📁 Testing directory creation...")
    
    directories = ['uploads', 'logs', 'static', 'templates', 'config']
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Directory {directory} created/verified")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Futuristic Web Server - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_server_creation,
        test_directories
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nTo run the full application:")
        print("  python3 main.py  # GUI version")
        print("  python3 test_server.py  # Headless version")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)