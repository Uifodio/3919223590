#!/usr/bin/env python3
"""
Test script for Modern Server Administrator
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import psutil
        print("✓ psutil imported successfully")
    except ImportError as e:
        print(f"✗ psutil import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'web_server_admin.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js',
        'requirements.txt',
        'README.md'
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
    """Test if the web app can be imported"""
    print("\nTesting web application...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
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

def main():
    """Run all tests"""
    print("🚀 Modern Server Administrator - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_file_structure,
        test_web_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nTo start the application, run:")
        print("python3 web_server_admin.py")
        print("\nThen open your browser to: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)