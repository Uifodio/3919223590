# Nova Explorer

Nova Explorer is a Windows 11 native-style file manager + code editor built with Python and PySide6. It combines a fast Explorer with a built-in editor, ZIP browsing, drag-and-drop, backups, and multi-window project mode. Portable and MSI installer builds are supported.

## Features
- Explorer tree, tabbed views, dark theme
- Built-in editor with syntax highlighting, find/replace, autosave, undo/redo
- Image viewer and quick preview
- Fast search: names and in-file text
- Drag-and-drop between windows and to external apps (Unity, VS, browsers)
- File ops with progress: copy/move/rename/delete/duplicate; safe delete to Recycle Bin
- ZIP browsing/editing with .bak backups
- Recent locations, settings JSON, cross-window clipboard
- Multi-window project mode

## Quick Start (Windows)
1. Download the latest release from GitHub Releases.
2. Run `NovaExplorer.exe` (portable) or install with `NovaExplorer.msi`.

## Build From Source

1. Install Python 3.11+ and Git.
2. Clone the repo:
   ```bash
   git clone https://github.com/your-org/nova-explorer.git
   cd nova-explorer
   ```
3. Setup venv and dependencies:
   ```bash
   scripts\windows\setup_venv.bat
   ```
4. Run (portable dev):
   ```bash
   scripts\windows\run_dev.bat
   ```
5. Build EXE and MSI:
   ```bash
   scripts\windows\build_exe.bat
   scripts\windows\build_msi.bat
   ```

If Python is missing, the build script bootstraps a private embeddable Python automatically.

## Unity Integration
You can set Nova Explorer as the external code editor and double-click to open files. In Unity: Edit -> Preferences -> External Tools -> External Script Editor: browse to `NovaExplorer.exe`.

## License
MIT

# Perfect File Manager for Windows 11

A powerful file manager that combines the functionality of Windows File Explorer and Visual Studio Code, designed specifically for developers and Unity users.

## 🚀 Features

### Core File Management
- **File Explorer Tree View** - Standard left-panel navigation with full system access
- **Multi-window Support** - Open multiple independent windows (like running multiple explorers)
- **Seamless Drag & Drop** - Drag files directly to Unity, Visual Studio, browsers, and other applications
- **Quick File Replace Workflow** - Monitor download folders and auto-replace files with backup
- **Cross-window Clipboard** - Cut/copy in one window, paste in another

### Built-in Code Editor
- **Native Editor** - Open text/code files inside the manager
- **Syntax Highlighting** - Support for common programming languages
- **Auto-save & Undo** - Automatic saving and full undo/redo functionality
- **Quick Search** - Find text within files instantly
- **Line Numbers** - Professional code editing experience

### Advanced Features
- **ZIP Archive Support** - Open ZIP files as folders, edit contents seamlessly
- **Auto-backup System** - Creates .bak files automatically when editing
- **Multi-file Selection** - Shift/Ctrl select and apply actions to multiple files
- **Progress Bars** - Visual feedback for large operations
- **Dark Theme** - Modern, clean UI (default)
- **Safe Operations** - Files deleted go to system trash, not permanent removal

### Unity Integration
- **Unity Support** - Can be set as Unity's default code editor
- **Asset Management** - Perfect for Unity project file management
- **Quick Import** - Drag assets directly into Unity projects

## 🛠️ Installation

### Option 1: Automatic Installation (Recommended)
1. Download the project from GitHub
2. Run `install_and_run.bat`
3. The script will automatically install Python and all dependencies
4. The application will compile and run automatically

### Option 2: Manual Installation
1. Ensure Python 3.8+ is installed
2. Clone this repository
3. Run: `pip install -r requirements.txt`
4. Run: `python main.py`

### Building Executable
To create a standalone .exe file:
```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

## 🎯 Usage

### Basic Navigation
- **Double-click folders** to navigate inside
- **Double-click files** to open in built-in editor
- **Right-click** for context menu with all operations
- **Ctrl+A** to select all files
- **Shift/Ctrl+Click** for multi-selection

### Code Editing
- **Double-click any text file** to open in built-in editor
- **Ctrl+S** to save
- **Ctrl+F** to find text
- **Ctrl+Z** to undo
- **Ctrl+Y** to redo

### Multi-window Mode
- **File → New Window** to open additional windows
- **Drag files between windows** for quick operations
- **Each window is fully independent**

### Unity Integration
1. Open Unity
2. Go to Edit → Preferences → External Tools
3. Set "External Script Editor" to this file manager
4. Now double-clicking scripts in Unity opens them in the file manager

## 🔧 Configuration

The application uses `config.json` for all settings:
- Theme preferences
- Editor font size and family
- Default file associations
- Window positions and sizes
- Recent files and folders

## 📁 Supported File Types

### Text/Code Files
- All programming languages (Python, C#, JavaScript, etc.)
- Markdown, JSON, XML, HTML, CSS
- Configuration files
- Log files

### Media Files
- Images (PNG, JPG, GIF, etc.)
- Videos (MP4, AVI, etc.)
- Audio files

### Archives
- ZIP files (opened as folders)
- RAR files
- 7z files

## 🎨 Themes

- **Dark Theme** (default) - Modern, easy on the eyes
- **Light Theme** - Classic Windows look
- **Custom Themes** - Create your own via config.json

## 🔒 Security Features

- **Safe Delete** - Files go to Recycle Bin
- **Auto-backup** - .bak files created automatically
- **Permission Handling** - Proper Windows permissions
- **Virus Scan Integration** - Optional antivirus integration

## 🚀 Performance

- **Fast Startup** - Optimized for quick loading
- **Efficient Memory Usage** - Minimal resource consumption
- **Large File Support** - Handles files of any size
- **Background Operations** - Non-blocking file operations

## 🐛 Troubleshooting

### Common Issues
1. **Python not found** - Run the install script which will install Python automatically
2. **Permission errors** - Run as administrator for system folders
3. **Missing dependencies** - Run `pip install -r requirements.txt`

### Support
- Check the logs in `logs/` directory
- Report issues on GitHub
- Check the configuration file for settings

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Perfect File Manager** - The ultimate file management solution for Windows 11 developers and Unity users.