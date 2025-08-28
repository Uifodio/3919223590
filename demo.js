/**
 * Nexus Editor JavaScript Demo
 * Demonstrates syntax highlighting for JavaScript/TypeScript
 */

// Constants and configuration
const APP_CONFIG = {
    name: 'Nexus Editor',
    version: '1.0.0',
    theme: 'dark',
    features: ['syntax-highlighting', 'tabs', 'search', 'replace']
};

// Class definition for Editor
class CodeEditor {
    constructor(config = {}) {
        this.config = { ...APP_CONFIG, ...config };
        this.tabs = [];
        this.activeTabIndex = 0;
        this.isModified = false;
        this.searchQuery = '';
        this.searchResults = [];
        
        this.initialize();
    }
    
    /**
     * Initialize the editor
     */
    initialize() {
        console.log(`Initializing ${this.config.name} v${this.config.version}`);
        this.setupEventListeners();
        this.createDefaultTab();
        this.applyTheme();
    }
    
    /**
     * Setup event listeners for keyboard shortcuts
     */
    setupEventListeners() {
        document.addEventListener('keydown', (event) => {
            this.handleKeyboardShortcuts(event);
        });
        
        // Handle window focus/blur
        window.addEventListener('focus', () => {
            this.onWindowFocus();
        });
        
        window.addEventListener('blur', () => {
            this.onWindowBlur();
        });
    }
    
    /**
     * Handle keyboard shortcuts
     * @param {KeyboardEvent} event - The keyboard event
     */
    handleKeyboardShortcuts(event) {
        const { ctrlKey, shiftKey, key } = event;
        
        // File operations
        if (ctrlKey && !shiftKey) {
            switch (key) {
                case 'n':
                    event.preventDefault();
                    this.createNewTab();
                    break;
                case 'o':
                    event.preventDefault();
                    this.openFile();
                    break;
                case 's':
                    event.preventDefault();
                    this.saveFile();
                    break;
                case 'f':
                    event.preventDefault();
                    this.showSearchPanel();
                    break;
                case 'h':
                    event.preventDefault();
                    this.showReplacePanel();
                    break;
            }
        }
        
        // Tab operations
        if (ctrlKey && !shiftKey) {
            switch (key) {
                case 't':
                    event.preventDefault();
                    this.createNewTab();
                    break;
                case 'w':
                    event.preventDefault();
                    this.closeCurrentTab();
                    break;
            }
        }
        
        // Search navigation
        if (key === 'F3') {
            event.preventDefault();
            if (shiftKey) {
                this.findPrevious();
            } else {
                this.findNext();
            }
        }
    }
    
    /**
     * Create a new tab
     * @param {string} content - Initial content for the tab
     * @param {string} title - Tab title
     */
    createNewTab(content = '', title = 'Untitled') {
        const newTab = {
            id: this.generateId(),
            title: title,
            content: content,
            language: this.detectLanguage(title),
            modified: false,
            createdAt: new Date()
        };
        
        this.tabs.push(newTab);
        this.activeTabIndex = this.tabs.length - 1;
        this.updateTabDisplay();
        
        console.log(`Created new tab: ${title}`);
        return newTab;
    }
    
    /**
     * Open a file in a new tab
     * @param {string} filePath - Path to the file
     * @param {string} content - File content
     */
    openFile(filePath, content = '') {
        const fileName = this.extractFileName(filePath);
        const language = this.detectLanguage(filePath);
        
        const newTab = {
            id: this.generateId(),
            title: fileName,
            content: content,
            language: language,
            filePath: filePath,
            modified: false,
            openedAt: new Date()
        };
        
        this.tabs.push(newTab);
        this.activeTabIndex = this.tabs.length - 1;
        this.updateTabDisplay();
        
        console.log(`Opened file: ${fileName}`);
        return newTab;
    }
    
    /**
     * Save the current file
     */
    saveFile() {
        if (this.activeTabIndex >= 0 && this.activeTabIndex < this.tabs.length) {
            const activeTab = this.tabs[this.activeTabIndex];
            
            if (activeTab.filePath) {
                // Save to existing file
                this.writeFileToDisk(activeTab.filePath, activeTab.content);
                activeTab.modified = false;
                this.updateTabDisplay();
                console.log(`Saved file: ${activeTab.title}`);
            } else {
                // Save as new file
                this.saveFileAs();
            }
        }
    }
    
