# Aegis Editor - Dear PyGui Professional Code Editor

Aegis Editor is a fast, modern, GPU-accelerated code editor built with Dear PyGui.
It features native drag & drop, tabbed editing, global dark theme, search/replace,
undo/redo, fullscreen, always-on-top, and Windows-friendly packaging.

## Quick Start (Windows)

1) Double-click Run_Aegis.bat
- Creates .venv
- Installs dearpygui + pygments
- Launches editor

Alternative:
```bash
py -3 run_aegis.py
```

## Features
- Professional dark theme
- Tabbed editor (unlimited tabs)
- Drag & Drop files onto the window to open
- Open/Save/Save As
- Modified indicator per tab
- Undo/Redo
- Search/Replace panel
- Status bar (cursor position, encoding, file path)
- Fullscreen toggle, Always-on-top
- Keyboard shortcuts (Ctrl+N/O/S/Shift+S, Ctrl+F/H, F11)

## Build EXE (Windows)
```bash
py -3 build_aegis.py
```
Produces a single-folder dist with a launcher.

## Files
- run_aegis.py         - Main Dear PyGui application
- build_aegis.py       - PyInstaller builder
- Run_Aegis.bat        - Bulletproof Windows launcher with venv
- Run_Aegis.ps1        - PowerShell launcher with venv

## Notes
- Dear PyGui provides robust docking, tab bars, and theming.
- Pygments used for syntax highlighting (language-aware).
- No external GUI dependencies beyond Dear PyGui.