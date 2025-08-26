# Nova Explorer

A powerful Windows file manager with built-in code editor, designed for developers and Unity users. Combines File Explorer functionality with Visual Studio Code features in one application.

## Features

- **File Explorer**: Tree view, file list, address bar, dark theme
- **Built-in Editor**: Syntax highlighting, find/replace, autosave, undo/redo for 20+ languages
- **Drag & Drop**: Between windows and to external apps (Unity, VS, browsers)
- **File Operations**: Copy/move/rename/delete with progress and safe delete to Recycle Bin
- **ZIP Support**: Browse/edit ZIP archives as folders with auto-backup
- **Multi-window**: Independent windows with cross-window clipboard
- **Unity Integration**: Set as external script editor for seamless workflow

## Quick Start

### Option 1: Run from Source (Recommended)
1. Download the project
2. Double-click `run.bat`
3. Everything installs automatically and starts

### Option 2: Build EXE
1. Run `run.bat` first (installs Python 3.11)
2. Run `build.bat` to create standalone EXE
3. Your EXE will be in `dist/NovaExplorer.exe`

## Unity Integration

1. Build the EXE using `build.bat`
2. In Unity: **Edit → Preferences → External Tools**
3. Set **External Script Editor** to `NovaExplorer.exe`
4. Double-click any script to open in Nova Explorer

## Requirements

- Windows 10/11
- Internet connection (for first-time setup)
- 100MB free disk space

## Troubleshooting

**If run.bat fails:**
- Check internet connection
- Run as administrator if needed
- Check Windows Defender isn't blocking

**If build.bat fails:**
- Make sure you ran `run.bat` first
- Ensure Python 3.11 is installed
- Check antivirus isn't blocking PyInstaller

## Project Structure

```
nova-explorer/
├── run.bat              # Auto-install and run
├── build.bat            # Build EXE
├── requirements.txt     # Dependencies
├── main.py             # Application entry
├── src/                # Source code
│   ├── main_window.py  # Main UI
│   ├── utils/          # Utilities
│   └── widgets/        # UI components
└── dist/               # Built EXE (after build)
```

## License

MIT License