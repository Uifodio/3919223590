# Unity File Manager Pro

A powerful, modern file manager designed specifically for Unity developers and Windows 11 users. This application combines the functionality of Windows File Explorer with advanced code editing capabilities, making Unity development seamless and efficient.

## 🚀 Features

### Core File Management
- **File Explorer Tree View** - Standard left-panel navigation with full system access
- **Multi-window Support** - Open multiple independent windows
- **Drag & Drop** - Seamless file operations between windows and external applications
- **Search** - Fast file/folder name search + inside-file text search
- **Multi-file Selection** - Shift/Ctrl select and apply actions to multiple files

### Built-in Code Editor
- **Native Editor** - Lightweight, full edit+save functionality
- **Syntax Highlighting** - Support for common programming languages
- **Auto-save/Undo** - Automatic backup and undo functionality
- **Quick Search** - Find text within files instantly
- **Line Numbers** - Professional code editing experience

### Unity Integration
- **Unity Support** - Configure as default code editor in Unity
- **Asset Management** - Drag files directly to Unity for instant import
- **Project Workflow** - Streamlined Unity project management

### Advanced Features
- **ZIP Handling** - Open and edit ZIP archives as folders
- **Auto-backup** - Automatic .bak file creation on edits
- **Progress Bars** - Visual feedback for large operations
- **Dark Theme** - Modern, eye-friendly interface
- **Cross-window Clipboard** - Cut/copy between windows
- **Safe Operations** - Trash instead of permanent deletion

## 🛠️ Installation

### Prerequisites
- Windows 11 (or Windows 10)
- Python 3.8 or higher
- Git

### Quick Setup

#### Option 1: Automatic Setup (Recommended)
1. Download and extract the project
2. Double-click `setup.bat` (Windows) or run `python quick_start.py`
3. The script will automatically install dependencies and start the application

#### Option 2: Manual Setup
1. Clone this repository:
```bash
git clone https://github.com/yourusername/unity-file-manager-pro.git
cd unity-file-manager-pro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

#### Option 3: Build Executable
1. Run the build script:
```bash
python build.py
```

2. The executable will be created in the `dist/` folder
3. Run `UnityFileManagerPro.exe` directly

### Unity Integration Setup
1. Open Unity
2. Go to Edit > Preferences > External Tools
3. Set "External Script Editor" to the path of your UnityFileManager.exe
4. Restart Unity

## 📁 Project Structure

```
unity-file-manager-pro/
├── main.py                 # Main application entry point
├── src/
│   ├── __init__.py
│   ├── main_window.py      # Main window implementation
│   ├── file_explorer.py    # File explorer tree and list views
│   ├── code_editor.py      # Built-in code editor
│   ├── file_operations.py  # File operations (copy, move, delete)
│   ├── zip_handler.py      # ZIP archive handling
│   ├── search.py           # Search functionality
│   ├── settings.py         # Settings and configuration
│   ├── unity_integration.py # Unity-specific features
│   └── utils.py            # Utility functions
├── resources/
│   ├── icons/              # Application icons
│   ├── themes/             # UI themes
│   └── config/             # Configuration files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎯 Usage

### Basic File Management
- **Navigate**: Use the tree view on the left to browse folders
- **Open Files**: Double-click files to open in the built-in editor
- **Multi-select**: Use Ctrl+Click or Shift+Click for multiple files
- **Drag & Drop**: Drag files between windows or to external applications

### Code Editing
- **Open Code Files**: Double-click any text/code file
- **Syntax Highlighting**: Automatic language detection
- **Auto-save**: Changes are saved automatically
- **Search**: Use Ctrl+F to find text within files

### Unity Workflow
- **Import Assets**: Drag files directly to Unity
- **Edit Scripts**: Double-click C# scripts to edit
- **Quick Replace**: Download → Drag → Auto-replace with backup

### Advanced Features
- **ZIP Archives**: Double-click ZIP files to browse contents
- **Multiple Windows**: File > New Window for parallel work
- **Search**: Use the search bar for quick file location
- **Settings**: Customize appearance and behavior

## ⚙️ Configuration

The application uses a JSON configuration file for settings:

```json
{
  "theme": "dark",
  "font_size": 12,
  "auto_save": true,
  "backup_on_edit": true,
  "show_hidden_files": false,
  "default_editor": "built_in"
}
```

## 🔧 Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=resources/icons/app.ico main.py
```

The executable will be created in the `dist/` folder.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🎉 Acknowledgments

- PyQt6 for the GUI framework
- Pygments for syntax highlighting
- Unity Technologies for Unity integration inspiration