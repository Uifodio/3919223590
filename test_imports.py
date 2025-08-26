#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    
    try:
        print("✓ Importing utils...")
        from src.utils import FileUtils, SystemUtils, config_manager, clipboard_manager
        print("✓ Utils imported successfully")
        
        print("✓ Importing file_explorer...")
        from src.file_explorer import FileExplorer
        print("✓ File explorer imported successfully")
        
        print("✓ Importing code_editor...")
        from src.code_editor import CodeEditor, CodeEditorWindow
        print("✓ Code editor imported successfully")
        
        print("✓ Importing unity_integration...")
        from src.unity_integration import UnityIntegration
        print("✓ Unity integration imported successfully")
        
        print("✓ Importing main_window...")
        from src.main_window import MainWindow
        print("✓ Main window imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)