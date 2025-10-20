# Modern Server Administrator

A professional, modern web server management tool with a sleek dark theme interface. This application allows you to easily manage multiple local web servers without using the terminal.

## Features

### 🚀 Server Management
- **Multiple Server Support**: Run up to 10 servers simultaneously
- **Port Assignment**: Assign custom ports to each server
- **Server Types**: Support for HTTP, HTTPS, PHP, and Node.js servers
- **Real-time Status**: Live status monitoring for all servers
- **One-click Start/Stop**: Easy server control with modern UI

### 📊 Professional Logging
- **Real-time Logs**: View detailed logs for each server
- **Log Export**: Copy logs to clipboard for sharing
- **Professional Display**: Clean, formatted log viewer
- **Error Highlighting**: Easy identification of issues

### 📁 File Management
- **File Browser**: Browse and manage website files
- **Upload Support**: Drag-and-drop file uploads
- **Video Support**: Special handling for video files
- **File Operations**: Delete, view, and organize files
- **Size Display**: File size and modification date info

### 🎨 Modern Interface
- **Dark Theme**: Professional dark UI design
- **Responsive Layout**: Adapts to different screen sizes
- **Intuitive Controls**: Easy-to-use interface
- **Status Indicators**: Visual feedback for all operations
- **Professional Styling**: Modern, clean design

### 🔒 Security Features
- **Port Validation**: Prevents port conflicts
- **File Type Validation**: Secure file uploads
- **Error Handling**: Comprehensive error management
- **Process Management**: Safe server process handling

## Installation

1. **Clone or download** this repository
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Starting a Server
1. Click **"Browse"** to select your website folder
2. Enter a **port number** (default: 8000)
3. Select **server type** (HTTP, HTTPS, PHP, Node.js)
4. Click **"➕ Add Server"** to start

### Managing Servers
- **View Logs**: Double-click any server to view detailed logs
- **Stop Server**: Use the stop button in the log viewer
- **Open in Browser**: Click the browser button to open your site
- **Monitor Status**: Real-time status updates in the server list

### File Management
- **Upload Files**: Use the upload buttons to add files
- **Upload Videos**: Special video upload with format validation
- **Delete Files**: Select and delete unwanted files
- **Open Files**: Double-click to open files in default application

### System Information
- Click **"📊 System Info"** to view system details
- Monitor active servers and system resources
- View Python and OS information

## Supported Server Types

- **HTTP**: Python's built-in HTTP server
- **HTTPS**: Secure HTTP server (requires SSL certificates)
- **PHP**: PHP built-in development server
- **Node.js**: Node.js HTTP server (requires Node.js installation)

## System Requirements

- **Python 3.7+**
- **Windows 10/11** (primary target)
- **4GB RAM** minimum
- **50MB disk space**

## Features in Detail

### Server Management
- Run multiple servers on different ports
- Automatic port conflict detection
- Process monitoring and management
- Graceful server shutdown

### Logging System
- Real-time log capture
- Formatted log display
- Log export functionality
- Error and warning highlighting

### File Operations
- Secure file uploads
- File type detection
- Size and date information
- Context menu operations

### User Interface
- Modern dark theme
- Responsive design
- Intuitive controls
- Professional styling

## Troubleshooting

### Common Issues

**Port Already in Use**
- Choose a different port number
- Check if another application is using the port

**Server Won't Start**
- Verify the folder path is correct
- Check if Python/PHP is installed
- Ensure the port is available

**File Upload Fails**
- Check folder permissions
- Verify file size limits
- Ensure sufficient disk space

### Getting Help

If you encounter issues:
1. Check the system information panel
2. Review server logs for error messages
3. Verify all requirements are installed
4. Ensure proper folder permissions

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Modern Server Administrator** - Making web development easier with a professional, modern interface.