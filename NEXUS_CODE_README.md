# 🔥 Nexus Code - Professional Dark Code Editor

**Nexus Code** is a professional, dark-themed code editor built with Python and Tkinter, featuring advanced drag and drop capabilities, syntax highlighting, and Windows integration.

## 🎯 Features

### 🔥 **Absolute Brute Force Drag & Drop**
- **8 different drag and drop methods** for maximum compatibility
- **Windows API integration** with native drag and drop
- **Multiple drop zones** visible on screen
- **File system monitoring** for automatic file detection
- **Clipboard monitoring** for file path detection
- **Windows message hook** for WM_DROPFILES handling

### 🎨 **Professional Dark Theme**
- **Dark color scheme** optimized for long coding sessions
- **Syntax highlighting** for multiple languages
- **Professional window behavior** with Alt+Tab support
- **Always-on-top** and fullscreen modes
- **Tabbed interface** for multiple files

### 💻 **Advanced Code Editing**
- **Syntax highlighting** for Python, C#, JavaScript, HTML, CSS
- **Search and replace** with skip functionality
- **Line numbers** and status bar
- **Undo/redo** functionality
- **Auto-indent** and code formatting
- **Multiple language support**

### 🪟 **Windows Integration**
- **Native Windows drag and drop** using Shell32
- **Professional window appearance** with taskbar integration
- **File association support** for common file types
- **Windows message handling** for system integration
- **Professional keyboard shortcuts** (Alt+Tab, F11, Escape)

## 🚀 Quick Start

### **Method 1: Using the Launcher**
```bash
python3 launch_nexus.py
```

### **Method 2: Direct Launch**
```bash
python3 nexus_code.py
```

### **Method 3: With File**
```bash
python3 nexus_code.py your_file.py
```

### **Method 4: Build Executable**
```bash
python3 build_exe_alternative.py
```

## 🔧 Installation

### **Dependencies**
```bash
pip install tkinterdnd2
pip install pywin32
pip install pygments
```

### **Optional Dependencies**
```bash
pip install pyinstaller  # For building executables
```

## 🎯 Drag & Drop Methods

### **Method 1: tkinterdnd2**
- Primary drag and drop library
- Works on text widgets and main window
- Handles multiple file formats

### **Method 2: Windows API**
- Native Windows drag and drop
- Uses win32gui and win32con
- WS_EX_ACCEPTFILES window style

### **Method 3: Shell32 Integration**
- Shell32.DragAcceptFiles
- Shell32.DragQueryFile
- Native Windows file handling

### **Method 4: Windows Message Hook**
- WM_DROPFILES message handling
- Direct Windows message processing
- Professional system integration

### **Method 5: Multiple Drop Zones**
- 6 visible drop zones on screen
- Color-coded for easy identification
- Clickable for manual file opening

### **Method 6: File System Monitoring**
- Monitors for new files
- Automatic file detection
- Background file scanning

### **Method 7: Clipboard Monitoring**
- Detects file paths in clipboard
- Continuous clipboard monitoring
- Automatic file opening

### **Method 8: Fallback Methods**
- Manual file opening (Ctrl+O)
- File dialog integration
- Error handling and recovery

## 🎨 Syntax Highlighting

### **Supported Languages**
- **Python** (.py) - Keywords, strings, comments
- **C#** (.cs) - Unity integration, keywords, strings
- **JavaScript** (.js) - ES6+ features, keywords, strings
- **HTML** (.html) - Tags, attributes, content
- **CSS** (.css) - Properties, values, selectors
- **JSON** (.json) - Structure, values, formatting
- **Generic** - Strings, comments, basic highlighting

### **Highlighting Methods**
- **Language-specific** highlighting for each language
- **Pattern matching** with regex
- **Character-by-character** parsing
- **Line-by-line** analysis
- **Generic fallback** for unknown languages

## 🪟 Windows Features

### **Professional Window Behavior**
- **Alt+Tab** - Professional window switching
- **F11** - Fullscreen toggle
- **Escape** - Exit fullscreen, clear selection
- **Alt+F4** - Professional application quit

### **Window Integration**
- **Taskbar grouping** with proper window class
- **File association** for common file types
- **Professional appearance** with dark theme
- **Centered window positioning**

### **Drag & Drop Integration**
- **Native Windows drag and drop**
- **Multiple drop targets** on every widget
- **Visual feedback** during drag operations
- **File path parsing** and validation

## 🔥 Advanced Features

### **Professional Code Editing**
- **Tabbed interface** for multiple files
- **Search and replace** with skip functionality
- **Line numbers** and status bar
- **Undo/redo** with history
- **Auto-save** and file monitoring

### **Developer Tools**
- **Syntax highlighting** with multiple methods
- **Code formatting** and indentation
- **Error detection** and highlighting
- **Professional keyboard shortcuts**
- **Status bar** with file information

### **File Management**
- **Multiple file types** support
- **File association** for common formats
- **Recent files** tracking
- **File monitoring** for changes
- **Professional file dialogs**

## 🚀 Building Executables

### **Alternative Build Method**
```bash
python3 build_exe_alternative.py
```

### **Build Features**
- **Directory mode** for better compatibility
- **Hidden imports** for all dependencies
- **Excluded modules** for smaller size
- **Professional launcher** batch file
- **Error handling** and recovery

### **Executable Features**
- **NexusCode.exe** - Main executable
- **launch_nexus.bat** - Launcher script
- **Professional appearance** with icon
- **Windows integration** and taskbar support

## 🎯 Testing

### **Test Files**
- **test_nexus_windows_drag.py** - Windows drag and drop test
- **test_absolute_brute_force.py** - Absolute brute force test
- **test_brute_force.py** - General functionality test

### **Test Features**
- **Multiple drag and drop methods**
- **Windows API integration**
- **Syntax highlighting** verification
- **Professional window behavior**
- **Error handling** and recovery

## 🔧 Troubleshooting

### **Common Issues**
1. **Drag and drop not working** - Try different drop zones or use Ctrl+O
2. **Syntax highlighting issues** - Check file extension and language support
3. **Window not responding** - Use Alt+F4 to close and restart
4. **File not opening** - Check file permissions and path

### **Solutions**
- **Multiple fallback methods** ensure functionality
- **Detailed logging** for debugging
- **Error handling** prevents crashes
- **Professional recovery** mechanisms

## 🎉 Why Nexus Code?

### **Unique Features**
- **Absolute brute force drag and drop** - 8 different methods
- **Professional Windows integration** - Native API support
- **Dark theme optimized** - Perfect for long coding sessions
- **Advanced syntax highlighting** - Multiple highlighting methods
- **Professional window behavior** - Alt+Tab, F11, Escape support

### **Professional Quality**
- **Robust error handling** - No crashes, always functional
- **Detailed logging** - See exactly what's happening
- **Multiple fallback methods** - If one fails, others work
- **Windows integration** - Professional system behavior
- **Professional appearance** - Dark theme with modern UI

## 🔥 Get Started

1. **Download** the files
2. **Install dependencies** with pip
3. **Run the launcher** or main file
4. **Drag and drop** files to test
5. **Enjoy professional** code editing!

**Nexus Code** - Where professional coding meets absolute reliability! 🔥