#!/usr/bin/env python3
"""
Complete test suite for Modern Server Administrator
"""

import sys
import os
import subprocess
import time
import threading
import requests
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    required_packages = ['flask', 'psutil', 'PIL', 'werkzeug']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
            print(f"✓ {package} imported successfully")
        except ImportError as e:
            print(f"✗ {package} import failed: {e}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'web_server_admin.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js',
        'requirements.txt',
        'README.md',
        'demo_website/index.html',
        'demo_website/index.php'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_web_app():
    """Test if the web app can be imported and started"""
    print("\nTesting web application...")
    
    try:
        # Import the web app
        from web_server_admin import app
        print("✓ Web application imported successfully")
        
        # Test if app is a Flask instance
        if hasattr(app, 'route'):
            print("✓ Flask app instance created")
        else:
            print("✗ Invalid Flask app instance")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Web application test failed: {e}")
        return False

def test_server_startup():
    """Test if the server can start up"""
    print("\nTesting server startup...")
    
    try:
        # Start the server in a separate thread
        from web_server_admin import app
        import threading
        import time
        
        def run_server():
            app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get('http://127.0.0.1:5001', timeout=5)
            if response.status_code == 200:
                print("✓ Server started and responding")
                return True
            else:
                print(f"✗ Server responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Server not responding: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Server startup test failed: {e}")
        return False

def test_php_detection():
    """Test PHP detection"""
    print("\nTesting PHP detection...")
    
    try:
        from web_server_admin import check_php_available
        php_available = check_php_available()
        if php_available:
            print("✓ PHP detected")
        else:
            print("⚠️  PHP not detected (this is normal if PHP is not installed)")
        return True
    except Exception as e:
        print(f"✗ PHP detection test failed: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("\nTesting file operations...")
    
    try:
        from web_server_admin import get_file_size, allowed_file
        
        # Test file size function
        test_file = 'requirements.txt'
        if os.path.exists(test_file):
            size = get_file_size(test_file)
            print(f"✓ File size function works: {size}")
        else:
            print("⚠️  Test file not found for size test")
        
        # Test allowed file function
        if allowed_file('test.txt'):
            print("✓ Allowed file function works")
        else:
            print("✗ Allowed file function failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False

def test_demo_files():
    """Test demo files"""
    print("\nTesting demo files...")
    
    try:
        # Check if demo files exist and are valid
        demo_files = [
            'demo_website/index.html',
            'demo_website/index.php',
            'demo_website/style.css',
            'demo_website/script.js'
        ]
        
        for file_path in demo_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 0:
                        print(f"✓ {file_path} is valid")
                    else:
                        print(f"✗ {file_path} is empty")
                        return False
            else:
                print(f"✗ {file_path} not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Demo files test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Modern Server Administrator - Complete Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_file_structure,
        test_web_app,
        test_php_detection,
        test_file_operations,
        test_demo_files,
        test_server_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nTo start the application:")
        print("1. Run: python web_server_admin.py")
        print("2. Open your browser to: http://localhost:5000")
        print("3. Or use the startup script: ./start.sh (Linux/Mac) or start.bat (Windows)")
        print("\nTo build EXE (Windows only):")
        print("1. Run: python build_exe.py")
        print("2. Run: install.bat to install the application")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("   Make sure all dependencies are installed: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)