const { ipcRenderer } = require('electron');
const path = require('path');

// Global variables
let editor = null;
let currentFile = null;
let openTabs = [];
let currentTab = null;
let fileTreeData = [];
let currentDirectory = process.cwd();

// DOM elements
const fileTree = document.getElementById('fileTree');
const tabContainer = document.getElementById('tabContainer');
const editorContainer = document.getElementById('editor');
const currentFileSpan = document.getElementById('currentFile');
const lineInfoSpan = document.getElementById('lineInfo');
const saveFileBtn = document.getElementById('saveFileBtn');
const newFileBtn = document.getElementById('newFileBtn');
const openFileBtn = document.getElementById('openFileBtn');
const refreshExplorerBtn = document.getElementById('refreshExplorerBtn');
const newFolderBtn = document.getElementById('newFolderBtn');
const contextMenu = document.getElementById('contextMenu');
const modal = document.getElementById('modal');

// Initialize the application
async function init() {
    console.log('🚀 Initializing Unity Code Editor...');
    
    // Initialize Monaco Editor
    await initMonacoEditor();
    
    // Load file tree
    await loadFileTree();
    
    // Set up event listeners
    setupEventListeners();
    
    console.log('✅ Unity Code Editor initialized successfully!');
}

// Initialize Monaco Editor
async function initMonacoEditor() {
    return new Promise((resolve) => {
        require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
        
        require(['vs/editor/editor.main'], function () {
            // Configure Monaco Editor
            monaco.editor.defineTheme('vs-dark', {
                base: 'vs-dark',
                inherit: true,
                rules: [],
                colors: {
                    'editor.background': '#1e1e1e',
                    'editor.foreground': '#d4d4d4',
                    'editor.lineHighlightBackground': '#2a2d2e',
                    'editor.selectionBackground': '#094771',
                    'editor.inactiveSelectionBackground': '#3a3d3e'
                }
            });
            
            // Create editor instance
            editor = monaco.editor.create(editorContainer, {
                value: '// Welcome to Unity Code Editor!\n// Open a file to start editing.',
                language: 'javascript',
                theme: 'vs-dark',
                automaticLayout: true,
                minimap: { enabled: true },
                scrollBeyondLastLine: false,
                fontSize: 14,
                fontFamily: 'Consolas, "Courier New", monospace',
                lineNumbers: 'on',
                roundedSelection: false,
                scrollbar: {
                    vertical: 'visible',
                    horizontal: 'visible'
                }
            });
            
            // Set up editor event listeners
            editor.onDidChangeCursorPosition((e) => {
                updateLineInfo(e.position.lineNumber, e.position.column);
            });
            
            editor.onDidChangeModelContent(() => {
                if (currentFile) {
                    currentFile.modified = true;
                    updateTabTitle(currentFile);
                }
            });
            
            resolve();
        });
    });
}

// Load file tree
async function loadFileTree() {
    try {
        const result = await ipcRenderer.invoke('read-directory', currentDirectory);
        if (result.success) {
            fileTreeData = result.items;
            renderFileTree();
        } else {
            showError('Failed to load file tree: ' + result.error);
        }
    } catch (error) {
        showError('Error loading file tree: ' + error.message);
    }
}

// Render file tree
function renderFileTree() {
    fileTree.innerHTML = '';
    
    if (fileTreeData.length === 0) {
        fileTree.innerHTML = '<div class="loading">No files found</div>';
        return;
    }
    
    // Sort: folders first, then files
    const sortedItems = fileTreeData.sort((a, b) => {
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
    });
    
    sortedItems.forEach(item => {
        const itemElement = createFileTreeItem(item);
        fileTree.appendChild(itemElement);
    });
}

// Create file tree item element
function createFileTreeItem(item) {
    const div = document.createElement('div');
    div.className = `file-tree-item ${item.isDirectory ? 'folder' : 'file'}`;
    div.dataset.path = item.path;
    
    const icon = document.createElement('i');
    if (item.isDirectory) {
        icon.className = 'fas fa-folder';
    } else {
        icon.className = getFileIcon(item.name);
        div.classList.add(getFileExtension(item.name));
    }
    
    const name = document.createElement('span');
    name.className = 'file-name';
    name.textContent = item.name;
    
    div.appendChild(icon);
    div.appendChild(name);
    
    // Add event listeners
    div.addEventListener('click', (e) => {
        e.stopPropagation();
        selectFileTreeItem(div);
        
        if (!item.isDirectory) {
            openFile(item.path);
        }
    });
    
    div.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showContextMenu(e, item);
    });
    
    return div;
}

