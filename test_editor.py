#!/usr/bin/env python3
"""
Simple test script for Anora Editor
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
        
        from tkinter import ttk, filedialog, messagebox, simpledialog
        print("✓ tkinter widgets imported successfully")
        
        import json
        print("✓ json imported successfully")
        
        import threading
        print("✓ threading imported successfully")
        
        import re
        print("✓ re imported successfully")
        
        try:
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name, TextLexer
            print("✓ pygments imported successfully")
        except ImportError:
            print("⚠ pygments not available - syntax highlighting will be disabled")
            
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_editor_creation():
    """Test if the editor can be created"""
    try:
        from anora_editor_advanced import AnoraEditor
        print("✓ AnoraEditor class imported successfully")
        
        # Create editor instance (but don't run it)
        editor = AnoraEditor()
        print("✓ AnoraEditor instance created successfully")
        
        # Test basic properties
        assert hasattr(editor, 'root'), "Editor should have root window"
        assert hasattr(editor, 'colors'), "Editor should have colors"
        assert hasattr(editor, 'tabs'), "Editor should have tabs"
        
        print("✓ Editor properties verified")
        
        return True
        
    except Exception as e:
        print(f"✗ Editor creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("Anora Editor - Test Suite")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
        
    # Test editor creation
    if not test_editor_creation():
        print("\n❌ Editor creation tests failed")
        return False
        
    print("\n✅ All tests passed!")
    print("The Anora Editor is ready to use.")
    print("\nTo run the editor:")
    print("1. Activate virtual environment: source anora_env/bin/activate")
    print("2. Run launcher: python launch_anora.py")
    print("3. Or run directly: python anora_editor_advanced.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)