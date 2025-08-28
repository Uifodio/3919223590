// Nexus Editor - Pure JavaScript Implementation
class NexusEditor {
    constructor() {
        this.tabs = [];
        this.activeTabIndex = 0;
        this.closedTabs = [];
        this.searchResults = [];
        this.currentSearchIndex = 0;
        this.isSearchMode = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.createDefaultTab();
        this.updateLineNumbers();
        this.updateStatusBar();
        this.loadSession();
    }

    setupEventListeners() {
        // Toolbar buttons
        document.getElementById('newBtn').addEventListener('click', () => this.newFile());
        document.getElementById('openBtn').addEventListener('click', () => this.openFile());
        document.getElementById('saveBtn').addEventListener('click', () => this.saveFile());
        document.getElementById('findBtn').addEventListener('click', () => this.showSearchPanel('find'));
        document.getElementById('replaceBtn').addEventListener('click', () => this.showSearchPanel('replace'));
        document.getElementById('pinBtn').addEventListener('click', () => this.toggleAlwaysOnTop());
        document.getElementById('fullBtn').addEventListener('click', () => this.toggleFullscreen());

        // New tab button
        document.getElementById('newTabBtn').addEventListener('click', () => this.createNewTab());

        // Editor events
        const editor = document.getElementById('editor');
        editor.addEventListener('input', () => this.onEditorChange());
        editor.addEventListener('scroll', () => this.syncLineNumbers());
        editor.addEventListener('keydown', (e) => this.handleKeyDown(e));

        // Search panel events
        document.getElementById('findInput').addEventListener('input', () => this.performSearch());
        document.getElementById('replaceInput').addEventListener('input', () => this.performSearch());
        document.getElementById('caseSensitive').addEventListener('change', () => this.performSearch());
        document.getElementById('wholeWord').addEventListener('change', () => this.performSearch());

        // Search action buttons
        document.getElementById('findBtn').addEventListener('click', () => this.findNext());
        document.getElementById('replaceBtn').addEventListener('click', () => this.replaceCurrent());
        document.getElementById('replaceAllBtn').addEventListener('click', () => this.replaceAll());
        document.getElementById('prevBtn').addEventListener('click', () => this.findPrevious());
        document.getElementById('nextBtn').addEventListener('click', () => this.findNext());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleGlobalKeyDown(e));
    }

    createDefaultTab() {
        const tab = {
            id: this.generateId(),
            title: 'Untitled',
            content: '',
            filePath: null,
            modified: false
        };
        
        this.tabs = [tab];
        this.activeTabIndex = 0;
        this.updateTabBar();
        this.updateEditorContent();
    }

    createNewTab() {
        const tab = {
            id: this.generateId(),
            title: 'Untitled',
            content: '',
            filePath: null,
            modified: false
        };
        
        this.tabs.push(tab);
        this.activeTabIndex = this.tabs.length - 1;
        this.updateTabBar();
        this.updateEditorContent();
        this.updateLineNumbers();
    }

    closeTab(tabElement) {
        const tabId = tabElement.closest('.tab').dataset.tabId;
        const tabIndex = this.tabs.findIndex(tab => tab.id === tabId);
        
        if (tabIndex === -1) return;
        
        // Save to closed tabs history
        this.closedTabs.unshift(this.tabs[tabIndex]);
        if (this.closedTabs.length > 10) {
            this.closedTabs.pop();
        }
        
        // Remove tab
        this.tabs.splice(tabIndex, 1);
        
        // Adjust active tab index
        if (this.tabs.length === 0) {
            this.createDefaultTab();
        } else if (this.activeTabIndex >= this.tabs.length) {
            this.activeTabIndex = this.tabs.length - 1;
        } else if (this.activeTabIndex > tabIndex) {
            this.activeTabIndex--;
        }
        
        this.updateTabBar();
        this.updateEditorContent();
        this.updateLineNumbers();
        this.updateStatusBar();
    }

    updateTabBar() {
        const tabList = document.getElementById('tabList');
        tabList.innerHTML = '';
        
        this.tabs.forEach((tab, index) => {
            const tabElement = document.createElement('div');
            tabElement.className = `tab ${index === this.activeTabIndex ? 'active' : ''}`;
            tabElement.dataset.tabId = tab.id;
            tabElement.onclick = () => this.switchToTab(index);
            
            tabElement.innerHTML = `
                <span class="tab-title">${tab.title}${tab.modified ? ' *' : ''}</span>
                <button class="tab-close" onclick="event.stopPropagation(); editor.closeTab(this)">×</button>
            `;
            
            tabList.appendChild(tabElement);
        });
    }

    switchToTab(index) {
        if (index === this.activeTabIndex) return;
        
        this.activeTabIndex = index;
        this.updateTabBar();
        this.updateEditorContent();
        this.updateLineNumbers();
        this.updateStatusBar();
    }

    updateEditorContent() {
        const editor = document.getElementById('editor');
        const activeTab = this.tabs[this.activeTabIndex];
        
        if (activeTab) {
            editor.value = activeTab.content;
            editor.focus();
        }
    }

    onEditorChange() {
        const editor = document.getElementById('editor');
        const activeTab = this.tabs[this.activeTabIndex];
        
        if (activeTab) {
            const newContent = editor.value;
            const wasModified = activeTab.modified;
            
            activeTab.content = newContent;
            activeTab.modified = newContent !== '';
            
            if (wasModified !== activeTab.modified) {
                this.updateTabBar();
            }
            
            this.updateLineNumbers();
            this.updateStatusBar();
            this.saveSession();
        }
    }

    updateLineNumbers() {
        const lineNumbers = document.getElementById('lineNumbers');
        const editor = document.getElementById('editor');
        const lines = editor.value.split('\n');
        
        lineNumbers.innerHTML = '';
        
        for (let i = 1; i <= Math.max(lines.length, 1); i++) {
            const lineNumber = document.createElement('div');
            lineNumber.className = 'line-number';
            lineNumber.textContent = i;
            lineNumbers.appendChild(lineNumber);
        }
    }

    syncLineNumbers() {
        const editor = document.getElementById('editor');
        const lineNumbers = document.getElementById('lineNumbers');
        lineNumbers.scrollTop = editor.scrollTop;
    }

    updateStatusBar() {
        const editor = document.getElementById('editor');
        const cursorPos = editor.selectionStart;
        const textBeforeCursor = editor.value.substring(0, cursorPos);
        const lines = textBeforeCursor.split('\n');
        const line = lines.length;
        const column = lines[lines.length - 1].length + 1;
        const totalLines = editor.value.split('\n').length;
        
        document.getElementById('statusText').textContent = `Line ${line}, Column ${column}`;
        document.getElementById('totalLines').textContent = `Total: ${totalLines} line${totalLines !== 1 ? 's' : ''}`;
    }

    showSearchPanel(mode) {
        const searchPanel = document.getElementById('searchPanel');
        const replaceGroup = document.getElementById('replaceGroup');
        const replaceBtn = document.getElementById('replaceBtn');
        const replaceAllBtn = document.getElementById('replaceAllBtn');
        const searchMode = document.querySelector('.search-mode');
        
        this.isSearchMode = mode;
        
        if (mode === 'replace') {
            replaceGroup.style.display = 'block';
            replaceBtn.style.display = 'block';
            replaceAllBtn.style.display = 'block';
            searchMode.textContent = '🔍 Replace';
        } else {
            replaceGroup.style.display = 'none';
            replaceBtn.style.display = 'none';
            replaceAllBtn.style.display = 'none';
            searchMode.textContent = '🔍 Find';
        }
        
        searchPanel.style.display = 'block';
        document.getElementById('findInput').focus();
        document.getElementById('findInput').select();
    }

    hideSearchPanel() {
        document.getElementById('searchPanel').style.display = 'none';
        document.getElementById('editor').focus();
    }

    performSearch() {
        const findText = document.getElementById('findInput').value;
        const replaceText = document.getElementById('replaceInput').value;
        const caseSensitive = document.getElementById('caseSensitive').checked;
        const wholeWord = document.getElementById('wholeWord').checked;
        
        if (!findText.trim()) {
            this.searchResults = [];
            this.currentSearchIndex = 0;
            return;
        }
        
        const editor = document.getElementById('editor');
        const content = editor.value;
        const searchTerm = caseSensitive ? findText : findText.toLowerCase();
        const searchContent = caseSensitive ? content : content.toLowerCase();
        
        this.searchResults = [];
        let searchIndex = 0;
        
        while (true) {
            const index = searchContent.indexOf(searchTerm, searchIndex);
            if (index === -1) break;
            
            if (wholeWord) {
                const before = searchContent[index - 1] || ' ';
                const after = searchContent[index + searchTerm.length] || ' ';
                const wordBoundary = /[a-zA-Z0-9_]/.test(before) || /[a-zA-Z0-9_]/.test(after);
                if (wordBoundary) {
                    searchIndex = index + 1;
                    continue;
                }
            }
            
            this.searchResults.push({
                index: index,
                length: searchTerm.length
            });
            
            searchIndex = index + 1;
        }
        
        this.currentSearchIndex = 0;
        this.highlightSearchResults();
    }

    highlightSearchResults() {
        const editor = document.getElementById('editor');
        const content = editor.value;
        
        // Remove previous highlights
        editor.style.background = '#1e1e1e';
        
        if (this.searchResults.length > 0) {
            // Highlight current result
            const current = this.searchResults[this.currentSearchIndex];
            const before = content.substring(0, current.index);
            const after = content.substring(current.index + current.length);
            
            // Scroll to current result
            const lines = before.split('\n');
            const lineNumber = lines.length;
            const lineHeight = 21;
            const scrollTop = (lineNumber - 1) * lineHeight;
            editor.scrollTop = scrollTop;
            
            // Set cursor to current result
            editor.setSelectionRange(current.index, current.index + current.length);
            editor.focus();
        }
    }

    findNext() {
        if (this.searchResults.length === 0) return;
        
        this.currentSearchIndex = (this.currentSearchIndex + 1) % this.searchResults.length;
        this.highlightSearchResults();
    }

    findPrevious() {
        if (this.searchResults.length === 0) return;
        
        this.currentSearchIndex = this.currentSearchIndex === 0 ? 
            this.searchResults.length - 1 : this.currentSearchIndex - 1;
        this.highlightSearchResults();
    }

    replaceCurrent() {
        if (this.searchResults.length === 0) return;
        
        const replaceText = document.getElementById('replaceInput').value;
        const current = this.searchResults[this.currentSearchIndex];
        const editor = document.getElementById('editor');
        const content = editor.value;
        
        const newContent = content.substring(0, current.index) + 
                          replaceText + 
                          content.substring(current.index + current.length);
        
        editor.value = newContent;
        this.tabs[this.activeTabIndex].content = newContent;
        this.tabs[this.activeTabIndex].modified = true;
        
        // Remove the replaced result
        this.searchResults.splice(this.currentSearchIndex, 1);
        if (this.searchResults.length === 0) {
            this.currentSearchIndex = 0;
        } else {
            this.currentSearchIndex = Math.min(this.currentSearchIndex, this.searchResults.length - 1);
        }
        
        this.updateTabBar();
        this.updateLineNumbers();
        this.updateStatusBar();
        this.highlightSearchResults();
    }

    replaceAll() {
        const findText = document.getElementById('findInput').value;
        const replaceText = document.getElementById('replaceInput').value;
        const caseSensitive = document.getElementById('caseSensitive').checked;
        const wholeWord = document.getElementById('wholeWord').checked;
        
        if (!findText.trim() || this.searchResults.length === 0) return;
        
        const editor = document.getElementById('editor');
        let content = editor.value;
        let offset = 0;
        
        // Sort results by index in descending order to avoid offset issues
        const sortedResults = [...this.searchResults].sort((a, b) => b.index - a.index);
        
        for (const result of sortedResults) {
            const before = content.substring(0, result.index + offset);
            const after = content.substring(result.index + result.length + offset);
            content = before + replaceText + after;
            offset += replaceText.length - result.length;
        }
        
        editor.value = content;
        this.tabs[this.activeTabIndex].content = content;
        this.tabs[this.activeTabIndex].modified = true;
        
        this.searchResults = [];
        this.currentSearchIndex = 0;
        
        this.updateTabBar();
        this.updateLineNumbers();
        this.updateStatusBar();
    }

    handleKeyDown(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            
            e.target.value = e.target.value.substring(0, start) + '  ' + e.target.value.substring(end);
            e.target.selectionStart = e.target.selectionEnd = start + 2;
            this.onEditorChange();
        } else if (e.key === 'Enter') {
            // Auto-indent
            const start = e.target.selectionStart;
            const lines = e.target.value.substring(0, start).split('\n');
            const currentLine = lines[lines.length - 1];
            const indent = currentLine.match(/^(\s*)/)[0];
            
            setTimeout(() => {
                const newValue = e.target.value.substring(0, start) + '\n' + indent + e.target.value.substring(start);
                e.target.value = newValue;
                e.target.selectionStart = e.target.selectionEnd = start + 1 + indent.length;
                this.onEditorChange();
            }, 0);
        }
    }

    handleGlobalKeyDown(e) {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'n':
                    e.preventDefault();
                    this.newFile();
                    break;
                case 'o':
                    e.preventDefault();
                    this.openFile();
                    break;
                case 's':
                    e.preventDefault();
                    this.saveFile();
                    break;
                case 'f':
                    e.preventDefault();
                    this.showSearchPanel('find');
                    break;
                case 'h':
                    e.preventDefault();
                    this.showSearchPanel('replace');
                    break;
                case 't':
                    e.preventDefault();
                    this.createNewTab();
                    break;
                case 'w':
                    e.preventDefault();
                    if (this.tabs.length > 1) {
                        this.closeTab(document.querySelector('.tab.active'));
                    }
                    break;
            }
        } else if (e.key === 'F3') {
            e.preventDefault();
            if (e.shiftKey) {
                this.findPrevious();
            } else {
                this.findNext();
            }
        } else if (e.key === 'Escape') {
            if (this.isSearchMode) {
                this.hideSearchPanel();
            }
        }
    }

    newFile() {
        this.createNewTab();
    }

    openFile() {
        if (window.electronAPI?.openFileDialog) {
            window.electronAPI.openFileDialog().then(result => {
                if (result && !result.canceled && result.filePaths.length > 0) {
                    this.loadFile(result.filePaths[0]);
                }
            });
        } else {
            // Browser fallback
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.txt,.js,.py,.cs,.html,.css,.json,.c,.cpp,.h';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        this.loadFileContent(file.name, e.target.result);
                    };
                    reader.readAsText(file);
                }
            };
            input.click();
        }
    }

    loadFile(filePath) {
        if (window.electronAPI?.readFile) {
            window.electronAPI.readFile(filePath).then(result => {
                if (result.success) {
                    this.loadFileContent(filePath.split('/').pop() || filePath.split('\\').pop(), result.content);
                }
            });
        }
    }

    loadFileContent(fileName, content) {
        const tab = {
            id: this.generateId(),
            title: fileName,
            content: content,
            filePath: fileName,
            modified: false
        };
        
        this.tabs.push(tab);
        this.activeTabIndex = this.tabs.length - 1;
        this.updateTabBar();
        this.updateEditorContent();
        this.updateLineNumbers();
        this.updateStatusBar();
    }

    saveFile() {
        const activeTab = this.tabs[this.activeTabIndex];
        if (!activeTab) return;
        
        if (window.electronAPI?.saveFileDialog) {
            window.electronAPI.saveFileDialog(activeTab.filePath || 'untitled.txt').then(result => {
                if (result && !result.canceled && result.filePath) {
                    this.saveFileContent(result.filePath, activeTab.content);
                    activeTab.filePath = result.filePath;
                    activeTab.title = result.filePath.split('/').pop() || result.filePath.split('\\').pop();
                    activeTab.modified = false;
                    this.updateTabBar();
                }
            });
        } else {
            // Browser fallback
            const blob = new Blob([activeTab.content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = activeTab.filePath || 'untitled.txt';
            a.click();
            URL.revokeObjectURL(url);
        }
    }

    saveFileContent(filePath, content) {
        if (window.electronAPI?.writeFile) {
            window.electronAPI.writeFile(filePath, content);
        }
    }

    toggleAlwaysOnTop() {
        if (window.electronAPI?.setAlwaysOnTop) {
            const pinBtn = document.getElementById('pinBtn');
            const isActive = pinBtn.classList.contains('active');
            window.electronAPI.setAlwaysOnTop(!isActive);
            pinBtn.classList.toggle('active');
        }
    }

    toggleFullscreen() {
        if (window.electronAPI?.setFullscreen) {
            const fullBtn = document.getElementById('fullBtn');
            const isActive = fullBtn.classList.contains('active');
            window.electronAPI.setFullscreen(!isActive);
            fullBtn.classList.toggle('active');
        }
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    saveSession() {
        try {
            const session = {
                tabs: this.tabs,
                activeTabIndex: this.activeTabIndex,
                timestamp: Date.now()
            };
            localStorage.setItem('nexus-editor-session', JSON.stringify(session));
        } catch (error) {
            console.log('Could not save session');
        }
    }

    loadSession() {
        try {
            const sessionData = localStorage.getItem('nexus-editor-session');
            if (sessionData) {
                const session = JSON.parse(sessionData);
                if (session.tabs && session.tabs.length > 0) {
                    this.tabs = session.tabs;
                    this.activeTabIndex = Math.min(session.activeTabIndex || 0, this.tabs.length - 1);
                    this.updateTabBar();
                    this.updateEditorContent();
                    this.updateLineNumbers();
                    this.updateStatusBar();
                }
            }
        } catch (error) {
            console.log('Could not load session');
        }
    }
}

// Initialize the editor when the page loads
let editor;
document.addEventListener('DOMContentLoaded', () => {
    editor = new NexusEditor();
});

// Make editor globally accessible for onclick handlers
window.editor = editor;