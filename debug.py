#!/usr/bin/env python3
"""
Debug script to identify Kivy installation issues
"""

import sys
import traceback

def test_basic_imports():
    """Test basic Python imports"""
    print("Testing basic imports...")
    try:
        import os
        print("✓ os imported")
        import sys
        print("✓ sys imported")
        return True
    except Exception as e:
        print(f"✗ Basic imports failed: {e}")
        return False

def test_kivy_import():
    """Test Kivy import step by step"""
    print("\nTesting Kivy imports...")
    
    try:
        print("Importing kivy...")
        import kivy
        print(f"✓ Kivy version: {kivy.__version__}")
        
        print("Importing kivy.app...")
        from kivy.app import App
        print("✓ kivy.app imported")
        
        print("Importing kivy.uix.label...")
        from kivy.uix.label import Label
        print("✓ kivy.uix.label imported")
        
        print("Importing kivy.uix.button...")
        from kivy.uix.button import Button
        print("✓ kivy.uix.button imported")
        
        print("Importing kivy.uix.boxlayout...")
        from kivy.uix.boxlayout import BoxLayout
        print("✓ kivy.uix.boxlayout imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Kivy import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_simple_app():
    """Test creating a simple app"""
    print("\nTesting simple app creation...")
    try:
        from kivy.app import App
        from kivy.uix.label import Label
        
        class TestApp(App):
            def build(self):
                return Label(text='Test')
        
        print("✓ Simple app class created")
        return True
        
    except Exception as e:
        print(f"✗ Simple app creation failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def main():
    print("Kivy Debug Information")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    basic_ok = test_basic_imports()
    kivy_ok = test_kivy_import()
    app_ok = test_simple_app()
    
    print("\n" + "=" * 50)
    if basic_ok and kivy_ok and app_ok:
        print("✓ All tests passed! Try running simple_test.py")
    else:
        print("✗ Some tests failed. Check the errors above.")
        print("\nTroubleshooting tips:")
        print("1. Try: pip uninstall kivy && pip install kivy==2.1.0")
        print("2. Make sure you have the latest pip: pip install --upgrade pip")
        print("3. Try installing in a virtual environment")

if __name__ == '__main__':
    main()