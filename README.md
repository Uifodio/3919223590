# Super File Manager

A professional file manager with built-in code editor, multi-window support, and seamless drag-and-drop functionality. Built with Electron, React, and Monaco Editor.

## 🚀 Features

### Core File Management
- **File Explorer Tree View** – Standard left-panel navigation with expandable folders
- **Multi-window Support** – Open multiple independent windows (like running multiple explorers)
- **Drag & Drop** – Move/copy files between windows or to external applications
- **Full File Operations** – Copy, rename, delete, duplicate, create folders/files
- **Hidden Files Support** – Toggle visibility of hidden files and folders
- **Multiple View Modes** – List and grid view with customizable sorting

### Built-in Code Editor
- **Monaco Editor Integration** – Full-featured code editor with syntax highlighting
- **Auto-save** – Automatic file saving with configurable intervals
- **Undo/Redo** – Full undo/redo support
- **Find/Replace** – Quick search and replace functionality
- **Syntax Highlighting** – Support for 20+ programming languages
- **Line Numbers** – Configurable line number display
- **Word Wrap** – Toggle word wrapping
- **Minimap** – Code overview with minimap

### Advanced Features
- **Cross-window Clipboard** – Copy/cut in one window, paste in another
- **Progress Tracking** – Visual progress bars for large operations
- **Auto-backup** – Automatic .bak file creation on edits
- **ZIP Support** – Open and edit files inside ZIP archives
- **Quick Search** – Fast file/folder name search
- **Breadcrumb Navigation** – Easy path navigation with copy functionality
- **Context Menus** – Right-click context menus for quick actions
- **Keyboard Shortcuts** – Full keyboard navigation support

### System Integration
- **Drive Detection** – Automatic detection of all system drives
- **External App Integration** – Open files with default applications
- **Unity Integration** – Can be set as Unity's external code editor
- **Dark Theme** – Modern dark theme by default
- **Settings Persistence** – All settings saved to JSON config file

## 🛠️ Installation

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SuperFileManager
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

### Building for Production

#### Windows
```bash
npm run dist:win
```

#### Linux
```bash
npm run dist:linux
```

#### macOS
```bash
npm run dist:mac
```

#### All Platforms
```bash
npm run dist
```

## 🎯 Usage

### Basic Navigation
- **Left Panel**: Navigate through drives and folders
- **Right Panel**: View files and folders in current directory
- **Double-click**: Open folders or edit files
- **Right-click**: Access context menu for file operations

### File Operations
- **Copy**: Select files and press Ctrl+C or use toolbar
- **Cut**: Select files and press Ctrl+X or use toolbar  
- **Paste**: Press Ctrl+V or use toolbar to paste from clipboard
- **Delete**: Select files and press Delete or use toolbar
- **Rename**: Right-click file and select "Rename"

### Multi-window Usage
- **New Window**: File → New Window or Ctrl+N
- **Cross-window Operations**: Copy in one window, paste in another
- **Independent Navigation**: Each window maintains its own state

### Code Editing
- **Open File**: Double-click any text/code file
- **Save**: Ctrl+S or use the save button
- **Auto-save**: Files are automatically saved based on settings
- **Search**: Ctrl+F to search within the file
- **Close Editor**: Click the X button or press Ctrl+W

### Keyboard Shortcuts
- `Ctrl+N` - New window
- `Ctrl+O` - Open folder
- `Ctrl+C` - Copy
- `Ctrl+X` - Cut
- `Ctrl+V` - Paste
- `Delete` - Delete selected files
- `Ctrl+F` - Search in current file
- `Ctrl+S` - Save current file
- `Ctrl+W` - Close current file
- `F5` - Refresh current directory

## ⚙️ Configuration

Settings are stored in `settings.json` in the app's user data directory:

```json
{
  "theme": "dark",
  "fontSize": 14,
  "showHiddenFiles": false,
  "autoSave": true,
  "autoSaveInterval": 30000,
  "editor": {
    "fontSize": 14,
    "theme": "vs-dark",
    "wordWrap": "on",
    "minimap": { "enabled": true },
    "lineNumbers": "on"
  },
  "fileManager": {
    "viewMode": "list",
    "sortBy": "name",
    "sortOrder": "asc"
  }
}
```

## 🔧 Unity Integration

To use Super File Manager as Unity's external code editor:

1. Open Unity
2. Go to Edit → Preferences → External Tools
3. Set "External Script Editor" to Super File Manager executable
4. Unity will now open scripts in Super File Manager

## 🏗️ Project Structure

```
SuperFileManager/
├── electron.main.js          # Electron main process
├── preload.js               # Preload script for security
├── package.json             # Project dependencies and scripts
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── src/
│   ├── App.jsx              # Main React application
│   ├── main.jsx             # React entry point
│   ├── components/          # React components
│   │   ├── FileTree.jsx     # Left panel file tree
│   │   ├── FileExplorer.jsx # Main file explorer
│   │   ├── FileEditor.jsx   # Monaco editor wrapper
│   │   ├── Toolbar.jsx      # Top toolbar
│   │   ├── SearchBar.jsx    # Search functionality
│   │   ├── Breadcrumb.jsx   # Path navigation
│   │   ├── ContextMenu.jsx  # Right-click menus
│   │   ├── StatusBar.jsx    # Bottom status bar
│   │   └── ProgressBar.jsx  # Operation progress
│   ├── utils/               # Utility functions
│   │   ├── useFileManager.js # File operations hook
│   │   ├── useSettings.js   # Settings management hook
│   │   └── cn.js           # Class name utility
│   └── styles/
│       └── global.css       # Global styles and Tailwind
└── public/                  # Static assets
```

## 🐛 Troubleshooting

### Common Issues

**App won't start**
- Ensure Node.js 16+ is installed
- Run `npm install` to install dependencies
- Check console for error messages

**File operations fail**
- Ensure proper file permissions
- Check if files are locked by other applications
- Verify disk space availability

**Editor not working**
- Ensure Monaco Editor dependencies are installed
- Check browser console for JavaScript errors
- Verify file is a supported text format

### Development

**Hot reload not working**
- Ensure both Vite dev server and Electron are running
- Check port 5173 is available
- Restart development server

**Build fails**
- Clear `node_modules` and reinstall dependencies
- Ensure all required dependencies are in `package.json`
- Check for platform-specific build requirements

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🆘 Support

For issues and feature requests, please use the GitHub issues page.

---

**Super File Manager** - The professional file manager that replaces both File Explorer and Visual Studio Code for Unity development.