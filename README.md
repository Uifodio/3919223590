# Nova Explorer - Advanced File Manager

**The Ultimate File Manager with Built-in Editor - Like Windows Explorer + VS Code Combined!**

Built with **Kivy** for maximum reliability and simplicity. No complex dependencies, no terminal issues - just a solid, native Windows application.

## 🚀 **Features**

### **File Management**
- ✅ **Tree View Navigation** - Browse folders like Windows Explorer
- ✅ **File List with Details** - Name, size, type, date modified
- ✅ **Multi-file Selection** - Select multiple files for operations
- ✅ **Drag & Drop** - Move files between folders and to external apps
- ✅ **Quick Search** - Find files instantly
- ✅ **Hidden Files Toggle** - Show/hide system files

### **Built-in Editor**
- ✅ **Syntax Highlighting** - Support for Python, JavaScript, HTML, CSS, etc.
- ✅ **Auto-save** - Never lose your work
- ✅ **Find & Replace** - Powerful text search
- ✅ **Line Numbers** - Professional editing experience
- ✅ **Tab Support** - Edit multiple files at once
- ✅ **Backup on Save** - Automatic .bak file creation

### **Advanced Features**
- ✅ **Multi-window Support** - Open multiple independent windows
- ✅ **Recent Files/Folders** - Quick access to recent locations
- ✅ **File Operations** - Copy, move, delete, rename, duplicate
- ✅ **Safe Delete** - Files go to Recycle Bin
- ✅ **Progress Bars** - Visual feedback for large operations
- ✅ **Dark/Light Themes** - Choose your preferred look

### **Unity Integration**
- ✅ **Set as External Editor** - Use Nova Explorer as Unity's code editor
- ✅ **Asset Management** - Perfect for Unity project file management
- ✅ **Script Editing** - Edit C# scripts with syntax highlighting

## 🛠️ **Installation & Usage**

### **Option 1: Quick Start (Recommended)**
```bash
# Just double-click this file:
build_kivy.bat
```

This will:
- ✅ Install Python if needed
- ✅ Install all Kivy dependencies
- ✅ Build the executable
- ✅ Create `dist\NovaExplorer.exe`

### **Option 2: Manual Installation**
```bash
# Install dependencies
pip install kivy==2.2.1 kivymd==1.1.1 pillow==10.1.0 pywin32==306 psutil==5.9.6 pyperclip==1.8.2 send2trash==1.8.3 pyinstaller==6.2.0

# Run the application
python main.py

# Build executable
python -m PyInstaller --onefile --windowed --name "NovaExplorer" main.py
```

## 🎯 **Why Kivy?**

- ✅ **Reliable** - No complex dependency chains
- ✅ **Cross-platform** - Works on Windows, Mac, Linux
- ✅ **Native Performance** - Fast and responsive
- ✅ **Modern UI** - Beautiful, customizable interface
- ✅ **Easy Distribution** - Single EXE file
- ✅ **No Terminal Required** - Pure GUI application

## 🎮 **Unity Integration**

1. **Open Unity**
2. **Go to Edit > Preferences > External Tools**
3. **Set External Script Editor to:** `path\to\NovaExplorer.exe`
4. **Enjoy seamless script editing!**

## 🎨 **Customization**

### **Themes**
- **Dark Theme** (Default) - Easy on the eyes
- **Light Theme** - Classic look
- **Custom Colors** - Modify in settings

### **Settings**
- **Font Size** - Adjust text size
- **Auto-save Interval** - Set backup frequency
- **File Operations** - Configure behavior
- **Editor Options** - Tab size, word wrap, etc.

## 📁 **File Operations**

### **Basic Operations**
- **Double-click** - Open files/folders
- **Right-click** - Context menu
- **Ctrl+C/V** - Copy/paste
- **Delete** - Move to Recycle Bin
- **F2** - Rename
- **F5** - Refresh

### **Advanced Operations**
- **Ctrl+A** - Select all
- **Ctrl+F** - Find files
- **Ctrl+Shift+N** - New folder
- **Ctrl+N** - New file
- **Ctrl+S** - Save file
- **Ctrl+Z** - Undo

## 🔧 **Troubleshooting**

### **Common Issues**

**Q: The app won't start**
A: Make sure Python is installed and run `build_kivy.bat`

**Q: Files don't open in editor**
A: Check file permissions and ensure the file is not locked

**Q: Performance is slow**
A: Try disabling auto-save or reducing the interval in settings

**Q: Can't see hidden files**
A: Enable "Show Hidden Files" in the Tools menu

### **Support**

If you encounter any issues:
1. Check the console output for error messages
2. Try running `python main.py` directly
3. Ensure all dependencies are installed correctly

## 🎉 **What Makes This Special**

- **No Terminal Dependency** - Pure GUI application
- **Reliable Build Process** - Kivy is much more stable than PySide6
- **Modern Interface** - Beautiful, responsive design
- **Professional Features** - Everything you need for file management
- **Unity Ready** - Perfect for game development
- **Cross-platform** - Works everywhere Python runs

## 📄 **License**

MIT License - Feel free to modify and distribute!

---

**Built with ❤️ using Kivy - The most reliable Python GUI framework!**