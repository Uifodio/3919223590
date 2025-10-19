// Futuristic Web Server - Main JavaScript

class FuturisticWebServer {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.searchBox = document.getElementById('searchBox');
        this.fileGrid = document.getElementById('fileGrid');
        this.uploadProgress = document.getElementById('uploadProgress');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadFiles();
        this.setupDragAndDrop();
        this.setupSearch();
        this.setupAnimations();
    }
    
    setupEventListeners() {
        // File upload
        if (this.uploadArea && this.fileInput) {
            this.uploadArea.addEventListener('click', () => this.fileInput.click());
            this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files));
        }
        
        // Search functionality
        if (this.searchBox) {
            this.searchBox.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }
    }
    
    setupDragAndDrop() {
        if (!this.uploadArea) return;
        
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });
        
        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });
        
        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFileUpload(e.dataTransfer.files);
        });
    }
    
    setupSearch() {
        if (!this.searchBox) return;
        
        // Debounce search input
        let searchTimeout;
        this.searchBox.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.handleSearch(e.target.value);
            }, 300);
        });
    }
    
    setupAnimations() {
        // Add loading animation to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', function() {
                this.classList.add('loading');
                setTimeout(() => {
                    this.classList.remove('loading');
                }, 1000);
            });
        });
    }
    
    async handleFileUpload(files) {
        if (!files || files.length === 0) return;
        
        this.showUploadProgress(true);
        this.uploadProgress.max = files.length;
        this.uploadProgress.value = 0;
        
        const formData = new FormData();
        for (let file of files) {
            formData.append('file', file);
        }
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.showNotification('Error: ' + data.error, 'error');
            } else {
                this.showNotification(`Successfully uploaded ${files.length} file(s)`, 'success');
                this.loadFiles(); // Refresh file list
            }
        } catch (error) {
            this.showNotification('Upload failed: ' + error.message, 'error');
        } finally {
            this.showUploadProgress(false);
        }
    }
    
    async loadFiles() {
        try {
            const response = await fetch('/api/files');
            const files = await response.json();
            this.renderFiles(files);
        } catch (error) {
            console.error('Failed to load files:', error);
        }
    }
    
    renderFiles(files) {
        if (!this.fileGrid) return;
        
        this.fileGrid.innerHTML = '';
        
        files.forEach((file, index) => {
            const fileCard = this.createFileCard(file, index);
            this.fileGrid.appendChild(fileCard);
        });
    }
    
    createFileCard(file, index) {
        const card = document.createElement('div');
        card.className = 'file-card';
        card.style.animationDelay = `${index * 0.1}s`;
        
        const icon = this.getFileIcon(file.name);
        const size = this.formatFileSize(file.size);
        const modified = new Date(file.modified * 1000).toLocaleDateString();
        
        card.innerHTML = `
            <div class="file-icon">${icon}</div>
            <div class="file-name">${this.escapeHtml(file.name)}</div>
            <div class="file-size">${size}</div>
            <div class="file-actions">
                <a href="/api/stream/${encodeURIComponent(file.name)}" class="btn btn-info" target="_blank">
                    <i class="fas fa-eye"></i> View
                </a>
                <a href="/api/download/${encodeURIComponent(file.name)}" class="btn btn-success">
                    <i class="fas fa-download"></i> Download
                </a>
                <a href="/api/qr/${encodeURIComponent(file.name)}" class="btn btn-warning">
                    <i class="fas fa-qrcode"></i> QR
                </a>
                <button onclick="futuristicApp.deleteFile('${this.escapeHtml(file.name)}')" class="btn btn-danger">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        `;
        
        return card;
    }
    
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const iconMap = {
            'txt': '📄', 'pdf': '📕', 'doc': '📘', 'docx': '📘',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️',
            'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'mkv': '🎬', 'webm': '🎬',
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵',
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦',
            'exe': '⚙️', 'msi': '⚙️', 'deb': '⚙️',
            'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨', 'json': '📋',
            'xml': '📋', 'csv': '📊', 'xlsx': '📊', 'pptx': '📊'
        };
        return iconMap[ext] || '📁';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    handleSearch(searchTerm) {
        if (!this.fileGrid) return;
        
        const cards = this.fileGrid.querySelectorAll('.file-card');
        const term = searchTerm.toLowerCase();
        
        cards.forEach(card => {
            const fileName = card.querySelector('.file-name').textContent.toLowerCase();
            const shouldShow = fileName.includes(term);
            
            card.style.display = shouldShow ? 'block' : 'none';
            card.style.opacity = shouldShow ? '1' : '0.3';
        });
    }
    
    async deleteFile(filename) {
        if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/delete/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.message) {
                this.showNotification('File deleted successfully', 'success');
                this.loadFiles(); // Refresh file list
            } else {
                this.showNotification('Error: ' + data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Delete failed: ' + error.message, 'error');
        }
    }
    
    showUploadProgress(show) {
        if (this.uploadProgress) {
            this.uploadProgress.style.display = show ? 'block' : 'none';
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    getNotificationColor(type) {
        const colors = {
            'success': '#4CAF50',
            'error': '#F44336',
            'warning': '#FF9800',
            'info': '#2196F3'
        };
        return colors[type] || '#2196F3';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.futuristicApp = new FuturisticWebServer();
});

// Add some global utility functions
window.utils = {
    // Copy text to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            futuristicApp.showNotification('Copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy: ', err);
        }
    },
    
    // Generate shareable link
    generateShareLink(filename) {
        const baseUrl = window.location.origin;
        return `${baseUrl}/api/stream/${encodeURIComponent(filename)}`;
    },
    
    // Share file
    async shareFile(filename) {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: filename,
                    url: this.generateShareLink(filename)
                });
            } catch (err) {
                console.log('Error sharing:', err);
            }
        } else {
            // Fallback to copying link
            this.copyToClipboard(this.generateShareLink(filename));
        }
    }
};