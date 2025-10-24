// Professional Server Manager - Main JavaScript
class ServerManager {
    constructor() {
        this.servers = new Map();
        this.currentSection = 'dashboard';
        this.availablePorts = new Set();
        this.initializePorts();
        this.initializeEventListeners();
        this.loadServers();
        this.updateStats();
    }

    initializePorts() {
        // Reserve ports 3000-3009 for our servers
        for (let i = 3000; i <= 3009; i++) {
            this.availablePorts.add(i);
        }
    }

    initializeEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.showSection(section);
            });
        });

        // New server button
        document.getElementById('newServerBtn').addEventListener('click', () => {
            this.showNewServerModal();
        });

        // Modal close
        document.querySelector('.modal-close').addEventListener('click', () => {
            this.hideNewServerModal();
        });

        // Modal backdrop click
        document.getElementById('newServerModal').addEventListener('click', (e) => {
            if (e.target.id === 'newServerModal') {
                this.hideNewServerModal();
            }
        });

        // Form submission
        document.getElementById('newServerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createServer();
        });

        // Auto-refresh stats every 5 seconds
        setInterval(() => {
            this.updateStats();
        }, 5000);

        // Auto-assign port
        document.getElementById('serverType').addEventListener('change', () => {
            this.autoAssignPort();
        });
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        document.getElementById(sectionName).classList.add('active');

        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            servers: 'Servers',
            logs: 'Logs',
            settings: 'Settings'
        };

        const subtitles = {
            dashboard: 'Monitor and manage your local servers',
            servers: 'Manage your local development servers',
            logs: 'Monitor server logs and system events',
            settings: 'Configure your server environment'
        };

        document.getElementById('pageTitle').textContent = titles[sectionName];
        document.getElementById('pageSubtitle').textContent = subtitles[sectionName];

        this.currentSection = sectionName;

        // Load section-specific data
        if (sectionName === 'servers') {
            this.renderServers();
        } else if (sectionName === 'logs') {
            this.loadLogs();
        }
    }

    showNewServerModal(type = null) {
        const modal = document.getElementById('newServerModal');
        const form = document.getElementById('newServerForm');
        
        // Reset form
        form.reset();
        
        // Set server type if provided
        if (type) {
            document.getElementById('serverType').value = type;
        }
        
        // Auto-assign port
        this.autoAssignPort();
        
        // Show modal
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hideNewServerModal() {
        const modal = document.getElementById('newServerModal');
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    autoAssignPort() {
        const portInput = document.getElementById('serverPort');
        const nextPort = this.getNextAvailablePort();
        if (nextPort) {
            portInput.value = nextPort;
        }
    }

    getNextAvailablePort() {
        for (const port of this.availablePorts) {
            if (!this.servers.has(port)) {
                return port;
            }
        }
        return null;
    }

    createServer() {
        const formData = {
            name: document.getElementById('serverName').value,
            type: document.getElementById('serverType').value,
            port: parseInt(document.getElementById('serverPort').value),
            directory: document.getElementById('serverDirectory').value,
            description: document.getElementById('serverDescription').value
        };

        // Validate form
        if (!formData.name || !formData.type || !formData.port || !formData.directory) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        // Check if port is available
        if (this.servers.has(formData.port)) {
            this.showNotification('Port is already in use', 'error');
            return;
        }

        // Create server
        const server = {
            id: Date.now(),
            ...formData,
            status: 'stopped',
            startTime: null,
            process: null
        };

        this.servers.set(formData.port, server);
        this.saveServers();
        this.updateStats();
        this.renderServers();
        this.hideNewServerModal();
        this.showNotification(`Server "${formData.name}" created successfully`, 'success');
        this.addActivity(`Created server "${formData.name}" on port ${formData.port}`);
    }

    async startServer(port) {
        const server = this.servers.get(port);
        if (!server) return;

        try {
            // Simulate server start (in real implementation, this would start actual processes)
            server.status = 'running';
            server.startTime = new Date();
            server.process = { pid: Math.floor(Math.random() * 10000) };

            this.servers.set(port, server);
            this.saveServers();
            this.updateStats();
            this.renderServers();
            this.showNotification(`Server "${server.name}" started on port ${port}`, 'success');
            this.addActivity(`Started server "${server.name}" on port ${port}`);
            this.addLog(`[INFO] Server "${server.name}" started on port ${port}`);

            // Simulate opening server in browser
            setTimeout(() => {
                this.addLog(`[INFO] Server "${server.name}" is responding on http://localhost:${port}`);
            }, 1000);

        } catch (error) {
            this.showNotification(`Failed to start server: ${error.message}`, 'error');
            this.addLog(`[ERROR] Failed to start server "${server.name}": ${error.message}`);
        }
    }

    async stopServer(port) {
        const server = this.servers.get(port);
        if (!server) return;

        try {
            // Simulate server stop
            server.status = 'stopped';
            server.startTime = null;
            server.process = null;

            this.servers.set(port, server);
            this.saveServers();
            this.updateStats();
            this.renderServers();
            this.showNotification(`Server "${server.name}" stopped`, 'success');
            this.addActivity(`Stopped server "${server.name}" on port ${port}`);
            this.addLog(`[INFO] Server "${server.name}" stopped on port ${port}`);

        } catch (error) {
            this.showNotification(`Failed to stop server: ${error.message}`, 'error');
            this.addLog(`[ERROR] Failed to stop server "${server.name}": ${error.message}`);
        }
    }

    async deleteServer(port) {
        const server = this.servers.get(port);
        if (!server) return;

        if (confirm(`Are you sure you want to delete server "${server.name}"?`)) {
            this.servers.delete(port);
            this.availablePorts.add(port);
            this.saveServers();
            this.updateStats();
            this.renderServers();
            this.showNotification(`Server "${server.name}" deleted`, 'success');
            this.addActivity(`Deleted server "${server.name}"`);
        }
    }

    stopAllServers() {
        if (confirm('Are you sure you want to stop all servers?')) {
            let stoppedCount = 0;
            this.servers.forEach((server, port) => {
                if (server.status === 'running') {
                    this.stopServer(port);
                    stoppedCount++;
                }
            });
            this.showNotification(`Stopped ${stoppedCount} servers`, 'success');
        }
    }

    renderServers() {
        const grid = document.getElementById('serversGrid');
        if (this.servers.size === 0) {
            grid.innerHTML = `
                <div class="card" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                    <div class="card-content">
                        <i class="fas fa-server" style="font-size: 48px; color: var(--text-tertiary); margin-bottom: 16px;"></i>
                        <h3 style="margin-bottom: 8px;">No servers created</h3>
                        <p style="color: var(--text-secondary); margin-bottom: 24px;">Create your first server to get started</p>
                        <button class="btn btn-primary" onclick="serverManager.showNewServerModal()">
                            <i class="fas fa-plus"></i>
                            Create Server
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        grid.innerHTML = '';
        this.servers.forEach((server, port) => {
            const card = this.createServerCard(server, port);
            grid.appendChild(card);
        });
    }

    createServerCard(server, port) {
        const card = document.createElement('div');
        card.className = 'server-card';
        
        const uptime = server.startTime ? 
            Math.floor((new Date() - new Date(server.startTime)) / 1000) : 0;
        
        card.innerHTML = `
            <div class="server-header">
                <div class="server-name">
                    <i class="fas fa-server"></i>
                    ${server.name}
                </div>
                <div class="server-status ${server.status}">
                    ${server.status.toUpperCase()}
                </div>
            </div>
            
            <div class="server-details">
                <div class="server-detail">
                    <span>Type:</span>
                    <span>${server.type.toUpperCase()}</span>
                </div>
                <div class="server-detail">
                    <span>Port:</span>
                    <span>${port}</span>
                </div>
                <div class="server-detail">
                    <span>Directory:</span>
                    <span>${server.directory}</span>
                </div>
                ${server.status === 'running' ? `
                <div class="server-detail">
                    <span>Uptime:</span>
                    <span>${this.formatUptime(uptime)}</span>
                </div>
                ` : ''}
                ${server.description ? `
                <div class="server-detail">
                    <span>Description:</span>
                    <span>${server.description}</span>
                </div>
                ` : ''}
            </div>
            
            <div class="server-actions">
                ${server.status === 'running' ? `
                    <button class="btn btn-outline btn-sm" onclick="serverManager.openServer(${port})">
                        <i class="fas fa-external-link-alt"></i>
                        Open
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="serverManager.stopServer(${port})">
                        <i class="fas fa-stop"></i>
                        Stop
                    </button>
                ` : `
                    <button class="btn btn-primary btn-sm" onclick="serverManager.startServer(${port})">
                        <i class="fas fa-play"></i>
                        Start
                    </button>
                `}
                <button class="btn btn-outline btn-sm" onclick="serverManager.editServer(${port})">
                    <i class="fas fa-edit"></i>
                    Edit
                </button>
                <button class="btn btn-danger btn-sm" onclick="serverManager.deleteServer(${port})">
                    <i class="fas fa-trash"></i>
                    Delete
                </button>
            </div>
        `;
        
        return card;
    }

    openServer(port) {
        const server = this.servers.get(port);
        if (server && server.status === 'running') {
            window.open(`http://localhost:${port}`, '_blank');
            this.addActivity(`Opened server "${server.name}" in browser`);
        }
    }

    editServer(port) {
        const server = this.servers.get(port);
        if (!server) return;

        // Pre-fill form with server data
        document.getElementById('serverName').value = server.name;
        document.getElementById('serverType').value = server.type;
        document.getElementById('serverPort').value = port;
        document.getElementById('serverDirectory').value = server.directory;
        document.getElementById('serverDescription').value = server.description || '';

        this.showNewServerModal();
    }

    updateStats() {
        const totalServers = this.servers.size;
        const runningServers = Array.from(this.servers.values()).filter(s => s.status === 'running').length;
        const stoppedServers = totalServers - runningServers;

        document.getElementById('totalServers').textContent = totalServers;
        document.getElementById('runningServers').textContent = runningServers;
        document.getElementById('stoppedServers').textContent = stoppedServers;
        document.getElementById('serverCount').textContent = totalServers;

        // Simulate memory usage
        const memoryUsage = Math.floor(Math.random() * 30) + 20;
        document.getElementById('memoryUsage').textContent = `${memoryUsage}%`;
    }

    addActivity(message) {
        const activityList = document.getElementById('activityList');
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-icon">
                <i class="fas fa-info-circle"></i>
            </div>
            <div class="activity-content">
                <p>${message}</p>
                <span class="activity-time">Just now</span>
            </div>
        `;
        activityList.insertBefore(activityItem, activityList.firstChild);

        // Keep only last 10 activities
        while (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
    }

    addLog(message) {
        const logViewer = document.getElementById('logViewer');
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        
        const now = new Date();
        const timestamp = now.toISOString().replace('T', ' ').substring(0, 19);
        const level = message.includes('[ERROR]') ? 'error' : 
                     message.includes('[WARN]') ? 'warn' : 'info';
        
        logEntry.innerHTML = `
            <span class="log-time">[${timestamp}]</span>
            <span class="log-level ${level}">[${level.toUpperCase()}]</span>
            <span class="log-message">${message}</span>
        `;
        
        logViewer.appendChild(logEntry);
        logViewer.scrollTop = logViewer.scrollHeight;

        // Keep only last 100 log entries
        while (logViewer.children.length > 100) {
            logViewer.removeChild(logViewer.firstChild);
        }
    }

    loadLogs() {
        // In a real implementation, this would load logs from files
        this.addLog('[INFO] Log viewer initialized');
    }

    clearLogs() {
        if (confirm('Are you sure you want to clear all logs?')) {
            document.getElementById('logViewer').innerHTML = '';
            this.addLog('[INFO] Logs cleared');
        }
    }

    exportLogs() {
        const logs = Array.from(document.querySelectorAll('.log-entry')).map(entry => entry.textContent).join('\n');
        const blob = new Blob([logs], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `server-logs-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    refreshServers() {
        this.renderServers();
        this.updateStats();
        this.showNotification('Servers refreshed', 'success');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-sm);
            padding: 16px 20px;
            color: var(--text-primary);
            box-shadow: var(--shadow-lg);
            z-index: 3000;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 'info-circle';
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <i class="fas fa-${icon}" style="color: var(--accent-${type === 'success' ? 'primary' : type === 'error' ? 'danger' : 'secondary'});"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }

    saveServers() {
        const serversArray = Array.from(this.servers.entries()).map(([port, server]) => ({
            port,
            ...server,
            process: null // Don't save process reference
        }));
        localStorage.setItem('serverManager_servers', JSON.stringify(serversArray));
    }

    loadServers() {
        const saved = localStorage.getItem('serverManager_servers');
        if (saved) {
            try {
                const serversArray = JSON.parse(saved);
                serversArray.forEach(({ port, ...server }) => {
                    server.status = 'stopped'; // Reset status on load
                    server.startTime = null;
                    server.process = null;
                    this.servers.set(port, server);
                });
            } catch (error) {
                console.error('Failed to load saved servers:', error);
            }
        }
    }
}

// Global functions for HTML onclick handlers
function showNewServerModal(type = null) {
    serverManager.showNewServerModal(type);
}

function stopAllServers() {
    serverManager.stopAllServers();
}

function refreshServers() {
    serverManager.refreshServers();
}

function clearLogs() {
    serverManager.clearLogs();
}

function exportLogs() {
    serverManager.exportLogs();
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
let serverManager;
document.addEventListener('DOMContentLoaded', () => {
    serverManager = new ServerManager();
    
    // Add some sample data for demonstration
    if (serverManager.servers.size === 0) {
        serverManager.addLog('[INFO] Professional Server Manager initialized');
        serverManager.addLog('[INFO] Ready to manage local development servers');
        serverManager.addActivity('System initialized successfully');
    }
});