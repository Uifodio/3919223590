# Windows File Manager

A comprehensive file manager application built with Python and Tkinter that provides a modern, user-friendly interface for managing files and folders on Windows systems.

## Features

### 🗂️ File Navigation
- **Dual-pane interface**: Folder tree on the left, file list on the right
- **Address bar**: Direct path navigation with auto-completion
- **Drive access**: Full access to all system drives
- **Navigation buttons**: Back, Up, and Refresh functionality

### 📁 File Operations
- **Create**: New folders and files
- **Copy/Cut/Paste**: Full clipboard support with duplicate handling
- **Delete**: Safe deletion with confirmation
- **Rename**: In-place file and folder renaming
- **Open**: Double-click to open files with default applications

### 🔍 Search & View
- **File search**: Recursive search through directories
- **File properties**: Detailed file information display
- **Multiple views**: List view with columns (Name, Size, Type, Modified)
- **File type detection**: Automatic file type identification

### ⌨️ Keyboard Shortcuts
- `Ctrl+A`: Select all files
- `Ctrl+C`: Copy selected files
- `Ctrl+X`: Cut selected files
- `Ctrl+V`: Paste files
- `Delete`: Delete selected files
- `F5` or `Ctrl+R`: Refresh current directory
- `Ctrl+L`: Focus address bar

### 🖱️ Context Menu
- Right-click context menu with common operations
- Open, Cut, Copy, Paste, Delete, Rename, Properties

## Installation

### Prerequisites
- Python 3.6 or higher
- Windows operating system (primary target)
- Linux/macOS support (limited drive enumeration)

### Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd file-manager
   ```

2. **Install dependencies** (optional, for enhanced Windows functionality)
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python file_manager.py
   ```

## Usage

### Starting the Application
```bash
python file_manager.py
```

The file manager will start in your home directory and display:
- **Toolbar**: Quick access buttons for common operations
- **Address bar**: Current directory path with navigation
- **Folder tree**: Hierarchical view of drives and folders
- **File list**: Detailed view of current directory contents
- **Status bar**: Information about current location and file counts

### Basic Operations

#### Navigation
- **Double-click folders** in the file list to open them
- **Click folders** in the tree view to navigate
- **Use the address bar** to type a specific path
- **Use navigation buttons** (Back, Up, Refresh)

#### File Management
1. **Select files**: Click to select individual files, Ctrl+click for multiple
2. **Copy/Cut**: Select files and use toolbar buttons or Ctrl+C/Ctrl+X
3. **Paste**: Navigate to destination and use toolbar button or Ctrl+V
4. **Delete**: Select files and press Delete or use toolbar button
5. **Rename**: Right-click file and select "Rename"

#### Search
1. Click the "🔍 Search" button or use the search function
2. Enter your search term
3. Results will appear in a new window
4. Double-click results to open files or navigate to folders

## File Type Support

The file manager recognizes and displays appropriate icons and types for:
- **Documents**: .txt, .doc, .docx, .pdf, .xls, .xlsx, .ppt, .pptx
- **Images**: .jpg, .jpeg, .png, .gif, .bmp
- **Audio/Video**: .mp3, .mp4, .avi
- **Archives**: .zip, .rar, .7z
- **Code files**: .py, .js, .html, .css, .json, .xml
- **System files**: .exe, .msi, .dll, .sys, .ini, .log

## System Requirements

- **Operating System**: Windows 10/11 (primary), Linux, macOS
- **Python**: 3.6 or higher
- **Memory**: 100MB RAM minimum
- **Storage**: 50MB free space

## Troubleshooting

### Common Issues

1. **Drive enumeration fails on Windows**
   - Install pywin32: `pip install pywin32`
   - Run as administrator if needed

2. **File operations fail**
   - Check file permissions
   - Ensure files aren't in use by other applications
   - Run as administrator for system folders

3. **GUI doesn't display properly**
   - Update your Python installation
   - Check if tkinter is properly installed
   - Try running on a different display scale

### Error Messages

- **"Path does not exist"**: Check the address bar path for typos
- **"Could not open file"**: File may be corrupted or require specific permissions
- **"Could not delete"**: File may be in use or require elevated permissions

## Development

### Project Structure
```
file-manager/
├── file_manager.py      # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Future Enhancements
- [ ] File preview functionality
- [ ] Drag and drop support
- [ ] Multiple tabs/windows
- [ ] File compression/decompression
- [ ] Network drive support
- [ ] File synchronization
- [ ] Advanced search filters
- [ ] Custom themes and icons

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:
- Create an issue on the project repository
- Check the troubleshooting section above
- Ensure you're using a supported Python version

---

**Note**: This file manager is designed for educational and personal use. Always backup important files before performing bulk operations.