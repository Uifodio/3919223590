// Modern Server Administrator - JavaScript Application

class ServerAdmin {
    constructor() {
        this.currentServer = null;
        this.selectedFiles = new Set();
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadServers();
        this.loadFiles();
        this.startAutoRefresh();
    }

    bindEvents() {
        // Control panel events
        document.getElementById('browseFolder').addEventListener('click', () => this.browseFolder());
        document.getElementById('addServer').addEventListener('click', () => this.addServer());
        document.getElementById('refreshAll').addEventListener('click', () => this.refreshAll());
        document.getElementById('systemInfo').addEventListener('click', () => this.showSystemInfo());

        // File manager events
        document.getElementById('openFolder').addEventListener('click', () => this.openFolder());
        document.getElementById('uploadFile').addEventListener('click', () => this.uploadFile());
        document.getElementById('uploadVideo').addEventListener('click', () => this.uploadVideo());
        document.getElementById('deleteFile').addEventListener('click', () => this.deleteFile());
        document.getElementById('refreshFiles').addEventListener('click', () => this.loadFiles());

        // File input events
        document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileUpload(e, 'file'));
        document.getElementById('videoInput').addEventListener('change', (e) => this.handleFileUpload(e, 'video'));

        // Modal events
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal')));
        });

        // Log modal events
        document.getElementById('refreshLogs').addEventListener('click', () => this.refreshLogs());
        document.getElementById('copyLogs').addEventListener('click', () => this.copyLogs());
        document.getElementById('openBrowser').addEventListener('click', () => this.openBrowser());
        document.getElementById('stopServer').addEventListener('click', () => this.stopServer());

        // Select all checkbox
        document.getElementById('selectAll').addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });
    }

    async browseFolder() {
        // In a real implementation, this would open a folder picker
        // For now, we'll use a prompt
        const folder = prompt('Enter folder path:');
        if (folder) {
            document.getElementById('folderPath').value = folder;
            await this.setFolder(folder);
        }
    }

    async setFolder(folder) {
        try {
            const response = await fetch('/api/set_folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ folder })
            });
            const result = await response.json();
            if (result.success) {
                this.showNotification(result.message, 'success');
                this.loadFiles();
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error setting folder', 'error');
        }
    }

    async addServer() {
        const folder = document.getElementById('folderPath').value;
        const port = document.getElementById('serverPort').value;
        const type = document.getElementById('serverType').value;

        if (!folder || !port) {
            this.showNotification('Please select a folder and enter a port number', 'error');
            return;
        }

        try {
            const response = await fetch('/api/add_server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ folder, port: parseInt(port), type })
            });
            const result = await response.json();
            if (result.success) {
                this.showNotification(result.message, 'success');
                this.loadServers();
                this.updateStatus('Server Added', 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error adding server', 'error');
        }
    }

    async stopServer() {
        if (!this.currentServer) return;

        try {
            const response = await fetch('/api/stop_server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: this.currentServer })
            });
            const result = await response.json();
            if (result.success) {
                this.showNotification(result.message, 'success');
                this.closeModal(document.getElementById('logModal'));
                this.loadServers();
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error stopping server', 'error');
        }
    }

    async loadServers() {
        try {
            const response = await fetch('/api/servers');
            const servers = await response.json();
            this.renderServers(servers);
        } catch (error) {
            console.error('Error loading servers:', error);
        }
    }

    renderServers(servers) {
        const tbody = document.getElementById('serverTableBody');
        tbody.innerHTML = '';

        if (Object.keys(servers).length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state">
                        <i class="fas fa-server"></i>
                        <h3>No servers running</h3>
                        <p>Add a server to get started</p>
                    </td>
                </tr>
            `;
            document.getElementById('serverCount').textContent = '0 servers running';
            return;
        }

        let runningCount = 0;
        Object.values(servers).forEach(server => {
            if (server.status === 'Running') runningCount++;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${server.name}</td>
                <td>${server.port}</td>
                <td>${server.type}</td>
                <td><span class="status-badge status-${server.status.toLowerCase()}">${server.status}</span></td>
                <td>${server.folder.split('/').pop()}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn view-logs" onclick="serverAdmin.showLogs('${server.name}')">
                            <i class="fas fa-file-alt"></i> View Logs
                        </button>
                        <button class="action-btn open-browser" onclick="serverAdmin.openServerInBrowser('${server.name}')">
                            <i class="fas fa-external-link-alt"></i> Open
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        document.getElementById('serverCount').textContent = `${runningCount} servers running`;
    }

    async showLogs(serverName) {
        this.currentServer = serverName;
        document.getElementById('logModalTitle').textContent = `Logs - ${serverName}`;
        document.getElementById('logModal').style.display = 'block';
        await this.refreshLogs();
    }

    async refreshLogs() {
        if (!this.currentServer) return;

        try {
            const response = await fetch(`/api/server_logs/${this.currentServer}`);
            const data = await response.json();
            
            const logContent = document.getElementById('logContent');
            logContent.innerHTML = '';
            
            if (data.logs.length === 0) {
                logContent.textContent = 'No logs available';
                return;
            }

            data.logs.forEach(log => {
                const logLine = document.createElement('div');
                logLine.innerHTML = `<span style="color: #888;">[${log.timestamp}]</span> ${log.message}`;
                logContent.appendChild(logLine);
            });

            logContent.scrollTop = logContent.scrollHeight;
        } catch (error) {
            console.error('Error loading logs:', error);
        }
    }

    async openBrowser() {
        if (!this.currentServer) return;
        await this.openServerInBrowser(this.currentServer);
    }

    async openServerInBrowser(serverName) {
        try {
            const response = await fetch(`/api/open_browser/${serverName}`);
            const result = await response.json();
            if (result.success) {
                this.showNotification(result.message, 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error opening browser', 'error');
        }
    }

    async copyLogs() {
        const logContent = document.getElementById('logContent').textContent;
        try {
            await navigator.clipboard.writeText(logContent);
            this.showNotification('Logs copied to clipboard', 'success');
        } catch (error) {
            this.showNotification('Failed to copy logs', 'error');
        }
    }

    async loadFiles() {
        try {
            const response = await fetch('/api/files');
            const data = await response.json();
            this.renderFiles(data.files);
        } catch (error) {
            console.error('Error loading files:', error);
        }
    }

    renderFiles(files) {
        const tbody = document.getElementById('fileTableBody');
        tbody.innerHTML = '';

        if (files.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state">
                        <i class="fas fa-folder-open"></i>
                        <h3>No files found</h3>
                        <p>Select a folder or upload some files</p>
                    </td>
                </tr>
            `;
            return;
        }

        files.forEach(file => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><input type="checkbox" class="file-checkbox" data-filename="${file.name}"></td>
                <td><i class="fas ${this.getFileIcon(file.type)} file-icon"></i>${file.name}</td>
                <td>${file.size}</td>
                <td>${file.type}</td>
                <td>${file.modified}</td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn view-logs" onclick="serverAdmin.openFile('${file.name}')">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button class="action-btn stop-server" onclick="serverAdmin.deleteFileByName('${file.name}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    getFileIcon(type) {
        if (type.startsWith('video/')) return 'fa-video';
        if (type.startsWith('image/')) return 'fa-image';
        if (type.startsWith('audio/')) return 'fa-music';
        if (type.includes('pdf')) return 'fa-file-pdf';
        if (type.includes('text')) return 'fa-file-alt';
        if (type.includes('javascript')) return 'fa-file-code';
        if (type.includes('css')) return 'fa-file-code';
        if (type.includes('html')) return 'fa-file-code';
        return 'fa-file';
    }

    uploadFile() {
        document.getElementById('fileInput').click();
    }

    uploadVideo() {
        document.getElementById('videoInput').click();
    }

    async handleFileUpload(event, type) {
        const files = event.target.files;
        if (files.length === 0) return;

        for (let file of files) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.success) {
                    this.showNotification(result.message, 'success');
                } else {
                    this.showNotification(result.message, 'error');
                }
            } catch (error) {
                this.showNotification('Error uploading file', 'error');
            }
        }

        this.loadFiles();
        event.target.value = ''; // Reset input
    }

    async deleteFile() {
        const selectedFiles = Array.from(document.querySelectorAll('.file-checkbox:checked'));
        if (selectedFiles.length === 0) {
            this.showNotification('Please select files to delete', 'error');
            return;
        }

        if (!confirm(`Are you sure you want to delete ${selectedFiles.length} file(s)?`)) {
            return;
        }

        for (let checkbox of selectedFiles) {
            const filename = checkbox.dataset.filename;
            await this.deleteFileByName(filename);
        }

        this.loadFiles();
    }

    async deleteFileByName(filename) {
        try {
            const response = await fetch('/api/delete_file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename })
            });
            const result = await response.json();
            if (result.success) {
                this.showNotification(result.message, 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error deleting file', 'error');
        }
    }

    openFile(filename) {
        // In a real implementation, this would open the file
        this.showNotification(`Opening ${filename}`, 'info');
    }

    openFolder() {
        this.showNotification('Opening folder in file manager', 'info');
    }

    toggleSelectAll(checked) {
        document.querySelectorAll('.file-checkbox').forEach(checkbox => {
            checkbox.checked = checked;
        });
    }

    async refreshAll() {
        await this.loadServers();
        await this.loadFiles();
        this.updateStatus('Refreshed', 'success');
    }

    async showSystemInfo() {
        try {
            const response = await fetch('/api/system_info');
            const info = await response.json();
            
            const content = document.getElementById('systemInfoContent');
            content.innerHTML = `
                <h4>System Information</h4>
                <p><strong>OS:</strong> ${info.os}</p>
                <p><strong>Architecture:</strong> ${info.architecture}</p>
                <p><strong>Python Version:</strong> ${info.python_version}</p>
                <p><strong>CPU Cores:</strong> ${info.cpu_cores}</p>
                <p><strong>Memory Total:</strong> ${info.memory_total} GB</p>
                <p><strong>Memory Available:</strong> ${info.memory_available} GB</p>
                <p><strong>Disk Free:</strong> ${info.disk_free} GB</p>
                <p><strong>Active Servers:</strong> ${info.active_servers}</p>
            `;
            
            document.getElementById('systemModal').style.display = 'block';
        } catch (error) {
            this.showNotification('Error loading system info', 'error');
        }
    }

    closeModal(modal) {
        modal.style.display = 'none';
    }

    updateStatus(text, type) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        statusText.textContent = text;
        
        if (type === 'success') {
            statusDot.style.background = '#4caf50';
        } else if (type === 'error') {
            statusDot.style.background = '#f44336';
        } else {
            statusDot.style.background = '#ff9800';
        }
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 500;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    startAutoRefresh() {
        // Refresh servers and files every 30 seconds
        setInterval(() => {
            this.loadServers();
            this.loadFiles();
        }, 30000);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize the application
let serverAdmin;
document.addEventListener('DOMContentLoaded', () => {
    serverAdmin = new ServerAdmin();
});