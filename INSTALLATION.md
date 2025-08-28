# Anora Code Editor - Installation Guide

## 🚀 Quick Start

### For Windows Users (Recommended)

1. **Download the project**
   - Extract the ZIP file to any folder
   - Open Command Prompt in the extracted folder

2. **Run the launcher**
   ```cmd
   python run_anora.py
   ```
   This will automatically:
   - Check Python version
   - Install dependencies
   - Create sample files
   - Launch the editor

### For Linux/Mac Users

1. **Open terminal in the project folder**

2. **Run the launcher**
   ```bash
   python3 run_anora.py
   ```

## 📋 Requirements

- **Python 3.7 or higher**
- **Windows 10/11** (primary target)
- **Linux/macOS** (supported)

## 🔧 Manual Installation

If the automatic launcher doesn't work:

1. **Install Python dependencies**
   ```bash
   pip install pygments pillow
   ```

2. **Run the editor directly**
   ```bash
   python anora_editor_advanced.py
   ```

## 🎯 Features

### Professional UI
- **Dark theme** with VS Code-style colors
- **Smooth animations** at 60 FPS
- **Modern buttons** with hover effects
- **Responsive design** that adapts to window size

### Code Editing
- **Multi-tab support** for working with multiple files
- **Syntax highlighting** for Python, C#, JavaScript, HTML, CSS, JSON, C/C++
- **Line numbers** with smooth scrolling
- **Search and replace** with highlighting
- **Auto-save** every 500ms

### Unity Integration
- **Always on top** mode for overlay editing
- **C# support** optimized for Unity scripts
- **Fast tab switching** between Unity files
- **Professional appearance** matching modern IDEs

### Keyboard Shortcuts
- `Ctrl+N`: New file
- `Ctrl+O`: Open file
- `Ctrl+S`: Save
- `Ctrl+F`: Find
- `Ctrl+H`: Replace
- `Ctrl+T`: New tab
- `Ctrl+W`: Close tab
- `Ctrl+Shift+T`: Reopen closed tab
- `F3/Shift+F3`: Next/Previous search result

## 📁 File Support

The editor supports:
- **Python** (.py)
- **C#** (.cs) - Perfect for Unity
- **JavaScript** (.js)
- **HTML** (.html)
- **CSS** (.css)
- **JSON** (.json)
- **C/C++** (.c, .cpp, .h)
- **Text** (.txt)

## 🎨 Customization

### Color Theme
The editor uses a professional dark theme:
- Background: `#1e1e1e`
- Text: `#d4d4d4`
- Selection: `#264f78`
- Keywords: `#569cd6`
- Strings: `#ce9178`
- Comments: `#6a9955`

### Window Layout
- **Default size**: 1000x700 pixels
- **Minimum size**: 600x400 pixels
- **Resizable**: Fully responsive
- **Always on top**: Toggle with pin button
- **Fullscreen**: Toggle with full button

## 🔧 File Associations (Windows)

To set Anora as the default editor for file types:

1. **Run PowerShell as Administrator**
2. **Navigate to the project folder**
3. **Execute the installer**
   ```powershell
   .\install_windows_default_editor.ps1
   ```

This will allow you to double-click files to open them in Anora.

## 🐛 Troubleshooting

### Editor won't start
- Ensure Python 3.7+ is installed
- Run `python run_anora.py` for automatic setup
- Check that all dependencies are installed

### Syntax highlighting not working
- Verify Pygments is installed: `pip install pygments`
- Check file extension is supported
- Restart the editor

### Performance issues
- Close unnecessary tabs
- Reduce window size if needed
- Check system resources

### File associations not working
- Run PowerShell as Administrator
- Execute `.\install_windows_default_editor.ps1`
- Check Windows file association settings

## 📞 Support

If you encounter any issues:

1. **Check the troubleshooting section above**
2. **Ensure all dependencies are installed**
3. **Try running the test script**: `python test_editor.py`
4. **Check the sample files** for syntax highlighting examples

## 🎉 Success!

Once installed, you'll have a professional code editor that:
- Looks and feels like modern IDEs
- Works perfectly with Unity development
- Provides smooth animations and responsive UI
- Supports all major programming languages
- Saves your work automatically

**Happy coding with Anora!** 🚀