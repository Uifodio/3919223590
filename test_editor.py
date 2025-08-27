#!/usr/bin/env python3
"""
Test script for Anora Editor
Verifies that the editor can be imported and basic functionality works
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import tkinter as tk
        print("✅ Tkinter imported successfully")
    except ImportError as e:
        print(f"❌ Tkinter import failed: {e}")
        return False
    
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        print("✅ Pygments imported successfully")
    except ImportError as e:
        print(f"❌ Pygments import failed: {e}")
        return False
    
    return True

def test_editor_creation():
    """Test if the editor can be created"""
    print("\n🔍 Testing editor creation...")
    
    try:
        from anora_editor import AnoraEditor
        print("✅ AnoraEditor class imported successfully")
        
        # Create editor instance (but don't run it)
        editor = AnoraEditor()
        print("✅ AnoraEditor instance created successfully")
        
        # Test basic properties
        assert hasattr(editor, 'root'), "Editor should have root window"
        assert hasattr(editor, 'colors'), "Editor should have colors configuration"
        assert hasattr(editor, 'tabs'), "Editor should have tabs list"
        
        print("✅ Basic editor properties verified")
        
        # Clean up
        editor.root.destroy()
        print("✅ Editor cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Editor creation failed: {e}")
        return False

def test_syntax_highlighting():
    """Test syntax highlighting functionality"""
    print("\n🔍 Testing syntax highlighting...")
    
    try:
        from pygments.lexers import get_lexer_by_name
        
        # Test Python syntax
        python_code = "def hello_world():\n    print('Hello, World!')"
        lexer = get_lexer_by_name('python')
        tokens = list(lexer.get_tokens(python_code))
        
        assert len(tokens) > 0, "Should generate tokens for Python code"
        print("✅ Python syntax highlighting works")
        
        # Test C# syntax
        csharp_code = "public class Test {\n    public void Method() {}\n}"
        lexer = get_lexer_by_name('csharp')
        tokens = list(lexer.get_tokens(csharp_code))
        
        assert len(tokens) > 0, "Should generate tokens for C# code"
        print("✅ C# syntax highlighting works")
        
        return True
        
    except Exception as e:
        print(f"❌ Syntax highlighting test failed: {e}")
        return False

def create_test_files():
    """Create test files for the editor"""
    print("\n📝 Creating test files...")
    
    test_files = {
        'test_python.py': '''#!/usr/bin/env python3
"""
Test Python file for Anora Editor
"""

def hello_world():
    """Simple hello world function"""
    print("Hello, World!")
    return True

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    hello_world()
    test = TestClass()
    print(f"Value: {test.get_value()}")
''',
        'test_csharp.cs': '''using UnityEngine;

public class TestScript : MonoBehaviour
{
    [SerializeField] private string message = "Hello from Unity!";
    
    void Start()
    {
        Debug.Log(message);
    }
    
    void Update()
    {
        // Update logic here
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Debug.Log("Space pressed!");
        }
    }
}
''',
        'test_javascript.js': '''// Test JavaScript file
function greet(name) {
    return `Hello, ${name}!`;
}

class Calculator {
    constructor() {
        this.result = 0;
    }
    
    add(value) {
        this.result += value;
        return this;
    }
    
    getResult() {
        return this.result;
    }
}

// Usage
const calc = new Calculator();
console.log(calc.add(5).add(3).getResult());
''',
        'test_html.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test HTML</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Anora Editor</h1>
        <p>This is a test HTML file to demonstrate syntax highlighting.</p>
        <script>
            console.log("JavaScript in HTML works!");
        </script>
    </div>
</body>
</html>
'''
    }
    
    for filename, content in test_files.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created {filename}")
    
    return list(test_files.keys())

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 Anora Editor Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Editor creation
    if test_editor_creation():
        tests_passed += 1
    
    # Test 3: Syntax highlighting
    if test_syntax_highlighting():
        tests_passed += 1
    
    # Create test files
    test_files = create_test_files()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    print("=" * 50)
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Anora Editor is ready to use.")
        print("\n📁 Test files created:")
        for file in test_files:
            print(f"   - {file}")
        print("\n🚀 To run the editor:")
        print("   python anora_editor.py")
        print("\n💡 You can open the test files in the editor to see syntax highlighting!")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)