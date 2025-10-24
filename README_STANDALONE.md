# Professional Server Administrator - Standalone Setup

A complete, standalone server management solution with GitHub-inspired professional UI, built with Flask, PHP, and Node.js support.

## 🚀 Quick Start

### One-Command Setup
```bash
./start_standalone.sh
```

This will:
- ✅ Check all dependencies (Python, PHP, Node.js)
- ✅ Install missing packages automatically
- ✅ Create necessary directories
- ✅ Start the professional web interface
- ✅ Display access URLs and system information

## 🌐 Access URLs

Once started, access the application at:
- **Local**: http://127.0.0.1:5000
- **Network**: http://[YOUR_IP]:5000

## ✨ Features

### 🎨 Professional GitHub-Inspired UI
- **Dark Theme**: Beautiful dark interface inspired by GitHub
- **Modern Design**: Clean, professional layout with smooth animations
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **Interactive**: Drag-and-drop file uploads, real-time updates

### 🖥️ Multi-Server Management
- **HTTP Servers**: Python's built-in HTTP server
- **PHP Servers**: Full PHP 8.4+ support with all extensions
- **Node.js Servers**: Custom Node.js static file servers
- **Port Management**: Automatic port detection and conflict resolution
- **Real-time Monitoring**: Live status updates and health checks

### 📁 File Management
- **Upload Support**: Drag-and-drop ZIP files and folders
- **File Browser**: Browse and manage website files
- **Auto-Import**: Automatically import and register new projects
- **File Operations**: Delete, view, and organize files

### 📊 Advanced Features
- **Real-time Logs**: Color-coded server logs with timestamps
- **System Information**: CPU, memory, and system details
- **Auto-Refresh**: Background monitoring and updates
- **Export Logs**: Copy logs to clipboard
- **Process Management**: Safe server process handling

## 🛠️ System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+, macOS 10.15+, Windows 10+
- **Python**: 3.7+ (included in most systems)
- **Memory**: 2GB RAM
- **Disk**: 100MB for application + space for websites
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

### Included Dependencies
- ✅ **Python 3.7+** with Flask, psutil, Pillow
- ✅ **PHP 8.4+** with all common extensions
- ✅ **Node.js 22+** for JavaScript server support
- ✅ **All required Python packages** automatically installed

## 📁 Project Structure

```
Professional Server Administrator/
├── web_server_admin.py          # Main Flask application
├── start_standalone.sh          # One-command startup script
├── requirements.txt             # Python dependencies
├── templates/
│   └── index.html              # GitHub-inspired UI template
├── static/
│   ├── css/style.css           # Professional styling
│   └── js/app.js               # Interactive functionality
├── sites/                      # Website storage directory
│   └── demo-website/          # Demo website (HTML + PHP)
├── logs/                       # Server logs directory
├── uploads/                    # File upload directory
└── README_STANDALONE.md        # This file
```

## 🎯 Demo Websites

The application includes demo websites to showcase functionality:

### HTML Demo
- **URL**: http://localhost:8000 (when running)
- **Features**: Modern responsive design, GitHub-inspired styling
- **Purpose**: Demonstrates HTTP server capabilities

### PHP Demo
- **URL**: http://localhost:8002 (when running)
- **Features**: PHP system information, memory usage, extensions
- **Purpose**: Demonstrates PHP server integration

## 🔧 Usage Guide

### Starting Servers
1. **Open the web interface** at http://localhost:5000
2. **Click "Add Server"** in the top-right corner
3. **Select folder** or enter path to your website
4. **Choose server type** (HTTP, PHP, or Node.js)
5. **Set port** (auto-detected if available)
6. **Click "Add Server"** to start

### Managing Servers
- **Start/Stop**: Click the appropriate button on each server card
- **View Logs**: Click "Logs" to see real-time server output
- **Open Browser**: Click "Open" to view your website
- **Delete**: Click "Delete" to remove a server

### File Management
- **Upload ZIP**: Use "Upload ZIP" to upload compressed websites
- **Upload Folder**: Use "Upload Folder" for multiple files
- **Auto-Register**: Automatically register uploaded projects as servers
- **Auto-Start**: Optionally start servers immediately after upload

### System Information
- **System Info**: View OS, Python, PHP, Node.js versions
- **Check PHP**: Verify PHP installation and extensions
- **Server Stats**: See running/stopped server counts
- **Memory Usage**: Monitor system resources

## 🚨 Troubleshooting

