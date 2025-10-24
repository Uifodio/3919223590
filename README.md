# 🚀 Windows-Compatible Workspace Server

**Professional Multi-Project Development Environment**

A production-style local development server that can run PHP, Node.js, Python, and static sites simultaneously through a central Python reverse proxy. Perfect for multi-project development with unified access through one localhost port.

![Workspace Server](https://img.shields.io/badge/Version-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![PHP](https://img.shields.io/badge/PHP-8.3+-purple)
![Node.js](https://img.shields.io/badge/Node.js-18+-green)
![Windows](https://img.shields.io/badge/Windows-Compatible-blue)

## ✨ Features

### 🎯 **Multi-Project Management**
- **Central Reverse Proxy**: All projects accessible through `localhost:8000`
- **Multiple Backends**: PHP, Node.js, Python, and static sites simultaneously
- **Route-Based Access**: Each project gets its own route (e.g., `/myproject`)
- **Real-time Monitoring**: Live status updates and project management

### 🪟 **Windows Compatibility**
- **Portable PHP**: Standalone PHP installation included
- **Auto-Detection**: Automatically finds PHP and Node.js installations
- **Auto-Installation**: One-click installation of dependencies
- **Windows Paths**: Supports common Windows development environments

### 🎨 **Professional Interface**
- **Modern UI**: GitHub-themed dark interface with professional styling
- **Real-time Dashboard**: Live project status and statistics
- **Project Management**: Add, start, stop, and delete projects easily
- **File Upload**: Drag-and-drop project uploads and ZIP extraction
- **Logging**: Real-time logs for each project with export capabilities

### ⚡ **Development Features**
- **Hot Reloading**: Automatic server restart on file changes
- **Port Management**: Automatic port assignment with conflict detection
- **Process Monitoring**: Background monitoring of all running servers
- **Error Handling**: Comprehensive error logging and user feedback

## 🚀 Quick Start

### **One-Click Setup (Recommended)**

1. **Download** the workspace server files
2. **Run** `setup_complete.bat` as Administrator
3. **Wait** for automatic setup to complete
4. **Run** `start_workspace.bat` to start the server
5. **Open** your browser to `http://localhost:8000`

### **Manual Setup**

1. **Install Python 3.7+** from [python.org](https://python.org)
2. **Run** `setup_complete.bat` to install dependencies
3. **Start** the server with `start_workspace.bat`

## 📁 Project Structure

```
workspace-server/
├── web_server_admin.py          # Main Flask application
├── templates/
│   └── index.html               # Modern dashboard UI
├── static/
│   ├── css/style.css            # Professional styling
│   └── js/app.js                # Interactive functionality
├── php_standalone/              # Portable PHP installation
│   ├── php.exe                  # PHP executable
│   ├── php.ini                  # PHP configuration
│   └── ...                      # PHP extensions
├── sites/                       # Project storage
├── logs/                        # Server logs
├── uploads/                     # File uploads
├── requirements.txt             # Python dependencies
├── setup_complete.bat           # Complete setup script
├── start_workspace.bat          # Windows startup script
└── README.md                    # This file
```

## 🎯 Usage

### **Adding Projects**

1. **Click "New Project"** in the dashboard
2. **Select Project Type**:
   - **Static Site**: HTML, CSS, JS files
   - **PHP Application**: PHP files with built-in server
   - **Node.js Application**: Node.js projects with package.json
   - **Python Application**: Flask, Django, or other Python web apps
3. **Set Source Path**: Point to your project folder
4. **Configure Route**: Optional custom route (defaults to project name)
5. **Start Project**: Click "Start" to launch the server

### **Project Management**

- **Start/Stop**: Control individual projects
- **View Logs**: Real-time logging for debugging
- **Open in Browser**: Direct access to project URLs
- **Delete Projects**: Remove projects and clean up files

### **Accessing Projects**

All projects are accessible through the central proxy:

- **Dashboard**: `http://localhost:8000`
- **Project Routes**: `http://localhost:8000/projectname`
- **Custom Routes**: `http://localhost:8000/custom-route`

## 🔧 Configuration

### **Runtime Options**

The server can be configured by modifying `RUNTIME_OPTIONS` in `web_server_admin.py`:

```python
RUNTIME_OPTIONS = {
    'ENABLE_REVERSE_PROXY': True,      # Enable reverse proxy
    'PROXY_PORT': 8000,                # Main proxy port
    'PROXY_HOST': '0.0.0.0',          # Main proxy host
    'AUTO_OPEN_BROWSER': True,         # Auto-open browser on Windows
    'WINDOWS_AUTO_INSTALL': True,      # Auto-install PHP/Node.js
    'AUTO_REFRESH_INTERVAL': 2.0,      # UI refresh interval
    'MAX_WORKERS': 32,                 # Thread pool size
    'LOG_TAIL_LINES': 200,             # Log lines to display
}
```

### **Windows-Specific Settings**

The server automatically detects common Windows development environments:

- **PHP Paths**: Portable PHP, XAMPP, WAMP, Laragon, standalone PHP
- **Node.js Paths**: Program Files, user installations
- **Auto-Installation**: Downloads and installs missing dependencies

## 🎨 UI Features

### **Dashboard**
- **Project Grid**: Visual project cards with status indicators
- **Statistics**: Running/stopped project counts
- **Quick Actions**: One-click project creation
- **Real-time Updates**: Auto-refreshing project status

### **Project Cards**
- **Status Indicators**: Visual running/stopped status
- **Project Info**: Type, port, route, creation date
- **Action Buttons**: Start, stop, view logs, delete
- **Type Icons**: Visual indicators for different project types

### **Modals**
- **Add Project**: Comprehensive project creation form
- **View Logs**: Real-time log viewing with export
- **System Info**: Environment and dependency status

## 🔒 Security Features

- **Port Validation**: Prevents port conflicts
- **File Type Validation**: Secure file uploads
- **Path Sanitization**: Safe file path handling
- **Process Isolation**: Each project runs in its own process

## 🚀 Advanced Features

### **Reverse Proxy**
- **Unified Access**: All projects through one port
- **Route Management**: Automatic route assignment
- **Load Balancing**: Distribute requests to appropriate backends
- **Error Handling**: Graceful fallbacks for failed projects

### **Process Management**
- **Background Monitoring**: Continuous process health checks
- **Graceful Shutdown**: Proper cleanup on exit
- **Resource Management**: Efficient memory and CPU usage
- **Log Rotation**: Automatic log file management

### **File Management**
- **Upload Support**: Drag-and-drop file uploads
- **ZIP Extraction**: Automatic project extraction
- **File Browser**: Browse and manage project files
- **Size Tracking**: File size and modification date display

## 🧪 Testing

### **Manual Testing**
1. **Start the server**: `start_workspace.bat`
2. **Access dashboard**: `http://localhost:8000`
3. **Add a project**: Create a test project
4. **Start project**: Verify it starts successfully
5. **Access project**: Open in browser via proxy
6. **View logs**: Check real-time logging
7. **Stop project**: Verify clean shutdown

## 📊 Performance

- **Lightweight**: Minimal memory usage
- **Fast Startup**: Quick project initialization
- **Efficient**: Optimized for multiple concurrent projects
- **Scalable**: Supports up to 20 projects simultaneously

## 🎯 Target Users

- **Web Developers**: Multi-project development workflows
- **Students**: Learning different web technologies
- **Designers**: Quick website testing and prototyping
- **Professionals**: Efficient development environments
- **Teams**: Shared development server setup

## 🔧 Troubleshooting

### **Common Issues**

**Server Won't Start**
- Verify Python 3.7+ is installed
- Check if port 8000 is available
- Run `pip install -r requirements.txt`

**PHP Projects Won't Work**
- Use "Check PHP" button to verify installation
- Install PHP manually if auto-detection fails
- Check PHP path in system PATH

**Node.js Projects Won't Work**
- Use "Check Node.js" button to verify installation
- Install Node.js manually if auto-detection fails
- Verify package.json exists in project folder

**Projects Not Accessible**
- Check if project is running (green status)
- Verify route is correct
- Check firewall settings

### **Getting Help**

1. **Check System Info**: Click info button in dashboard
2. **Review Logs**: Check project logs for errors
3. **Verify Dependencies**: Use check buttons for PHP/Node.js
4. **Check Ports**: Ensure no port conflicts

## 📈 Future Enhancements

- **Database Integration**: Support for database management
- **SSL Certificate Management**: Easy HTTPS setup
- **Team Collaboration**: Multi-user project sharing
- **Plugin System**: Extensible architecture
- **Mobile App**: Companion mobile application
- **Cloud Integration**: Deploy to cloud platforms

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Windows-Compatible Workspace Server** - Professional multi-project development environment that makes web development easier and more efficient.

## 🎉 What's New in v2.0

- **Complete UI Redesign**: Modern, professional interface
- **Portable PHP**: Standalone PHP installation included
- **Enhanced Windows Support**: Better compatibility and auto-setup
- **Improved Performance**: Faster startup and better resource management
- **Better Error Handling**: More informative error messages and logging
- **Mobile Responsive**: Works great on all screen sizes
- **Dark Theme**: Professional dark interface with GitHub-inspired design