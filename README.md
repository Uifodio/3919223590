# Unity Code Editor

A lightweight, professional code editor with integrated file manager designed specifically for Unity development. This replaces the bulky Visual Studio with a fast, modern alternative.

## Features

- **File Manager**: Windows Explorer-like file tree with drag & drop
- **Code Editor**: Professional Monaco Editor (same as VS Code) with syntax highlighting
- **Unity Integration**: Optimized for C# and Unity development
- **Modern UI**: Dark theme with professional styling
- **Multiple Tabs**: Edit multiple files simultaneously
- **Context Menus**: Right-click file operations
- **Keyboard Shortcuts**: Standard editor shortcuts (Ctrl+S, Ctrl+O, etc.)

## System Requirements

- Windows 11 (recommended) or Windows 10
- Node.js 16+ (you already have this)
- Git (you already have this)
- At least 1GB free disk space

## Quick Start

### Step 1: Run Diagnostic
First, let's check if your system is ready:

```bash
node diagnostic.js
```

This will check all your dependencies and system configuration. If everything is green, you're ready to proceed!

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Test the App
```bash
npm start
```

This will open the Unity Code Editor in development mode. You should see:
- A file explorer on the left
- A code editor area on the right
- Professional dark theme
- Your current directory files listed

### Step 4: Build the Executable
```bash
npm run build-win
```

This will create a Windows executable in the `dist` folder. The process may take a few minutes.

## Usage

### Opening Files
- Click on any file in the file explorer to open it
- Use File → Open File (Ctrl+O) to open files from anywhere
- Drag and drop files from Windows Explorer

### Editing
- Syntax highlighting for C#, JavaScript, Python, HTML, CSS, and more
- Auto-completion and IntelliSense
- Line numbers and error highlighting
- Multiple tabs for different files

### File Operations
- Right-click files for context menu (Open, Rename, Delete, Copy Path)
- Create new files and folders with the toolbar buttons
- Save files with Ctrl+S or the Save button

### Unity Integration
- Perfect for C# scripts
- Recognizes Unity project structure
- Optimized for Unity development workflow

## Troubleshooting

### If the diagnostic shows errors:
1. **Node.js not found**: Download and install Node.js from https://nodejs.org/
2. **Permission errors**: Run Command Prompt as Administrator
3. **Disk space**: Free up at least 1GB of space

### If the app doesn't start:
1. Check the console for error messages
2. Make sure all dependencies are installed: `npm install`
3. Try running in development mode: `npm run dev`

### If the build fails:
1. Make sure you have enough disk space
2. Try running as Administrator
3. Check that electron-builder is installed: `npm install -g electron-builder`

## Development

### Project Structure
```
unity-code-editor/
├── main.js              # Main Electron process
├── renderer.js          # Frontend logic
├── index.html           # Main interface
├── styles.css           # Styling
├── diagnostic.js        # System diagnostic
├── package.json         # Dependencies and scripts
└── README.md           # This file
```

### Adding Features
The app is built with:
- **Electron**: Desktop app framework
- **Monaco Editor**: Professional code editor
- **HTML/CSS/JavaScript**: Frontend interface

### Customization
- Edit `styles.css` to change the appearance
- Modify `renderer.js` to add new features
- Update `main.js` for system-level changes

## Support

If you encounter any issues:
1. Run the diagnostic: `node diagnostic.js`
2. Check the console for error messages
3. Make sure all dependencies are up to date

## License

MIT License - Feel free to modify and distribute!

---

**Built with ❤️ for Unity developers who are tired of Visual Studio's bulkiness!**