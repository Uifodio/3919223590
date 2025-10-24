/**
 * Modern Workspace Server - Professional Frontend
 * Enhanced JavaScript with modern ES6+ features
 */

class WorkspaceServer {
    constructor() {
        this.projects = [];
        this.autoRefreshInterval = null;
        this.logsInterval = null;
        this.isPageVisible = true;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadProjects();
        this.checkSystemStatus();
        this.startAutoRefresh();
        this.hideLoading();
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            this.isPageVisible = !document.hidden;
            if (this.isPageVisible) {
                this.startAutoRefresh();
            } else {
                this.stopAutoRefresh();
            }
        });
    }

    bindEvents() {
        // Modal events
        this.bindModalEvents();
        
        // Upload events
        this.bindUploadEvents();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllModals();
            }
        });
    }

    bindModalEvents() {
        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideAllModals();
            }
        });

        // Form submissions
        const addProjectForm = document.getElementById('addProjectForm');
        if (addProjectForm) {
            addProjectForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createProject();
            });
        }
    }

    bindUploadEvents() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        if (uploadArea && fileInput) {
            // Click to browse
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

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
                this.handleFileUpload(files);
            });

            // File input change
            fileInput.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files);
            });
        }
    }

    async loadProjects() {
        try {
            this.showLoading();
            const response = await fetch('/api/servers');
            const data = await response.json();
            
            this.projects = data.servers || [];
            this.renderProjects();
            this.updateStats();
        } catch (error) {
            console.error('Error loading projects:', error);
            this.showToast('Error loading projects', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async refreshProjects() {
        await this.loadProjects();
        this.showToast('Projects refreshed', 'success');
    }

    renderProjects() {
        const projectsGrid = document.getElementById('projectsGrid');
        const emptyState = document.getElementById('emptyState');

        if (!projectsGrid) return;

        if (this.projects.length === 0) {
            projectsGrid.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }

        projectsGrid.style.display = 'grid';
        emptyState.style.display = 'none';

        projectsGrid.innerHTML = this.projects.map(project => 
            this.createProjectCard(project)
        ).join('');
    }

    createProjectCard(project) {
        const statusClass = project.status === 'Running' ? 'running' : 'stopped';
        const statusText = project.status === 'Running' ? 'Running' : 'Stopped';
        const typeIcon = this.getTypeIcon(project.type);
        const typeClass = project.type?.toLowerCase() || 'static';

        return `
            <div class="project-card fade-in">
                <div class="project-header">
                    <div class="project-title">
                        <i class="${typeIcon}"></i>
                        ${this.escapeHtml(project.name)}
                    </div>
                    <div class="project-type ${typeClass}">
                        ${this.escapeHtml(project.type || 'Static')}
                    </div>
                </div>

                <div class="project-info">
                    <div class="project-detail">
                        <i class="fas fa-circle"></i>
                        <span class="project-status">
                            <span class="status-dot ${statusClass}"></span>
                            ${statusText}
                        </span>
                    </div>
                    
                    ${project.port ? `
                        <div class="project-detail">
                            <i class="fas fa-plug"></i>
                            <span>Port: ${project.port}</span>
                        </div>
                    ` : ''}
                    
                    ${project.route ? `
                        <div class="project-detail">
                            <i class="fas fa-route"></i>
                            <span>Route: /${project.route}</span>
                        </div>
                    ` : ''}
                    
                    <div class="project-detail">
                        <i class="fas fa-folder"></i>
                        <span>${this.escapeHtml(project.path || 'No path')}</span>
                    </div>
                    
                    ${project.created ? `
                        <div class="project-detail">
                            <i class="fas fa-calendar"></i>
                            <span>Created: ${this.formatDate(project.created)}</span>
                        </div>
                    ` : ''}
                </div>

                <div class="project-actions">
                    ${project.status === 'Running' ? `
                        <button class="btn btn-danger btn-sm" onclick="workspaceServer.stopProject('${project.name}')">
                            <i class="fas fa-stop"></i>
                            Stop
                        </button>
                        <button class="btn btn-outline btn-sm" onclick="workspaceServer.openProject('${project.name}')">
                            <i class="fas fa-external-link-alt"></i>
                            Open
                        </button>
                    ` : `
                        <button class="btn btn-success btn-sm" onclick="workspaceServer.startProject('${project.name}')">
                            <i class="fas fa-play"></i>
                            Start
                        </button>
                    `}
                    
                    <button class="btn btn-outline btn-sm" onclick="workspaceServer.viewLogs('${project.name}')">
                        <i class="fas fa-file-alt"></i>
                        Logs
                    </button>
                    
                    <button class="btn btn-outline btn-sm" onclick="workspaceServer.deleteProject('${project.name}')">
                        <i class="fas fa-trash"></i>
                        Delete
                    </button>
                </div>
            </div>
        `;
    }

    getTypeIcon(type) {
        const icons = {
            'static': 'fas fa-file-code',
            'php': 'fab fa-php',
            'nodejs': 'fab fa-node-js',
            'python': 'fab fa-python',
            'http': 'fas fa-globe'
        };
        return icons[type?.toLowerCase()] || 'fas fa-globe';
    }

    updateStats() {
        const totalProjects = this.projects.length;
        const runningProjects = this.projects.filter(p => p.status === 'Running').length;
        const stoppedProjects = totalProjects - runningProjects;
        const activeRoutes = this.projects.filter(p => p.status === 'Running' && p.route).length;

        this.updateElement('totalProjects', totalProjects);
        this.updateElement('runningProjects', runningProjects);
        this.updateElement('stoppedProjects', stoppedProjects);
        this.updateElement('activeRoutes', activeRoutes);
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    async checkSystemStatus() {
        try {
            // Check PHP
            const phpResponse = await fetch('/api/check-php');
            const phpData = await phpResponse.json();
            this.updateStatusIndicator('phpStatus', phpData.available);

            // Check Node.js
            const nodeResponse = await fetch('/api/check-node');
            const nodeData = await nodeResponse.json();
            this.updateStatusIndicator('nodeStatus', nodeData.available);

            // Proxy is always available if we can make requests
            this.updateStatusIndicator('proxyStatus', true);
        } catch (error) {
            console.error('Error checking system status:', error);
            this.updateStatusIndicator('phpStatus', false);
            this.updateStatusIndicator('nodeStatus', false);
            this.updateStatusIndicator('proxyStatus', false);
        }
    }

    updateStatusIndicator(elementId, available) {
        const element = document.getElementById(elementId);
        if (element) {
            element.className = `status-indicator ${available ? 'available' : 'unavailable'}`;
            element.textContent = available ? 'Available' : 'Unavailable';
        }
    }

    // Modal Management
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    hideAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.remove('show');
        });
        document.body.style.overflow = '';
    }

    // Project Management
    async createProject() {
        const form = document.getElementById('addProjectForm');
        const formData = new FormData(form);
        
        const projectData = {
            name: formData.get('name'),
            type: formData.get('type'),
            path: formData.get('path'),
            route: formData.get('route') || formData.get('name'),
            port: formData.get('port') ? parseInt(formData.get('port')) : null
        };

        try {
            this.showLoading();
            const response = await fetch('/api/servers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData)
            });

            if (response.ok) {
                this.showToast('Project created successfully', 'success');
                this.hideModal('addProjectModal');
                form.reset();
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showToast(error.error || 'Failed to create project', 'error');
            }
        } catch (error) {
            console.error('Error creating project:', error);
            this.showToast('Error creating project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async startProject(projectName) {
        try {
            this.showLoading();
            const response = await fetch(`/api/servers/${projectName}/start`, {
                method: 'POST'
            });

            if (response.ok) {
                this.showToast('Project started successfully', 'success');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showToast(error.error || 'Failed to start project', 'error');
            }
        } catch (error) {
            console.error('Error starting project:', error);
            this.showToast('Error starting project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async stopProject(projectName) {
        try {
            this.showLoading();
            const response = await fetch(`/api/servers/${projectName}/stop`, {
                method: 'POST'
            });

            if (response.ok) {
                this.showToast('Project stopped successfully', 'success');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showToast(error.error || 'Failed to stop project', 'error');
            }
        } catch (error) {
            console.error('Error stopping project:', error);
            this.showToast('Error stopping project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async deleteProject(projectName) {
        if (!confirm(`Are you sure you want to delete project "${projectName}"?`)) {
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`/api/servers/${projectName}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Project deleted successfully', 'success');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showToast(error.error || 'Failed to delete project', 'error');
            }
        } catch (error) {
            console.error('Error deleting project:', error);
            this.showToast('Error deleting project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    openProject(projectName) {
        const project = this.projects.find(p => p.name === projectName);
        if (project && project.status === 'Running') {
            const url = `http://localhost:8000/${project.route || project.name}`;
            window.open(url, '_blank');
        }
    }

    viewLogs(projectName) {
        const project = this.projects.find(p => p.name === projectName);
        if (project) {
            document.getElementById('logsProjectName').textContent = project.name;
            this.showModal('logsModal');
            this.loadLogs(projectName);
        }
    }

    async loadLogs(projectName) {
        const logsContent = document.getElementById('logsContent');
        if (!logsContent) return;

        try {
            const response = await fetch(`/api/servers/${projectName}/logs`);
            const data = await response.json();
            
            logsContent.innerHTML = data.logs.map(log => `
                <div class="log-entry">
                    <span class="log-time">${this.formatDate(log.timestamp)}</span>
                    <span class="log-message">${this.escapeHtml(log.message)}</span>
                </div>
            `).join('');

            // Auto-scroll if enabled
            const autoScroll = document.getElementById('autoScroll');
            if (autoScroll && autoScroll.checked) {
                logsContent.scrollTop = logsContent.scrollHeight;
            }
        } catch (error) {
            console.error('Error loading logs:', error);
            logsContent.innerHTML = '<div class="log-entry">Error loading logs</div>';
        }
    }

    clearLogs() {
        const logsContent = document.getElementById('logsContent');
        if (logsContent) {
            logsContent.innerHTML = '<div class="log-entry">Logs cleared</div>';
        }
    }

    copyLogs() {
        const logsContent = document.getElementById('logsContent');
        if (logsContent) {
            const text = logsContent.innerText;
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Logs copied to clipboard', 'success');
            }).catch(() => {
                this.showToast('Failed to copy logs', 'error');
            });
        }
    }

    // Quick Actions
    showAddProjectModal() {
        this.showModal('addProjectModal');
    }

    showQuickCreateModal() {
        this.showModal('quickCreateModal');
    }

    showUploadModal() {
        this.showModal('uploadModal');
    }

    quickCreate(type) {
        const projectName = prompt(`Enter project name for ${type} project:`);
        if (!projectName) return;

        const projectPath = prompt(`Enter project path:`);
        if (!projectPath) return;

        const projectData = {
            name: projectName,
            type: type,
            path: projectPath,
            route: projectName
        };

        this.createProjectFromData(projectData);
        this.hideModal('quickCreateModal');
    }

    async createProjectFromData(projectData) {
        try {
            this.showLoading();
            const response = await fetch('/api/servers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData)
            });

            if (response.ok) {
                this.showToast('Project created successfully', 'success');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showToast(error.error || 'Failed to create project', 'error');
            }
        } catch (error) {
            console.error('Error creating project:', error);
            this.showToast('Error creating project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    // File Upload
    handleFileUpload(files) {
        if (files.length === 0) return;

        const file = files[0];
        const formData = new FormData();
        formData.append('file', file);

        this.uploadFile(formData);
    }

    async uploadFile(formData) {
        try {
            this.showLoading();
            const progressBar = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.showToast('File uploaded successfully', 'success');
                await this.loadProjects();
            } else {
                const error = await response.json();
                this.showToast(error.error || 'Failed to upload file', 'error');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            this.showToast('Error uploading file', 'error');
        } finally {
            this.hideLoading();
        }
    }

    // Utility Functions
    browsePath() {
        // Simple path input for now - in a real app, you'd use a file dialog
        const path = prompt('Enter project path:');
        if (path) {
            document.getElementById('projectPath').value = path;
        }
    }

    startAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }

        this.autoRefreshInterval = setInterval(() => {
            if (this.isPageVisible) {
                this.loadProjects();
            }
        }, 5000); // Refresh every 5 seconds
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    showToast(message, type = 'info', title = '') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type} show`;
        
        const icon = this.getToastIcon(type);
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${icon}"></i>
            </div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch (error) {
            return 'Invalid date';
        }
    }
}

// Global functions for HTML onclick handlers
function showAddProjectModal() {
    workspaceServer.showAddProjectModal();
}

function showQuickCreateModal() {
    workspaceServer.showQuickCreateModal();
}

function showUploadModal() {
    workspaceServer.showUploadModal();
}

function refreshProjects() {
    workspaceServer.refreshProjects();
}

function quickCreate(type) {
    workspaceServer.quickCreate(type);
}

function browsePath() {
    workspaceServer.browsePath();
}

function createProject() {
    workspaceServer.createProject();
}

function startProject(name) {
    workspaceServer.startProject(name);
}

function stopProject(name) {
    workspaceServer.stopProject(name);
}

function deleteProject(name) {
    workspaceServer.deleteProject(name);
}

function openProject(name) {
    workspaceServer.openProject(name);
}

function viewLogs(name) {
    workspaceServer.viewLogs(name);
}

function clearLogs() {
    workspaceServer.clearLogs();
}

function copyLogs() {
    workspaceServer.copyLogs();
}

function hideModal(modalId) {
    workspaceServer.hideModal(modalId);
}

// Initialize the application
let workspaceServer;
document.addEventListener('DOMContentLoaded', () => {
    workspaceServer = new WorkspaceServer();
});