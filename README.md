# Aurora File Manager (Windows)

A modern, lightweight file manager for Windows 11 with a built-in editor, ZIP browsing/editing with backups, fast search, multi-window, cross-window clipboard, drag-and-drop to external apps, and dark theme by default.

## Features
- Built-in code editor: syntax highlighting, line numbers, undo/redo, autosave (optional), find/replace, quick in-file search
- File tree explorer with multi-selection
- Fast name search and in-file text search
- Multi-window mode (open multiple windows from the app)
- Drag & Drop: within app, between windows, to desktop/other apps (e.g., Unity, VS)
- Copy, Move, Rename, Delete (safe delete to system Recycle Bin)
- Duplicate and Quick Replace workflow with automatic `.bak` backup
- ZIP handling: open ZIP like a folder, edit files inside, auto `.bak` backup of zip on save
- Progress bars for long operations
- Recent locations list and quick open
- JSON settings (theme, fonts, editor options)

## Quick Start (Windows 11)
1. Download this repository as a ZIP and extract it anywhere.
2. Double-click `run.bat` to launch the app (first run will auto-setup a local Python 3.12 env and install dependencies).
3. Optional: Use `build_windows.bat` to produce a standalone EXE in `dist/` with PyInstaller.

## Scripts
- `run.bat`: Sets up a local venv (Python 3.12) if missing, installs requirements if needed, and runs the app.
- `build_windows.bat`: Ensures Python 3.12 is available (installs via `winget` if missing), builds a Windows EXE using PyInstaller.

## Notes
- Drag-and-drop to external apps uses standard Windows shell file URLs; it should work in Unity, Visual Studio, and browsers that accept dropped files.
- Safe delete uses the system Recycle Bin via `send2trash`.
- When editing inside a ZIP, the app automatically creates a `.bak` of the original zip before writing changes.
- Settings are stored in `%APPDATA%/AuroraFileManager/settings.json`.

## Troubleshooting
- The scripts use Python 3.12 to match PySide6 compatibility. If you have a different default `py` launcher, the script forces `-3.12`.
- If `winget` is missing, install it from the Microsoft Store or install Python 3.12 from `https://www.python.org/downloads/windows/` and re-run the scripts.
- If antivirus blocks the EXE, add the `dist/` folder to your allow-list or run via `run.bat`.

## License
MIT