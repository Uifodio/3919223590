#!/usr/bin/env python3
"""
Test script to verify Kivy installation
Run this before trying to run the main application
"""

def test_kivy_import():
    """Test if Kivy can be imported successfully"""
    try:
        import kivy
        print(f"✓ Kivy version {kivy.__version__} imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Kivy: {e}")
        return False

def test_kivy_modules():
    """Test if essential Kivy modules can be imported"""
    modules_to_test = [
        'kivy.app',
        'kivy.uix.boxlayout',
        'kivy.uix.button',
        'kivy.uix.label',
        'kivy.core.window'
    ]
    
    all_good = True
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {module}: {e}")
            all_good = False
    
    return all_good

def test_pyinstaller():
    """Test if PyInstaller is available"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller version {PyInstaller.__version__} available")
        return True
    except ImportError:
        print("✗ PyInstaller not installed. Install with: pip install pyinstaller")
        return False

def main():
    print("Testing Kivy Installation...")
    print("=" * 40)
    
    kivy_ok = test_kivy_import()
    modules_ok = test_kivy_modules()
    pyinstaller_ok = test_pyinstaller()
    
    print("\n" + "=" * 40)
    if kivy_ok and modules_ok:
        print("✓ Kivy installation is working correctly!")
        print("You can now run: python main.py")
    else:
        print("✗ Kivy installation has issues.")
        print("Please check the installation instructions in README.md")
    
    if pyinstaller_ok:
        print("✓ PyInstaller is ready for compilation!")
        print("You can now run: pyinstaller CounterApp.spec")
    else:
        print("✗ PyInstaller not available for compilation.")

if __name__ == '__main__':
    main()