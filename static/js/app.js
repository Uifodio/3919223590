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
        this.startAutoRefresh();
        this.checkSystemRequirements();
    }

    bindEvents() {
        // Control panel events
        document.getElementById('browseFolderBtn').addEventListener('click', () => this.browseFolder());
        document.getElementById('manualFolderBtn').addEventListener('click', () => this.manualFolder());
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
        // Try webkitdirectory first, then fallback to manual input
        if (document.getElementById('folderInput').webkitdirectory !== undefined) {
            document.getElementById('folderInput').click();
        } else {
            // Fallback for browsers that don't support webkitdirectory
            this.manualFolder();
        }
    }

    async manualFolder() {
        const folderPath = prompt('Enter the full path to your website folder:\n\nExamples:\n- C:\\Users\\YourName\\Documents\\MyWebsite\n- /home/username/MyWebsite\n- ./my-website');
        if (folderPath && folderPath.trim()) {
            document.getElementById('folderPath').value = folderPath.trim();
            this.setFolder(folderPath.trim());
        }
    }

    handleFolderSelection(event) {
        const files = event.target.files;
        if (files.length > 0) {
            // Get the folder path from the first file
            const folderPath = files[0].webkitRelativePath.split('/')[0];
            
            // For web browsers, we'll use the folder name as a relative path
            // and let the backend handle the path resolution
            let fullPath = folderPath;
            
            // Try to get the full path if available (for desktop apps)
            if (files[0].path) {
                fullPath = files[0].path.split(folderPath)[0] + folderPath;
            }
            
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

    async startServer(serverName) {
        try {
            const response = await fetch('/api/start_server', {
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
            this.showNotification('Error starting server: ' + error.message, 'error');
        }
    }

    async deleteServer(serverName) {
        if (!confirm(`Are you sure you want to delete server "${serverName}"? This action cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch('/api/delete_server', {
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
            this.showNotification('Error deleting server: ' + error.message, 'error');
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
            
            // Create server card container
            const serverCard = document.createElement('div');
            serverCard.className = `server-card ${server.status.toLowerCase()}`;
            
            // Create header
            const header = document.createElement('div');
            header.className = 'server-header';
            
            const serverInfo = document.createElement('div');
            serverInfo.className = 'server-info';
            
            const serverName = document.createElement('h3');
            serverName.style.cssText = 'color: var(--text-primary); font-weight: 600;';
            serverName.textContent = server.name;
            
            const serverFolder = document.createElement('p');
            serverFolder.style.cssText = 'color: var(--text-secondary); font-weight: 500;';
            serverFolder.textContent = server.folder.split('/').pop();
            
            serverInfo.appendChild(serverName);
            serverInfo.appendChild(serverFolder);
            
            const serverStatus = document.createElement('div');
            serverStatus.className = 'server-status';
            
            const statusBadge = document.createElement('span');
            statusBadge.className = `status-badge status-${server.status.toLowerCase()}`;
            statusBadge.textContent = server.status;
            
            serverStatus.appendChild(statusBadge);
            header.appendChild(serverInfo);
            header.appendChild(serverStatus);
            
            // Create details
            const details = document.createElement('div');
            details.className = 'server-details';
            
            const detailsData = [
                { label: 'Port', value: server.port },
                { label: 'Type', value: server.type },
                { label: 'Started', value: server.start_time },
                { label: 'URL', value: `http://localhost:${server.port}` }
            ];
            
            detailsData.forEach(item => {
                const detailItem = document.createElement('div');
                detailItem.className = 'detail-item';
                
                const label = document.createElement('div');
                label.className = 'detail-label';
                label.textContent = item.label;
                
                const value = document.createElement('div');
                value.className = 'detail-value';
                value.style.cssText = 'color: var(--text-primary); font-weight: 600;';
                value.textContent = item.value;
                
                detailItem.appendChild(label);
                detailItem.appendChild(value);
                details.appendChild(detailItem);
            });
            
            // Create actions container
            const actions = document.createElement('div');
            actions.className = 'server-actions';
            
            // Button 1: View Logs
            const viewLogsBtn = document.createElement('button');
            viewLogsBtn.className = 'action-btn view-logs';
            viewLogsBtn.title = 'View Server Logs';
            viewLogsBtn.innerHTML = '<i class="fas fa-file-alt"></i> View Logs';
            viewLogsBtn.onclick = () => this.showLogs(server.name);
            
            // Button 2: Open Browser
            const openBrowserBtn = document.createElement('button');
            openBrowserBtn.className = 'action-btn open-browser';
            openBrowserBtn.title = 'Open in Browser';
            openBrowserBtn.innerHTML = '<i class="fas fa-external-link-alt"></i> Open Browser';
            openBrowserBtn.onclick = () => this.openServerInBrowser(server.name);
            
            // Button 3: Start/Stop Server
            const startStopBtn = document.createElement('button');
            if (server.status === 'Running') {
                startStopBtn.className = 'action-btn stop-server';
                startStopBtn.title = 'Stop Server';
                startStopBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Server';
                startStopBtn.onclick = () => this.stopServer(server.name);
            } else {
                startStopBtn.className = 'action-btn start-server';
                startStopBtn.title = 'Start Server';
                startStopBtn.innerHTML = '<i class="fas fa-play"></i> Start Server';
                startStopBtn.onclick = () => this.startServer(server.name);
            }
            
            // Button 4: Delete Server
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'action-btn delete-server';
            deleteBtn.title = 'Delete Server';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Delete';
            deleteBtn.onclick = () => this.deleteServer(server.name);
            
            // Add all buttons to actions container
            actions.appendChild(viewLogsBtn);
            actions.appendChild(openBrowserBtn);
            actions.appendChild(startStopBtn);
            actions.appendChild(deleteBtn);
            
            // Assemble the card
            serverCard.appendChild(header);
            serverCard.appendChild(details);
            serverCard.appendChild(actions);
            
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