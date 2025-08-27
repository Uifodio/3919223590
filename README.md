# Anora Editor - Professional Code Editor for Unity

A lightweight, professional code editor specifically designed for Unity development. Built with Python and Tkinter, featuring a dark theme, tabbed interface, and drag-and-drop functionality.

## ✨ Features

### Core Features
- **Professional Dark Theme** - Easy on the eyes during long coding sessions
- **Tabbed Interface** - Work with multiple files simultaneously
- **Syntax Highlighting** - Support for Python, C#, JavaScript, HTML, CSS, JSON, and more
- **Line Numbers** - Easy navigation and debugging
- **Search & Replace** - Find and replace text with highlighting
- **Always on Top** - Keep the editor floating above Unity
- **Fullscreen Mode** - Maximize workspace when needed
- **Drag & Drop** - Simply drag files onto the editor to open them

### Unity-Focused Features
- **Compact Design** - Small enough to overlay Unity viewport
- **Fast File Operations** - Quick save, open, and edit capabilities
- **C# Support** - Full syntax highlighting for Unity scripts
- **Quick Actions** - Select all, undo/redo, cut/copy/paste with shortcuts
- **Professional UI** - Clean, modern interface that doesn't distract from Unity

### Keyboard Shortcuts
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `Ctrl+Shift+S` - Save as
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+T` - New tab
- `Ctrl+W` - Close tab
- `Ctrl+A` - Select all
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+X` - Cut
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste

## 🚀 Installation

### Option 1: Run from Source (Recommended for Development)

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd anora-editor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the editor**
   ```bash
   python anora_editor.py
   ```

### Option 2: Build Executable

1. **Install build dependencies**
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**
   ```bash
   python build_exe.py
   ```

3. **Install the application**
   - Run `install_anora.bat` as administrator, OR
   - Manually copy `dist/AnoraEditor.exe` to your desired location

## 📁 Project Structure

```
anora-editor/
├── anora_editor.py      # Main application
├── build_exe.py         # Build script for executable
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── dist/               # Built executable (after building)
│   └── AnoraEditor.exe
└── install_anora.bat   # Installer script (after building)
```

## 🎯 Usage

### Getting Started
1. Launch Anora Editor
2. The editor opens with a new untitled tab
3. Start coding or open existing files

### Working with Files
- **Open Files**: Use `Ctrl+O` or drag files onto the editor
- **Save Files**: Use `Ctrl+S` to save, `Ctrl+Shift+S` to save as
- **Multiple Tabs**: Use `Ctrl+T` for new tabs, `Ctrl+W` to close tabs
- **Drag & Drop**: Simply drag any text file onto the editor window

### Unity Integration
1. **Always on Top**: Click the "📌 Pin" button to keep the editor floating
2. **Compact Mode**: Resize the window to overlay Unity viewport
3. **Quick Editing**: Use the small floating window for rapid code changes
4. **Fullscreen**: Click "⛶ Full" for distraction-free coding

### Search and Replace
1. Press `Ctrl+F` to open search panel
2. Enter search term and press "Find"
3. Use "Replace" to replace current match
4. Use "Replace All" to replace all occurrences
5. Press `Ctrl+H` for replace mode

## 🎨 Customization

### Theme Colors
The editor uses a professional dark theme with the following colors:
- Background: `#1e1e1e`
- Text: `#d4d4d4`
- Selection: `#264f78`
- Tabs: `#2d2d30`
- Buttons: `#3e3e42`

### Syntax Highlighting
Supported file types with syntax highlighting:
- `.py` - Python
- `.cs` - C# (Unity scripts)
- `.js` - JavaScript
- `.html` - HTML
- `.css` - CSS
- `.json` - JSON
- `.xml` - XML
- `.cpp`, `.c`, `.h` - C/C++

## 🔧 Development

### Prerequisites
- Python 3.7+
- Tkinter (usually included with Python)
- Pygments (for syntax highlighting)

### Running in Development Mode
```bash
python anora_editor.py
```

### Building for Distribution
```bash
python build_exe.py
```

## 🐛 Troubleshooting

### Common Issues

**"Tkinter not found"**
- Tkinter is usually included with Python
- On Linux: `sudo apt-get install python3-tk`
- On macOS: Install Python from python.org

**"Pygments not found"**
```bash
pip install pygments
```

**"PyInstaller not found"**
```bash
pip install pyinstaller
```

**Drag & Drop not working**
- Ensure you're running the latest version
- Try running as administrator on Windows
- Check if your system supports drag & drop

### Performance Tips
- Close unused tabs to improve performance
- Use "Always on Top" sparingly on slower systems
- Keep the editor window reasonably sized

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Guidelines
1. Follow PEP 8 style guidelines
2. Add comments for complex logic
3. Test on multiple platforms
4. Update documentation for new features

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python and Tkinter
- Syntax highlighting powered by Pygments
- Icons and emojis for better UX
- Inspired by modern code editors like VS Code

---

**Made with ❤️ for Unity developers**

*Anora Editor - Where speed meets simplicity*