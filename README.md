# 🚀 Unified Server Administrator

A professional, production-ready web server administration tool that unifies all server types through a single nginx-based architecture.

## ✨ Features

### 🎯 **Unified Architecture**
- **Single nginx reverse proxy** handling all server types
- **PHP via php-fpm** with optimized configuration
- **Node.js via internal proxy** with backend processes  
- **Static files** served directly by nginx
- **Professional nginx configuration** with security headers, gzip, caching

### 🎨 **Professional UI**
- **GitHub-like dark theme** with modern design
- **Responsive design** for all devices
- **Real-time monitoring** with live status updates
- **Modern animations** and smooth transitions
- **Professional typography** using Inter font

### 🔒 **Production Features**
- **Security headers** and rate limiting
- **Gzip compression** and static file caching
- **Real-time logs** with live streaming
- **System monitoring** and health checks
- **Automatic configuration** generation

## 🚀 Quick Start

### 1. Start the Server
```bash
python3 start.py
```

### 2. Open Web Interface
- Navigate to `http://localhost:5000`
- Professional GitHub-like interface will load

### 3. Create Your First Server
1. Enter server name (e.g., "my-website")
2. Select server type:
   - **Static Files** - HTML, CSS, JS files
   - **PHP** - PHP applications with php-fpm
   - **Node.js** - JavaScript applications
3. Set port (e.g., 8000)
4. Enter site path (e.g., "/workspace/demo_site")
5. Click "Create Server"

### 4. Access Your Site
- Your site will be available at `http://localhost:8000`
- Nginx automatically generates optimized configuration
- All security headers and optimizations applied

## 📁 Project Structure

```
/workspace/
├── web_server_admin.py          # Main unified server application
├── start.py                     # Quick start script
├── nginx_config_generator.py    # Nginx configuration generator
├── requirements.txt             # Python dependencies
├── templates/
│   └── index.html              # Professional GitHub-like UI
├── static/
│   ├── css/style.css           # Professional dark theme
│   └── js/app.js               # Modern JavaScript application
├── sites/                      # Directory for website files
├── demo_site/                  # Demo sites for testing
│   ├── index.html              # Static demo
│   └── info.php                # PHP demo
└── php/                        # Complete PHP installation
```

## 🎯 Server Types

### 📄 Static Files
- Served directly by nginx
- Optimized with gzip compression
- Static file caching enabled
- Perfect for HTML, CSS, JS, images

### 🐘 PHP Applications
- Processed via php-fpm
- Individual pool for each site
- Socket-based communication
- Full PHP feature support

### 🟢 Node.js Applications
- Reverse proxy to internal Node.js process
- Automatic process management
- Upstream load balancing
- WebSocket support

## 🔧 Advanced Features

### Nginx Integration
- Automatic configuration generation
- Security headers (XSS, CSRF, etc.)
- Rate limiting and DDoS protection
- Gzip compression and caching
- SSL/TLS ready

### Real-time Monitoring
- Live server status updates
- Real-time log streaming
- System resource monitoring
- Health checks and alerts

### Professional UI
- GitHub-inspired design
- Responsive for all devices
- Dark theme with high contrast
- Smooth animations and transitions
- Accessibility features

## 🛠️ System Requirements

- **Python 3.8+**
- **Nginx** (installed automatically)
- **PHP 8.1+** (optional, for PHP sites)
- **Node.js** (optional, for Node.js sites)

## 📦 Installation

1. **Clone/Download** the project
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the server:**
   ```bash
   python3 start.py
   ```

## 🎉 Demo Sites

The project includes demo sites to test all server types:

- **Static Demo:** `/workspace/demo_site/index.html`
- **PHP Demo:** `/workspace/demo_site/info.php`

## 🔒 Security Features

- **Security Headers:** X-Frame-Options, X-XSS-Protection, etc.
- **Rate Limiting:** Protection against abuse
- **Input Validation:** Secure file uploads and processing
- **Process Isolation:** Each site runs in its own context
- **Access Control:** Proper file permissions and restrictions

## 🚀 Production Ready

This system is **production-ready** with:
- Professional appearance and UX
- Unified nginx-based architecture
- All three server types working seamlessly
- Production-grade security and performance
- Easy management through web interface

**Ready to sell and deploy!** 🎯

## 📞 Support

For issues or questions, check the system information panel in the web interface or review the logs for detailed error information.

---

**Unified Server Administrator** - Professional web server management made simple! 🚀