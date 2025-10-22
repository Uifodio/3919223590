// Modern Server Administrator - Professional JavaScript Application (upgraded)
//
// This file contains all the original behaviour plus upgrades:
// - Full folder uploads (via <input webkitdirectory> or multiple files upload) preserving subpaths
// - Zip upload support (uploads .zip -> /api/upload_zip)
// - Upload progress reporting (uses XHR so you can show progress bars)
// - open_browser: uses backend returned URL and opens it on the client (so phones open the correct host IP)
// - Auto-refresh on first load and on page reload (UI fetches servers immediately)
// - Logs auto-refresh while the logs modal is open (polls /api/server_logs every 2s)
// - Safe fallbacks and feature detection for browsers that don't support folder picks
// - No features removed; all previous routes / behaviors preserved
//
// NOTE: this expects the backend endpoints we built previously:
//   /api/servers, /api/add_server, /api/stop_server, /api/start_server, /api/delete_server,
//   /api/server_logs/:name, /api/open_browser/:name, /api/upload_zip, /api/upload_folder, /api/system_info,
//   /api/check_php, /api/check_node, /api/set_folder, /api/install_php
//
// If your HTML doesn't provide some optional UI elements (upload buttons, progress bar), the code will still work — it just won't show progress.

class ServerAdmin {
    constructor() {
        this.currentServer = null;
        this.autoRefreshInterval = null;
        this.logsInterval = null;
        this.selectedFiles = [];     // FileList or array used for folder upload
        this.folderMode = false;     // whether the last selection was via folder input
        this.init();
    }

    init() {
        this.bindEvents();
        // Immediately load servers (auto refresh on app entry)
        this.loadServers();
        // Start auto-refresh (periodic)
        this.startAutoRefresh();
        this.checkSystemRequirements();
    }

    bindEvents() {
        // Keep original buttons (if they exist)
        const browseBtn = document.getElementById('browseFolderBtn');
        if (browseBtn) browseBtn.addEventListener('click', () => this.browseFolder());

        const manualBtn = document.getElementById('manualFolderBtn');
        if (manualBtn) manualBtn.addEventListener('click', () => this.manualFolder());

        const addBtn = document.getElementById('addServerBtn');
        if (addBtn) addBtn.addEventListener('click', () => this.addServer());

        const refreshBtn = document.getElementById('refreshAllBtn');
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.refreshAll());

        const sysBtn = document.getElementById('systemInfoBtn');
        if (sysBtn) sysBtn.addEventListener('click', () => this.showSystemInfo());

        // Folder input (supports webkitdirectory)
        const folderInput = document.getElementById('folderInput');
        if (folderInput) {
            // Accept directories (in supporting browsers)
            // <input id="folderInput" type="file" webkitdirectory multiple />
            folderInput.addEventListener('change', (e) => this.handleFolderSelection(e));
        }

        // Upload controls (new)
        const uploadFolderBtn = document.getElementById('uploadFolderBtn');
        if (uploadFolderBtn) uploadFolderBtn.addEventListener('click', () => this.uploadSelectedFolder());

        const uploadZipBtn = document.getElementById('uploadZipBtn');
        if (uploadZipBtn) uploadZipBtn.addEventListener('click', () => this.uploadZipFile());

        const zipInput = document.getElementById('zipInput');
        if (zipInput) {
            zipInput.addEventListener('change', (e) => {
                // store selected zip for upload
                this.zipFile = e.target.files && e.target.files.length ? e.target.files[0] : null;
            });
        }

