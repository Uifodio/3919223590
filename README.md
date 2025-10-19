# 🚀 Futuristic Web Server - Professional Edition

A modern, professional web server application with a sleek UI and advanced features, designed to replace outdated server management tools with a futuristic, user-friendly interface.

## ✨ Features

### 🌟 Core Features
- **Dual Server Support**: Run two independent servers simultaneously on different ports
- **Modern UI**: Sleek, dark-themed interface with professional design
- **File Management**: Advanced file upload, download, and management capabilities
- **Media Streaming**: Stream videos, audio, and images directly in the browser
- **QR Code Generation**: Generate QR codes for easy file sharing
- **Thumbnail Generation**: Automatic thumbnails for images and videos
- **Search Functionality**: Real-time file search with instant results
- **Drag & Drop**: Intuitive file upload with drag and drop support

### 🔧 Advanced Features
- **Real-time Logs**: Monitor server activity with live log viewing
- **Security**: File type validation and secure upload handling
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Cross-platform**: Runs on Windows, macOS, and Linux
- **Standalone EXE**: Build as a single executable file for easy distribution
- **Professional Theming**: Multiple color schemes and modern animations

### 📱 User Interface
- **Dark Theme**: Professional dark theme with modern aesthetics
- **Animated Elements**: Smooth animations and transitions
- **Grid Layout**: Beautiful file grid with hover effects
- **Progress Indicators**: Real-time upload progress tracking
- **Notification System**: Toast notifications for user feedback
- **Mobile Responsive**: Optimized for all screen sizes

## 🛠️ Installation

### Quick Setup
1. Clone or download the project
2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Run the application:
   ```bash
   python main.py
   ```

### Manual Installation
1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create necessary directories:
   ```bash
   mkdir -p uploads logs static templates config
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## 🚀 Building Executable

To create a standalone EXE file:

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Run the build script:
   ```bash
   python build_exe.py
   ```

3. The executable will be created in the `dist/` folder

## 📖 Usage

### Starting Servers
1. Launch the application
2. Configure Server 1:
   - Set port (default: 8080)
   - Select directory to serve
   - Click "Start Server"
3. Configure Server 2:
   - Set port (default: 8081)
   - Select directory to serve
   - Click "Start Server"

### File Management
- **Upload**: Drag and drop files or click to select
- **Download**: Click the download button on any file
- **View**: Click view to stream media files
- **Share**: Generate QR codes for easy sharing
- **Delete**: Remove files with confirmation

### Web Interface
- Access your files through the web browser
- Use the search box to find files quickly
- View thumbnails for images and videos
- Stream media files directly in the browser

## 🔧 Configuration

Edit `config/server_config.json` to customize:
- File size limits
- Allowed file types
- Security settings
- UI preferences
- Rate limiting

## 📁 Project Structure

```
futuristic-web-server/
├── main.py                 # Main application entry point
├── server_manager.py       # Web server management
├── build_exe.py           # Executable build script
├── setup.sh               # Setup script
├── requirements.txt       # Python dependencies
├── config/
│   └── server_config.json # Server configuration
├── static/
│   ├── css/
│   │   └── style.css      # Stylesheets
│   ├── js/
│   │   └── main.js        # JavaScript
│   └── images/            # Static images
├── templates/
│   └── base.html          # HTML templates
├── uploads/               # Upload directory
├── logs/                  # Log files
└── README.md             # This file
```

## 🎨 Customization

### Themes
The application uses CSS custom properties for easy theming. Edit `static/css/style.css` to customize colors and styles.

### File Types
Add or remove supported file types in `config/server_config.json`.

### UI Elements
Modify the PyQt6 interface in `main.py` to add or remove UI components.

## 🔒 Security Features

- File type validation
- Size limits on uploads
- Secure filename handling
- CORS protection
- Rate limiting (configurable)
- Optional authentication

## 🌐 API Endpoints

- `GET /` - Main file browser interface
- `GET /api/files` - List all files
- `POST /api/upload` - Upload files
- `GET /api/download/<filename>` - Download file
- `GET /api/stream/<filename>` - Stream file
- `GET /api/qr/<filename>` - Generate QR code
- `GET /api/thumbnail/<filename>` - Get thumbnail
- `GET /api/info/<filename>` - Get file info
- `DELETE /api/delete/<filename>` - Delete file

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port number in the UI
2. **Permission denied**: Check file permissions for the target directory
3. **Upload fails**: Check file size limits and allowed file types
4. **Build fails**: Ensure all dependencies are installed

### Logs
Check the `logs/server.log` file for detailed error information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- PyQt6 for the modern UI framework
- Flask for the web server backend
- All the open-source libraries that make this possible

## 📞 Support

For support, feature requests, or bug reports, please open an issue on the project repository.

---

**Made with ❤️ for the future of web server management**