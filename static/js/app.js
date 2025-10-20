// Modern Server Administrator - Professional JavaScript Application

class ServerAdmin {
    constructor() {
        this.currentServer = null;
        this.autoRefreshInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadServers();
        this.startAutoRefresh();
        this.checkPHPStatus();
    }

    bindEvents() {
        // Control panel events
        document.getElementById('browseFolderBtn').addEventListener('click', () => this.browseFolder());
        document.getElementById('addServerBtn').addEventListener('click', () => this.addServer());
        document.getElementById('refreshAllBtn').addEventListener('click', () => this.refreshAll());
        document.getElementById('systemInfoBtn').addEventListener('click', () => this.showSystemInfo());

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
        }
    }

    async addServer() {
        const folder = document.getElementById('folderPath').value;
        const port = parseInt(document.getElementById('serverPort').value);
        const serverType = document.getElementById('serverType').value;

        if (!folder) {
            this.showNotification('Please select a website folder', 'error');
            return;
        }

        if (!port || port < 1000 || port > 65535) {
            this.showNotification('Please enter a valid port number (1000-65535)', 'error');
            return;
        }

        // Check if port is already in use
        const isPortInUse = await this.checkPortInUse(port);
        if (isPortInUse) {
            this.showNotification(`Port ${port} is already in use`, 'error');
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
            this.showNotification('Error adding server', 'error');
        } finally {
            addBtn.innerHTML = originalText;
            addBtn.disabled = false;
        }
    }

    async checkPortInUse(port) {
        try {
            const response = await fetch(`/api/check_port/${port}`);
            const result = await response.json();
            return result.inUse;
        } catch {
            return false;
        }
    }

    async stopServer(serverName) {
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
        const container = document.getElementById('serversContainer');
        container.innerHTML = '';

        if (Object.keys(servers).length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-server"></i>
                    <h3>No servers running</h3>
                    <p>Add a server to get started with your development</p>
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
                        <h3>${server.name}</h3>
                        <p>${server.folder.split('/').pop()}</p>
                    </div>
                    <div class="server-status">
                        <span class="status-badge status-${server.status.toLowerCase()}">${server.status}</span>
                    </div>
                </div>
                
                <div class="server-details">
                    <div class="detail-item">
                        <div class="detail-label">Port</div>
                        <div class="detail-value">${server.port}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Type</div>
                        <div class="detail-value">${server.type}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Started</div>
                        <div class="detail-value">${server.start_time}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">URL</div>
                        <div class="detail-value">http://localhost:${server.port}</div>
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
            this.showNotification('Error opening browser', 'error');
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

    async refreshAll() {
        await this.loadServers();
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
            `;
            
            document.getElementById('systemModal').classList.add('show');
        } catch (error) {
            this.showNotification('Error loading system info', 'error');
        }
    }

    async checkPHPStatus() {
        try {
            const response = await fetch('/api/check_php');
            const result = await response.json();
            
            if (!result.available) {
                this.showNotification('PHP is not available - PHP servers will not work', 'warning');
            }
        } catch (error) {
            console.error('Error checking PHP status:', error);
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
        // Refresh servers every 30 seconds
        this.autoRefreshInterval = setInterval(() => {
            this.loadServers();
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