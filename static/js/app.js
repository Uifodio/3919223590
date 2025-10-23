// Workspace Server - Professional JavaScript

class WorkspaceServer {
    constructor() {
        this.projects = {};
        this.currentLogsProject = null;
        this.autoRefreshInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadProjects();
        this.startAutoRefresh();
        this.hideLoading();
    }

    bindEvents() {
        // Header actions
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshProjects());
        document.getElementById('addProjectBtn').addEventListener('click', () => this.showAddProjectModal());

        // Modal events
        this.bindModalEvents();

        // Quick actions
        document.getElementById('uploadProjectBtn').addEventListener('click', () => this.uploadProject());
        document.getElementById('createStaticBtn').addEventListener('click', () => this.createQuickProject('static'));
        document.getElementById('createPhpBtn').addEventListener('click', () => this.createQuickProject('php'));
        document.getElementById('createNodeBtn').addEventListener('click', () => this.createQuickProject('nodejs'));
    }

    bindModalEvents() {
        // Add Project Modal
        const addProjectModal = document.getElementById('addProjectModal');
        const addProjectForm = document.getElementById('addProjectForm');
        const closeAddProjectModal = document.getElementById('closeAddProjectModal');
        const cancelAddProject = document.getElementById('cancelAddProject');
        const browsePathBtn = document.getElementById('browsePathBtn');

        closeAddProjectModal.addEventListener('click', () => this.hideModal('addProjectModal'));
        cancelAddProject.addEventListener('click', () => this.hideModal('addProjectModal'));
        browsePathBtn.addEventListener('click', () => this.browsePath());
        addProjectForm.addEventListener('submit', (e) => this.handleAddProject(e));

        // Logs Modal
        const logsModal = document.getElementById('logsModal');
        const closeLogsModal = document.getElementById('closeLogsModal');
        const copyLogsBtn = document.getElementById('copyLogsBtn');
        const clearLogsBtn = document.getElementById('clearLogsBtn');

        closeLogsModal.addEventListener('click', () => this.hideModal('logsModal'));
        copyLogsBtn.addEventListener('click', () => this.copyLogs());
        clearLogsBtn.addEventListener('click', () => this.clearLogs());

        // Close modals on backdrop click
        [addProjectModal, logsModal].forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }

    async loadProjects() {
        try {
            this.showLoading();
            const response = await fetch('/api/projects');
            const data = await response.json();
            this.projects = data;
            this.renderProjects();
            this.updateStats();
            this.hideLoading();
        } catch (error) {
            console.error('Failed to load projects:', error);
            this.showToast('Error loading projects', 'error');
            this.hideLoading();
        }
    }

    async refreshProjects() {
        try {
            await this.loadProjects();
            this.showToast('Projects refreshed', 'success');
        } catch (error) {
            console.error('Failed to refresh projects:', error);
            this.showToast('Refresh failed', 'error');
        }
    }

    renderProjects() {
        const projectsGrid = document.getElementById('projectsGrid');
        projectsGrid.innerHTML = '';

        if (Object.keys(this.projects).length === 0) {
            projectsGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <h3>No projects found</h3>
                    <p>Add your first project to get started</p>
                    <button class="btn btn-primary" onclick="workspaceServer.showAddProjectModal()">
                        <i class="fas fa-plus"></i>
                        Add Project
                    </button>
                </div>
            `;
            return;
        }

        Object.entries(this.projects).forEach(([name, project]) => {
            const projectCard = this.createProjectCard(name, project);
            projectsGrid.appendChild(projectCard);
        });
    }

    createProjectCard(name, project) {
        const card = document.createElement('div');
        card.className = 'project-card fade-in';
        
        const statusClass = project.status.toLowerCase();
        const statusIcon = project.status === 'running' ? 'play-circle' : 'stop-circle';
        const typeIcon = this.getProjectTypeIcon(project.type);
        
        card.innerHTML = `
            <div class="project-header">
                <h3 class="project-name">${this.escapeHtml(name)}</h3>
                <span class="project-status ${statusClass}">
                    <i class="fas fa-${statusIcon}"></i>
                    ${project.status}
                </span>
            </div>
            <div class="project-info">
                <div class="project-info-item">
                    <i class="fas fa-folder"></i>
                    <span>${this.escapeHtml(project.source_path || 'N/A')}</span>
                </div>
                <div class="project-info-item">
                    <i class="fas fa-network-wired"></i>
                    <span>Port: ${project.port || 'N/A'}</span>
                </div>
                <div class="project-info-item">
                    <i class="${typeIcon}"></i>
                    <span>Type: ${project.type || 'static'}</span>
                </div>
                <div class="project-info-item">
                    <i class="fas fa-route"></i>
                    <span>Route: ${project.route || '/' + name}</span>
                </div>
                ${project.created_at ? `
                <div class="project-info-item">
                    <i class="fas fa-clock"></i>
                    <span>Created: ${this.formatDate(project.created_at)}</span>
                </div>
                ` : ''}
            </div>
            <div class="project-actions">
                ${project.status === 'running' ? `
                    <button class="btn btn-ghost btn-sm" onclick="workspaceServer.stopProject('${name}')">
                        <i class="fas fa-stop"></i>
                        Stop
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="workspaceServer.openProject('${name}')">
                        <i class="fas fa-external-link-alt"></i>
                        Open
                    </button>
                ` : `
                    <button class="btn btn-primary btn-sm" onclick="workspaceServer.startProject('${name}')">
                        <i class="fas fa-play"></i>
                        Start
                    </button>
                `}
                <button class="btn btn-ghost btn-sm" onclick="workspaceServer.viewLogs('${name}')">
                    <i class="fas fa-file-alt"></i>
                    Logs
                </button>
                <button class="btn btn-danger btn-sm" onclick="workspaceServer.deleteProject('${name}')">
                    <i class="fas fa-trash"></i>
                    Delete
                </button>
            </div>
        `;
        
        return card;
    }

    getProjectTypeIcon(type) {
        const icons = {
            'static': 'fas fa-file-code',
            'php': 'fab fa-php',
            'nodejs': 'fab fa-node-js',
            'python': 'fab fa-python'
        };
        return icons[type] || 'fas fa-folder';
    }

    updateStats() {
        const totalProjects = Object.keys(this.projects).length;
        const runningProjects = Object.values(this.projects).filter(p => p.status === 'running').length;
        const stoppedProjects = totalProjects - runningProjects;
        const activeRoutes = Object.values(this.projects).filter(p => p.status === 'running').length;

        document.getElementById('totalProjects').textContent = totalProjects;
        document.getElementById('runningProjects').textContent = runningProjects;
        document.getElementById('stoppedProjects').textContent = stoppedProjects;
        document.getElementById('activeRoutes').textContent = activeRoutes;
    }

    showAddProjectModal() {
        this.showModal('addProjectModal');
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
        if (modalId === 'addProjectModal') {
            document.getElementById('addProjectForm').reset();
        }
    }

    async handleAddProject(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            type: formData.get('type'),
            source_path: formData.get('source_path'),
            route: formData.get('route') || undefined,
            port: formData.get('port') ? parseInt(formData.get('port')) : undefined
        };

        try {
            this.showLoading();
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Project created successfully', 'success');
                this.hideModal('addProjectModal');
                await this.loadProjects();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to create project:', error);
            this.showToast('Failed to create project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async startProject(name) {
        try {
            this.showLoading();
            const response = await fetch(`/api/projects/${name}/start`, {
                method: 'POST'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Project started', 'success');
                await this.loadProjects();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to start project:', error);
            this.showToast('Failed to start project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async stopProject(name) {
        try {
            this.showLoading();
            const response = await fetch(`/api/projects/${name}/stop`, {
                method: 'POST'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Project stopped', 'success');
                await this.loadProjects();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to stop project:', error);
            this.showToast('Failed to stop project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async deleteProject(name) {
        if (!confirm(`Are you sure you want to delete project "${name}"?`)) {
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`/api/projects/${name}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Project deleted', 'success');
                await this.loadProjects();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to delete project:', error);
            this.showToast('Failed to delete project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async openProject(name) {
        if (!(name in this.projects)) {
            this.showToast('Project not found', 'error');
            return;
        }

        const project = this.projects[name];
        if (project.status !== 'running') {
            this.showToast('Project is not running', 'error');
            return;
        }

        const route = project.route || `/${name}`;
        const url = `${window.location.origin}${route}`;
        window.open(url, '_blank');
        this.showToast('Opening project in new tab', 'success');
    }

    async viewLogs(name) {
        this.currentLogsProject = name;
        const modal = document.getElementById('logsModal');
        const title = document.getElementById('logsModalTitle');
        
        title.textContent = `Logs - ${name}`;
        this.showModal('logsModal');
        
        // For now, show placeholder logs
        const logsContent = document.getElementById('logsContent');
        logsContent.innerHTML = '<div class="log-entry info">Logs feature coming soon...</div>';
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

    browsePath() {
        // This would typically open a file dialog
        // For now, we'll just show a prompt
        const path = prompt('Enter project path:');
        if (path) {
            document.getElementById('projectPath').value = path;
        }
    }

    createQuickProject(type) {
        const name = prompt(`Enter ${type} project name:`);
        if (!name) return;

        const path = prompt(`Enter project path:`);
        if (!path) return;

        const data = {
            name: name,
            type: type,
            source_path: path
        };

        this.createProject(data);
    }

    async createProject(data) {
        try {
            this.showLoading();
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Project created successfully', 'success');
                await this.loadProjects();
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Failed to create project:', error);
            this.showToast('Failed to create project', 'error');
        } finally {
            this.hideLoading();
        }
    }

    uploadProject() {
        this.showToast('Upload feature coming soon...', 'info');
    }

    startAutoRefresh() {
        // Refresh every 10 seconds
        this.autoRefreshInterval = setInterval(() => {
            this.loadProjects();
        }, 10000);
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

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        } catch (e) {
            return dateString;
        }
    }
}

// Initialize the application
const workspaceServer = new WorkspaceServer();

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        workspaceServer.stopAutoRefresh();
    } else {
        workspaceServer.startAutoRefresh();
    }
});

// Handle beforeunload
window.addEventListener('beforeunload', () => {
    workspaceServer.stopAutoRefresh();
});