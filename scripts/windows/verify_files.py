#!/usr/bin/env python3
"""
Verify that all required files exist before building.
"""

import os
import sys

REQUIRED_FILES = [
    "main.py",
    "requirements_windows.txt",
    "src/main_window.py",
    "src/utils/config_manager.py",
    "src/utils/logger.py",
    "src/widgets/file_tree.py",
    "src/widgets/file_list.py",
    "src/widgets/editor_widget.py",
    "src/widgets/address_bar.py",
]

def main():
    print("=== File Verification ===")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    missing = []
    for file_path in REQUIRED_FILES:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\nERROR: {len(missing)} required files are missing:")
        for file_path in missing:
            print(f"  - {file_path}")
        return 1
    
    print("\nAll required files present.")
    return 0

if __name__ == "__main__":
    sys.exit(main())