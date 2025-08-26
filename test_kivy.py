#!/usr/bin/env python3
"""
Simple Kivy test to verify installation
"""

import sys
import os

def test_kivy_import():
    """Test if Kivy can be imported"""
    try:
        import kivy
        print(f"✓ Kivy imported successfully: {kivy.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Kivy import failed: {e}")
        return False

def test_kivy_app():
    """Test basic Kivy app creation"""
    try:
        from kivy.app import App
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        
        print("✓ Kivy components imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Kivy components import failed: {e}")
        return False

def test_simple_app():
    """Test creating a simple Kivy app"""
    try:
        from kivy.app import App
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        
        class TestApp(App):
            def build(self):
                layout = BoxLayout(orientation='vertical')
                layout.add_widget(Label(text='Kivy Test - Working!'))
                layout.add_widget(Button(text='Click Me!'))
                return layout
        
        print("✓ Simple Kivy app created successfully")
        return True
    except Exception as e:
        print(f"✗ Simple app creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Kivy installation...")
    print("=" * 40)
    
    tests = [
        ("Kivy Import", test_kivy_import),
        ("Kivy Components", test_kivy_app),
        ("Simple App", test_simple_app)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All tests passed! Kivy is working correctly.")
        print("\nYou can now run the main application:")
        print("python main.py")
    else:
        print("❌ Some tests failed. Please check your Kivy installation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to continue...")
    sys.exit(0 if success else 1)