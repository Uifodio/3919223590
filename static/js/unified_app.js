// Unified Server Administrator - Professional JavaScript Application

class UnifiedServerAdmin {
    constructor() {
        this.currentServer = null;
        this.autoRefreshInterval = null;
        this.logsInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadServers();
        this.startAutoRefresh();
        this.checkSystemRequirements();
    }

    bindEvents() {
        // Form controls
        const createServerBtn = document.getElementById('createServerBtn');
        if (createServerBtn) {
            createServerBtn.addEventListener('click', () => this.createServer());
        }

        const refreshAllBtn = document.getElementById('refreshAllBtn');
        if (refreshAllBtn) {
            refreshAllBtn.addEventListener('click', () => this.refreshAll());
        }

        const browsePathBtn = document.getElementById('browsePathBtn');
        if (browsePathBtn) {
            browsePathBtn.addEventListener('click', () => this.browsePath());
        }

        // System info and settings
        const systemInfoBtn = document.getElementById('systemInfoBtn');
        if (systemInfoBtn) {
            systemInfoBtn.addEventListener('click', () => this.showSystemInfo());
        }

        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.showSettings());
        }

        // Modal controls
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal')));
        });

        // Log modal events
        const refreshLogsBtn = document.getElementById('refreshLogsBtn');
        if (refreshLogsBtn) {
            refreshLogsBtn.addEventListener('click', () => this.refreshLogs());
        }

        const copyLogsBtn = document.getElementById('copyLogsBtn');
        if (copyLogsBtn) {
            copyLogsBtn.addEventListener('click', () => this.copyLogs());
        }

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target.classList && e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Escape key closes modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeAllModals();
        });

        // Port validation
        const portInput = document.getElementById('serverPort');
        if (portInput) {
            portInput.addEventListener('input', (ev) => this.validatePort(ev.target));
        }
    }

    // Server Management
    async createServer() {
        const name = document.getElementById('serverName').value.trim();
        const serverType = document.getElementById('serverType').value;
        const port = parseInt(document.getElementById('serverPort').value);
        const sitePath = document.getElementById('sitePath').value.trim();
        const domain = document.getElementById('domain').value.trim() || null;

        if (!name) {
            this.showNotification('Server name is required', 'error');
            return;
        }

        if (!sitePath) {
            this.showNotification('Site path is required', 'error');
            return;
        }

        if (!port || port < 1000 || port > 65535) {
            this.showNotification('Port must be between 1000 and 65535', 'error');
            return;
        }

        const createBtn = document.getElementById('createServerBtn');
        const originalText = createBtn ? createBtn.innerHTML : null;
        
        if (createBtn) {
            createBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
            createBtn.disabled = true;
        }

        try {
            const response = await fetch('/api/add_server', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    type: serverType,
                    port,
                    site_path: sitePath,
                    domain
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(result.message, 'success');
                this.clearForm();
                await this.loadServers();
            } else {
                this.showNotification(result.message || 'Failed to create server', 'error');
            }
        } catch (error) {
            this.showNotification('Error creating server: ' + (error.message || error), 'error');
        } finally {
            if (createBtn) {
                createBtn.innerHTML = originalText;
                createBtn.disabled = false;
            }
        }
    }

    async deleteServer(serverName) {
        if (!confirm(`Are you sure you want to delete server "${serverName}"? This action cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch('/api/delete_server', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: serverName })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(result.message, 'success');
                await this.loadServers();
            } else {
                this.showNotification(result.message || 'Failed to delete server', 'error');
            }
        } catch (error) {
            this.showNotification('Error deleting server: ' + (error.message || error), 'error');
        }
    }

    // Server Listing
    async loadServers() {
        try {
            const response = await fetch('/api/servers');
            const servers = await response.json();
            this.renderServers(servers);
            this.updateStats(servers);
        } catch (error) {
            console.error('Error loading servers:', error);
            this.showNotification('Error loading servers', 'error');
        }
    }

    renderServers(servers) {
        const container = document.getElementById('serversContainer');
        container.innerHTML = '';

        if (!servers || Object.keys(servers).length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-server"></i>
                    <h3>No servers configured</h3>
                    <p>Create your first server to get started</p>
                </div>
            `;
            return;
        }

        Object.values(servers).forEach(server => {
            const serverCard = document.createElement('div');
            serverCard.className = `server-card ${server.status.toLowerCase()}`;

            // Header
            const header = document.createElement('div');
            header.className = 'server-header';

            const serverInfo = document.createElement('div');
            serverInfo.className = 'server-info';

            const serverName = document.createElement('h3');
            serverName.textContent = server.name;

            const serverType = document.createElement('p');
            serverType.textContent = `${server.type} Server`;

            serverInfo.appendChild(serverName);
            serverInfo.appendChild(serverType);

            const serverStatus = document.createElement('div');
            serverStatus.className = 'server-status';

            const statusBadge = document.createElement('span');
            statusBadge.className = `status-badge status-${(server.status || 'Stopped').toLowerCase()}`;
            statusBadge.textContent = server.status || 'Stopped';

            serverStatus.appendChild(statusBadge);
            header.appendChild(serverInfo);
            header.appendChild(serverStatus);

            // Details
            const details = document.createElement('div');
            details.className = 'server-details';
            
            const detailsData = [
                { label: 'Port', value: server.port || '—' },
                { label: 'Type', value: server.type || 'Static' },
                { label: 'Started', value: server.start_time || '—' },
                { label: 'Domain', value: server.domain || '—' }
            ];

            detailsData.forEach(item => {
                const detailItem = document.createElement('div');
                detailItem.className = 'detail-item';
                
                const label = document.createElement('div');
                label.className = 'detail-label';
                label.textContent = item.label;
                
                const value = document.createElement('div');
                value.className = 'detail-value';
                value.textContent = item.value;
                
                detailItem.appendChild(label);
                detailItem.appendChild(value);
                details.appendChild(detailItem);
            });

            // Actions
            const actions = document.createElement('div');
            actions.className = 'server-actions';

            const viewLogsBtn = document.createElement('button');
            viewLogsBtn.className = 'action-btn view-logs';
            viewLogsBtn.title = 'View Server Logs';
            viewLogsBtn.innerHTML = '<i class="fas fa-file-alt"></i> View Logs';
            viewLogsBtn.onclick = () => this.showLogs(server.name);

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'action-btn delete-server';
            deleteBtn.title = 'Delete Server';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Delete';
            deleteBtn.onclick = () => this.deleteServer(server.name);

            actions.appendChild(viewLogsBtn);
            actions.appendChild(deleteBtn);

            serverCard.appendChild(header);
            serverCard.appendChild(details);
            serverCard.appendChild(actions);
            container.appendChild(serverCard);
        });
    }

    updateStats(servers) {
        const totalServers = Object.keys(servers).length;
        const runningServers = Object.values(servers).filter(s => s.status === 'Running').length;
        const phpServers = Object.values(servers).filter(s => s.type === 'PHP').length;
        const nodeServers = Object.values(servers).filter(s => s.type === 'Node.js').length;

        const totalElement = document.getElementById('totalServers');
        const runningElement = document.getElementById('runningServers');
        const phpElement = document.getElementById('phpServers');
        const nodeElement = document.getElementById('nodeServers');

        if (totalElement) totalElement.textContent = totalServers;
        if (runningElement) runningElement.textContent = runningServers;
        if (phpElement) phpElement.textContent = phpServers;
        if (nodeElement) nodeElement.textContent = nodeServers;

        const serverCountElement = document.getElementById('serverCount');
        if (serverCountElement) {
            serverCountElement.textContent = `${totalServers} server${totalServers !== 1 ? 's' : ''}`;
        }
    }

    // Logs Management
    async showLogs(serverName) {
        this.currentServer = serverName;
        const title = document.getElementById('logModalTitle');
        if (title) {
            title.innerHTML = `<i class="fas fa-file-alt"></i> Logs - ${serverName}`;
        }
        
        const modal = document.getElementById('logModal');
        if (modal) {
            modal.classList.add('show');
        }
        
        await this.refreshLogs();
        this.startLogsAutoRefresh();
    }

    async refreshLogs() {
        if (!this.currentServer) return;
        
        try {
            const response = await fetch(`/api/server_logs/${encodeURIComponent(this.currentServer)}`);
            const data = await response.json();
            const logContent = document.getElementById('logContent');
            
            if (!logContent) return;
            
            logContent.innerHTML = '';
            
            if (!data.logs || data.logs.length === 0) {
                logContent.textContent = 'No logs available yet...';
                return;
            }
            
            data.logs.forEach(log => {
                const logLine = document.createElement('div');
                const timestamp = log.timestamp || new Date().toLocaleTimeString();
                const message = log.message || '';
                const type = log.type || 'info';
                
                logLine.innerHTML = `
                    <span style="color: var(--text-muted);">[${timestamp}]</span> 
                    <span style="color: ${type === 'error' ? 'var(--error)' : 'var(--text-primary)'};">${this.escapeHtml(message)}</span>
                `;
                logContent.appendChild(logLine);
            });
            
            logContent.scrollTop = logContent.scrollHeight;
        } catch (error) {
            console.error('Error loading logs:', error);
            const logContent = document.getElementById('logContent');
            if (logContent) {
                logContent.textContent = 'Error loading logs: ' + (error.message || error);
            }
        }
    }

    startLogsAutoRefresh() {
        this.stopLogsAutoRefresh();
        this.logsInterval = setInterval(() => this.refreshLogs(), 2000);
        
        const liveBadge = document.getElementById('logLiveBadge');
        if (liveBadge) {
            liveBadge.style.display = 'flex';
        }
    }

    stopLogsAutoRefresh() {
        if (this.logsInterval) {
            clearInterval(this.logsInterval);
            this.logsInterval = null;
        }
        
        const liveBadge = document.getElementById('logLiveBadge');
        if (liveBadge) {
            liveBadge.style.display = 'none';
        }
    }

    async copyLogs() {
        const logContent = document.getElementById('logContent');
        if (!logContent) {
            this.showNotification('No logs to copy', 'warning');
            return;
        }
        
        try {
            await navigator.clipboard.writeText(logContent.innerText);
            this.showNotification('Logs copied to clipboard', 'success');
        } catch (error) {
            this.showNotification('Failed to copy logs', 'error');
        }
    }

    // System Information
    async showSystemInfo() {
        try {
            const response = await fetch('/api/system_info');
            const info = await response.json();
            const content = document.getElementById('systemInfoContent');
            
            if (!content) return;
            
            content.innerHTML = `
                <h4>System Information</h4>
                <p><strong>Operating System:</strong> ${this.escapeHtml(info.os || 'Unknown')}</p>
                <p><strong>CPU Cores:</strong> ${this.escapeHtml(info.cpu_cores || 'Unknown')}</p>
                <p><strong>Python Version:</strong> ${this.escapeHtml(info.python_version || 'Unknown')}</p>
                <p><strong>Active Servers:</strong> ${this.escapeHtml(String(info.active_servers || '0'))}</p>
                <p><strong>Sites Folder:</strong> ${this.escapeHtml(info.sites_folder || 'Unknown')}</p>
                <p><strong>PHP Available:</strong> ${info.php_available ? 'Yes' : 'No'}</p>
                <p><strong>Node.js Available:</strong> ${info.node_available ? 'Yes' : 'No'}</p>
                <p><strong>Nginx Available:</strong> ${info.nginx_available ? 'Yes' : 'No'}</p>
            `;
            
            document.getElementById('systemModal').classList.add('show');
        } catch (error) {
            this.showNotification('Error loading system info: ' + (error.message || error), 'error');
        }
    }

    showSettings() {
        document.getElementById('settingsModal').classList.add('show');
    }

    // Utility Functions
    async refreshAll() {
        await this.loadServers();
        this.updateStatus('Refreshed', 'success');
    }

    async checkSystemRequirements() {
        try {
            const response = await fetch('/api/system_info');
            const info = await response.json();
            
            if (!info.nginx_available) {
                this.showNotification('Nginx is not available - server creation will not work', 'error');
            }
            
            if (!info.php_available) {
                this.showNotification('PHP is not available - PHP servers will not work', 'warning');
            }
            
            if (!info.node_available) {
                this.showNotification('Node.js is not available - Node.js servers will not work', 'warning');
            }
        } catch (error) {
            console.error('Error checking system requirements:', error);
        }
    }

    browsePath() {
        // For now, just show a prompt. In a real implementation, you might use a file picker
        const path = prompt('Enter the full path to your website folder:');
        if (path && path.trim()) {
            document.getElementById('sitePath').value = path.trim();
        }
    }

    clearForm() {
        document.getElementById('serverName').value = '';
        document.getElementById('serverType').value = 'Static';
        document.getElementById('serverPort').value = '8000';
        document.getElementById('sitePath').value = '';
        document.getElementById('domain').value = '';
    }

    validatePort(input) {
        const port = parseInt(input.value);
        if (port < 1000 || port > 65535) {
            input.style.borderColor = 'var(--error)';
        } else {
            input.style.borderColor = 'var(--border-primary)';
        }
    }

    // Modal Management
    closeModal(modal) {
        if (modal) {
            modal.classList.remove('show');
        }
        
        if (modal && modal.id === 'logModal') {
            this.stopLogsAutoRefresh();
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(m => m.classList.remove('show'));
        this.stopLogsAutoRefresh();
    }

    updateStatus(text, type) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (!statusText) return;
        
        statusText.textContent = text;
        
        if (statusDot) {
            if (type === 'success') statusDot.style.background = 'var(--success)';
            else if (type === 'error') statusDot.style.background = 'var(--error)';
            else if (type === 'warning') statusDot.style.background = 'var(--warning)';
            else statusDot.style.background = 'var(--info)';
        }
        
        // Reset after 3 seconds
        setTimeout(() => {
            if (statusText) statusText.textContent = 'Ready';
            if (statusDot) statusDot.style.background = 'var(--success)';
        }, 3000);
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        if (!container) {
            console.log(`[${type.toUpperCase()}] ${message}`);
            return;
        }
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        }[type] || 'fa-info-circle';
        
        notification.innerHTML = `<i class="fas ${icon}"></i><span>${this.escapeHtml(message)}</span>`;
        container.appendChild(notification);
        
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

    // Auto Refresh
    startAutoRefresh() {
        this.loadServers();
        this.autoRefreshInterval = setInterval(() => {
            this.loadServers();
        }, 30000); // 30 seconds
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    escapeHtml(unsafe) {
        return String(unsafe)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize application
let unifiedServerAdmin;

document.addEventListener('DOMContentLoaded', () => {
    unifiedServerAdmin = new UnifiedServerAdmin();
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    if (unifiedServerAdmin) {
        unifiedServerAdmin.stopAutoRefresh();
    }
});