### Common Issues

**Application Won't Start**
```bash
# Check Python installation
python3 --version

# Install dependencies manually
pip3 install -r requirements.txt --user

# Check file permissions
chmod +x start_standalone.sh
```

**PHP Servers Won't Work**
```bash
# Check PHP installation
php --version

# Install PHP (Ubuntu/Debian)
sudo apt update && sudo apt install php php-cli

# Install PHP (macOS)
brew install php

# Install PHP (Windows)
# Download from https://php.net
```

**Port Already in Use**
- Choose a different port number (1000-65535)
- Check if another application is using the port
- Use the auto-detection feature to find free ports

**File Upload Fails**
- Check folder permissions: `chmod 755 sites uploads`
- Verify file type is allowed
- Ensure sufficient disk space

### Getting Help

1. **Check System Info**: Click the info button in the web interface
2. **Review Logs**: Check server logs for error messages
3. **Run Diagnostics**: Use the built-in system information
4. **Check Dependencies**: Verify all requirements are installed

## 🔒 Security Features

- **Port Validation**: Prevents port conflicts and invalid ranges
- **File Type Validation**: Secure file upload with type checking
- **Process Isolation**: Safe server process management
- **Error Handling**: Comprehensive error management and logging
- **Input Sanitization**: All user inputs are properly sanitized

## 📊 Performance

- **Lightweight**: Minimal memory usage (~50MB base)
- **Fast**: Quick server startup and response times
- **Efficient**: Optimized for performance and scalability
- **Scalable**: Supports multiple servers simultaneously
- **Background Processing**: Non-blocking operations

## 🎨 UI Features

### GitHub-Inspired Design
- **Color Scheme**: Professional dark theme with blue accents
- **Typography**: Inter font family for modern readability
- **Layout**: Clean, organized card-based interface
- **Animations**: Subtle hover effects and smooth transitions

### Professional Elements
- **Status Indicators**: Visual feedback for all operations
- **Loading States**: Professional loading animations
- **Toast Notifications**: Non-intrusive status messages
- **Modal Dialogs**: Clean, focused interaction patterns

### Responsive Design
- **Mobile-First**: Optimized for all screen sizes
- **Touch-Friendly**: Large buttons and touch targets
- **Adaptive Layout**: Flexible grid system
- **Cross-Platform**: Consistent experience across devices

## 🚀 Advanced Usage

### Custom Server Types
The application supports three server types:

1. **HTTP Server** (Python)
   - Built-in Python HTTP server
   - Static file serving
   - Cross-platform compatibility

2. **PHP Server**
   - PHP built-in development server
   - Full PHP functionality
   - All PHP extensions available

3. **Node.js Server**
   - Custom Node.js static server
   - MIME type detection
   - Error handling

### API Endpoints
The application provides RESTful API endpoints:

- `GET /api/servers` - List all servers
- `POST /api/add_server` - Add new server
- `POST /api/start_server` - Start server
- `POST /api/stop_server` - Stop server
- `POST /api/delete_server` - Delete server
- `GET /api/server_logs/<name>` - Get server logs
- `POST /api/upload_zip` - Upload ZIP file
- `POST /api/upload_folder` - Upload folder
- `GET /api/system_info` - Get system information

## 📈 Future Enhancements

- **Database Integration**: Support for database management
- **SSL Certificate Management**: Easy HTTPS setup
- **Team Collaboration**: Multi-user server management
- **Plugin System**: Extensible architecture
- **Mobile App**: Companion mobile application
- **Cloud Integration**: Deploy to cloud platforms

## 🏆 Success Metrics

- ✅ **Complete Standalone Setup**: No external dependencies required
- ✅ **Professional UI**: GitHub-inspired modern interface
- ✅ **Multi-Server Support**: HTTP, PHP, and Node.js servers
- ✅ **Real-time Monitoring**: Live logs and status updates
- ✅ **File Management**: Upload, organize, and manage files
- ✅ **Cross-Platform**: Works on Windows, Mac, and Linux
- ✅ **Easy Installation**: One-command setup
- ✅ **Comprehensive Testing**: Full functionality verification

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Professional Server Administrator** - Making web development easier and more enjoyable with a beautiful, professional interface.

## 🎉 Getting Started

1. **Clone or download** this repository
2. **Run** `./start_standalone.sh`
3. **Open** http://localhost:5000 in your browser
4. **Start managing** your web servers!

Enjoy your new professional server management experience! 🚀