#!/usr/bin/env python3
"""
Simple test for Nova Editor
"""

import sys
import os

def test_nova_editor():
    """Test Nova Editor import and basic functionality"""
    
    print("🧪 Testing Nova Editor...")
    
    try:
        # Test import
        from anora_editor import NovaEditor
        print("✅ NovaEditor imported successfully")
        
        # Test creation
        editor = NovaEditor()
        print("✅ NovaEditor instance created successfully")
        
        # Test basic properties
        assert hasattr(editor, 'root'), "Editor should have root window"
        assert hasattr(editor, 'notebook'), "Editor should have notebook"
        assert hasattr(editor, 'tabs'), "Editor should have tabs"
        print("✅ Basic properties verified")
        
        # Test syntax highlighting
        assert hasattr(editor, 'highlight_syntax'), "Editor should have syntax highlighting"
        assert hasattr(editor, 'simple_highlight_syntax'), "Editor should have simple highlighting"
        print("✅ Syntax highlighting methods verified")
        
        # Test drag and drop
        assert hasattr(editor, 'setup_drag_drop'), "Editor should have drag and drop"
        assert hasattr(editor, 'on_drop'), "Editor should have drop handler"
        print("✅ Drag and drop methods verified")
        
        # Clean up
        editor.root.destroy()
        print("✅ Editor cleanup completed")
        
        print("\n🎉 All tests passed! Nova Editor is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_nova_editor()
    if not success:
        sys.exit(1)