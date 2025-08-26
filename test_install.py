#!/usr/bin/env python3
"""
Test script to verify installation and dependencies
"""

import sys
import os
import traceback

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    modules = [
        ('PySide6', 'PySide6'),
        ('PIL', 'Pillow'),
        ('psutil', 'psutil'),
        ('watchdog', 'watchdog'),
        ('pyperclip', 'pyperclip'),
        ('send2trash', 'send2trash')
    ]
    
    # Add Windows-specific modules only on Windows
    if sys.platform == "win32":
        modules.append(('win32api', 'pywin32'))
    
    failed = []
    for module_name, package_name in modules:
        try:
            if module_name == 'PIL':
                import PIL
                print(f"✓ {package_name} ({PIL.__version__})")
            elif module_name == 'PySide6':
                import PySide6
                print(f"✓ {package_name} ({PySide6.__version__})")
            elif module_name == 'psutil':
                import psutil
                print(f"✓ {package_name} ({psutil.__version__})")
            else:
                __import__(module_name)
                print(f"✓ {package_name}")
        except ImportError as e:
            print(f"✗ {package_name}: {e}")
            failed.append(package_name)
        except Exception as e:
            print(f"? {package_name}: {e}")
            failed.append(package_name)
    
    return failed

def test_pyside6():
    """Test PySide6 functionality"""
    print("\nTesting PySide6...")
    try:
        import os
        # Set environment variable for offscreen rendering
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        
        # Create a minimal app
        app = QApplication([])
        print("✓ QApplication created successfully")
        
        # Test basic widgets
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Test")
        layout.addWidget(label)
        print("✓ Basic widgets work")
        
        app.quit()
        print("✓ PySide6 test completed")
        return True
    except Exception as e:
        print(f"✗ PySide6 test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_file_operations():
    """Test file operations"""
    print("\nTesting file operations...")
    try:
        import tempfile
        import shutil
        from pathlib import Path
        
        # Test basic file operations
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        # Test path operations
        path = Path(temp_file)
        print(f"✓ File created: {path}")
        print(f"✓ File exists: {path.exists()}")
        print(f"✓ File size: {path.stat().st_size}")
        
        # Cleanup
        os.unlink(temp_file)
        print("✓ File operations test completed")
        return True
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False

def test_application_modules():
    """Test application-specific modules"""
    print("\nTesting application modules...")
    
    # Add src to path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    modules = [
        'src.main_window',
        'src.utils.config_manager',
        'src.utils.logger',
        'src.widgets.file_tree',
        'src.widgets.file_list',
        'src.widgets.editor_widget',
        'src.widgets.address_bar'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
        except Exception as e:
            print(f"? {module}: {e}")
            failed.append(module)
    
    return failed

def main():
    """Run all tests"""
    print("=" * 50)
    print("Nova Explorer - Installation Test")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    
    # Test imports
    failed_imports = test_imports()
    
    # Test PySide6
    pyside6_ok = test_pyside6()
    
    # Test file operations
    file_ops_ok = test_file_operations()
    
    # Test application modules
    failed_app_modules = test_application_modules()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    if failed_imports:
        print(f"✗ Failed imports: {failed_imports}")
    else:
        print("✓ All imports successful")
    
    if pyside6_ok:
        print("✓ PySide6 functionality working")
    else:
        print("✗ PySide6 functionality failed")
    
    if file_ops_ok:
        print("✓ File operations working")
    else:
        print("✗ File operations failed")
    
    if failed_app_modules:
        print(f"✗ Failed app modules: {failed_app_modules}")
    else:
        print("✓ All application modules loaded")
    
    if not failed_imports and pyside6_ok and file_ops_ok and not failed_app_modules:
        print("\n🎉 ALL TESTS PASSED! Installation is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())