#!/usr/bin/env python3
"""
Preflight check for Windows: verifies required modules and attempts to auto-install if missing.
Prints clear diagnostics and exits 0 on success, 1 on failure.
"""

import os
import sys
import subprocess

REQUIRED = [
    ("PySide6", "PySide6"),
    ("PIL", "Pillow"),
    ("psutil", "psutil"),
    ("watchdog", "watchdog"),
    ("pyperclip", "pyperclip"),
    ("send2trash", "send2trash"),
]

# Windows-only
if sys.platform == "win32":
    REQUIRED.append(("win32api", "pywin32"))


def try_import(module_name: str):
    try:
        __import__(module_name)
        return True, None
    except Exception as e:
        return False, str(e)


def pip_install(package: str) -> bool:
    exe = sys.executable or "python"
    try:
        print(f"Installing {package}...")
        result = subprocess.run([exe, "-m", "pip", "install", package], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return True
        else:
            print(f"Install failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"Install timed out for {package}")
        return False
    except Exception as e:
        print(f"Install error for {package}: {e}")
        return False


def main() -> int:
    print("=== Nova Explorer Preflight Check (Windows) ===")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    print()

    missing = []
    for module_name, package in REQUIRED:
        ok, err = try_import(module_name)
        if ok:
            print(f"✓ {package} present")
        else:
            print(f"✗ {package} missing: {err}")
            missing.append((module_name, package))

    if not missing:
        print("\nAll dependencies are present.")
        return 0

    print(f"\nAttempting to auto-install {len(missing)} missing packages...")
    any_installed = False
    for module_name, package in missing:
        ok, _ = try_import(module_name)
        if ok:
            continue
        if pip_install(package):
            print(f"✓ Installed {package}")
            any_installed = True
        else:
            print(f"✗ Failed to install {package}")

    # Re-check
    still_missing = []
    for module_name, package in missing:
        ok, err = try_import(module_name)
        if not ok:
            still_missing.append((module_name, package, err))

    if still_missing:
        print("\nCritical dependencies missing after install attempts:")
        for module_name, package, err in still_missing:
            print(f" - {package} ({module_name}): {err}")
        print("\nPlease run: pip install -r requirements_windows.txt")
        return 1

    print("\nAll missing dependencies installed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())