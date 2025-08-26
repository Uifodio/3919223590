# Nova Explorer

Nova Explorer is a Windows 11 native-style file manager + code editor built with Python and PySide6. It combines a fast Explorer with a built-in editor, ZIP browsing, drag-and-drop, backups, and multi-window project mode. Portable and MSI installer builds are supported.

## Features

- **Explorer Interface**: Tree view, tabbed views, dark theme, address bar with path completion
- **Built-in Editor**: Syntax highlighting, find/replace, autosave, undo/redo for 20+ languages
- **Image Viewer**: Quick preview for images and generic file types
- **Fast Search**: Name search and in-file text search with real-time results
- **Drag & Drop**: Between windows and to external apps (Unity, VS, browsers) with progress
- **File Operations**: Copy/move/rename/delete/duplicate with progress bar and safe delete to Recycle Bin
- **ZIP Support**: Browse/edit ZIP archives as folders with .bak backups on save
- **Recent Locations**: Quick access to recent files/folders with settings JSON config
- **Multi-window**: Cross-window clipboard and independent project windows
- **Unity Integration**: Set as external script editor for seamless workflow

## Quick Start (Windows)

### Automatic Installation
1. Download the latest release from GitHub Releases
2. Run `install_and_run.bat` - it will:
   - Auto-install Python 3.11 if missing
   - Install all dependencies
   - Run installation tests
   - Start the application
3. Check `debug_install.log` if any issues occur

### Manual Installation
1. Install Python 3.11+ from [python.org](https://python.org)
2. Clone the repo:
   ```bash
   git clone https://github.com/your-org/nova-explorer.git
   cd nova-explorer
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements_windows.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Build From Source

### Windows Build
1. Install Python 3.11+ and Git
2. Clone and setup:
   ```bash
   git clone https://github.com/your-org/nova-explorer.git
   cd nova-explorer
   scripts\windows\setup_venv.bat
   ```
3. Run (dev mode):
   ```bash
   scripts\windows\run_dev.bat
   ```
4. Build EXE and MSI:
   ```bash
   scripts\windows\build_exe.bat
   scripts\windows\build_msi.bat
   ```

### Linux/Mac Build
1. Install Python 3.11+ and dependencies:
   ```bash
   sudo apt install python3.13-venv python3-pip libxcb-cursor0 libegl1 libopengl0
   ```
2. Setup and run:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

## Unity Integration

Set Nova Explorer as the external code editor in Unity:

1. In Unity: **Edit → Preferences → External Tools**
2. Set **External Script Editor** to `NovaExplorer.exe`
3. Double-click any script file to open in Nova Explorer
4. Changes are automatically detected by Unity

## Troubleshooting

### Installation Issues

**Python not found:**
- Run `install_and_run.bat` - it auto-installs Python 3.11
- Or manually install from [python.org](https://python.org)

**PySide6 import errors:**
- Install OpenGL libraries: `sudo apt install libxcb-cursor0 libegl1 libopengl0` (Linux)
- Use Python 3.11 instead of 3.13 for better compatibility

**Missing dependencies:**
- Check `debug_install.log` for specific errors
- Run `python test_install.py` to diagnose issues
- Try individual package installation: `pip install PySide6>=6.6.1`

### Runtime Issues

**Application crashes on startup:**
- Check `logs/app_debug.log` for detailed error information
- Ensure all dependencies are installed correctly
- Try running in safe mode: `python main.py --safe`

**GUI not displaying:**
- Linux: Install X11 libraries and set display
- Windows: Check graphics drivers and DirectX
- Use offscreen mode: `QT_QPA_PLATFORM=offscreen python main.py`

**File operations failing:**
- Check file permissions
- Ensure antivirus isn't blocking operations
- Verify disk space availability

### Performance Issues

**Slow startup:**
- Disable antivirus real-time scanning for the app directory
- Use SSD storage for better performance
- Close other resource-intensive applications

**Memory usage:**
- Large directories may use significant memory
- Use the tree view to navigate instead of loading all files
- Restart the application periodically for long sessions

## Development

### Project Structure
```
nova-explorer/
├── main.py                 # Application entry point
├── install_and_run.bat     # Windows auto-installer
├── test_install.py         # Installation test script
├── requirements.txt        # Cross-platform dependencies
├── requirements_windows.txt # Windows-specific dependencies
├── src/
│   ├── main_window.py      # Main application window
│   ├── utils/              # Utility modules
│   │   ├── config_manager.py
│   │   ├── clipboard_manager.py
│   │   ├── file_operations.py
│   │   ├── zip_handler.py
│   │   └── logger.py
│   └── widgets/            # UI components
│       ├── file_tree.py    # Directory tree view
│       ├── file_list.py    # File list with DnD
│       ├── editor_widget.py # Code editor
│       └── address_bar.py  # Path navigation
└── scripts/windows/        # Build scripts
    ├── setup_venv.bat
    ├── run_dev.bat
    ├── build_exe.bat
    └── build_msi.bat
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_install.py`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join GitHub Discussions for help
- **Documentation**: Check the wiki for detailed guides
- **Debug Logs**: Check `logs/app_debug.log` and `debug_install.log` for troubleshooting