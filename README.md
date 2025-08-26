# Windows File Manager Pro (Python + PySide6)

Professional file manager for Windows with a built-in editor. Minimal dependencies, easy build to EXE via PyInstaller.

## Features (initial)
- File system tree on the left (QFileSystemModel)
- Open folder, open file, save file
- Text editor on the right
- Status bar messages
- Settings persisted to `%USERPROFILE%\.wfmp_settings.json`

Roadmap: advanced search, zip handling, theme switching, tabs, drag & drop, bulk ops.

## Requirements
- Windows 10/11
- Python 3.10+

## Quick Start (Build EXE)
1. Right-click `build.bat` → Run as administrator
2. The script will:
   - Create a `.venv`
   - Install `PySide6` and `pyinstaller`
   - Build EXE into `dist-py/Windows File Manager Pro/`
   - Open the output folder

## Dev Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app\main.py
```

## Project Structure
```
app/
  main.py           # PySide6 main window
requirements.txt
build.ps1           # Build to EXE (venv + pyinstaller)
build.bat           # Calls build.ps1 with policy bypass
README.md
```