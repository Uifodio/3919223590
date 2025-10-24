# Modern Server Administrator

A professional, bulletproof server management tool with GitHub-themed dark UI, full PHP support, file management, and standalone EXE build capability.

## 🚀 Features

### Server Management
- **Multiple Servers**: Run up to 10 servers simultaneously
- **Port Assignment**: Custom ports with conflict detection
- **Server Types**: HTTP, PHP, Node.js support
- **Real-time Status**: Live monitoring with status badges
- **One-click Control**: Start/stop servers with professional buttons

### Professional Logging
- **Real-time Logs**: Detailed logs in sleek modal windows
- **Log Export**: Copy logs to clipboard
- **Error Highlighting**: Color-coded log messages
- **Professional Display**: Monospace font with timestamps

### File Management
- **File Browser**: Browse and manage website files
- **Upload Support**: Drag-and-drop file uploads
- **Video Support**: Special handling for video files
- **File Operations**: Delete, view, and organize files
- **Size & Date Info**: Display file sizes and modification dates

### GitHub-Themed UI
- **Dark Theme**: Professional GitHub-inspired dark interface
- **Modern Design**: Beautiful cards with glassmorphism effects
- **Responsive Layout**: Works perfectly on all screen sizes
- **Smooth Animations**: Subtle hover effects and transitions

### PHP Support
- **Auto-Detection**: Automatically detects PHP installation
- **Auto-Installation**: Windows auto-installer for PHP
- **Full Support**: Complete PHP built-in server implementation
- **Error Handling**: Proper PHP error logging and display

### Standalone EXE
- **Windows EXE**: Build standalone executable
- **Auto-Installer**: Professional installation script
- **No Dependencies**: Runs without Python installation
- **Portable**: Can run from any location

## 🛠️ Installation

### Quick Start (Windows)
1. **Download** the application files
2. **Run** `start.bat` to start the application
3. **Open** your browser to `http://localhost:5000`

### Manual Installation
1. **Install Python 3.7+** from [python.org](https://python.org)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python web_server_admin.py
   ```

### Build Standalone EXE (Windows)
1. **Install build dependencies**:
   ```bash
   pip install pyinstaller
   ```
2. **Build EXE**:
   ```bash
   python build_exe.py
   ```
3. **Install application**:
   ```bash
   install.bat
   ```

## 🎯 Usage

### Starting a Server
1. **Select Folder**: Click "Browse" to select your website folder
2. **Set Port**: Enter port number (1000-65535)
3. **Choose Type**: Select HTTP, PHP, or Node.js
4. **Add Server**: Click "Add Server"

### Managing Servers
- **View Logs**: Double-click any server to view detailed logs
- **Open Browser**: Click "Open Browser" to view your website
- **Stop Server**: Click "Stop Server" to stop the server

### File Management
- **Upload Files**: Use upload buttons to add files
- **Upload Videos**: Special video upload with format validation
- **Delete Files**: Select and delete unwanted files
- **Browse Files**: View all files in your website folder

### PHP Support
- **Auto-Detection**: Application automatically detects PHP
- **Auto-Installation**: Use "Install PHP" button for Windows
- **Full Support**: Complete PHP server functionality

## 🔧 System Requirements

- **Python 3.7+** (for source version)
- **Operating System**: Windows 10/11, macOS, or Linux
- **Memory**: 4GB RAM minimum
- **Disk Space**: 100MB for application + space for websites
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

## 📁 Project Structure

```
Modern Server Administrator/
├── web_server_admin.py          # Main Flask application
├── templates/index.html         # GitHub-themed UI
├── static/css/style.css         # Professional styling
├── static/js/app.js            # Interactive functionality
├── requirements.txt            # Python dependencies
├── build_exe.py               # EXE build script
├── start.bat                  # Windows startup script
├── install.bat                # Windows installer
├── demo.py                    # Demo setup script
├── test_complete.py           # Comprehensive test suite
├── demo_website/              # Sample website files
│   ├── index.html            # HTML demo
│   ├── index.php             # PHP demo
│   ├── style.css             # Modern CSS
│   └── script.js             # Interactive JavaScript
└── uploads/                   # File upload directory
```

## 🎨 UI Features

### GitHub Theme
- **Dark Background**: Professional dark interface
- **Blue Accents**: GitHub-inspired color scheme
- **Modern Typography**: Inter font family
- **Smooth Animations**: Subtle hover effects

### Professional Design
- **Card Layout**: Beautiful server cards
- **Status Indicators**: Visual feedback for all operations
- **Responsive Design**: Perfect on all screen sizes
- **Intuitive Controls**: Easy-to-use interface

## 🔒 Security Features

- **Port Validation**: Prevents port conflicts
- **File Type Validation**: Secure file uploads
- **Error Handling**: Comprehensive error management
- **Process Management**: Safe server process handling

## 🚀 Advanced Features

### Auto-Installation
- **PHP Auto-Install**: Windows PHP auto-installer
- **Dependency Management**: Automatic dependency checking
- **System Detection**: Automatic system requirement detection

### Professional Logging
- **Real-time Monitoring**: Live log updates
- **Error Tracking**: Comprehensive error logging
- **Export Functionality**: Copy logs to clipboard

### File Management
- **Multiple Upload**: Support for multiple file uploads
- **Video Support**: Special video file handling
- **File Organization**: Easy file management

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_complete.py
```

Tests include:
- Import validation
- File structure verification
- Web application functionality
- PHP detection
- File operations
- Demo files validation
- Server startup testing

## 📊 Performance

- **Lightweight**: Minimal memory usage
- **Fast**: Quick server startup and response
- **Efficient**: Optimized for performance
- **Scalable**: Supports multiple servers

## 🎯 Target Users

- **Web Developers**: Easy local server management
- **Students**: Learning web development
- **Designers**: Quick website testing
- **Professionals**: Efficient development workflows

## 🔧 Troubleshooting

### Common Issues

**Application Won't Start**
- Verify Python 3.7+ is installed
- Check if all dependencies are installed
- Run `python test_complete.py` to diagnose issues

**PHP Servers Won't Work**
- Use "Install PHP" button in the application
- Or install PHP manually from [php.net](https://php.net)

**Port Already in Use**
- Choose a different port number
- Check if another application is using the port

**File Upload Fails**
- Check folder permissions
- Verify file type is allowed
- Ensure sufficient disk space

### Getting Help

1. **Check System Info**: Click info button in the application
2. **Review Logs**: Check server logs for error messages
3. **Run Tests**: Use the test suite to diagnose issues
4. **Check Dependencies**: Ensure all requirements are installed

## 📈 Future Enhancements

- **Database Integration**: Support for database management
- **SSL Certificate Management**: Easy HTTPS setup
- **Team Collaboration**: Multi-user server management
- **Plugin System**: Extensible architecture
- **Mobile App**: Companion mobile application
- **Cloud Integration**: Deploy to cloud platforms

## 🏆 Success Metrics

- ✅ **All Core Features**: Server management, file operations, logging
- ✅ **Professional UI**: GitHub-themed dark interface
- ✅ **Cross-platform**: Works on Windows, Mac, Linux
- ✅ **Easy Installation**: One-command setup
- ✅ **Comprehensive Testing**: Full test suite
- ✅ **Standalone EXE**: Windows executable build
- ✅ **PHP Support**: Full PHP server support
- ✅ **File Management**: Complete file operations

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Modern Server Administrator** - Professional server management with a GitHub-themed interface that makes web development easier and more enjoyable.