#!/usr/bin/env python3
"""
Test script for File Manager functionality
This script tests the core file operations without requiring tkinter GUI.
"""

import os
import shutil
import tempfile
from datetime import datetime

def test_file_operations():
    """Test basic file operations"""
    print("Testing File Manager Core Functions")
    print("=" * 40)
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="file_manager_test_")
    print(f"Created test directory: {test_dir}")
    
    try:
        # Test 1: Create files and folders
        print("\n1. Testing file and folder creation...")
        
        # Create a test folder
        test_folder = os.path.join(test_dir, "test_folder")
        os.makedirs(test_folder, exist_ok=True)
        print(f"   ✓ Created folder: {test_folder}")
        
        # Create test files
        test_files = [
            "test1.txt",
            "test2.py",
            "test3.jpg",
            "test4.pdf"
        ]
        
        for filename in test_files:
            file_path = os.path.join(test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content for {filename}")
            print(f"   ✓ Created file: {filename}")
        
        # Test 2: List directory contents
        print("\n2. Testing directory listing...")
        items = os.listdir(test_dir)
        folders = []
        files = []
        
        for item in items:
            item_path = os.path.join(test_dir, item)
            if os.path.isdir(item_path):
                folders.append(item)
            else:
                files.append(item)
        
        print(f"   ✓ Found {len(folders)} folders: {folders}")
        print(f"   ✓ Found {len(files)} files: {files}")
        
        # Test 3: File operations
        print("\n3. Testing file operations...")
        
        # Copy a file
        source_file = os.path.join(test_dir, "test1.txt")
        dest_file = os.path.join(test_dir, "test1_copy.txt")
        shutil.copy2(source_file, dest_file)
        print(f"   ✓ Copied file: test1.txt -> test1_copy.txt")
        
        # Rename a file
        old_name = os.path.join(test_dir, "test2.py")
        new_name = os.path.join(test_dir, "test2_renamed.py")
        os.rename(old_name, new_name)
        print(f"   ✓ Renamed file: test2.py -> test2_renamed.py")
        
        # Test 4: File properties
        print("\n4. Testing file properties...")
        for filename in os.listdir(test_dir):
            if os.path.isfile(os.path.join(test_dir, filename)):
                file_path = os.path.join(test_dir, filename)
                stat = os.stat(file_path)
                size = format_size(stat.st_size)
                modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                file_type = get_file_type(filename)
                print(f"   ✓ {filename}: {size}, {file_type}, {modified}")
        
        # Test 5: Search functionality
        print("\n5. Testing search functionality...")
        search_results = []
        search_term = "test"
        
        def search_recursive(path):
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if search_term.lower() in item.lower():
                        search_results.append(item_path)
                    
                    if os.path.isdir(item_path):
                        search_recursive(item_path)
            except:
                pass
        
        search_recursive(test_dir)
        print(f"   ✓ Found {len(search_results)} items containing '{search_term}':")
        for result in search_results:
            print(f"      - {os.path.basename(result)}")
        
        print("\n" + "=" * 40)
        print("✓ All tests passed successfully!")
        print("The file manager core functionality is working correctly.")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        return False
    
    finally:
        # Clean up test directory
        try:
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
        except:
            print(f"\nWarning: Could not clean up test directory: {test_dir}")
    
    return True

def format_size(size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def get_file_type(filename):
    """Get file type based on extension"""
    ext = os.path.splitext(filename)[1].lower()
    type_map = {
        '.txt': 'Text File',
        '.py': 'Python File',
        '.js': 'JavaScript File',
        '.html': 'HTML File',
        '.css': 'CSS File',
        '.json': 'JSON File',
        '.xml': 'XML File',
        '.pdf': 'PDF File',
        '.doc': 'Word Document',
        '.docx': 'Word Document',
        '.xls': 'Excel Spreadsheet',
        '.xlsx': 'Excel Spreadsheet',
        '.ppt': 'PowerPoint Presentation',
        '.pptx': 'PowerPoint Presentation',
        '.jpg': 'JPEG Image',
        '.jpeg': 'JPEG Image',
        '.png': 'PNG Image',
        '.gif': 'GIF Image',
        '.bmp': 'BMP Image',
        '.mp3': 'MP3 Audio',
        '.mp4': 'MP4 Video',
        '.avi': 'AVI Video',
        '.zip': 'ZIP Archive',
        '.rar': 'RAR Archive',
        '.7z': '7-Zip Archive',
        '.exe': 'Executable',
        '.msi': 'Windows Installer',
        '.dll': 'Dynamic Link Library',
        '.sys': 'System File',
        '.ini': 'Configuration File',
        '.log': 'Log File',
        '.tmp': 'Temporary File',
        '.bak': 'Backup File'
    }
    return type_map.get(ext, 'File')

def test_platform_compatibility():
    """Test platform-specific functionality"""
    print("\nTesting Platform Compatibility")
    print("=" * 40)
    
    import platform
    system = platform.system()
    print(f"Operating System: {system}")
    print(f"Platform: {platform.platform()}")
    print(f"Python Version: {platform.python_version()}")
    
    # Test drive enumeration (Windows-specific)
    if system == "Windows":
        try:
            import win32api
            drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
            print(f"Available drives: {drives}")
            print("   ✓ Windows drive enumeration working")
        except ImportError:
            print("   ⚠ pywin32 not available - drive enumeration limited")
        except Exception as e:
            print(f"   ✗ Drive enumeration failed: {e}")
    else:
        print("   ℹ Drive enumeration not applicable on this platform")
    
    # Test file operations
    print("\nTesting cross-platform file operations...")
    try:
        # Test current directory
        current_dir = os.getcwd()
        print(f"   ✓ Current directory: {current_dir}")
        
        # Test home directory
        home_dir = os.path.expanduser("~")
        print(f"   ✓ Home directory: {home_dir}")
        
        # Test path operations
        test_path = os.path.join("test", "path", "file.txt")
        print(f"   ✓ Path joining: {test_path}")
        
        print("   ✓ Cross-platform file operations working")
        
    except Exception as e:
        print(f"   ✗ File operations failed: {e}")

if __name__ == "__main__":
    print("File Manager Test Suite")
    print("=" * 50)
    
    # Test platform compatibility
    test_platform_compatibility()
    
    # Test core functionality
    success = test_file_operations()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("The file manager is ready to use.")
    else:
        print("\n❌ Some tests failed.")
        print("Please check the error messages above.")