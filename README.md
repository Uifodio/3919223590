# 🚀 Windows File Manager Pro - Professional File Management Solution

A feature-rich, modern file manager for Windows 11/10 built with C# and WPF, designed for developers, designers, and power users who demand professional-grade file management capabilities.

## ✨ Features Overview

### 🔧 Core File Operations
- **File Explorer Tree View** - Standard left-panel navigation with expandable folders
- **Multi-window Support** - Open multiple independent instances (like running 9 explorers)
- **Drag & Drop** - Seamless file operations between windows and external applications
- **Copy, Rename, Delete, Duplicate** - Full basic file operations with progress tracking
- **Multi-file Selection** - Shift/Ctrl select and apply actions to multiple files
- **Safe Operations** - Files sent to system trash with undo capability

### 📝 Built-in Code Editor
- **Native Text Editor** - No external applications required
- **Syntax Highlighting** - Support for 50+ programming languages
- **Auto-save & Undo** - Automatic saving with comprehensive undo/redo
- **Find & Replace** - Quick text search within files
- **Line Numbers** - Professional code editing experience
- **Multiple Tabs** - Edit multiple files simultaneously

### 🔍 Advanced Search & Navigation
- **Fast File Search** - Instant file/folder name search
- **Content Search** - Search inside files with preview
- **Recent Files** - Quick access to recently opened items
- **Favorites** - Bookmark frequently used locations

### 📦 Archive & ZIP Support
- **ZIP as Folders** - Open ZIP archives as regular folders
- **Edit Inside Archives** - Modify files within ZIPs seamlessly
- **Auto-backup** - Automatic .bak creation when editing archived files
- **Archive Creation** - Create new ZIP files with drag & drop

### 🎨 Modern UI/UX
- **Dark Theme (Default)** - Clean, modern interface optimized for long sessions
- **Light Theme Option** - Alternative light mode available
- **Customizable Interface** - Adjustable font sizes, colors, and layouts
- **Progress Bars** - Visual feedback for all operations
- **Responsive Design** - Adapts to different screen sizes

### ⚙️ Configuration & Customization
- **JSON Settings** - Everything customizable via configuration files
- **Cross-window Clipboard** - Cut/copy in one window, paste in another
- **Keyboard Shortcuts** - Full keyboard navigation support
- **Custom Themes** - Create and share custom color schemes

## 🚀 Installation

### Prerequisites
- Windows 10 (version 1903 or later) or Windows 11
- .NET 6.0 Desktop Runtime or later
- Minimum 4GB RAM
- 100MB free disk space

### Quick Start
1. **Download** the latest release from GitHub
2. **Extract** the ZIP file to your preferred location
3. **Run** `WindowsFileManagerPro.exe`
4. **Enjoy** professional file management!

### Build from Source
```bash
git clone https://github.com/yourusername/windows-file-manager-pro.git
cd windows-file-manager-pro
dotnet restore
dotnet build --configuration Release
```

## 📖 Usage Guide

### Basic Operations
- **Navigate**: Use the tree view on the left or address bar
- **Select Files**: Click to select, Ctrl+Click for multiple, Shift+Click for range
- **Open Files**: Double-click to open in built-in editor or default application
- **New Window**: File → New Window or Ctrl+N

### Advanced Features
- **Drag & Drop**: Drag files between windows or to external applications
- **Quick Replace**: Monitor download folder and drag files to project windows
- **Archive Editing**: Open ZIP files as folders and edit contents directly
- **Multi-window Clipboard**: Copy in one window, paste in another

### Keyboard Shortcuts
- `Ctrl+N` - New Window
- `Ctrl+O` - Open File
- `Ctrl+S` - Save File
- `Ctrl+F` - Find in File
- `Ctrl+H` - Find and Replace
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `F5` - Refresh
- `F2` - Rename
- `Delete` - Move to Trash
- `Shift+Delete` - Permanent Delete

## 🛠️ Configuration

The application uses JSON configuration files located in:
```
%APPDATA%\WindowsFileManagerPro\settings.json
```

### Customizable Options
- Theme selection (Dark/Light/Custom)
- Font sizes and families
- Editor preferences
- File associations
- Keyboard shortcuts
- Interface layout

## 🔧 Technical Details

- **Framework**: .NET 6.0 WPF
- **Language**: C# 10.0
- **Architecture**: MVVM pattern with dependency injection
- **Performance**: Optimized for large file operations and real-time search
- **Compatibility**: Windows 10/11 (x64)

## 🐛 Troubleshooting

### Common Issues
1. **Application won't start**: Ensure .NET 6.0 Runtime is installed
2. **Slow performance**: Check available RAM and close unnecessary applications
3. **File operations fail**: Verify file permissions and antivirus settings

### Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides in the docs folder
- **Community**: Join discussions in GitHub Discussions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Windows development technologies
- Inspired by professional file management needs
- Community-driven feature development
- Performance-focused architecture

---

**Windows File Manager Pro** - Professional file management for the modern Windows user.

*Built with ❤️ for Windows developers and power users*