#!/usr/bin/env python3
"""
Create a launcher script that handles DLL path issues for the built executable.
"""

import os
import sys
import subprocess

def get_python_dll_path():
    """Get the path to Python DLL"""
    python_dir = os.path.dirname(sys.executable)
    dll_name = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
    dll_path = os.path.join(python_dir, dll_name)
    
    if os.path.exists(dll_path):
        return dll_path
    
    # Try alternative locations
    alt_paths = [
        os.path.join(python_dir, "DLLs", dll_name),
        os.path.join(os.path.dirname(python_dir), "DLLs", dll_name),
    ]
    
    for path in alt_paths:
        if os.path.exists(path):
            return path
    
    return None

def create_launcher():
    """Create a launcher batch file"""
    dll_path = get_python_dll_path()
    
    if not dll_path:
        print("ERROR: Could not find Python DLL")
        return False
    
    launcher_content = f"""@echo off
setlocal

:: Set DLL path for the executable
set PATH={os.path.dirname(dll_path)};%PATH%

:: Run the application
"%~dp0NovaExplorer.exe" %*

endlocal
"""
    
    # Write launcher
    with open("dist/NovaExplorer_Launcher.bat", "w") as f:
        f.write(launcher_content)
    
    print(f"Created launcher: dist/NovaExplorer_Launcher.bat")
    print(f"DLL path: {dll_path}")
    return True

if __name__ == "__main__":
    if not os.path.exists("dist/NovaExplorer.exe"):
        print("ERROR: NovaExplorer.exe not found in dist/")
        print("Please run the build script first.")
        sys.exit(1)
    
    if create_launcher():
        print("Launcher created successfully!")
        print("Use NovaExplorer_Launcher.bat to run the application.")
    else:
        print("Failed to create launcher.")
        sys.exit(1)