        // Modal close buttons
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal')));
        });

        // Log modal events
        const refreshLogsBtn = document.getElementById('refreshLogsBtn');
        if (refreshLogsBtn) refreshLogsBtn.addEventListener('click', () => this.refreshLogs());

        const copyLogsBtn = document.getElementById('copyLogsBtn');
        if (copyLogsBtn) copyLogsBtn.addEventListener('click', () => this.copyLogs());

        const openBrowserBtn = document.getElementById('openBrowserBtn');
        if (openBrowserBtn) openBrowserBtn.addEventListener('click', () => this.openBrowser());

        // File selection: "Select all" checkbox
        const selectAll = document.getElementById('selectAllFiles');
        if (selectAll) selectAll.addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target.classList && e.target.classList.contains && e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Escape key closes modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeAllModals();
        });

        // Port validation
        const portInput = document.getElementById('serverPort');
        if (portInput) portInput.addEventListener('input', (ev) => this.validatePort(ev.target));

        // Open browser action: handled on each server card's button in renderServers()
    }

    /****************
     * Folder handling
     ****************/
    async browseFolder() {
        const folderInput = document.getElementById('folderInput');
        if (folderInput && folderInput.webkitdirectory !== undefined) {
            // show native picker which allows folder selection in supporting browsers
            folderInput.click();
        } else {
            // fallback: ask for manual path
            this.manualFolder();
        }
    }

    async manualFolder() {
        const folderPath = prompt('Enter the full path to your website folder:\n\nExamples:\n- C:\\Users\\YourName\\Documents\\MyWebsite\n- /home/username/MyWebsite\n- ./my-website');
        if (folderPath && folderPath.trim()) {
            document.getElementById('folderPath').value = folderPath.trim();
            // keep selectedFiles empty (we are pointing to server-side path)
            this.selectedFiles = [];
            this.folderMode = false;
            await this.setFolder(folderPath.trim());
        }
    }

    handleFolderSelection(event) {
        // When user picks a folder using input[webkitdirectory], we get a FileList with webkitRelativePath for each file
        const files = Array.from(event.target.files || []);
        if (!files.length) return;

        // Store files for upload (we will preserve webkitRelativePath when uploading)
        this.selectedFiles = files;
        this.folderMode = true;

        // Derive a friendly folder name to show in the UI (the first file's webkitRelativePath's top folder)
        let folderName = '';
        if (files[0].webkitRelativePath) {
            folderName = files[0].webkitRelativePath.split('/')[0];
        } else {
            // fallback - use file input name
            folderName = files[0].name;
        }
        document.getElementById('folderPath').value = folderName;
        // For convenience, also set the folder as current folder on the server side (optional)
        // but many times the browser doesn't know full absolute path, so we only set folder path in field for server to import if user clicks Add Server.
    }

    /****************
     * Upload (folder & zip)
     ****************/
    uploadSelectedFolder() {
        // Called by UI "Upload Folder" button: sends selectedFiles[] with webkitRelativePath preserved
        if (!this.selectedFiles || this.selectedFiles.length === 0) {
            this.showNotification('No folder selected to upload. Use "Browse Folder" first.', 'error');
            return;
        }

        const uploadBtn = document.getElementById('uploadFolderBtn');
        const origHTML = uploadBtn ? uploadBtn.innerHTML : null;
        if (uploadBtn) {
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
            uploadBtn.disabled = true;
        }

        // Build FormData: append each file as files[] and set filename to webkitRelativePath to preserve paths
        const fd = new FormData();
        this.selectedFiles.forEach(f => {
            // Preserve directory structure by using webkitRelativePath when available
            const filename = f.webkitRelativePath ? f.webkitRelativePath : f.name;
            fd.append('files[]', f, filename);
        });
        fd.append('folder_name', document.getElementById('folderPath').value || `site-${Date.now()}`);
        // call /api/upload_folder via XHR to get upload progress
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/upload_folder', true);

        xhr.upload.onprogress = (ev) => {
            const progressBar = document.getElementById('uploadProgress');
            const progressLabel = document.getElementById('uploadProgressLabel');
            const progressSize = document.getElementById('uploadProgressSize');
            
            if (progressBar && ev.lengthComputable) {
                const percent = Math.round((ev.loaded / ev.total) * 100);
                const loadedMB = (ev.loaded / (1024 * 1024)).toFixed(1);
                const totalMB = (ev.total / (1024 * 1024)).toFixed(1);
                
                const bar = progressBar.querySelector('.bar');
                if (bar) bar.style.width = percent + '%';
                
                if (progressLabel) {
                    progressLabel.textContent = `Uploading... ${percent}%`;
                    progressLabel.className = 'progress-text';
                }
                if (progressSize) {
                    progressSize.textContent = `${loadedMB}MB / ${totalMB}MB`;
                    progressSize.className = 'progress-size';
                }
            }
        };

        xhr.onload = async () => {
            if (uploadBtn) { uploadBtn.innerHTML = origHTML; uploadBtn.disabled = false; }
            const progressBar = document.getElementById('uploadProgress');
            const progressLabel = document.getElementById('uploadProgressLabel');
            const progressSize = document.getElementById('uploadProgressSize');
            if (progressBar) { 
                const bar = progressBar.querySelector('.bar');
                if (bar) bar.style.width = '0%';
            }
            if (progressLabel) {
                progressLabel.textContent = 'No upload in progress';
                progressLabel.className = '';
            }
            if (progressSize) {
                progressSize.textContent = '';
                progressSize.className = '';
            }
            try {
                const res = JSON.parse(xhr.responseText);
                if (res.success) {
                    this.showNotification('Folder uploaded successfully', 'success');
                    // auto-register happened server-side; refresh servers list
                    await this.loadServers();
                } else {
                    this.showNotification(res.message || 'Upload failed', 'error');
                }
            } catch (err) {
                this.showNotification('Upload failed: invalid response', 'error');
            }
        };

        xhr.onerror = () => {
            if (uploadBtn) { uploadBtn.innerHTML = origHTML; uploadBtn.disabled = false; }
            this.showNotification('Upload failed due to network error', 'error');
        };

        xhr.send(fd);
    }

    uploadZipFile() {
        // Uploads a zip file via /api/upload_zip using XHR to allow progress
        const zipInput = document.getElementById('zipInput');
        let file = null;
        if (zipInput && zipInput.files && zipInput.files.length > 0) {
            file = zipInput.files[0];
        } else if (this.zipFile) {
            file = this.zipFile;
        }
        if (!file) {
            this.showNotification('No zip file selected', 'error');
            return;
        }
        if (!file.name.toLowerCase().endsWith('.zip')) {
            this.showNotification('Selected file is not a .zip', 'error');
            return;
        }

        const uploadBtn = document.getElementById('uploadZipBtn');
        const origHtml = uploadBtn ? uploadBtn.innerHTML : null;
        if (uploadBtn) { uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...'; uploadBtn.disabled = true; }

        const fd = new FormData();
        fd.append('file', file, file.name);
        fd.append('auto_register', 'true');

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/upload_zip', true);

        xhr.upload.onprogress = (ev) => {
            const progressBar = document.getElementById('uploadProgress');
            const progressLabel = document.getElementById('uploadProgressLabel');
            const progressSize = document.getElementById('uploadProgressSize');
            
            if (progressBar && ev.lengthComputable) {
                const percent = Math.round((ev.loaded / ev.total) * 100);
                const loadedMB = (ev.loaded / (1024 * 1024)).toFixed(1);
                const totalMB = (ev.total / (1024 * 1024)).toFixed(1);
                
                const bar = progressBar.querySelector('.bar');
                if (bar) bar.style.width = percent + '%';
                
                if (progressLabel) {
                    progressLabel.textContent = `Uploading... ${percent}%`;
                    progressLabel.className = 'progress-text';
                }
                if (progressSize) {
                    progressSize.textContent = `${loadedMB}MB / ${totalMB}MB`;
                    progressSize.className = 'progress-size';
                }
            }
        };
        xhr.onload = async () => {
            if (uploadBtn) { uploadBtn.innerHTML = origHtml; uploadBtn.disabled = false; }
            const progressBar = document.getElementById('uploadProgress');
            const progressLabel = document.getElementById('uploadProgressLabel');
            const progressSize = document.getElementById('uploadProgressSize');
            if (progressBar) { 
                const bar = progressBar.querySelector('.bar');
                if (bar) bar.style.width = '0%';
            }
            if (progressLabel) {
                progressLabel.textContent = 'No upload in progress';
                progressLabel.className = '';
            }
            if (progressSize) {
                progressSize.textContent = '';
                progressSize.className = '';
            }
            try {
                const res = JSON.parse(xhr.responseText);
                if (res.success) {
                    this.showNotification('Zip uploaded & extracted successfully', 'success');
                    await this.loadServers();
                } else {
                    this.showNotification(res.message || 'Zip extraction failed', 'error');
                }
            } catch (err) {
                this.showNotification('Upload failed: invalid response', 'error');
            }
        };
        xhr.onerror = () => {
            if (uploadBtn) { uploadBtn.innerHTML = origHtml; uploadBtn.disabled = false; }
            this.showNotification('Upload failed due to network error', 'error');
        };
        xhr.send(fd);
    }

    /****************
     * Server control API calls
     ****************/
    async addServer() {
        // preserved original behavior but account for folderMode (if user selected local folder files we uploaded earlier)
        const folder = document.getElementById('folderPath').value.trim();
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

        // Provide user feedback
        const addBtn = document.getElementById('addServerBtn');
        const originalText = addBtn ? addBtn.innerHTML : null;
        if (addBtn) {
            addBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding Server...';
            addBtn.disabled = true;
        }

        try {
            // If folderMode (we have selected files), it may be preferable to upload those files first to backend and get a site folder.
            // But since backend's /api/add_server will import a server-side path, we rely on the user uploading first (via Upload Folder / Zip).
            // Here we simply post the folder path (which for remote phones might be a phrase used by backend to find the proper site in sites/).
            const response = await fetch('/api/add_server', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder, port, type: serverType })
            });
            const result = await response.json();
            if (result.success) {
                this.showNotification(result.message, 'success');
                await this.loadServers();
            } else {
                this.showNotification(result.message || 'Failed to add server', 'error');
            }
        } catch (error) {
            this.showNotification('Error adding server: ' + (error.message || error), 'error');
        } finally {
            if (addBtn) { addBtn.innerHTML = originalText; addBtn.disabled = false; }
        }
    }

    async stopServer(serverName) {
        if (!confirm(`Are you sure you want to stop ${serverName}?`)) return;
        try {
            const res = await fetch('/api/stop_server', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: serverName })
            });
            const r = await res.json();
            if (r.success) {
                this.showNotification(r.message, 'success');
                this.loadServers();
            } else {
                this.showNotification(r.message, 'error');
            }
        } catch (e) {
            this.showNotification('Error stopping server: ' + e.message, 'error');
        }
    }

    async startServer(serverName) {
        try {
            const res = await fetch('/api/start_server', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: serverName })
            });
            const r = await res.json();
            if (r.success) {
                this.showNotification(r.message, 'success');
                this.loadServers();
            } else {
                this.showNotification(r.message, 'error');
            }
        } catch (e) {
            this.showNotification('Error starting server: ' + e.message, 'error');
        }
    }

    async deleteServer(serverName) {
        if (!confirm(`Are you sure you want to delete server "${serverName}"? This action cannot be undone.`)) return;
        try {
            const res = await fetch('/api/delete_server', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: serverName })
            });
            const r = await res.json();
            if (r.success) {
                this.showNotification(r.message, 'success');
                this.loadServers();
            } else {
                this.showNotification(r.message || 'Failed to delete', 'error');
            }
        } catch (e) {
            this.showNotification('Error deleting server: ' + e.message, 'error');
        }
    }

    /****************
     * Server listing + rendering
     ****************/
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

        if (!servers || Object.keys(servers).length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-server"></i>
                    <h3 style="color: var(--text-primary);">No servers registered</h3>
                    <p style="color: var(--text-secondary);">Upload a folder or add a server to get started</p>
                </div>
            `;
            if (document.getElementById('serverCount')) document.getElementById('serverCount').textContent = '0 servers running';
            return;
        }

        let runningCount = 0;
        Object.values(servers).forEach(server => {
            if (server.status === 'Running') runningCount++;

            const serverCard = document.createElement('div');
            serverCard.className = `server-card ${server.status.toLowerCase()}`;

            // header
            const header = document.createElement('div');
            header.className = 'server-header';

            const serverInfo = document.createElement('div');
            serverInfo.className = 'server-info';

            const serverName = document.createElement('h3');
            serverName.style.cssText = 'color: var(--text-primary); font-weight: 600;';
            serverName.textContent = server.name;

            const serverFolder = document.createElement('p');
            serverFolder.style.cssText = 'color: var(--text-secondary); font-weight: 500;';
            // show folder name only
            serverFolder.textContent = (server.folder || '').split('/').pop();

            serverInfo.appendChild(serverName);
            serverInfo.appendChild(serverFolder);

            const serverStatus = document.createElement('div');
            serverStatus.className = 'server-status';

            const statusBadge = document.createElement('span');
            statusBadge.className = `status-badge status-${(server.status || 'Stopped').toLowerCase()}`;
            statusBadge.textContent = server.status || 'Stopped';

            serverStatus.appendChild(statusBadge);
            header.appendChild(serverInfo);
            header.appendChild(serverStatus);

            // details
            const details = document.createElement('div');
            details.className = 'server-details';
            const detailsData = [
                { label: 'Port', value: server.port || '—' },
                { label: 'Type', value: server.type || 'HTTP' },
                { label: 'Started', value: server.start_time || '—' },
                // Do not assume localhost: show a helpful hint instead (client should use open button to get correct URL)
                { label: 'URL', value: server.port ? `Click "Open Browser" to get device URL` : 'Not started' }
            ];
            detailsData.forEach(item => {
                const detailItem = document.createElement('div');
                detailItem.className = 'detail-item';
                const label = document.createElement('div'); label.className = 'detail-label'; label.textContent = item.label;
                const value = document.createElement('div'); value.className = 'detail-value'; value.style.cssText = 'color: var(--text-primary); font-weight: 600;';
                value.textContent = item.value;
                detailItem.appendChild(label); detailItem.appendChild(value);
                details.appendChild(detailItem);
            });

            // actions
            const actions = document.createElement('div');
            actions.className = 'server-actions';

            const viewLogsBtn = document.createElement('button');
            viewLogsBtn.className = 'action-btn view-logs';
            viewLogsBtn.title = 'View Server Logs';
            viewLogsBtn.innerHTML = '<i class="fas fa-file-alt"></i> View Logs';
            viewLogsBtn.onclick = () => this.showLogs(server.name);

            const openBrowserBtn = document.createElement('button');
            openBrowserBtn.className = 'action-btn open-browser';
            openBrowserBtn.title = 'Open in Browser';
            openBrowserBtn.innerHTML = '<i class="fas fa-external-link-alt"></i> Open Browser';
            openBrowserBtn.onclick = () => this.openServerInBrowser(server.name);

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

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'action-btn delete-server';
            deleteBtn.title = 'Delete Server';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Delete';
            deleteBtn.onclick = () => this.deleteServer(server.name);

            actions.appendChild(viewLogsBtn);
            actions.appendChild(openBrowserBtn);
            actions.appendChild(startStopBtn);
            actions.appendChild(deleteBtn);

            serverCard.appendChild(header);
            serverCard.appendChild(details);
            serverCard.appendChild(actions);
            container.appendChild(serverCard);
        });

        if (document.getElementById('serverCount')) document.getElementById('serverCount').textContent = `${runningCount} servers running`;
    }

    /****************
     * Logs UI with Live Streaming
     ****************/
    async showLogs(serverName) {
        this.currentServer = serverName;
        const title = document.getElementById('logModalTitle');
        if (title) title.innerHTML = `<i class="fas fa-file-alt"></i> Logs - ${serverName}`;
        const modal = document.getElementById('logModal');
        if (modal) modal.classList.add('show');
        
        // Show live indicator
        const liveBadge = document.getElementById('logLiveBadge');
        if (liveBadge) liveBadge.style.display = 'flex';
        
        // Immediately load logs and start live streaming
        await this.refreshLogs();
        this.startLiveLogStream();
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
                logLine.innerHTML = `<span style="color: var(--text-muted);">[${timestamp}]</span> <span style="color:${type === 'error' ? 'var(--error)' : 'var(--text-primary)'};">${this.escapeHtml(message)}</span>`;
                logContent.appendChild(logLine);
            });
            logContent.scrollTop = logContent.scrollHeight;
        } catch (error) {
            console.error('Error loading logs:', error);
            const logContent = document.getElementById('logContent');
            if (logContent) logContent.textContent = 'Error loading logs: ' + (error.message || error);
        }
    }

    startLiveLogStream() {
        // Stop existing streams
        this.stopLiveLogStream();
        
        if (!this.currentServer) return;
        
        // Try Server-Sent Events first
        if (typeof EventSource !== 'undefined') {
            try {
                this.eventSource = new EventSource(`/api/server_logs_stream/${encodeURIComponent(this.currentServer)}`);
                
                this.eventSource.onmessage = (event) => {
                    try {
                        const logEntry = JSON.parse(event.data);
                        if (logEntry.type === 'heartbeat') return;
                        this.appendLogEntry(logEntry);
                    } catch (e) {
                        console.warn('Failed to parse log entry:', e);
                    }
                };
                
                this.eventSource.onerror = (error) => {
                    console.warn('SSE connection error, falling back to polling:', error);
                    this.eventSource.close();
                    this.eventSource = null;
                    this.startLogsPolling();
                };
                
                return;
            } catch (e) {
                console.warn('SSE not supported, falling back to polling:', e);
            }
        }
        
        // Fallback to polling
        this.startLogsPolling();
    }
    
    startLogsPolling() {
        this.stopLogsAutoRefresh();
        this.logsInterval = setInterval(() => this.refreshLogs(), 2000);
    }

    stopLiveLogStream() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        this.stopLogsAutoRefresh();
    }

    stopLogsAutoRefresh() {
        if (this.logsInterval) {
            clearInterval(this.logsInterval);
            this.logsInterval = null;
        }
    }
    
    appendLogEntry(logEntry) {
        const logContent = document.getElementById('logContent');
        if (!logContent) return;
        
        const logLine = document.createElement('div');
        const timestamp = logEntry.timestamp || new Date().toLocaleTimeString();
        const message = logEntry.message || '';
        const type = logEntry.type || 'info';
        
        logLine.innerHTML = `<span style="color: var(--text-muted);">[${timestamp}]</span> <span style="color:${type === 'error' ? 'var(--error)' : 'var(--text-primary)'};">${this.escapeHtml(message)}</span>`;
        logContent.appendChild(logLine);
        
        // Auto-scroll to bottom
        logContent.scrollTop = logContent.scrollHeight;
        
        // Limit number of log lines to prevent memory issues
        const maxLines = 1000;
        while (logContent.children.length > maxLines) {
            logContent.removeChild(logContent.firstChild);
        }
    }

    async copyLogs() {
        const logContent = document.getElementById('logContent');
        if (!logContent) return this.showNotification('No logs to copy', 'warning');
        try {
            await navigator.clipboard.writeText(logContent.innerText);
            this.showNotification('Logs copied to clipboard', 'success');
        } catch (error) {
            this.showNotification('Failed to copy logs', 'error');
        }
    }

    /****************
     * Open Browser behavior (uses backend url)
     ****************/
    async openServerInBrowser(serverName) {
        try {
            const response = await fetch(`/api/open_browser/${encodeURIComponent(serverName)}`);
            const result = await response.json();
            // backend returns { success, url, message }
            if (result.success && result.url) {
                // open on client device automatically
                window.open(result.url, '_blank');
                this.showNotification(`Opened ${result.url}`, 'success');
            } else if (result.success && !result.url) {
                // fallback message
                this.showNotification(result.message || 'URL returned empty', 'warning');
            } else {
                // error from backend
                this.showNotification(result.message || 'Failed to open', 'error');
            }
        } catch (error) {
            this.showNotification('Error opening browser: ' + (error.message || error), 'error');
        }
    }

    async openBrowser() {
        if (!this.currentServer) return;
        await this.openServerInBrowser(this.currentServer);
    }

    /****************
     * Misc utilities / small UI bits
     ****************/
    async refreshAll() {
        await this.loadServers();
        this.updateStatus('Refreshed', 'success');
    }

    async showSystemInfo() {
        try {
            const response = await fetch('/api/system_info');
            const info = await response.json();
            const content = document.getElementById('systemInfoContent');
            if (!content) return;
            content.innerHTML = `
                <h4>System Information</h4>
                <p><strong>Operating System:</strong> ${this.escapeHtml(info.os || '')}</p>
                <p><strong>Architecture:</strong> ${this.escapeHtml(info.architecture || '')}</p>
                <p><strong>Python Version:</strong> ${this.escapeHtml(info.python_version || '')}</p>
                <p><strong>CPU Cores:</strong> ${this.escapeHtml(info.cpu_cores || '')}</p>
                <p><strong>Memory Total (GB):</strong> ${this.escapeHtml(String(info.memory_total_gb || info.memory_total || ''))}</p>
                <p><strong>Memory Available (GB):</strong> ${this.escapeHtml(String(info.memory_available_gb || info.memory_available || ''))}</p>
                <p><strong>Disk Free (GB):</strong> ${this.escapeHtml(String(info.disk_free_gb || info.disk_free || ''))}</p>
                <p><strong>Active Servers:</strong> ${this.escapeHtml(String(info.active_servers || '0'))}</p>
                <p><strong>PHP Available:</strong> ${(info.php_available ? 'Yes' : 'No')}</p>
                ${info.php_version ? `<p><strong>PHP Version:</strong> ${this.escapeHtml(info.php_version)}</p>` : ''}
                <p><strong>Node.js Available:</strong> ${(info.node_available ? 'Yes' : 'No')}</p>
                ${info.node_version ? `<p><strong>Node.js Version:</strong> ${this.escapeHtml(info.node_version)}</p>` : ''}
                <p><strong>Sites Folder:</strong> ${this.escapeHtml(info.sites_folder || info.current_folder || '')}</p>
            `;
            document.getElementById('systemModal').classList.add('show');
        } catch (error) {
            this.showNotification('Error loading system info: ' + (error.message || error), 'error');
        }
    }

    async checkSystemRequirements() {
        try {
            const [phpResponse, nodeResponse] = await Promise.all([fetch('/api/check_php'), fetch('/api/check_node')]);
            const phpInfo = await phpResponse.json();
            const nodeInfo = await nodeResponse.json();
            if (!phpInfo.available) {
                this.showNotification('PHP is not available - PHP servers will not work. Use the Install PHP button.', 'warning');
                const btn = document.getElementById('installPhpBtn'); if (btn) btn.style.display = 'inline-flex';
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
    
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();
            if (data.success) {
                this.updateSettingsUI(data.settings);
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
    
    updateSettingsUI(settings) {
        // Update toggle states based on backend settings
        const toggles = {
            'chkAutoRefresh': settings.AUTO_REFRESH_ON_LOAD,
            'chkAutoRestore': settings.AUTO_RESTORE_RUNNING,
            'chkBindAll': settings.BIND_ALL_DEFAULT,
            'chkAllowRemoteOpen': settings.ALLOW_REMOTE_OPEN_BROWSER,
            'chkDeleteFiles': settings.DELETE_SITE_ON_REMOVE
        };
        
        Object.entries(toggles).forEach(([id, value]) => {
            const checkbox = document.getElementById(id);
            if (checkbox) {
                checkbox.checked = value;
                const toggle = checkbox.closest('.toggle');
                if (toggle) {
                    if (value) toggle.classList.add('on');
                    else toggle.classList.remove('on');
                }
            }
        });
    }
    
    async saveSettings() {
        try {
            const settings = {};
            const toggles = {
                'chkAutoRefresh': 'AUTO_REFRESH_ON_LOAD',
                'chkAutoRestore': 'AUTO_RESTORE_RUNNING',
                'chkBindAll': 'BIND_ALL_DEFAULT',
                'chkAllowRemoteOpen': 'ALLOW_REMOTE_OPEN_BROWSER',
                'chkDeleteFiles': 'DELETE_SITE_ON_REMOVE'
            };
            
            Object.entries(toggles).forEach(([id, key]) => {
                const checkbox = document.getElementById(id);
                if (checkbox) {
                    settings[key] = checkbox.checked;
                }
            });
            
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            
            const data = await response.json();
            if (data.success) {
                this.showNotification('Settings saved successfully', 'success');
            } else {
                this.showNotification('Failed to save settings', 'error');
            }
        } catch (error) {
            this.showNotification('Error saving settings: ' + error.message, 'error');
        }
    }

    async installPHP() {
        const installBtn = document.getElementById('installPhpBtn');
        if (!installBtn) return this.showNotification('Install button missing', 'error');
        const orig = installBtn.innerHTML;
        installBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Installing PHP...';
        installBtn.disabled = true;
        try {
            const response = await fetch('/api/install_php', { method: 'POST' });
            const res = await response.json();
            if (res.success) {
                this.showNotification(res.message, 'success');
                installBtn.style.display = 'none';
            } else {
                this.showNotification(res.message || 'Install failed', 'error');
            }
        } catch (e) {
            this.showNotification('Error installing PHP: ' + (e.message || e), 'error');
        } finally {
            installBtn.innerHTML = orig;
            installBtn.disabled = false;
        }
    }

    closeModal(modal) {
        if (modal) modal.classList.remove('show');
        // stop any log streaming when closing logs modal
        if (modal && modal.id === 'logModal') {
            this.stopLiveLogStream();
            // Hide live indicator
            const liveBadge = document.getElementById('logLiveBadge');
            if (liveBadge) liveBadge.style.display = 'none';
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
        // reset
        setTimeout(() => {
            if (statusText) statusText.textContent = 'Ready';
            if (statusDot) statusDot.style.background = 'var(--success)';
        }, 3000);
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        if (!container) {
            // fallback alert
            if (type === 'error') console.error(message);
            else console.log(message);
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
                setTimeout(() => { if (notification.parentNode) notification.parentNode.removeChild(notification); }, 300);
            }
        }, 5000);
    }

    /****************
     * Auto refresh + cleanup with mobile optimization
     ****************/
    startAutoRefresh() {
        // Immediately refresh on start (ensures UI is always up-to-date)
        this.loadServers();
        
        // Adaptive refresh interval based on device type
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const interval = isMobile ? 15000 : 30000; // More frequent updates on mobile
        
        if (this.autoRefreshInterval) clearInterval(this.autoRefreshInterval);
        this.autoRefreshInterval = setInterval(() => {
            this.loadServers();
        }, interval);
        
        // Also check for server status changes more frequently
        this.startStatusCheck();
    }
    
    startStatusCheck() {
        if (this.statusInterval) clearInterval(this.statusInterval);
        this.statusInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                if (status.success) {
                    this.updateServerCount(status.running_servers, status.total_servers);
                }
            } catch (e) {
                console.warn('Status check failed:', e);
            }
        }, 5000); // Check every 5 seconds
    }
    
    updateServerCount(running, total) {
        const countElement = document.getElementById('serverCount');
        if (countElement) {
            countElement.textContent = `${running} of ${total} servers running`;
        }
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
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

    validatePort(input) {
        const port = parseInt(input.value);
        if (port < 1000 || port > 65535) {
            input.style.borderColor = 'var(--error)';
        } else {
            input.style.borderColor = 'var(--border-primary)';
        }
    }

    toggleSelectAll(checked) {
        // This was originally intended for selecting individual file checkboxes;
        // keep as a noop to not break existing UI unless you add file list checkboxes.
        this.showNotification('Toggle select all not wired to file list UI (implement if needed)', 'info');
    }

    /****************
     * Helpers for debugging / convenience
     ****************/
    async installPHP_if_button_exists() {
        const btn = document.getElementById('installPhpBtn');
        if (btn) btn.addEventListener('click', () => this.installPHP());
    }
}

// Ensure small CSS animation exists (keeps original style addition)
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    /* Minimal upload progress element (if present) */
    #uploadProgressBar { width: 100%; background: #111; height: 6px; border-radius: 3px; overflow: hidden; margin-top:6px; }
    #uploadProgressBar > .bar { width: 0%; height:100%; text-align:center; font-size:11px; line-height:6px; color:#fff; }
`;
document.head.appendChild(style);

// Initialize
let serverAdmin;
document.addEventListener('DOMContentLoaded', () => {
    serverAdmin = new ServerAdmin();
    // Hook install PHP button if exists
    serverAdmin.installPHP_if_button_exists();
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    if (serverAdmin) serverAdmin.stopAutoRefresh();
});
