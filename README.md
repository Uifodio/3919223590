# 🚀 Futuristic Web Server

A simple, working web server application with a modern tkinter GUI. No complex dependencies, just pure Python with tkinter.

## ✨ Features

- **Modern Tkinter GUI** with dark theme
- **File Upload/Download** with drag & drop support
- **Web Interface** accessible in any browser
- **Real-time Logs** and file monitoring
- **Simple Setup** - just Python and tkinter
- **Cross-platform** - works on Windows, macOS, and Linux

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   python3 setup.py
   ```

2. **Run the application:**
   ```bash
   python3 main.py
   ```

3. **Use the GUI:**
   - Set port (default: 8080)
   - Choose directory to serve
   - Click "Start Server"
   - Click "Open in Browser" to access web interface

## 📁 What You Get

- **GUI Application**: Modern tkinter interface with dark theme
- **Web Server**: HTTP server that serves files and handles uploads
- **File Browser**: Web interface to view, upload, and download files
- **Real-time Logs**: See what's happening in real-time
- **File Management**: Upload, download, and organize files

## 🛠️ Requirements

- Python 3.6+
- tkinter (usually included with Python)
- pygments (for syntax highlighting in logs)

## 📖 How to Use

1. **Start the Server:**
   - Open the application
   - Set your desired port
   - Choose a directory to serve
   - Click "Start Server"

2. **Access Files:**
   - Click "Open in Browser" to open the web interface
   - Upload files using the web interface
   - Download files by clicking the download button
   - View files in the GUI file list

3. **Monitor Activity:**
   - Watch real-time logs in the GUI
   - See file uploads and server activity
   - Refresh file list to see new files

## 🎯 Why This Works

- **Simple Dependencies**: Only uses tkinter and basic Python libraries
- **No Complex Setup**: Just run and go
- **Cross-platform**: Works everywhere Python works
- **Lightweight**: Fast and efficient
- **User-friendly**: Easy to use interface

## 🔧 Technical Details

- **Backend**: Python's built-in `http.server` module
- **Frontend**: Tkinter for GUI, HTML/CSS/JS for web interface
- **File Handling**: Direct file serving and multipart upload handling
- **Threading**: Server runs in separate thread to keep GUI responsive

This is a working, simple web server that actually works without complex dependencies!