# Modern Server Administrator - Installation Guide

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the demo setup (creates sample files and startup script)
python3 demo.py

# Start the application
./start.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Start the application
python3 web_server_admin.py
```

## System Requirements

- **Python 3.7+** (Required)
- **Operating System**: Windows 10/11, macOS, or Linux
- **Memory**: 4GB RAM minimum
- **Disk Space**: 50MB for application + space for your websites
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

## Detailed Installation

### 1. Install Python
- **Windows**: Download from [python.org](https://python.org) or use Microsoft Store
- **macOS**: Use Homebrew: `brew install python3`
- **Linux**: Use package manager: `sudo apt install python3 python3-pip`

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

Required packages:
- `flask` - Web framework
- `psutil` - System information
- `Pillow` - Image processing

### 3. Run the Application
```bash
python3 web_server_admin.py
```

The application will start on `http://localhost:5000`

## Features Overview

### 🚀 Server Management
- **Multiple Servers**: Run up to 10 servers simultaneously
- **Port Assignment**: Custom ports for each server
- **Server Types**: HTTP, HTTPS, PHP, Node.js support
- **Real-time Status**: Live monitoring of all servers

### 📊 Professional Logging
- **Real-time Logs**: View detailed logs for each server
- **Log Export**: Copy logs to clipboard
- **Error Highlighting**: Easy identification of issues

### 📁 File Management
- **File Browser**: Browse and manage website files
- **Upload Support**: Drag-and-drop file uploads
- **Video Support**: Special handling for video files
- **File Operations**: Delete, view, and organize files

### 🎨 Modern Interface
- **Dark Theme**: Professional dark UI design
- **Responsive Layout**: Works on all screen sizes
- **Intuitive Controls**: Easy-to-use interface

## Usage Instructions

### Starting Your First Server

1. **Open the Application**
   - Navigate to `http://localhost:5000` in your browser

2. **Select a Website Folder**
   - Click "Browse" to select your website folder
   - Or enter the path manually

3. **Configure Server Settings**
   - Choose a port number (default: 8000)
   - Select server type (HTTP, PHP, etc.)

4. **Start the Server**
   - Click "Add Server" to start
   - Server will appear in the "Active Servers" list

5. **View Your Website**
   - Click "Open" next to your server
   - Or visit `http://localhost:[port]` directly

### Managing Multiple Servers

- **Add More Servers**: Use different ports for each server
- **View Logs**: Double-click any server to view detailed logs
- **Stop Servers**: Use the stop button in the log viewer
- **Monitor Status**: Real-time status updates

### File Management

- **Upload Files**: Use the upload buttons to add files
- **Upload Videos**: Special video upload with format validation
- **Delete Files**: Select and delete unwanted files
- **Browse Files**: View all files in your website folder

## Troubleshooting

### Common Issues

**Port Already in Use**
- Choose a different port number
- Check if another application is using the port
- Use ports 8000-8099 for development

**Server Won't Start**
- Verify the folder path is correct
- Check if Python/PHP is installed
- Ensure the port is available
- Check the logs for error messages

**File Upload Fails**
- Check folder permissions
- Verify file size limits
- Ensure sufficient disk space
- Check file type restrictions

**Application Won't Start**
- Verify Python 3.7+ is installed
- Check if all dependencies are installed
- Run `python3 test_app.py` to diagnose issues

### Getting Help

1. **Check System Info**: Click "System Info" button
2. **Review Logs**: Check server logs for error messages
3. **Verify Installation**: Run the test script
4. **Check Permissions**: Ensure proper folder permissions

## Advanced Configuration

### Custom Server Types

The application supports multiple server types:

- **HTTP**: Python's built-in HTTP server
- **HTTPS**: Secure HTTP server (requires SSL certificates)
- **PHP**: PHP built-in development server
- **Node.js**: Node.js HTTP server (requires Node.js)

### Port Management

- **Default Ports**: 8000-8099 recommended for development
- **Port Conflicts**: Application will warn about port conflicts
- **Multiple Servers**: Each server needs a unique port

### File Upload Limits

- **Supported Types**: All common web file types
- **Video Support**: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- **Size Limits**: No artificial limits (limited by available disk space)

## Security Features

- **Port Validation**: Prevents port conflicts
- **File Type Validation**: Secure file uploads
- **Error Handling**: Comprehensive error management
- **Process Management**: Safe server process handling

## Performance Tips

- **Memory Usage**: Each server uses minimal memory
- **CPU Usage**: Servers are lightweight and efficient
- **Disk Space**: Monitor available disk space
- **Network**: Servers only bind to localhost by default

## Uninstallation

To remove the application:

1. **Stop All Servers**: Use the application to stop all running servers
2. **Delete Files**: Remove the application folder
3. **Clean Dependencies**: `pip3 uninstall flask psutil Pillow`

## Support

For issues and questions:

1. Check this documentation
2. Run the test script: `python3 test_app.py`
3. Review the system information panel
4. Check server logs for error messages

---

**Modern Server Administrator** - Making web development easier with a professional, modern interface.