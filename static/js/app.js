// Modern Server Administrator - Professional JavaScript Application

class ServerAdmin {
    constructor() {
        this.currentServer = null;
        this.autoRefreshInterval = null;
        this.selectedFiles = new Set();
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadServers();
        this.loadFiles();
        this.startAutoRefresh();
        this.checkSystemRequirements();
    }

    bindEvents() {
        // Control panel events
        document.getElementById('browseFolderBtn').addEventListener('click', () => this.browseFolder());
        document.getElementById('addServerBtn').addEventListener('click', () => this.addServer());
        document.getElementById('refreshAllBtn').addEventListener('click', () => this.refreshAll());
        document.getElementById('systemInfoBtn').addEventListener('click', () => this.showSystemInfo());
        document.getElementById('installPhpBtn').addEventListener('click', () => this.installPHP());

        // File manager events
        document.getElementById('openFolderBtn').addEventListener('click', () => this.openFolder());
        document.getElementById('uploadFileBtn').addEventListener('click', () => this.uploadFile());
        document.getElementById('uploadVideoBtn').addEventListener('click', () => this.uploadVideo());
        document.getElementById('deleteFileBtn').addEventListener('click', () => this.deleteFile());
        document.getElementById('refreshFilesBtn').addEventListener('click', () => this.loadFiles());

        // File input events
        document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileUpload(e, 'file'));
        document.getElementById('videoInput').addEventListener('change', (e) => this.handleFileUpload(e, 'video'));

        // Folder input
        document.getElementById('folderInput').addEventListener('change', (e) => this.handleFolderSelection(e));

