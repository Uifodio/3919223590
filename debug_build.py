#!/usr/bin/env python3
"""
Debug script to diagnose PyInstaller build issues
"""

import os
import sys
import subprocess
import shutil

def check_python():
    """Check Python installation"""
    print("=== Python Check ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path[:3]}...")
    return True

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n=== Dependencies Check ===")
    required = [
        'PySide6', 'Pillow', 'psutil', 'pyperclip', 
        'send2trash', 'pywin32', 'PyInstaller'
    ]
    
    missing = []
    for module in required:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            missing.append(module)
    
    if missing:
        print(f"\nMissing modules: {missing}")
        return False
    return True

def check_files():
    """Check if required files exist"""
    print("\n=== Files Check ===")
    required_files = [
        'main.py',
        'requirements.txt',
        'src/main_window.py',
        'src/utils/config_manager.py',
        'src/widgets/file_tree.py',
        'src/widgets/file_list.py',
        'src/widgets/editor_widget.py',
        'src/widgets/address_bar.py'
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\nMissing files: {missing}")
        return False
    return True

def test_pyinstaller():
    """Test PyInstaller functionality"""
    print("\n=== PyInstaller Test ===")
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        
        # Test basic PyInstaller functionality
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller', '--version'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"PyInstaller working: {result.stdout.strip()}")
            return True
        else:
            print(f"PyInstaller error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"PyInstaller test failed: {e}")
        return False

def clean_build():
    """Clean previous build artifacts"""
    print("\n=== Cleaning Build ===")
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['NovaExplorer.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✓ Cleaned {dir_name}")
            except Exception as e:
                print(f"✗ Failed to clean {dir_name}: {e}")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"✓ Cleaned {file_name}")
            except Exception as e:
                print(f"✗ Failed to clean {file_name}: {e}")

def test_build():
    """Test a minimal build"""
    print("\n=== Testing Build ===")
    
    # Create a simple test script
    test_script = """
import sys
print("Hello from test script!")
print(f"Python version: {sys.version}")
"""
    
    with open('test_build.py', 'w') as f:
        f.write(test_script)
    
    try:
        # Try to build the test script
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--name', 'TestBuild',
            'test_build.py'
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ Test build successful")
            if os.path.exists('dist/TestBuild.exe'):
                print("✓ Test EXE created")
                return True
            else:
                print("✗ Test EXE not found")
                return False
        else:
            print(f"✗ Test build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Test build exception: {e}")
        return False
    finally:
        # Clean up test files
        if os.path.exists('test_build.py'):
            os.remove('test_build.py')
        if os.path.exists('dist/TestBuild.exe'):
            os.remove('dist/TestBuild.exe')

def main():
    """Run all diagnostics"""
    print("Nova Explorer - Build Diagnostics")
    print("=" * 50)
    
    checks = [
        ("Python", check_python),
        ("Dependencies", check_dependencies),
        ("Files", check_files),
        ("PyInstaller", test_pyinstaller),
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
            print(f"\n❌ {name} check failed")
        else:
            print(f"\n✅ {name} check passed")
    
    if all_passed:
        print("\n" + "=" * 50)
        print("All basic checks passed!")
        print("Testing build process...")
        
        clean_build()
        if test_build():
            print("\n✅ Build test successful!")
            print("The issue might be with the main application.")
        else:
            print("\n❌ Build test failed!")
            print("PyInstaller has issues on this system.")
    else:
        print("\n❌ Some checks failed!")
        print("Fix the issues above before building.")
    
    print("\nDiagnostics complete.")

if __name__ == "__main__":
    main()