// Get file icon based on extension
function getFileIcon(filename) {
    const ext = path.extname(filename).toLowerCase();
    const iconMap = {
        '.cs': 'fas fa-code',
        '.js': 'fab fa-js-square',
        '.py': 'fab fa-python',
        '.html': 'fab fa-html5',
        '.css': 'fab fa-css3-alt',
        '.json': 'fas fa-brackets-curly',
        '.xml': 'fas fa-file-code',
        '.txt': 'fas fa-file-alt',
        '.md': 'fas fa-file-alt',
        '.sh': 'fas fa-terminal',
        '.bat': 'fas fa-terminal',
        '.exe': 'fas fa-cog',
        '.dll': 'fas fa-cog',
        '.png': 'fas fa-image',
        '.jpg': 'fas fa-image',
        '.jpeg': 'fas fa-image',
        '.gif': 'fas fa-image',
        '.ico': 'fas fa-image',
        '.mp3': 'fas fa-music',
        '.mp4': 'fas fa-video',
        '.zip': 'fas fa-file-archive',
        '.rar': 'fas fa-file-archive',
        '.7z': 'fas fa-file-archive'
    };
    
    return iconMap[ext] || 'fas fa-file';
}

// Get file extension class
function getFileExtension(filename) {
    return path.extname(filename).toLowerCase().replace('.', '');
}

// Select file tree item
function selectFileTreeItem(element) {
    // Remove previous selection
    document.querySelectorAll('.file-tree-item.selected').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Add selection to current item
    element.classList.add('selected');
}

// Open file
async function openFile(filePath) {
    try {
        // Check if file is already open
        const existingTab = openTabs.find(tab => tab.path === filePath);
        if (existingTab) {
            switchToTab(existingTab);
            return;
        }
        
        // Read file content
        const result = await ipcRenderer.invoke('read-file', filePath);
        if (result.success) {
            // Create new tab
            const tab = {
                path: filePath,
                name: path.basename(filePath),
                content: result.content,
                modified: false
            };
            
            openTabs.push(tab);
            createTab(tab);
            switchToTab(tab);
            
            // Set editor content and language
            const language = getLanguageFromExtension(path.extname(filePath));
            monaco.editor.setModelLanguage(editor.getModel(), language);
            editor.setValue(result.content);
            
            // Update status
            currentFile = tab;
            currentFileSpan.textContent = filePath;
            saveFileBtn.disabled = false;
            
        } else {
            showError('Failed to open file: ' + result.error);
        }
    } catch (error) {
        showError('Error opening file: ' + error.message);
    }
}

// Get language from file extension
function getLanguageFromExtension(ext) {
    const languageMap = {
        '.cs': 'csharp',
        '.js': 'javascript',
        '.py': 'python',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.xml': 'xml',
        '.txt': 'plaintext',
        '.md': 'markdown',
        '.sh': 'shell',
        '.bat': 'batch',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.java': 'java',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.vue': 'html',
        '.svelte': 'html'
    };
    
    return languageMap[ext.toLowerCase()] || 'plaintext';
}

