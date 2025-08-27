# ANORA EDITOR - Professional Code Editor for Unity

A lightweight, fast, professional code editor designed specifically for Unity development. Features dark theme, syntax highlighting, tab management, and always-on-top capability.

![Anora Editor](https://img.shields.io/badge/Anora-Editor-blue?style=for-the-badge&logo=unity)

## ✨ Features

### 🎨 Visual Design
- **Dark theme** with VS Code-style colors
- **Professional appearance** matching modern IDEs
- **Clean, modern interface** with responsive UI
- **VS Code-inspired color scheme**

### 📝 Text Editor Features
- **Line numbers** with 4-digit format
- **Syntax highlighting** for Python, C#, JavaScript, HTML, CSS, JSON, C/C++
- **Current line highlighting** in darker blue
- **Matching brackets highlighting** in green
- **Auto-indent** on Enter (preserves leading whitespace)
- **Auto-close brackets/quotes**: (, {, [, ", '
- **Right-click context menu**: Cut, Copy, Paste, Select All

### 🔍 Search & Replace
- **Find panel** with real-time highlighting
- **Replace functionality** with Replace All option
- **Keyboard shortcuts**: F3 (Next), Shift+F3 (Previous)
- **All matches highlighted** yellow, current match green

### 📑 Tab Management
- **Multiple tabs** with file names
- **Modified tabs** show "*" indicator
- **Close tab** with Ctrl+W (prompts to save if modified)
- **Close Others**: keeps current tab, closes all others
- **Reopen Closed Tab**: Ctrl+Shift+T restores last closed tab

### 🎯 Unity Integration
- **Designed specifically for Unity development**
- **C# syntax highlighting**
- **Fast tab switching** between scripts
- **Always-on-top** for overlay editing
- **Compact design** to fit alongside Unity

### 💾 Session Persistence
- **Saves all open tabs** and content to `~/.anora_editor_session.json`
- **Restores session** on startup
- **Autosaves** every 500ms after changes
- **Recent files list** (last 10)

## 🚀 Quick Start

### Prerequisites
- **Python 3.7+** installed on your system
- **Windows 11/10/8.1** or **Linux** or **macOS**

### Installation

1. **Download** the Anora Editor files
2. **Extract** to any folder
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running Anora Editor

#### Windows
```bash
# Option 1: Direct Python execution
python anora_editor.py

# Option 2: Use the batch launcher
run_anora.bat

# Option 3: Double-click run_anora.bat
```

#### Linux/macOS
```bash
# Option 1: Direct Python execution
python3 anora_editor.py

# Option 2: Use the shell launcher
chmod +x run_anora.sh
./run_anora.sh

# Option 3: Make executable and run
chmod +x anora_editor.py
./anora_editor.py
```

## 📋 File Associations

### Windows
Run as Administrator:
```powershell
.\install_windows_default_editor.ps1
```

### Linux
```bash
chmod +x install_linux_default_editor.sh
./install_linux_default_editor.sh
```

### Supported File Types
- **Python**: `.py`
- **C#**: `.cs`
- **JavaScript**: `.js`
- **HTML**: `.html`
- **CSS**: `.css`
- **JSON**: `.json`
- **Text**: `.txt`
- **C/C++**: `.c`, `.cpp`, `.h`

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+F` | Find |
| `Ctrl+H` | Replace |
| `Ctrl+T` | New tab |
| `Ctrl+W` | Close tab |
| `Ctrl+Shift+T` | Reopen closed tab |
| `Ctrl+A` | Select all |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+X` | Cut |
| `Ctrl+C` | Copy |
| `Ctrl+V` | Paste |
| `Ctrl+G` | Go to line |
| `F3` | Next search result |
| `Shift+F3` | Previous search result |
| `Ctrl+Q` | Exit |

## 🎛️ Menu Bar

### File Menu
- **New** (Ctrl+N)
- **Open** (Ctrl+O)
- **Save** (Ctrl+S)
- **Save As** (Ctrl+Shift+S)
- **Open Recent** (submenu with last 10 files)
- **Exit** (Ctrl+Q)

### Edit Menu
- **Undo** (Ctrl+Z)
- **Redo** (Ctrl+Y)
- **Cut** (Ctrl+X)
- **Copy** (Ctrl+C)
- **Paste** (Ctrl+V)
- **Select All** (Ctrl+A)
- **Find** (Ctrl+F)
- **Replace** (Ctrl+H)

### View Menu
- **Always on Top** (toggle)
- **Fullscreen** (toggle)

### Window Menu
- **New Tab** (Ctrl+T)
- **Close Tab** (Ctrl+W)
- **Close Others**
- **Reopen Closed Tab** (Ctrl+Shift+T)

### Navigate Menu
- **Go To Line** (Ctrl+G)

## 🛠️ Toolbar

- **📄 New** - Create new file
- **📂 Open** - Open existing file
- **💾 Save** - Save current file
- **🔍 Find** - Show find panel
- **🔄 Replace** - Show replace panel
- **📌 Pin** - Toggle always on top
- **⛶ Full** - Toggle fullscreen

## 🎨 Color Scheme

- **Background**: `#1e1e1e` (dark gray)
- **Text**: `#d4d4d4` (light gray)
- **Selection**: `#264f78` (blue)
- **Current line**: `#33415e` (darker blue highlight)
- **Tabs**: `#2d2d30` (subtle gray)
- **Buttons**: `#3e3e42` (medium gray)
- **Keywords**: `#569cd6` (blue)
- **Strings**: `#ce9178` (orange)
- **Comments**: `#6a9955` (green)
- **Numbers**: `#b5cea8` (light green)
- **Functions**: `#dcdcaa` (yellow)

## 🔧 Performance Features

- **Syntax highlighting** only processes visible lines
- **200ms delay** on typing to prevent lag
- **Efficient line number updates**
- **Session autosave** with debouncing
- **Fast file operations**

## 📁 Project Structure

```
anora-editor/
├── anora_editor.py              # Main application
├── requirements.txt             # Python dependencies
├── run_anora.bat               # Windows launcher
├── run_anora.sh                # Linux/macOS launcher
├── install_windows_default_editor.ps1  # Windows file associations
├── install_linux_default_editor.sh     # Linux file associations
└── README.md                   # This file
```

## 🐛 Troubleshooting

### Python Not Found
- Ensure Python 3.7+ is installed
- Add Python to your system PATH
- On Windows, try `python` or `python3`
- On Linux/macOS, try `python3`

### Dependencies Missing
```bash
pip install -r requirements.txt
```

### File Associations Not Working
- **Windows**: Run PowerShell as Administrator
- **Linux**: Ensure `xdg-utils` is installed

### Performance Issues
- Close unnecessary tabs
- Disable syntax highlighting for large files
- Restart the application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **VS Code** for color scheme inspiration
- **Pygments** for syntax highlighting
- **Tkinter** for the GUI framework
- **Unity Technologies** for the development environment

---

**Anora Editor** - Professional Code Editor for Unity Development

*Fast, lightweight, and designed for Unity developers who need a professional editing experience without the bloat.*