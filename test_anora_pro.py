#!/usr/bin/env python3
"""
Test script for Anora Editor Pro
Verifies professional features and functionality
"""

import os
import sys
import subprocess
import platform

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'tkinter',
        'pygments',
        'PIL',
        'requests',
        'psutil',
        'git'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - Missing: {e}")
            return False
    
    return True

def test_editor_import():
    """Test if the professional editor can be imported"""
    print("\n🔍 Testing Anora Editor Pro import...")
    
    try:
        from anora_editor_pro import ProfessionalAnoraEditor
        print("✅ ProfessionalAnoraEditor - OK")
        return True
    except ImportError as e:
        print(f"❌ ProfessionalAnoraEditor - Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ ProfessionalAnoraEditor - Error: {e}")
        return False

def test_launcher_import():
    """Test if the professional launcher can be imported"""
    print("\n🔍 Testing Professional Launcher import...")
    
    try:
        import launch_anora_pro
        print("✅ Professional Launcher - OK")
        return True
    except ImportError as e:
        print(f"❌ Professional Launcher - Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Professional Launcher - Error: {e}")
        return False

def test_build_script():
    """Test if the build script can be imported"""
    print("\n🔍 Testing Build Script import...")
    
    try:
        import build_anora_pro
        print("✅ Build Script - OK")
        return True
    except ImportError as e:
        print(f"❌ Build Script - Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Build Script - Error: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'anora_editor_pro.py',
        'launch_anora_pro.py',
        'build_anora_pro.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            return False
    
    return True

def test_unity_detection():
    """Test Unity project detection"""
    print("\n🔍 Testing Unity project detection...")
    
    # Check current directory for Unity indicators
    unity_indicators = ['Assets', 'ProjectSettings', 'Packages', 'Library']
    found_indicators = []
    
    for indicator in unity_indicators:
        if os.path.exists(indicator):
            found_indicators.append(indicator)
    
    if found_indicators:
        print(f"✅ Unity project detected! Found: {', '.join(found_indicators)}")
        return True
    else:
        print("ℹ️ No Unity project detected in current directory")
        return True  # This is not an error

def test_syntax_highlighting():
    """Test syntax highlighting capabilities"""
    print("\n🔍 Testing syntax highlighting...")
    
    try:
        from pygments.lexers import CSharpLexer, PythonLexer, JavascriptLexer
        from pygments.token import Token
        
        # Test C# lexer
        csharp_lexer = CSharpLexer()
        csharp_code = "public class Test { public void Method() { } }"
        tokens = list(csharp_lexer.get_tokens(csharp_code))
        print(f"✅ C# syntax highlighting - {len(tokens)} tokens")
        
        # Test Python lexer
        python_lexer = PythonLexer()
        python_code = "def test(): return True"
        tokens = list(python_lexer.get_tokens(python_code))
        print(f"✅ Python syntax highlighting - {len(tokens)} tokens")
        
        return True
    except Exception as e:
        print(f"❌ Syntax highlighting test failed: {e}")
        return False

def test_platform_support():
    """Test platform-specific features"""
    print("\n🔍 Testing platform support...")
    
    system = platform.system()
    print(f"✅ Platform: {system}")
    
    if system == "Windows":
        try:
            import winreg
            print("✅ Windows registry support - OK")
        except ImportError:
            print("⚠️ Windows registry support - Not available")
    
    return True

def main():
    """Main test function"""
    print("🧪 Anora Editor Pro - Professional Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Required Imports", test_imports),
        ("Editor Import", test_editor_import),
        ("Launcher Import", test_launcher_import),
        ("Build Script Import", test_build_script),
        ("Unity Detection", test_unity_detection),
        ("Syntax Highlighting", test_syntax_highlighting),
        ("Platform Support", test_platform_support)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Anora Editor Pro is ready to use!")
        print("\n🚀 Next steps:")
        print("1. Run: python3 launch_anora_pro.py")
        print("2. Or build executable: python3 build_anora_pro.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)