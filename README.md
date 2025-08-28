# Anora Code Editor

A professional, standalone code editor designed specifically for Unity development with smooth animations, dark theme, and advanced features.

![Anora Editor](https://img.shields.io/badge/Anora-Editor-blue?style=for-the-badge&logo=visual-studio-code)
![Python](https://img.shields.io/badge/Python-3.7+-green?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)

## ✨ Features

### 🎨 Visual Design
- **Dark Theme**: VS Code-style colors with professional appearance
- **Smooth Animations**: 60 FPS animations for all UI interactions
- **Modern UI**: Rounded buttons, hover effects, and responsive design
- **Professional Layout**: Clean, intuitive interface optimized for Unity development

### 📝 Editor Features
- **Multi-tab Support**: Work with multiple files simultaneously
- **Syntax Highlighting**: Real-time highlighting for Python, C#, JavaScript, HTML, CSS, JSON, C/C++
- **Line Numbers**: 4-digit format with smooth scrolling
- **Search & Replace**: Advanced find/replace with highlighting
- **Auto-save**: Automatic session saving every 500ms
- **Recent Files**: Quick access to last 10 opened files

### ⌨️ Keyboard Shortcuts
- `Ctrl+N`: New file
- `Ctrl+O`: Open file
- `Ctrl+S`: Save
- `Ctrl+Shift+S`: Save As
- `Ctrl+F`: Find
- `Ctrl+H`: Replace
- `Ctrl+T`: New tab
- `Ctrl+W`: Close tab
- `Ctrl+Shift+T`: Reopen closed tab
- `Ctrl+A`: Select all
- `Ctrl+Z/Y`: Undo/Redo
- `Ctrl+X/C/V`: Cut/Copy/Paste
- `Ctrl+G`: Go to line
- `F3/Shift+F3`: Next/Previous search result
- `Ctrl+Q`: Exit

### 🎯 Unity Integration
- **Always on Top**: Pin editor above Unity for overlay editing
- **C# Support**: Full syntax highlighting for Unity scripts
- **Fast Tab Switching**: Quick navigation between Unity scripts
- **Compact Design**: Optimized to fit alongside Unity interface
- **Professional Appearance**: Matches modern IDE standards

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Windows 10/11 (primary target)

### Installation

1. **Download the project**
   ```bash
   git clone <repository-url>
   cd anora-editor
   ```

2. **Run the launcher** (recommended)
   ```bash
   python launch_anora.py
   ```
   This will automatically:
   - Check Python version
   - Install dependencies
   - Create sample files
   - Launch the editor

3. **Manual installation** (alternative)
   ```bash
   pip install -r requirements.txt
   python anora_editor_advanced.py
   ```

### First Launch
- The editor will open with a new untitled tab
- Sample files are created for testing
- Try opening `sample.py`, `sample.cs`, or `sample.html` to see syntax highlighting
- Use `Ctrl+O` to open files or drag files onto the editor

## 🎨 Customization

### Color Themes
The editor uses a professional dark theme with these colors:
- Background: `#1e1e1e` (dark gray)
- Text: `#d4d4d4` (light gray)
- Selection: `#264f78` (blue)
- Current line: `#33415e` (darker blue)
- Keywords: `#569cd6` (blue)
- Strings: `#ce9178` (orange)
- Comments: `#6a9955` (green)

### Window Layout
- **Default Size**: 1000x700 pixels
- **Minimum Size**: 600x400 pixels
- **Resizable**: Fully responsive design
- **Always on Top**: Toggle with pin button
- **Fullscreen**: Toggle with full button

## 📁 File Support

### Supported File Types
- **Python**: `.py` files with full syntax highlighting
- **C#**: `.cs` files optimized for Unity development
- **JavaScript**: `.js` files with ES6+ support
- **HTML**: `.html` files with embedded CSS/JS highlighting
- **CSS**: `.css` files with property highlighting
- **JSON**: `.json` files with structure highlighting
- **C/C++**: `.c`, `.cpp`, `.h` files
- **Text**: `.txt` files

### File Associations
Run the PowerShell script as Administrator to set Anora as default editor:
```powershell
.\install_windows_default_editor.ps1
```

## 🔧 Advanced Features

### Session Persistence
- Automatically saves open tabs and recent files
- Restores session on startup
- Session file: `~/.anora_editor_session.json`

### Search & Replace
- **Find Panel**: `Ctrl+F` to show search panel
- **Replace Panel**: `Ctrl+H` for find and replace
- **Highlighting**: All matches highlighted in yellow
- **Current Match**: Current match highlighted in green
- **Navigation**: F3/Shift+F3 to navigate matches

### Tab Management
- **Multiple Tabs**: Work with many files simultaneously
- **Modified Indicator**: Asterisk (*) shows unsaved changes
- **Close Others**: Keep current tab, close all others
- **Reopen Closed**: `Ctrl+Shift+T` to restore last closed tab

### Performance Optimizations
- **Syntax Highlighting**: Only processes visible lines
- **Debounced Updates**: 200ms delay on typing to prevent lag
- **Efficient Rendering**: Optimized for smooth 60 FPS animations
- **Background Processing**: Non-blocking operations

## 🛠️ Development

### Project Structure
```
anora-editor/
├── anora_editor_advanced.py    # Main editor application
├── launch_anora.py             # Auto-installer and launcher
├── requirements.txt            # Python dependencies
├── install_windows_default_editor.ps1  # File association installer
├── README.md                   # This file
├── sample.py                   # Sample Python file
├── sample.cs                   # Sample C# file
├── sample.js                   # Sample JavaScript file
└── sample.html                 # Sample HTML file
```

### Dependencies
- **tkinter**: Built-in GUI framework
- **pygments**: Syntax highlighting library
- **pillow**: Image processing (for advanced UI features)

### Building from Source
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the editor: `python anora_editor_advanced.py`

## 🎯 Unity Development Workflow

### Recommended Setup
1. **Install Anora Editor** using the launcher
2. **Set as Default Editor** for `.cs` files
3. **Pin Editor** (always on top) for overlay editing
4. **Open Unity Scripts** by double-clicking in Unity
5. **Use Multiple Tabs** for quick script switching

### Unity Integration Tips
- Use the pin button to keep Anora above Unity
- Open multiple Unity scripts in tabs for quick reference
- Use `Ctrl+F` to search within Unity scripts
- Save frequently with `Ctrl+S` (auto-save also enabled)
- Use `Ctrl+G` to jump to specific lines in large scripts

## 🐛 Troubleshooting

### Common Issues

**Editor won't start**
- Ensure Python 3.7+ is installed
- Run `python launch_anora.py` for automatic setup
- Check that all dependencies are installed

**Syntax highlighting not working**
- Verify Pygments is installed: `pip install pygments`
- Check file extension is supported
- Restart the editor

**File associations not working**
- Run PowerShell as Administrator
- Execute `.\install_windows_default_editor.ps1`
- Check Windows file association settings

**Performance issues**
- Close unnecessary tabs
- Reduce window size if needed
- Check system resources

### Getting Help
- Check the sample files for syntax highlighting examples
- Use the launcher script for automatic setup
- Ensure all dependencies are properly installed

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add comments for complex functionality
- Test on Windows 10/11
- Ensure smooth animations and responsive UI
- Maintain Unity development focus

---

**Anora Code Editor** - Professional Unity Development Made Simple

*Built with ❤️ for Unity developers*