// Create tab
function createTab(tab) {
    const tabElement = document.createElement('div');
    tabElement.className = 'tab';
    tabElement.dataset.path = tab.path;
    
    const name = document.createElement('span');
    name.className = 'tab-name';
    name.textContent = tab.name;
    
    const close = document.createElement('span');
    close.className = 'tab-close';
    close.innerHTML = '&times;';
    close.addEventListener('click', (e) => {
        e.stopPropagation();
        closeTab(tab);
    });
    
    tabElement.appendChild(name);
    tabElement.appendChild(close);
    
    tabElement.addEventListener('click', () => {
        switchToTab(tab);
    });
    
    // Remove placeholder if it exists
    const placeholder = tabContainer.querySelector('.tab-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    tabContainer.appendChild(tabElement);
}

// Switch to tab
function switchToTab(tab) {
    // Update tab selection
    document.querySelectorAll('.tab').forEach(tabEl => {
        tabEl.classList.remove('active');
    });
    
    const tabElement = document.querySelector(`[data-path="${tab.path}"]`);
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
    // Update editor content
    editor.setValue(tab.content);
    
    // Set language
    const language = getLanguageFromExtension(path.extname(tab.path));
    monaco.editor.setModelLanguage(editor.getModel(), language);
    
    // Update current file
    currentFile = tab;
    currentFileSpan.textContent = tab.path;
    saveFileBtn.disabled = false;
    
    currentTab = tab;
}

// Close tab
function closeTab(tab) {
    const index = openTabs.indexOf(tab);
    if (index > -1) {
        openTabs.splice(index, 1);
        
        // Remove tab element
        const tabElement = document.querySelector(`[data-path="${tab.path}"]`);
        if (tabElement) {
            tabElement.remove();
        }
        
        // If this was the current tab, switch to another
        if (currentTab === tab) {
            if (openTabs.length > 0) {
                const nextTab = openTabs[Math.min(index, openTabs.length - 1)];
                switchToTab(nextTab);
            } else {
                // No tabs left, show placeholder
                showTabPlaceholder();
                currentFile = null;
                currentTab = null;
                currentFileSpan.textContent = 'No file open';
                saveFileBtn.disabled = true;
                editor.setValue('// Welcome to Unity Code Editor!\n// Open a file to start editing.');
            }
        }
    }
}

// Show tab placeholder
function showTabPlaceholder() {
    tabContainer.innerHTML = `
        <div class="tab-placeholder">
            <i class="fas fa-file-code"></i>
            <p>Open a file to start editing</p>
        </div>
    `;
}

// Update tab title
function updateTabTitle(tab) {
    const tabElement = document.querySelector(`[data-path="${tab.path}"]`);
    if (tabElement) {
        const nameElement = tabElement.querySelector('.tab-name');
        nameElement.textContent = tab.modified ? tab.name + ' *' : tab.name;
    }
}

// Update line info
function updateLineInfo(line, column) {
    lineInfoSpan.textContent = `Line ${line}, Column ${column}`;
}

// Show context menu
function showContextMenu(event, item) {
    contextMenu.style.display = 'block';
    contextMenu.style.left = event.pageX + 'px';
    contextMenu.style.top = event.pageY + 'px';
    
    // Store current item for context menu actions
    contextMenu.dataset.currentItem = JSON.stringify(item);
}

// Hide context menu
function hideContextMenu() {
    contextMenu.style.display = 'none';
}

// Show modal
function showModal(title, content) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalContent').innerHTML = content;
    modal.style.display = 'flex';
}

// Hide modal
function hideModal() {
    modal.style.display = 'none';
}

// Show error
function showError(message) {
    console.error('Error:', message);
    // You can implement a proper error notification system here
    alert('Error: ' + message);
}

// Set up event listeners
function setupEventListeners() {
    // Button events
    newFileBtn.addEventListener('click', () => {
        showModal('New File', `
            <div class="form-group">
                <label for="newFileName">File Name:</label>
                <input type="text" id="newFileName" placeholder="Enter file name (e.g., script.cs)">
            </div>
        `);
        
        document.getElementById('modalConfirm').onclick = () => {
            const fileName = document.getElementById('newFileName').value;
            if (fileName) {
                const filePath = path.join(currentDirectory, fileName);
                createNewFile(filePath);
                hideModal();
            }
        };
    });
    
    openFileBtn.addEventListener('click', async () => {
        // This will be handled by the main process
        ipcRenderer.send('open-file-dialog');
    });
    
    saveFileBtn.addEventListener('click', () => {
        if (currentFile) {
            saveCurrentFile();
        }
    });
    
    refreshExplorerBtn.addEventListener('click', () => {
        loadFileTree();
    });
    
    newFolderBtn.addEventListener('click', () => {
        showModal('New Folder', `
            <div class="form-group">
                <label for="newFolderName">Folder Name:</label>
                <input type="text" id="newFolderName" placeholder="Enter folder name">
            </div>
        `);
        
        document.getElementById('modalConfirm').onclick = () => {
            const folderName = document.getElementById('newFolderName').value;
            if (folderName) {
                const folderPath = path.join(currentDirectory, folderName);
                createNewFolder(folderPath);
                hideModal();
            }
        };
    });
    
    // Context menu events
    document.addEventListener('click', hideContextMenu);
    
    contextMenu.addEventListener('click', (e) => {
        const action = e.target.closest('.context-item')?.dataset.action;
        if (action) {
            const item = JSON.parse(contextMenu.dataset.currentItem);
            handleContextMenuAction(action, item);
            hideContextMenu();
        }
    });
    
    // Modal events
    document.querySelector('.modal-close').addEventListener('click', hideModal);
    document.getElementById('modalCancel').addEventListener('click', hideModal);
    
    // IPC events
    ipcRenderer.on('new-file', () => {
        newFileBtn.click();
    });
    
    ipcRenderer.on('open-file', (event, filePath) => {
        openFile(filePath);
    });
    
    ipcRenderer.on('save-file', () => {
        saveFileBtn.click();
    });
    
    ipcRenderer.on('save-file-as', (event, filePath) => {
        if (currentFile) {
            saveFileAs(filePath);
        }
    });
}

