# 🚀 Windows File Manager Pro

A professional, modern file manager for Windows built with **Electron**, **React**, **TypeScript**, and **Vite**. This application provides a powerful, intuitive interface for file management with advanced features like built-in code editing, ZIP handling, and intelligent search.

## ✨ Features

### 🔧 Core File Operations
- **File Explorer Tree View** - Hierarchical folder navigation with expandable trees
- **Multi-window Support** - Open multiple independent instances
- **Drag & Drop** - Seamless file operations between windows and external applications
- **Copy, Rename, Delete, Duplicate** - Full file operations with progress tracking
- **Multi-file Selection** - Shift/Ctrl select and apply actions to multiple files
- **Safe Operations** - Files sent to system trash with undo capability

### 📝 Built-in Code Editor
- **Monaco Editor Integration** - Professional-grade code editing experience
- **Syntax Highlighting** - Support for 50+ programming languages
- **Auto-completion** - Intelligent code suggestions and IntelliSense
- **Multiple Tabs** - Edit multiple files simultaneously
- **Auto-save** - Automatic file saving with configurable intervals
- **Find & Replace** - Advanced search with regex support

### 🔍 Advanced Search & Navigation
- **Fast File Search** - Real-time search across file names and content
- **Content Search** - Search inside text files with preview
- **Advanced Filters** - Filter by size, date, type, and attributes
- **Search History** - Save and reuse search queries
- **Export Results** - Export search results to CSV or text format

### 📦 Archive & ZIP Support
- **ZIP as Folders** - Browse ZIP files as regular directories
- **Edit Inside Archives** - Modify files within ZIP archives
- **Auto-backup** - Automatic backup before editing archived files
- **Batch Operations** - Extract, compress, and manage multiple archives

### 🎨 Modern UI/UX
- **Dark/Light Themes** - Beautiful, customizable themes
- **Responsive Design** - Adapts to different screen sizes
- **Split Views** - Resizable panels for efficient workflow
- **Keyboard Shortcuts** - Full keyboard navigation support
- **Context Menus** - Right-click context menus for quick actions

### ⚙️ Configuration & Customization
- **Settings Panel** - Comprehensive configuration options
- **Theme Customization** - Create and share custom themes
- **Keyboard Shortcuts** - Customize all keyboard shortcuts
- **File Associations** - Configure default applications for file types
- **Plugin System** - Extensible architecture for custom features

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18.0.0 or higher
- **npm** 9.0.0 or higher
- **Windows 10/11** (primary target)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/windows-file-manager-pro.git
   cd windows-file-manager-pro
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run electron:dev
   ```

4. **Build for production**
   ```bash
   npm run electron:build
   ```

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start Vite dev server
- `npm run build` - Build React app for production
- `npm run electron:dev` - Start Electron in development mode
- `npm run electron:build` - Build Electron app for distribution
- `npm run electron:preview` - Preview built Electron app
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues

### Project Structure

```
windows-file-manager-pro/
├── electron/                 # Electron main process
│   ├── main.ts              # Main process entry point
│   └── preload.ts           # Preload script
├── src/                     # React application
│   ├── components/          # React components
│   ├── hooks/               # Custom React hooks
│   ├── stores/              # State management (Zustand)
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── App.tsx              # Main App component
│   └── main.tsx             # React entry point
├── dist/                    # Built React app
├── dist-electron/           # Built Electron app
├── package.json             # Dependencies and scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

### Technology Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Desktop**: Electron 28
- **Build Tool**: Vite 5
- **State Management**: Zustand
- **Code Editor**: Monaco Editor
- **Package Manager**: npm
- **Linting**: ESLint + TypeScript ESLint

## 📱 Usage

### Basic File Operations
1. **Navigate** - Use the tree view to browse folders
2. **Select Files** - Click to select, Ctrl+Click for multiple selection
3. **Copy/Move** - Drag and drop or use context menus
4. **Delete** - Select files and press Delete key or use context menu

### Code Editing
1. **Open File** - Double-click any text file or use File > Open
2. **Edit** - Use the built-in Monaco editor with full IDE features
3. **Save** - Ctrl+S or File > Save
4. **Multiple Tabs** - Open multiple files for simultaneous editing

### Advanced Search
1. **Search Panel** - Use the search icon in the toolbar
2. **File Search** - Search by name, extension, or content
3. **Filters** - Apply size, date, and type filters
4. **Export** - Save search results for later use

## 🎯 Roadmap

### Version 1.1
- [ ] File preview for images and documents
- [ ] FTP/SFTP support
- [ ] Cloud storage integration (OneDrive, Google Drive)
- [ ] Advanced file synchronization

### Version 1.2
- [ ] Plugin marketplace
- [ ] Custom themes and icons
- [ ] Advanced file comparison tools
- [ ] Batch file processing

### Version 1.3
- [ ] Multi-language support
- [ ] Accessibility improvements
- [ ] Performance optimizations
- [ ] Advanced scripting support

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

- **Electron** team for the amazing desktop framework
- **React** team for the powerful UI library
- **Monaco Editor** team for the professional code editor
- **Tailwind CSS** team for the utility-first CSS framework
- **Vite** team for the fast build tool

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/windows-file-manager-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/windows-file-manager-pro/discussions)
- **Email**: support@windowsfilemanagerpro.com

---

**Built with ❤️ for Windows developers and power users**

*Windows File Manager Pro - Professional file management reimagined*