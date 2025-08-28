# Nexus Editor

A professional, high-performance code editor designed specifically for Unity development, built with React + Electron.

![Nexus Editor](public/icon.png)

## ✨ Features

### 🎨 Visual Design
- **Dark Theme**: Professional dark theme with VS Code-inspired colors
- **Syntax Highlighting**: Blue keywords, Orange strings, Green comments, Yellow functions
- **Responsive UI**: Clean, modern interface that adapts to different screen sizes

### 🪟 Window Layout
- **Default Size**: 800x600 with minimum 400x300
- **Professional Layout**: Menu bar, toolbar, tabbed editor, status bar
- **Always on Top**: Pin button keeps editor floating above other windows
- **Fullscreen Mode**: Maximize for immersive coding experience

### 📋 Menu System
- **File**: New, Open, Save, Save As, Open Recent, Exit
- **Edit**: Undo, Redo, Cut, Copy, Paste, Select All, Find, Replace
- **View**: Always on Top, Fullscreen
- **Window**: New Tab, Close Tab, Close Others, Reopen Closed Tab
- **Navigate**: Go to Line

### 🔧 Toolbar
- **Quick Actions**: New, Open, Save, Find, Replace, Pin, Full
- **Visual Feedback**: Active states with color changes
- **Professional Icons**: Clear, intuitive button design

### 📝 Text Editor
- **Line Numbers**: 4-digit format with synchronized scrolling
- **Syntax Highlighting**: Support for Python, C#, JavaScript, HTML, CSS, JSON, C/C++
- **Current Line Highlighting**: Darker blue background for active line
- **Auto-indent**: Preserves leading whitespace on Enter
- **Auto-close**: Automatically closes brackets, quotes, and braces

### 🔍 Search & Replace
- **Find Panel**: Hidden by default, shows when activated
- **Replace Mode**: Full find and replace functionality
- **Options**: Case sensitive, whole word, regex support
- **Navigation**: F3 for next, Shift+F3 for previous

### 📑 Tab Management
- **Multiple Tabs**: Efficient tab switching between files
- **Modified Indicators**: Asterisk (*) shows unsaved changes
- **Tab Operations**: Close, close others, reopen closed tabs
- **Drag & Drop**: Drop files to open them in new tabs

### ⌨️ Keyboard Shortcuts
- **File Operations**: Ctrl+N (New), Ctrl+O (Open), Ctrl+S (Save)
- **Tab Management**: Ctrl+T (New Tab), Ctrl+W (Close Tab)
- **Search**: Ctrl+F (Find), Ctrl+H (Replace), F3 (Next)
- **Navigation**: Ctrl+G (Go to Line), Ctrl+Q (Exit)

### 💾 Session Persistence
- **Auto-save**: Saves session every 500ms after changes
- **Session Restoration**: Restores all open tabs on startup
- **Recent Files**: Tracks last 10 opened files
- **Storage**: Saves to `~/nexus_editor_session.json`

### 🔗 File Associations
- **Linux**: `install_linux_default_editor.sh` creates .desktop entry
- **Windows**: `install_windows_default_editor.ps1` registers file types
- **Supported Formats**: .py, .cs, .js, .html, .css, .json, .txt, .c, .cpp, .h
- **Double-click**: Open files directly from file explorer

### 🚀 Performance Features
- **Fast Rendering**: Optimized for smooth editing experience
- **Efficient Syntax Highlighting**: Only highlights visible lines
- **Memory Management**: Efficient tab and session handling
- **Responsive UI**: Smooth animations and transitions

### 🎯 Unity Integration
- **C# Support**: Full syntax highlighting for Unity scripts
- **Fast Tab Switching**: Quick navigation between Unity scripts
- **Always-on-top**: Perfect for overlay editing while Unity is running
- **Compact Design**: Fits alongside Unity interface

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ 
- npm 8+
- Electron 28+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nexus-editor
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Development mode**
   ```bash
   npm run electron-dev
   ```

4. **Build for production**
   ```bash
   npm run dist
   ```

### Development Commands

- `npm start` - Start React development server
- `npm run build` - Build React app for production
- `npm run electron` - Run Electron app
- `npm run electron-dev` - Run in development mode
- `npm run dist` - Build and package the application

## 🏗️ Project Structure

```
nexus-editor/
├── public/                 # Electron main process files
│   ├── electron.js        # Main Electron process
│   ├── preload.js         # Preload script for IPC
│   └── index.html         # Main HTML file
├── src/                   # React application source
│   ├── components/        # React components
│   │   ├── MenuBar.js     # Main menu bar
│   │   ├── Toolbar.js     # Toolbar with buttons
│   │   ├── TabManager.js  # Tab management
│   │   ├── CodeEditor.js  # Code editor component
│   │   ├── SearchPanel.js # Search and replace
│   │   └── StatusBar.js   # Status bar
│   ├── hooks/             # Custom React hooks
│   │   ├── useFileManager.js    # File operations
│   │   ├── useSessionManager.js # Session management
│   │   └── useKeyboardShortcuts.js # Keyboard handling
│   ├── styles/            # CSS stylesheets
│   ├── App.js             # Main application component
│   └── index.js           # React entry point
├── install_linux_default_editor.sh    # Linux installation
├── install_windows_default_editor.ps1 # Windows installation
└── package.json           # Project configuration
```

## 🎨 Customization

### Themes
The editor uses a VS Code Dark+ inspired theme with:
- Background: `#1e1e1e`
- Text: `#d4d4d4`
- Keywords: `#569cd6` (Blue)
- Strings: `#ce9178` (Orange)
- Comments: `#6a9955` (Green)
- Functions: `#dcdcaa` (Yellow)

### Syntax Highlighting
Supports multiple programming languages:
- C# (.cs)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Python (.py)
- HTML (.html, .htm)
- CSS (.css)
- JSON (.json)
- C/C++ (.c, .cpp, .h, .hpp)
- Text (.txt)

## 🔧 Configuration

### Session Settings
- Auto-save interval: 500ms
- Maximum recent files: 10
- Session storage: `~/nexus_editor_session.json`

### Window Settings
- Default size: 800x600
- Minimum size: 400x300
- Always on top: Configurable via menu or toolbar

## 📱 Platform Support

### Linux
- AppImage packaging
- .desktop file integration
- MIME type associations
- File type registration

### Windows
- NSIS installer
- File type associations
- Start Menu integration
- Registry integration

### macOS
- DMG packaging
- Native macOS integration
- File type associations

## 🐛 Troubleshooting

### Common Issues

1. **App won't start**
   - Check Node.js version (requires 16+)
   - Verify all dependencies are installed
   - Check console for error messages

2. **File associations not working**
   - Run installation script as Administrator (Windows)
   - Ensure .desktop file is executable (Linux)
   - Restart file explorer/desktop

3. **Syntax highlighting issues**
   - Verify language detection is working
   - Check file extensions are supported
   - Restart the application

### Debug Mode
Enable debug mode by running:
```bash
npm run electron-dev
```

This will open DevTools and show console output.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Guidelines
- Follow React best practices
- Use functional components with hooks
- Maintain consistent code style
- Add comments for complex logic
- Test on multiple platforms

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **VS Code**: Inspiration for the color scheme and UI design
- **Electron**: Cross-platform desktop app framework
- **React**: User interface library
- **Pygments**: Syntax highlighting inspiration

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Nexus Editor** - Professional code editing for Unity development 🚀

