// GitHub-inspired Professional Server Admin JavaScript

class ServerAdmin {
    constructor() {
        this.servers = {};
        this.currentLogsServer = null;
        this.autoRefreshInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadServers();
        this.startAutoRefresh();
        this.hideLoading();
    }

    bindEvents() {
        // Header actions
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshServers());
        document.getElementById('addServerBtn').addEventListener('click', () => this.showAddServerModal());

        // Modal events
        this.bindModalEvents();

        // Quick actions
        document.getElementById('uploadZipBtn').addEventListener('click', () => this.showUploadModal('zip'));
        document.getElementById('uploadFolderBtn').addEventListener('click', () => this.showUploadModal('folder'));
        document.getElementById('systemInfoBtn').addEventListener('click', () => this.showSystemInfo());
        document.getElementById('checkPhpBtn').addEventListener('click', () => this.checkPHP());

        // Upload events
        this.bindUploadEvents();
    }

    bindModalEvents() {
        // Add Server Modal
        const addServerModal = document.getElementById('addServerModal');
        const addServerForm = document.getElementById('addServerForm');
        const closeAddServerModal = document.getElementById('closeAddServerModal');
        const cancelAddServer = document.getElementById('cancelAddServer');
        const browseFolderBtn = document.getElementById('browseFolderBtn');

        closeAddServerModal.addEventListener('click', () => this.hideModal('addServerModal'));
        cancelAddServer.addEventListener('click', () => this.hideModal('addServerModal'));
        browseFolderBtn.addEventListener('click', () => this.browseFolder());
        addServerForm.addEventListener('submit', (e) => this.handleAddServer(e));

        // Upload Modal
        const uploadModal = document.getElementById('uploadModal');
        const closeUploadModal = document.getElementById('closeUploadModal');
        const cancelUpload = document.getElementById('cancelUpload');

        closeUploadModal.addEventListener('click', () => this.hideModal('uploadModal'));
        cancelUpload.addEventListener('click', () => this.hideModal('uploadModal'));

        // Logs Modal
        const logsModal = document.getElementById('logsModal');
        const closeLogsModal = document.getElementById('closeLogsModal');
        const copyLogsBtn = document.getElementById('copyLogsBtn');
        const clearLogsBtn = document.getElementById('clearLogsBtn');

        closeLogsModal.addEventListener('click', () => this.hideModal('logsModal'));
        copyLogsBtn.addEventListener('click', () => this.copyLogs());
        clearLogsBtn.addEventListener('click', () => this.clearLogs());

        // System Info Modal
        const systemInfoModal = document.getElementById('systemInfoModal');
        const closeSystemInfoModal = document.getElementById('closeSystemInfoModal');

        closeSystemInfoModal.addEventListener('click', () => this.hideModal('systemInfoModal'));

        // Close modals on backdrop click
        [addServerModal, uploadModal, logsModal, systemInfoModal].forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }

    bindUploadEvents() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            this.handleFileSelection(files);
        });

        // File input
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files);
        });

        // Upload button
        uploadBtn.addEventListener('click', () => this.uploadFiles());
    }

    async loadServers() {
        try {
            this.showLoading();
            const response = await fetch('/api/servers');
            const data = await response.json();
            this.servers = data;
            this.renderServers();
            this.updateStats();
            this.hideLoading();
        } catch (error) {
            console.error('Failed to load servers:', error);
            this.showToast('Error loading servers', 'error');
            this.hideLoading();
        }
    }

    async refreshServers() {
        try {
            const response = await fetch('/api/refresh', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                await this.loadServers();
                this.showToast('Servers refreshed', 'success');
            } else {
                this.showToast('Refresh failed: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('Failed to refresh servers:', error);
            this.showToast('Refresh failed', 'error');
        }
    }

    renderServers() {
        const serversGrid = document.getElementById('serversGrid');
        serversGrid.innerHTML = '';

        if (Object.keys(this.servers).length === 0) {
            serversGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-server"></i>
                    <h3>No servers found</h3>
                    <p>Add your first server to get started</p>
                    <button class="btn btn-primary" onclick="serverAdmin.showAddServerModal()">
                        <i class="fas fa-plus"></i>
                        Add Server
                    </button>
                </div>
            `;
            return;
        }

        Object.entries(this.servers).forEach(([name, server]) => {
            const serverCard = this.createServerCard(name, server);
            serversGrid.appendChild(serverCard);
        });
    }

    createServerCard(name, server) {
        const card = document.createElement('div');
        card.className = 'server-card fade-in';
        
        const statusClass = server.status.toLowerCase();
        const statusIcon = server.status === 'Running' ? 'play-circle' : 'stop-circle';
        
        card.innerHTML = `
            <div class="server-header">
                <h3 class="server-name">${this.escapeHtml(name)}</h3>
                <span class="server-status ${statusClass}">
                    <i class="fas fa-${statusIcon}"></i>
                    ${server.status}
                </span>
            </div>
            <div class="server-info">
                <div class="server-info-item">
                    <i class="fas fa-folder"></i>
                    <span>${this.escapeHtml(server.folder || 'N/A')}</span>
                </div>
                <div class="server-info-item">
                    <i class="fas fa-network-wired"></i>
                    <span>Port: ${server.port || 'N/A'}</span>
                </div>
                <div class="server-info-item">
                    <i class="fas fa-cog"></i>
                    <span>Type: ${server.type || 'HTTP'}</span>
                </div>
                ${server.start_time ? `
                <div class="server-info-item">
                    <i class="fas fa-clock"></i>
                    <span>Started: ${this.escapeHtml(server.start_time)}</span>
                </div>
                ` : ''}
            </div>
            <div class="server-actions">
                ${server.status === 'Running' ? `
                    <button class="btn btn-ghost btn-sm" onclick="serverAdmin.stopServer('${name}')">
                        <i class="fas fa-stop"></i>
                        Stop
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="serverAdmin.openBrowser('${name}')">
                        <i class="fas fa-external-link-alt"></i>
                        Open
                    </button>
                ` : `
                    <button class="btn btn-primary btn-sm" onclick="serverAdmin.startServer('${name}')">
                        <i class="fas fa-play"></i>
                        Start
                    </button>
                `}
                <button class="btn btn-ghost btn-sm" onclick="serverAdmin.viewLogs('${name}')">
                    <i class="fas fa-file-alt"></i>
                    Logs
                </button>
                <button class="btn btn-danger btn-sm" onclick="serverAdmin.deleteServer('${name}')">
                    <i class="fas fa-trash"></i>
                    Delete
                </button>
            </div>
        `;
        
        return card;
    }

    updateStats() {
        const totalServers = Object.keys(this.servers).length;
        const runningServers = Object.values(this.servers).filter(s => s.status === 'Running').length;
        const stoppedServers = totalServers - runningServers;

        document.getElementById('totalServers').textContent = totalServers;
        document.getElementById('runningServers').textContent = runningServers;
        document.getElementById('stoppedServers').textContent = stoppedServers;
        document.getElementById('totalSites').textContent = totalServers; // Assuming each server is a site
    }

    showAddServerModal() {
        this.showModal('addServerModal');
    }

    showUploadModal(type) {
        const modal = document.getElementById('uploadModal');
        const title = document.getElementById('uploadModalTitle');
        const fileInput = document.getElementById('fileInput');
        
        title.textContent = type === 'zip' ? 'Upload ZIP File' : 'Upload Folder';
        fileInput.accept = type === 'zip' ? '.zip' : '*';
        fileInput.multiple = type !== 'zip';
        
        this.showModal('uploadModal');
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('show');
        document.body.style.overflow = '';
        
        // Reset forms
        if (modalId === 'addServerModal') {
            document.getElementById('addServerForm').reset();
        } else if (modalId === 'uploadModal') {
            document.getElementById('fileInput').value = '';
            document.getElementById('uploadBtn').disabled = true;
            document.getElementById('uploadArea').classList.remove('dragover');
        }
    }

    async handleAddServer(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            folder: formData.get('folder'),
            port: parseInt(formData.get('port')),
            type: formData.get('type'),
            auto_import: formData.has('auto_import'),
            auto_start: formData.has('auto_start')
        };

        try {
            this.showLoading();
            const response = await fetch('/api/add_server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast(result.message, 'success');
                this.hideModal('addServerModal');
                await this.loadServers();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to add server:', error);
            this.showToast('Failed to add server', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async startServer(name) {
        try {
            this.showLoading();
            const response = await fetch('/api/start_server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Server started', 'success');
                await this.loadServers();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to start server:', error);
            this.showToast('Failed to start server', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async stopServer(name) {
        try {
            this.showLoading();
            const response = await fetch('/api/stop_server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Server stopped', 'success');
                await this.loadServers();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to stop server:', error);
            this.showToast('Failed to stop server', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async deleteServer(name) {
        if (!confirm(`Are you sure you want to delete server "${name}"?`)) {
            return;
        }

        try {
            this.showLoading();
            const response = await fetch('/api/delete_server', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, delete_files: true })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Server deleted', 'success');
                await this.loadServers();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to delete server:', error);
            this.showToast('Failed to delete server', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async openBrowser(name) {
        try {
            const response = await fetch(`/api/open_browser/${name}`);
            const result = await response.json();
            
            if (result.success) {
                window.open(result.url, '_blank');
                this.showToast('Opening in browser', 'success');
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to open browser:', error);
            this.showToast('Failed to open browser', 'error');
        }
    }

    async viewLogs(name) {
        this.currentLogsServer = name;
        const modal = document.getElementById('logsModal');
        const title = document.getElementById('logsModalTitle');
        
        title.textContent = `Logs - ${name}`;
        this.showModal('logsModal');
        
        await this.loadLogs(name);
    }

    async loadLogs(name) {
        try {
            const response = await fetch(`/api/server_logs/${name}`);
            const result = await response.json();
            
            const logsContent = document.getElementById('logsContent');
            logsContent.innerHTML = '';
            
            if (result.logs && result.logs.length > 0) {
                result.logs.forEach(log => {
                    const logEntry = document.createElement('div');
                    logEntry.className = `log-entry ${log.type || 'info'}`;
                    
                    const timestamp = log.timestamp ? `<span class="log-timestamp">[${log.timestamp}]</span>` : '';
                    logEntry.innerHTML = `${timestamp}${this.escapeHtml(log.message)}`;
                    
                    logsContent.appendChild(logEntry);
                });
                
                // Scroll to bottom
                logsContent.scrollTop = logsContent.scrollHeight;
            } else {
                logsContent.innerHTML = '<div class="log-entry info">No logs available</div>';
            }
        } catch (error) {
            console.error('Failed to load logs:', error);
            const logsContent = document.getElementById('logsContent');
            logsContent.innerHTML = '<div class="log-entry error">Failed to load logs</div>';
        }
    }

    copyLogs() {
        const logsContent = document.getElementById('logsContent');
        const text = logsContent.innerText;
        
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Logs copied to clipboard', 'success');
        }).catch(() => {
            this.showToast('Failed to copy logs', 'error');
        });
    }

    clearLogs() {
        const logsContent = document.getElementById('logsContent');
        logsContent.innerHTML = '<div class="log-entry info">Logs cleared</div>';
    }

    handleFileSelection(files) {
        const uploadBtn = document.getElementById('uploadBtn');
        uploadBtn.disabled = files.length === 0;
        
        if (files.length > 0) {
            const fileNames = Array.from(files).map(f => f.name).join(', ');
            this.showToast(`Selected ${files.length} file(s): ${fileNames}`, 'info');
        }
    }

    async uploadFiles() {
        const fileInput = document.getElementById('fileInput');
        const files = fileInput.files;
        const name = document.getElementById('uploadName').value;
        const autoRegister = document.getElementById('uploadAutoRegister').checked;
        const autoStart = document.getElementById('uploadAutoStart').checked;
        
        if (files.length === 0) {
            this.showToast('Please select files to upload', 'warning');
            return;
        }

        try {
            this.showLoading();
            
            const formData = new FormData();
            Array.from(files).forEach(file => {
                formData.append('files[]', file);
            });
            formData.append('folder_name', name);
            formData.append('auto_register', autoRegister);
            formData.append('auto_start', autoStart);

            const response = await fetch('/api/upload_folder', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Files uploaded successfully', 'success');
                this.hideModal('uploadModal');
                await this.loadServers();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to upload files:', error);
            this.showToast('Failed to upload files', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async showSystemInfo() {
        try {
            const response = await fetch('/api/system_info');
            const info = await response.json();
            
            const content = document.getElementById('systemInfoContent');
            content.innerHTML = `
                <div class="info-item">
                    <div class="info-item-label">Operating System</div>
                    <div class="info-item-value">${this.escapeHtml(info.os || 'Unknown')}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Python Version</div>
                    <div class="info-item-value">${this.escapeHtml(info.python_version || 'Unknown')}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">CPU Cores</div>
                    <div class="info-item-value">${info.cpu_cores || 'Unknown'}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Active Servers</div>
                    <div class="info-item-value">${info.active_servers || 0}</div>
                </div>
                <div class="info-item">
                    <div class="info-item-label">Sites Folder</div>
                    <div class="info-item-value">${this.escapeHtml(info.sites_folder || 'Unknown')}</div>
                </div>
            `;
            
            this.showModal('systemInfoModal');
        } catch (error) {
            console.error('Failed to load system info:', error);
            this.showToast('Failed to load system info', 'error');
        }
    }

    async checkPHP() {
        try {
            const response = await fetch('/api/check_php');
            const result = await response.json();
            
            if (result.available) {
                this.showToast(`PHP is available: ${result.version}`, 'success');
            } else {
                this.showToast('PHP is not available', 'warning');
            }
        } catch (error) {
            console.error('Failed to check PHP:', error);
            this.showToast('Failed to check PHP', 'error');
        }
    }

    browseFolder() {
        // This would typically open a file dialog
        // For now, we'll just show a prompt
        const folder = prompt('Enter folder path:');
        if (folder) {
            document.getElementById('serverFolder').value = folder;
        }
    }

    startAutoRefresh() {
        // Refresh every 5 seconds
        this.autoRefreshInterval = setInterval(() => {
            this.loadServers();
        }, 5000);
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('show');
    }

    showToast(message, type = 'info', title = '') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="toast-icon ${icons[type]}"></i>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${this.escapeHtml(title)}</div>` : ''}
                <div class="toast-message">${this.escapeHtml(message)}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application
const serverAdmin = new ServerAdmin();

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        serverAdmin.stopAutoRefresh();
    } else {
        serverAdmin.startAutoRefresh();
    }
});

// Handle beforeunload
window.addEventListener('beforeunload', () => {
    serverAdmin.stopAutoRefresh();
});