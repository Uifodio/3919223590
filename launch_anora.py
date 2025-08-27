#!/usr/bin/env python3
"""
Anora Editor Launcher
Professional Code Editor with Native Windows Integration
"""

import os
import sys
import subprocess
import platform
import shutil
import time
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anora_launcher.log')


def log(message: str) -> None:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {message}"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass
    # Avoid non-ASCII in console to prevent charmap errors on some Windows setups
    safe_line = line.encode('ascii', errors='replace').decode('ascii')
    print(safe_line, flush=True)


def pause_if_headless():
    try:
        if not sys.stdout.isatty():
            input("\nPress Enter to close this window...")
    except Exception:
        pass


def run_cmd(args, check=True) -> int:
    log(f"Running: {' '.join(args)}")
    try:
        return subprocess.check_call(args)
    except subprocess.CalledProcessError as e:
        log(f"Command failed with exit code {e.returncode}")
        if check:
            raise
        return e.returncode


def py_version_tag() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def try_imports(modules):
    missing = []
    for mod in modules:
        try:
            __import__(mod)
            log(f"OK {mod} available")
        except ImportError:
            log(f"MISSING {mod}")
            missing.append(mod)
    return missing


def ensure_pip() -> None:
    try:
        import pip  # noqa: F401
        return
    except Exception:
        log("pip not found; bootstrapping ensurepip...")
        try:
            import ensurepip
            ensurepip.bootstrap()
            log("ensurepip bootstrap completed")
        except Exception as e:
            log(f"ensurepip failed: {e}")


def pip_install(packages, user_fallback=True) -> bool:
    ensure_pip()
    pyexe = sys.executable

    cmds = [
        [pyexe, '-m', 'pip', 'install', '-U'] + packages,
    ]

    if platform.system() == 'Windows' and user_fallback:
        cmds.append([pyexe, '-m', 'pip', 'install', '--user', '-U'] + packages)
        cmds.append([pyexe, '-m', 'pip', 'install', '-U', '--only-binary', ':all:'] + packages)

    for cmd in cmds:
        try:
            run_cmd(cmd)
            return True
        except Exception as e:
            log(f"Install attempt failed: {e}")
            continue
    return False


def install_wxpython() -> bool:
    log("Installing wxPython...")
    index_url = 'https://extras.wxpython.org/wxPython4/extras/index.html'
    ok = pip_install(["wxPython>=4.2.1", '-f', index_url], user_fallback=True)
    if not ok:
        ok = pip_install(["wxPython>=4.2.1"], user_fallback=True)
    return ok


def install_optional_windows_features():
    if platform.system() == 'Windows':
        log("Installing Windows optional packages (pywin32, pygments)...")
        pip_install(["pywin32", "pygments"], user_fallback=True)
    else:
        log("Skipping Windows optional packages on non-Windows platform")


def check_and_install_dependencies() -> bool:
    required = ['wx', 'wx.stc', 'wx.aui', 'wx.adv', 'wx.html', 'wx.grid', 'wx.richtext']
    missing = try_imports(required)
    if not missing:
        return True

    log(f"Missing required modules: {', '.join(missing)}")
    if 'wx' in missing or any(m.startswith('wx') for m in missing):
        if not install_wxpython():
            log("Failed to install wxPython. See log for details.")
            return False
        missing = try_imports(required)
        if not missing:
            return True
        else:
            log(f"Still missing after install: {', '.join(missing)}")
            return False
    return True


def show_welcome():
    sep = "=" * 80
    print(sep)
    print(f"Welcome to Anora Editor Launcher (Python {py_version_tag()})")
    print(sep)
    print("This launcher verifies/installs dependencies automatically, then runs the editor.")
    print()


def launch_anora() -> int:
    if not os.path.exists('anora_editor.py'):
        log("anora_editor.py not found in current directory")
        return 1

    args = [sys.executable, 'anora_editor.py'] + sys.argv[1:]
    log(f"Launching editor: {args}")
    return subprocess.call(args)


def main() -> int:
    show_welcome()
    log(f"Launcher started with Python {sys.version}")
    log(f"Platform: {platform.platform()} | Arch: {platform.machine()}")

    ok = check_and_install_dependencies()
    if not ok:
        log("Attempting optional Windows packages to help resolve environment...")
        install_optional_windows_features()
        ok = check_and_install_dependencies()
        if not ok:
            log("Could not satisfy required dependencies. See anora_launcher.log for details.")
            pause_if_headless()
            return 2

    rc = launch_anora()
    if rc != 0:
        log(f"Editor exited with code {rc}")
    else:
        log("Editor closed normally")

    pause_if_headless()
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"Launcher crashed: {e}")
        pause_if_headless()
        raise