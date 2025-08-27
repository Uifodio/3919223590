#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

APP = 'AegisEditor'
MAIN = 'run_aegis.py'
DIST = 'dist'
BUILD = 'build'

EXTRA_OPTS = [
    '--noconfirm',
    '--onedir',
    '--name', APP,
    '--windowed',
]

def run(cmd):
    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd)


def main():
    if not Path(MAIN).exists():
        print(f'Missing {MAIN}')
        sys.exit(1)
    # Ensure deps
    subprocess.call([sys.executable, '-m', 'pip', 'install', '-U', 'dearpygui', 'pygments'])

    # Clean old
    for p in (Path(DIST), Path(BUILD), Path(f'{APP}.spec')):
        if p.exists():
            if p.is_file():
                p.unlink()
            else:
                import shutil; shutil.rmtree(p, ignore_errors=True)

    cmd = [sys.executable, '-m', 'PyInstaller', *EXTRA_OPTS, MAIN]
    run(cmd)
    print('Built in', DIST)

if __name__ == '__main__':
    main()