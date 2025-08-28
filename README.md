# 🚀 Anora Editor

**Professional Code Editor Designed for Unity Development**

A modern, feature-rich code editor built with React and Electron, specifically optimized for Unity development with C# support. Anora Editor provides a professional development experience with syntax highlighting, tab management, and powerful editing features.

![Anora Editor](https://img.shields.io/badge/Anora-Editor-007acc?style=for-the-badge&logo=visual-studio-code)

## ✨ Features

### 🎨 **Visual Design**
- **Dark Theme** with professional VS Code-inspired colors
- **Syntax Colors**: Blue keywords, Orange strings, Green comments, Yellow functions
- **Modern UI** with responsive design and smooth animations
- **Professional appearance** matching industry-standard IDEs

### 🖥️ **Window Layout**
- **800x600 default size** with minimum 400x300
- **Top**: Menu bar (File, Edit, View, Window, Navigate)
- **Toolbar**: Icon buttons for quick access
- **Center**: Tabbed notebook with line numbers
- **Bottom**: Status bar showing position and messages
- **Right-click**: Context menu on text area

### 📁 **File Management**
- **New File** (Ctrl+N)
- **Open File** (Ctrl+O) with file type filters
- **Save** (Ctrl+S) and **Save As** (Ctrl+Shift+S)
- **Recent Files** (last 10 files)
- **File associations** for common development files

### 🔍 **Search & Replace**
- **Find** (Ctrl+F) with real-time highlighting
- **Replace** (Ctrl+H) with replace all option
- **Search panel** with find/replace inputs
- **F3/Shift+F3** for next/previous matches
- **All matches highlighted** in yellow, current in green

### 📝 **Text Editor Features**
- **Line numbers** on left (4-digit format)
- **Syntax highlighting** for multiple languages:
  - C# (Unity), Python, JavaScript, HTML, CSS
  - JSON, C/C++, Text files
- **Current line highlighting** in darker blue
- **Matching brackets** highlighted in green
- **Auto-indent** on Enter
- **Auto-close** brackets and quotes
- **Right-click context menu**

### 🗂️ **Tab Management**
- **Multiple tabs** with file names
- **Modified tabs** show "*" indicator
- **Close tab** with Ctrl+W
- **Close Others** keeps current tab
- **Reopen Closed Tab** (Ctrl+Shift+T)
- **Tab switching** with mouse or keyboard

### ⚡ **Performance Features**
- **Syntax highlighting** only for visible lines
- **200ms delay** on typing to prevent lag
- **Efficient line number** updates
- **Session autosave** with debouncing
- **Fast file operations**

### 🎯 **Unity Integration**
- **Designed specifically** for Unity development
- **C# syntax highlighting** with Unity-specific features
- **Fast tab switching** between scripts
- **Always-on-top** for overlay editing
- **Compact design** to fit alongside Unity

## 🚀 Getting Started

### Prerequisites
- Node.js (version 16 or higher)
- npm or yarn package manager

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

3. **Start development mode**
   ```bash
   npm run electron-dev
   ```

### Available Scripts

- `npm start` - Start React development server only
- `npm run electron` - Start Electron app (requires built React app)
- `npm run electron-dev` - Start both React dev server and Electron
- `npm run build` - Build React app for production
- `npm run electron-pack` - Package the app for distribution

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New File | `Ctrl+N` |
| Open File | `Ctrl+O` |
| Save | `Ctrl+S` |
| Save As | `Ctrl+Shift+S` |
| Find | `Ctrl+F` |
| Replace | `Ctrl+H` |
| New Tab | `Ctrl+T` |
| Close Tab | `Ctrl+W` |
| Reopen Closed Tab | `Ctrl+Shift+T` |
| Select All | `Ctrl+A` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Y` |
| Cut | `Ctrl+X` |
| Copy | `Ctrl+C` |
| Paste | `Ctrl+V` |
| Go to Line | `Ctrl+G` |
| Next Search Result | `F3` |
| Previous Search Result | `Shift+F3` |
| Exit | `Ctrl+Q` |

## 🎨 Customization

### Themes
The editor uses a dark theme by default, optimized for long coding sessions. Colors can be customized in the CSS files.

### Language Support
Additional language support can be added by:
1. Adding language definitions to the Monaco editor
2. Updating the `getLanguageFromPath` function
3. Adding syntax highlighting rules

### Keybindings
Custom keybindings can be added by modifying the menu template in `public/electron.js`.

## 🔧 Development

### Project Structure
```
anora-editor/
├── public/
│   ├── electron.js          # Main Electron process
│   ├── preload.js           # Secure preload script
│   ├── index.html           # HTML entry point
│   └── manifest.json        # Web app manifest
├── src/
│   ├── App.js               # Main React component
│   ├── App.css              # Component styles
│   ├── index.js             # React entry point
│   └── index.css            # Global styles
├── package.json             # Dependencies and scripts
└── README.md                # This file
```

### Adding Features
1. **New Menu Items**: Add to the menu template in `electron.js`
2. **New Editor Features**: Extend the Monaco editor options
3. **New File Types**: Update language detection and syntax highlighting
4. **UI Components**: Add new React components to the main App

### Building for Distribution
```bash
# Build React app
npm run build

# Package for distribution
npm run electron-pack
```

## 🌟 Professional Features

### Security
- **Context isolation** enabled by default
- **Node integration** disabled for security
- **Remote module** disabled
- **Secure preload script** for IPC communication

### Cross-Platform
- **Windows**: NSIS installer with file associations
- **macOS**: DMG package with proper signing
- **Linux**: AppImage with desktop integration

### Session Persistence
- **Autosaves** every 500ms after changes
- **Restores** all open tabs on startup
- **Recent files** tracking (last 10)
- **Window bounds** and preferences saved

## 🐛 Troubleshooting

### Common Issues

**Editor won't start**
- Ensure all dependencies are installed: `npm install`
- Check Node.js version compatibility
- Verify Electron installation

**Syntax highlighting not working**
- Check Monaco editor installation
- Verify language detection in `getLanguageFromPath`
- Ensure file extensions are supported

**File operations failing**
- Check file permissions
- Verify file paths are correct
- Ensure Electron has proper file access

**Performance issues**
- Reduce syntax highlighting complexity
- Implement virtual scrolling for large files
- Optimize editor options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Monaco Editor** for the powerful text editing capabilities
- **Electron** for cross-platform desktop app framework
- **React** for the modern UI framework
- **Unity Technologies** for inspiring the focus on game development

## 🚀 Roadmap

- [ ] **Advanced C# IntelliSense** with Unity API support
- [ ] **Integrated Debugger** for Unity scripts
- [ ] **Git Integration** with visual diff tools
- [ ] **Plugin System** for extensibility
- [ ] **Multi-monitor Support** for large setups
- [ ] **Cloud Sync** for settings and snippets
- [ ] **Team Collaboration** features
- [ ] **Performance Profiling** tools

---

**Built with ❤️ for the Unity development community**

*Anora Editor - Where code meets creativity*

