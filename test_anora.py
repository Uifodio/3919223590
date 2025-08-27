#!/usr/bin/env python3
"""
Test script for Anora Editor
This script tests if the editor can run with available dependencies
"""

import sys
import os

def test_imports():
    """Test if required modules can be imported"""
    print("Testing imports...")
    
    # Test tkinter (built-in)
    try:
        import tkinter as tk
        print("✓ tkinter available")
    except ImportError as e:
        print(f"✗ tkinter not available: {e}")
        print("Install python3-tk package:")
        print("  Ubuntu/Debian: sudo apt install python3-tk")
        print("  CentOS/RHEL: sudo yum install python3-tkinter")
        print("  macOS: brew install python-tk")
        return False
    
    # Test pygments (for syntax highlighting)
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, TextLexer
        print("✓ pygments available")
    except ImportError as e:
        print(f"✗ pygments not available: {e}")
        print("Install with: pip install pygments")
        print("Or use: pip install -r requirements.txt")
        return False
    
    return True

def test_basic_functionality():
    """Test basic editor functionality"""
    print("\nTesting basic functionality...")
    
    try:
        # Import the main editor
        from anora_editor import AnoraEditor
        print("✓ AnoraEditor class imported successfully")
        
        # Test creating a simple window
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = AnoraEditor(root)
        print("✓ AnoraEditor instance created successfully")
        
        # Clean up
        root.destroy()
        print("✓ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Anora Editor - Test Script")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install missing dependencies.")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality test failed.")
        return False
    
    print("\n✅ All tests passed! Anora Editor is ready to use.")
    print("\nTo run the editor:")
    print("  python3 anora_editor.py")
    print("  or")
    print("  ./run_anora.sh")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)