// Handle context menu actions
async function handleContextMenuAction(action, item) {
    switch (action) {
        case 'open':
            if (!item.isDirectory) {
                openFile(item.path);
            }
            break;
        case 'rename':
            showModal('Rename', `
                <div class="form-group">
                    <label for="newName">New Name:</label>
                    <input type="text" id="newName" value="${item.name}">
                </div>
            `);
            
            document.getElementById('modalConfirm').onclick = () => {
                const newName = document.getElementById('newName').value;
                if (newName && newName !== item.name) {
                    renameItem(item.path, newName);
                    hideModal();
                }
            };
            break;
        case 'delete':
            if (confirm(`Are you sure you want to delete "${item.name}"?`)) {
                deleteItem(item.path);
            }
            break;
        case 'copy-path':
            navigator.clipboard.writeText(item.path);
            break;
    }
}

// Create new file
async function createNewFile(filePath) {
    try {
        const result = await ipcRenderer.invoke('write-file', filePath, '');
        if (result.success) {
            await loadFileTree();
            openFile(filePath);
        } else {
            showError('Failed to create file: ' + result.error);
        }
    } catch (error) {
        showError('Error creating file: ' + error.message);
    }
}

// Create new folder
async function createNewFolder(folderPath) {
    try {
        const result = await ipcRenderer.invoke('create-directory', folderPath);
        if (result.success) {
            await loadFileTree();
        } else {
            showError('Failed to create folder: ' + result.error);
        }
    } catch (error) {
        showError('Error creating folder: ' + error.message);
    }
}

// Save current file
async function saveCurrentFile() {
    if (!currentFile) return;
    
    try {
        const content = editor.getValue();
        const result = await ipcRenderer.invoke('write-file', currentFile.path, content);
        if (result.success) {
            currentFile.content = content;
            currentFile.modified = false;
            updateTabTitle(currentFile);
        } else {
            showError('Failed to save file: ' + result.error);
        }
    } catch (error) {
        showError('Error saving file: ' + error.message);
    }
}

// Save file as
async function saveFileAs(filePath) {
    try {
        const content = editor.getValue();
        const result = await ipcRenderer.invoke('write-file', filePath, content);
        if (result.success) {
            // Create new tab for the saved file
            const tab = {
                path: filePath,
                name: path.basename(filePath),
                content: content,
                modified: false
            };
            
            openTabs.push(tab);
            createTab(tab);
            switchToTab(tab);
        } else {
            showError('Failed to save file: ' + result.error);
        }
    } catch (error) {
        showError('Error saving file: ' + error.message);
    }
}

// Rename item
async function renameItem(oldPath, newName) {
    try {
        const newPath = path.join(path.dirname(oldPath), newName);
        // For now, we'll use a simple approach - delete and recreate
        // In a real implementation, you'd use fs.rename
        showError('Rename functionality not implemented yet');
    } catch (error) {
        showError('Error renaming item: ' + error.message);
    }
}

// Delete item
async function deleteItem(itemPath) {
    try {
        const result = await ipcRenderer.invoke('delete-item', itemPath);
        if (result.success) {
            // Close tab if it's open
            const openTab = openTabs.find(tab => tab.path === itemPath);
            if (openTab) {
                closeTab(openTab);
            }
            
            await loadFileTree();
        } else {
            showError('Failed to delete item: ' + result.error);
        }
    } catch (error) {
        showError('Error deleting item: ' + error.message);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);