    /**
     * Save file with a new name
     */
    saveFileAs() {
        // This would typically open a save dialog
        console.log('Save As dialog would open here');
    }
    
    /**
     * Close the current tab
     */
    closeCurrentTab() {
        if (this.tabs.length > 1) {
            const closedTab = this.tabs.splice(this.activeTabIndex, 1)[0];
            
            if (this.activeTabIndex >= this.tabs.length) {
                this.activeTabIndex = this.tabs.length - 1;
            }
            
            this.updateTabDisplay();
            console.log(`Closed tab: ${closedTab.title}`);
        }
    }
    
    /**
     * Show the search panel
     */
    showSearchPanel() {
        this.searchPanelVisible = true;
        this.updateSearchPanelDisplay();
        console.log('Search panel shown');
    }
    
    /**
     * Show the replace panel
     */
    showReplacePanel() {
        this.searchPanelVisible = true;
        this.replaceMode = true;
        this.updateSearchPanelDisplay();
        console.log('Replace panel shown');
    }
    
    /**
     * Find next occurrence
     */
    findNext() {
        if (this.searchQuery && this.searchResults.length > 0) {
            this.currentSearchIndex = (this.currentSearchIndex + 1) % this.searchResults.length;
            this.highlightCurrentSearchResult();
        }
    }
    
    /**
     * Find previous occurrence
     */
    findPrevious() {
        if (this.searchQuery && this.searchResults.length > 0) {
            this.currentSearchIndex = this.currentSearchIndex === 0 
                ? this.searchResults.length - 1 
                : this.currentSearchIndex - 1;
            this.highlightCurrentSearchResult();
        }
    }
    
    /**
     * Apply the current theme
     */
    applyTheme() {
        document.body.className = `theme-${this.config.theme}`;
        console.log(`Applied theme: ${this.config.theme}`);
    }
    
    /**
     * Update the tab display
     */
    updateTabDisplay() {
        // This would update the UI
        console.log('Tab display updated');
    }
    
    /**
     * Update the search panel display
     */
    updateSearchPanelDisplay() {
        // This would update the search panel UI
        console.log('Search panel display updated');
    }
    
    /**
     * Highlight the current search result
     */
    highlightCurrentSearchResult() {
        // This would highlight the current search result in the editor
        console.log(`Highlighting search result ${this.currentSearchIndex + 1}/${this.searchResults.length}`);
    }
    
    /**
     * Write file to disk (placeholder)
     * @param {string} filePath - File path
     * @param {string} content - File content
     */
    writeFileToDisk(filePath, content) {
        // This would use Electron's file system API
        console.log(`Writing ${content.length} characters to ${filePath}`);
    }
    
    /**
     * Extract filename from path
     * @param {string} filePath - Full file path
     * @returns {string} Filename
     */
    extractFileName(filePath) {
        return filePath.split(/[/\\]/).pop() || 'Untitled';
    }
    
    /**
     * Detect programming language from file extension
     * @param {string} fileName - Filename or path
     * @returns {string} Language identifier
     */
    detectLanguage(fileName) {
        const extension = fileName.split('.').pop()?.toLowerCase();
        
        const languageMap = {
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'py': 'python',
            'cs': 'csharp',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'c': 'c',
            'cpp': 'cpp',
            'h': 'c',
            'hpp': 'cpp'
        };
        
        return languageMap[extension] || 'text';
    }
    
    /**
     * Generate a unique ID
     * @returns {string} Unique identifier
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    /**
     * Handle window focus
     */
    onWindowFocus() {
        console.log('Editor window focused');
    }
    
    /**
     * Handle window blur
     */
    onWindowBlur() {
        console.log('Editor window blurred');
    }
    
    /**
     * Get editor statistics
     * @returns {Object} Editor statistics
     */
    getStats() {
        return {
            totalTabs: this.tabs.length,
            activeTabIndex: this.activeTabIndex,
            modifiedTabs: this.tabs.filter(tab => tab.modified).length,
            totalContentLength: this.tabs.reduce((sum, tab) => sum + tab.content.length, 0)
        };
    }
}

// Create editor instance
const editor = new CodeEditor({
    theme: 'dark',
    features: ['syntax-highlighting', 'tabs', 'search', 'replace', 'auto-save']
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CodeEditor;
}

// Log editor stats
setInterval(() => {
    const stats = editor.getStats();
    console.log('Editor Stats:', stats);
}, 30000); // Log every 30 seconds