# Anora Editor - Professional Unity Code Editor

A fast, lightweight, and professional code editor built specifically for Unity development, designed to replace Visual Studio with a focus on speed, efficiency, and professional workflow.

## 🚀 Features

### ✨ Core Editor Features
- **Professional Dark Theme** - VS Code-style colors with Unity-optimized aesthetics
- **Multi-tab Support** - Work with multiple files simultaneously
- **Syntax Highlighting** - Support for Python, C#, JavaScript, TypeScript, HTML, CSS, JSON, C/C++
- **Line Numbers** - 4-digit line numbering with scroll synchronization
- **Auto-indent** - Smart indentation for clean, readable code
- **Bracket Matching** - Visual highlighting of matching brackets and parentheses

### 🎯 Unity Development Features
- **C# Optimization** - Enhanced support for Unity C# scripts
- **Fast Tab Switching** - Quick navigation between multiple script files
- **Always on Top** - Keep editor visible while working in Unity
- **Professional Appearance** - Clean, distraction-free interface

### 🛠️ Advanced Features
- **Search & Replace** - Powerful find and replace with regex support
- **Session Persistence** - Automatically saves open tabs and content
- **Recent Files** - Quick access to recently opened files
- **File Associations** - Set as default editor for various file types
- **Cross-platform** - Works on Windows, macOS, and Linux

### ⌨️ Keyboard Shortcuts
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `Ctrl+Shift+S` - Save file as
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+W` - Always on top
- `Ctrl+T` - New tab
- `Ctrl+G` - Go to line
- `F3` - Find next
- `Shift+F3` - Find previous
- `Esc` - Close search/replace

## 🎨 Visual Design

### Color Scheme
- **Background**: #1e1e1e (Dark theme)
- **Text**: #d4d4d4 (Light gray)
- **Selection**: #264f78 (Blue)
- **Current Line**: #33415e (Dark blue)
- **Tabs**: #2d2d30 (Dark gray)
- **Buttons**: #3e3e42 (Medium gray)

### Syntax Highlighting Colors
- **Keywords**: #569cd6 (Blue)
- **Strings**: #ce9178 (Orange)
- **Comments**: #6a9955 (Green)
- **Numbers**: #b5cea8 (Light green)
- **Functions**: #dcdcaa (Yellow)

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd anora-editor
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Development mode**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   npm run build:electron
   ```

### Development Commands
- `npm run dev` - Start development servers (React + Electron)
- `npm run dev:react` - Start React development server only
- `npm run dev:electron` - Start Electron app only
- `npm run build` - Build React frontend
- `npm run build:electron` - Build Electron app
- `npm run dist` - Build both frontend and Electron app

## 🏗️ Project Structure

```
anora-editor/
├── src/                    # React source code
│   ├── components/         # React components
│   ├── hooks/             # Custom React hooks
│   ├── styles/            # CSS stylesheets
│   └── types/             # TypeScript type definitions
├── electron/               # Electron main process
├── public/                 # Static assets
├── dist/                   # Built React app
├── dist_electron/          # Built Electron app
└── package.json            # Project configuration
```

### Key Components
- **MenuBar** - Top menu with File, Edit, View, Window, Navigate
- **Toolbar** - Quick action buttons
- **EditorTabs** - Tab management and content editing
- **CodeEditor** - Core text editing with syntax highlighting
- **SearchReplacePanel** - Find and replace functionality
- **StatusBar** - Status information display

## 🔧 Configuration

### File Associations
The editor can be set as the default editor for various file types:

#### Linux
```bash
chmod +x install_linux_default_editor.sh
./install_linux_default_editor.sh
```

#### Windows
```powershell
# Run as Administrator
.\install_windows_default_editor.ps1
```

### Supported File Types
- Python (.py)
- C# (.cs)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- HTML (.html, .htm)
- CSS (.css)
- JSON (.json)
- C/C++ (.c, .cpp, .h, .hpp)
- Text (.txt)

## 🎯 Unity Integration

### Optimized for Unity Workflow
- **Fast Startup** - Quick loading for rapid script editing
- **Always on Top** - Keep editor visible while working in Unity
- **C# Support** - Enhanced syntax highlighting for Unity scripts
- **Tab Management** - Efficient handling of multiple script files
- **Professional UI** - Clean interface that matches Unity's aesthetic

### Performance Features
- **Visible-line-only highlighting** - Syntax highlighting only for visible lines
- **Debounced autosave** - Efficient session persistence
- **Optimized rendering** - Fast tab switching and content updates

## 🚀 Building and Distribution

### Development Build
```bash
npm run build
npm run build:electron
```

### Production Build
```bash
npm run dist
```

The built application will be available in the `dist_electron/` directory.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with React and Electron
- Inspired by VS Code and Visual Studio
- Designed for Unity developers
- Professional-grade code editor

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code examples

---

**Anora Editor** - Professional Unity Code Editor for the modern developer.