        // Modal events
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal')));
        });

        // Log modal events
        document.getElementById('refreshLogsBtn').addEventListener('click', () => this.refreshLogs());
        document.getElementById('copyLogsBtn').addEventListener('click', () => this.copyLogs());
        document.getElementById('openBrowserBtn').addEventListener('click', () => this.openBrowser());

        // File selection
        document.getElementById('selectAllFiles').addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // Form validation
        document.getElementById('serverPort').addEventListener('input', (e) => {
            this.validatePort(e.target);
        });
    }

    async browseFolder() {
        document.getElementById('folderInput').click();
    }

    handleFolderSelection(event) {
        const files = event.target.files;
        if (files.length > 0) {
            // Get the folder path from the first file
            const folderPath = files[0].webkitRelativePath.split('/')[0];
            const fullPath = files[0].path ? files[0].path.split(folderPath)[0] + folderPath : folderPath;
            document.getElementById('folderPath').value = fullPath;
            this.setFolder(fullPath);
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

    validatePort(input) {
        const port = parseInt(input.value);
        if (port < 1000 || port > 65535) {
            input.style.borderColor = 'var(--error)';
        } else {
            input.style.borderColor = 'var(--border-primary)';
        }
    }

    async addServer() {
        const folder = document.getElementById('folderPath').value.trim();
        const port = parseInt(document.getElementById('serverPort').value);
        const serverType = document.getElementById('serverType').value;

        // Validation
        if (!folder) {
            this.showNotification('Please select a website folder', 'error');
            return;
        }

        if (!port || port < 1000 || port > 65535) {
            this.showNotification('Please enter a valid port number (1000-65535)', 'error');
            return;
        }

        // Show loading state
        const addBtn = document.getElementById('addServerBtn');
        const originalText = addBtn.innerHTML;
        addBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding Server...';
        addBtn.disabled = true;

        try {
            const response = await fetch('/api/add_server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ folder, port, type: serverType })
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
            this.showNotification('Error adding server: ' + error.message, 'error');
        } finally {
            addBtn.innerHTML = originalText;
            addBtn.disabled = false;
        }
    }

    async stopServer(serverName) {
        if (!confirm(`Are you sure you want to stop ${serverName}?`)) {
            return;
        }

        try {
            const response = await fetch('/api/stop_server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: serverName })
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(result.message, 'success');
                this.loadServers();
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error stopping server: ' + error.message, 'error');
        }
    }

    async loadServers() {
        try {
            const response = await fetch('/api/servers');
            const servers = await response.json();
            this.renderServers(servers);
        } catch (error) {
            console.error('Error loading servers:', error);
            this.showNotification('Error loading servers', 'error');
        }
    }

    renderServers(servers) {
        const container = document.getElementById('serversContainer');
        container.innerHTML = '';

        if (Object.keys(servers).length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-server"></i>
                    <h3 style="color: var(--text-primary);">No servers running</h3>
                    <p style="color: var(--text-secondary);">Add a server to get started with your development</p>
                </div>
            `;
            document.getElementById('serverCount').textContent = '0 servers running';
            return;
        }

        let runningCount = 0;
        Object.values(servers).forEach(server => {
            if (server.status === 'Running') runningCount++;
            
            const serverCard = document.createElement('div');
            serverCard.className = `server-card ${server.status.toLowerCase()}`;
            
            serverCard.innerHTML = `
                <div class="server-header">
                    <div class="server-info">
                        <h3 style="color: var(--text-primary); font-weight: 600;">${server.name}</h3>
                        <p style="color: var(--text-secondary); font-weight: 500;">${server.folder.split('/').pop()}</p>
                    </div>
                    <div class="server-status">
                        <span class="status-badge status-${server.status.toLowerCase()}">${server.status}</span>
                    </div>
                </div>
                
                <div class="server-details">
                    <div class="detail-item">
                        <div class="detail-label">Port</div>
                        <div class="detail-value" style="color: var(--text-primary); font-weight: 600;">${server.port}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Type</div>
                        <div class="detail-value" style="color: var(--text-primary); font-weight: 600;">${server.type}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Started</div>
                        <div class="detail-value" style="color: var(--text-primary); font-weight: 600;">${server.start_time}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">URL</div>
                        <div class="detail-value" style="color: var(--text-primary); font-weight: 600;">http://localhost:${server.port}</div>
                    </div>
                </div>
                
                <div class="server-actions">
                    <button class="action-btn view-logs" onclick="serverAdmin.showLogs('${server.name}')">
                        <i class="fas fa-file-alt"></i>
                        View Logs
                    </button>
                    <button class="action-btn open-browser" onclick="serverAdmin.openServerInBrowser('${server.name}')">
                        <i class="fas fa-external-link-alt"></i>
                        Open Browser
                    </button>
                    <button class="action-btn stop-server" onclick="serverAdmin.stopServer('${server.name}')">
                        <i class="fas fa-stop"></i>
                        Stop Server
                    </button>
                </div>
            `;
            
            container.appendChild(serverCard);
        });

        document.getElementById('serverCount').textContent = `${runningCount} servers running`;
    }

    async showLogs(serverName) {
        this.currentServer = serverName;
        document.getElementById('logModalTitle').innerHTML = `<i class="fas fa-file-alt"></i> Logs - ${serverName}`;
        document.getElementById('logModal').classList.add('show');
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
                logContent.textContent = 'No logs available yet...';
                return;
            }

            data.logs.forEach(log => {
                const logLine = document.createElement('div');
                const timestamp = log.timestamp || new Date().toLocaleTimeString();
                const message = log.message || '';
                const type = log.type || 'info';
                
                logLine.innerHTML = `<span style="color: var(--text-muted);">[${timestamp}]</span> <span style="color: ${type === 'error' ? 'var(--error)' : 'var(--text-primary)'};">${message}</span>`;
                logContent.appendChild(logLine);
            });

            logContent.scrollTop = logContent.scrollHeight;
        } catch (error) {
            console.error('Error loading logs:', error);
            document.getElementById('logContent').textContent = 'Error loading logs: ' + error.message;
        }
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
            this.showNotification('Error opening browser: ' + error.message, 'error');
        }
    }

    async openBrowser() {
        if (!this.currentServer) return;
        await this.openServerInBrowser(this.currentServer);
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
            this.showNotification('Error loading files', 'error');
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
                        <h3 style="color: var(--text-primary);">No files found</h3>
                        <p style="color: var(--text-secondary);">Select a folder or upload some files</p>
                    </td>
                </tr>
            `;
            return;
        }

        files.forEach(file => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><input type="checkbox" class="file-checkbox" data-filename="${file.name}"></td>
                <td style="color: var(--text-primary); font-weight: 500;"><i class="fas ${this.getFileIcon(file.type)} file-icon"></i>${file.name}</td>
                <td style="color: var(--text-primary); font-weight: 500;">${file.size}</td>
                <td style="color: var(--text-primary); font-weight: 500;">${file.type}</td>
                <td style="color: var(--text-primary); font-weight: 500;">${file.modified}</td>
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
        if (type.includes('php')) return 'fa-file-code';
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
        event.target.value = '';
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
                <p><strong>Operating System:</strong> ${info.os}</p>
                <p><strong>Architecture:</strong> ${info.architecture}</p>
                <p><strong>Python Version:</strong> ${info.python_version}</p>
                <p><strong>CPU Cores:</strong> ${info.cpu_cores}</p>
                <p><strong>Memory Total:</strong> ${info.memory_total} GB</p>
                <p><strong>Memory Available:</strong> ${info.memory_available} GB</p>
                <p><strong>Disk Free:</strong> ${info.disk_free} GB</p>
                <p><strong>Active Servers:</strong> ${info.active_servers}</p>
                <p><strong>PHP Available:</strong> ${info.php_available ? 'Yes' : 'No'}</p>
                ${info.php_version ? `<p><strong>PHP Version:</strong> ${info.php_version}</p>` : ''}
                <p><strong>Node.js Available:</strong> ${info.node_available ? 'Yes' : 'No'}</p>
                ${info.node_version ? `<p><strong>Node.js Version:</strong> ${info.node_version}</p>` : ''}
                <p><strong>Current Folder:</strong> ${info.current_folder || 'None'}</p>
            `;
            
            document.getElementById('systemModal').classList.add('show');
        } catch (error) {
            this.showNotification('Error loading system info: ' + error.message, 'error');
        }
    }

    async checkSystemRequirements() {
        try {
            const [phpResponse, nodeResponse] = await Promise.all([
                fetch('/api/check_php'),
                fetch('/api/check_node')
            ]);
            
            const phpInfo = await phpResponse.json();
            const nodeInfo = await nodeResponse.json();
            
            if (!phpInfo.available) {
                this.showNotification('PHP is not available - PHP servers will not work. Use the Install PHP button.', 'warning');
                document.getElementById('installPhpBtn').style.display = 'inline-flex';
            } else {
                this.showNotification(`PHP detected: ${phpInfo.version}`, 'success');
            }
            
            if (!nodeInfo.available) {
                this.showNotification('Node.js is not available - Node.js servers will not work', 'warning');
            } else {
                this.showNotification(`Node.js detected: ${nodeInfo.version}`, 'success');
            }
        } catch (error) {
            console.error('Error checking system requirements:', error);
        }
    }

    async installPHP() {
        const installBtn = document.getElementById('installPhpBtn');
        const originalText = installBtn.innerHTML;
        installBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Installing PHP...';
        installBtn.disabled = true;

        try {
            const response = await fetch('/api/install_php', {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(result.message, 'success');
                document.getElementById('installPhpBtn').style.display = 'none';
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error installing PHP: ' + error.message, 'error');
        } finally {
            installBtn.innerHTML = originalText;
            installBtn.disabled = false;
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.classList.remove('show');
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
    }

    updateStatus(text, type) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        statusText.textContent = text;
        
        if (type === 'success') {
            statusDot.style.background = 'var(--success)';
        } else if (type === 'error') {
            statusDot.style.background = 'var(--error)';
        } else if (type === 'warning') {
            statusDot.style.background = 'var(--warning)';
        } else {
            statusDot.style.background = 'var(--info)';
        }

        // Reset status after 3 seconds
        setTimeout(() => {
            statusText.textContent = 'Ready';
            statusDot.style.background = 'var(--success)';
        }, 3000);
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        }[type] || 'fa-info-circle';
        
        notification.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
    }

    startAutoRefresh() {
        // Refresh servers and files every 30 seconds
        this.autoRefreshInterval = setInterval(() => {
            this.loadServers();
            this.loadFiles();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
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

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (serverAdmin) {
        serverAdmin.stopAutoRefresh();
    }
});