import React, { useState, useEffect, useCallback, useRef } from 'react';
import './App.css';

function App() {
  const [tabs, setTabs] = useState([]);
  const [activeTab, setActiveTab] = useState(null);
  const [searchPanel, setSearchPanel] = useState({ visible: false, findText: '', replaceText: '' });
  const [alwaysOnTop, setAlwaysOnTop] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Ready');
  const [recentFiles, setRecentFiles] = useState([]);
  const [closedTabs, setClosedTabs] = useState([]);
  
  const editorRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  // Load session on startup
  useEffect(() => {
    loadSession();
    loadRecentFiles();
    
    // Set up menu action listeners
    if (window.electronAPI) {
      window.electronAPI.onMenuAction((event, action, ...args) => {
        handleMenuAction(action, ...args);
      });
      
      window.electronAPI.onSaveSession(() => {
        saveSession();
      });
    } else {
      console.log('Electron API not available - running in browser mode');
    }

    return () => {
      if (window.electronAPI) {
        window.electronAPI.removeAllListeners('menu-action');
        window.electronAPI.removeAllListeners('save-session');
      }
    };
  }, []);

  const loadSession = async () => {
    try {
      if (window.electronAPI) {
        const session = await window.electronAPI.loadSession();
        if (session && session.length > 0) {
          setTabs(session);
          setActiveTab(session[0].id);
        } else {
          createNewTab();
        }
      } else {
        createNewTab();
      }
    } catch (error) {
      console.error('Failed to load session:', error);
      createNewTab();
    }
  };

  const loadRecentFiles = async () => {
    try {
      if (window.electronAPI) {
        const files = await window.electronAPI.getRecentFiles();
        setRecentFiles(files);
      }
    } catch (error) {
      console.error('Failed to load recent files:', error);
    }
  };

  const saveSession = async () => {
    try {
      if (window.electronAPI) {
        await window.electronAPI.saveSession(tabs);
      }
    } catch (error) {
      console.error('Failed to save session:', error);
    }
  };

  const createNewTab = (filePath = null, content = '') => {
    const newTab = {
      id: Date.now(),
      name: filePath ? filePath.split(/[/\\]/).pop() : 'Untitled',
      filePath: filePath,
      content: content,
      modified: false,
      language: getLanguageFromPath(filePath)
    };
    
    setTabs(prev => [...prev, newTab]);
    setActiveTab(newTab.id);
    return newTab;
  };

  const getLanguageFromPath = (filePath) => {
    if (!filePath) return 'plaintext';
    const ext = filePath.split('.').pop().toLowerCase();
    const languageMap = {
      'cs': 'csharp',
      'py': 'python',
      'js': 'javascript',
      'html': 'html',
      'htm': 'html',
      'css': 'css',
      'json': 'json',
      'c': 'c',
      'cpp': 'cpp',
      'h': 'c',
      'hpp': 'cpp',
      'txt': 'plaintext'
    };
    return languageMap[ext] || 'plaintext';
  };

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
  };

  const handleTabClose = (tabId) => {
    const tab = tabs.find(t => t.id === tabId);
    if (tab.modified) {
      // TODO: Show save prompt
      console.log('Tab modified, should show save prompt');
    }
    
    // Store in closed tabs for reopening
    setClosedTabs(prev => [tab, ...prev.slice(0, 9)]);
    
    setTabs(prev => prev.filter(t => t.id !== tabId));
    
    if (activeTab === tabId) {
      const remainingTabs = tabs.filter(t => t.id !== tabId);
      if (remainingTabs.length > 0) {
        setActiveTab(remainingTabs[remainingTabs.length - 1].id);
      } else {
        createNewTab();
      }
    }
  };

  const handleEditorChange = (value, event) => {
    if (activeTab) {
      setTabs(prev => prev.map(tab => 
        tab.id === activeTab 
          ? { ...tab, content: value, modified: true }
          : tab
      ));
      
      // Debounced autosave
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
      searchTimeoutRef.current = setTimeout(() => {
        saveSession();
      }, 500);
    }
  };

  const handleMenuAction = (action, ...args) => {
    switch (action) {
      case 'new-file':
        createNewTab();
        break;
      case 'open-file':
        openFile(args[0]);
        break;
      case 'save-file':
        saveCurrentFile();
        break;
      case 'save-as':
        saveFileAs(args[0]);
        break;
      case 'undo':
        // TODO: Implement undo for textarea
        break;
      case 'redo':
        // TODO: Implement redo for textarea
        break;
      case 'cut':
        document.execCommand('cut');
        break;
      case 'copy':
        document.execCommand('copy');
        break;
      case 'paste':
        document.execCommand('paste');
        break;
      case 'select-all':
        if (editorRef.current) {
          editorRef.current.select();
        }
        break;
      case 'find':
        setSearchPanel(prev => ({ ...prev, visible: true }));
        break;
      case 'replace':
        setSearchPanel(prev => ({ ...prev, visible: true, replaceMode: true }));
        break;
      case 'new-tab':
        createNewTab();
        break;
      case 'close-tab':
        if (activeTab) handleTabClose(activeTab);
        break;
      case 'close-others':
        const currentTab = tabs.find(t => t.id === activeTab);
        setTabs([currentTab]);
        break;
      case 'reopen-closed-tab':
        if (closedTabs.length > 0) {
          const [reopenedTab, ...remainingClosed] = closedTabs;
          setClosedTabs(remainingClosed);
          setTabs(prev => [...prev, { ...reopenedTab, id: Date.now() }]);
          setActiveTab(reopenedTab.id);
        }
        break;
      case 'go-to-line':
        // TODO: Implement go to line dialog
        break;
      case 'always-on-top':
        setAlwaysOnTop(args[0]);
        break;
      case 'fullscreen':
        setFullscreen(args[0]);
        break;
    }
  };

  const openFile = async (filePath) => {
    try {
      if (window.electronAPI) {
        const result = await window.electronAPI.readFile(filePath);
        if (result.success) {
          const newTab = createNewTab(filePath, result.content);
          await window.electronAPI.addRecentFile(filePath);
          setRecentFiles(prev => [filePath, ...prev.filter(f => f !== filePath)].slice(0, 10));
        } else {
          setStatusMessage(`Error opening file: ${result.error}`);
        }
      } else {
        setStatusMessage('File operations not available in browser mode');
      }
    } catch (error) {
      setStatusMessage(`Error opening file: ${error.message}`);
    }
  };

  const saveCurrentFile = async () => {
    if (!activeTab) return;
    
    const tab = tabs.find(t => t.id === activeTab);
    if (!tab.filePath) {
      // TODO: Show save as dialog
      setStatusMessage('Save As not implemented in browser mode');
      return;
    }
    
    try {
      if (window.electronAPI) {
        await window.electronAPI.writeFile(tab.filePath, tab.content);
        setTabs(prev => prev.map(t => 
          t.id === activeTab ? { ...t, modified: false } : t
        ));
        setStatusMessage(`Saved: ${tab.name}`);
      } else {
        setStatusMessage('File operations not available in browser mode');
      }
    } catch (error) {
      setStatusMessage(`Error saving file: ${error.message}`);
    }
  };

  const saveFileAs = async (filePath) => {
    if (!activeTab) return;
    
    const tab = tabs.find(t => t.id === activeTab);
    try {
      if (window.electronAPI) {
        await window.electronAPI.writeFile(filePath, tab.content);
        setTabs(prev => prev.map(t => 
          t.id === activeTab ? { ...t, filePath, name: filePath.split(/[/\\]/).pop(), modified: false } : t
        ));
        await window.electronAPI.addRecentFile(filePath);
        setStatusMessage(`Saved as: ${filePath.split(/[/\\]/).pop()}`);
      } else {
        setStatusMessage('File operations not available in browser mode');
      }
    } catch (error) {
      setStatusMessage(`Error saving file: ${error.message}`);
    }
  };

  const handleSearch = (findText, replaceText = '', replaceAll = false) => {
    if (!editorRef.current) return;
    
    const text = editorRef.current.value;
    const findIndex = text.indexOf(findText);
    
    if (findIndex !== -1) {
      if (replaceAll && replaceText !== '') {
        const newText = text.replace(new RegExp(findText, 'g'), replaceText);
        handleEditorChange(newText);
        setStatusMessage(`Replaced all occurrences of "${findText}"`);
      } else {
        editorRef.current.setSelectionRange(findIndex, findIndex + findText.length);
        setStatusMessage(`Found "${findText}"`);
      }
    } else {
      setStatusMessage('No matches found');
    }
  };

  const currentTab = tabs.find(t => t.id === activeTab);

  return (
    <div className="App">
      {/* Menu Bar - Handled by Electron */}
      
      {/* Toolbar */}
      <div className="toolbar">
        <button onClick={() => createNewTab()} title="New (Ctrl+N)">
          📄 New
        </button>
        <button onClick={() => handleMenuAction('open-file')} title="Open (Ctrl+O)">
          📂 Open
        </button>
        <button onClick={saveCurrentFile} title="Save (Ctrl+S)">
          💾 Save
        </button>
        <button onClick={() => setSearchPanel(prev => ({ ...prev, visible: true }))} title="Find (Ctrl+F)">
          🔍 Find
        </button>
        <button onClick={() => setSearchPanel(prev => ({ ...prev, visible: true, replaceMode: true }))} title="Replace (Ctrl+H)">
          🔄 Replace
        </button>
        <button 
          onClick={() => setAlwaysOnTop(!alwaysOnTop)} 
          className={alwaysOnTop ? 'active' : ''}
          title="Always on Top"
        >
          📌 Pin
        </button>
        <button 
          onClick={() => setFullscreen(!fullscreen)} 
          className={fullscreen ? 'active' : ''}
          title="Fullscreen (F11)"
        >
          ⛶ Full
        </button>
      </div>

      {/* Search & Replace Panel */}
      {searchPanel.visible && (
        <div className="search-panel">
          <input
            type="text"
            placeholder="Find..."
            value={searchPanel.findText}
            onChange={(e) => setSearchPanel(prev => ({ ...prev, findText: e.target.value }))}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchPanel.findText)}
          />
          {searchPanel.replaceMode && (
            <input
              type="text"
              placeholder="Replace with..."
              value={searchPanel.replaceText}
              onChange={(e) => setSearchPanel(prev => ({ ...prev, replaceText: e.target.value }))}
            />
          )}
          <button onClick={() => handleSearch(searchPanel.findText)}>Find</button>
          {searchPanel.replaceMode && (
            <>
              <button onClick={() => handleSearch(searchPanel.findText, searchPanel.replaceText)}>Replace</button>
              <button onClick={() => handleSearch(searchPanel.findText, searchPanel.replaceText, true)}>Replace All</button>
            </>
          )}
          <button onClick={() => setSearchPanel(prev => ({ ...prev, visible: false }))}>✕</button>
        </div>
      )}

      {/* Tab Bar */}
      <div className="tab-bar">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`tab ${tab.id === activeTab ? 'active' : ''} ${tab.modified ? 'modified' : ''}`}
            onClick={() => handleTabChange(tab.id)}
          >
            <span className="tab-name">{tab.name}</span>
            {tab.modified && <span className="modified-indicator">*</span>}
            <button
              className="tab-close"
              onClick={(e) => {
                e.stopPropagation();
                handleTabClose(tab.id);
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* Editor */}
      <div className="editor-container">
        {currentTab && (
          <textarea
            ref={editorRef}
            className="code-editor"
            value={currentTab.content}
            onChange={(e) => handleEditorChange(e.target.value)}
            placeholder="Start coding here..."
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
          />
        )}
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <span className="status-message">{statusMessage}</span>
        {currentTab && (
          <span className="position-info">
            Line {editorRef.current ? (editorRef.current.value.substring(0, editorRef.current.selectionStart).split('\n').length) : 1}, 
            Col {editorRef.current ? (editorRef.current.selectionStart - editorRef.current.value.substring(0, editorRef.current.selectionStart).lastIndexOf('\n') - 1) : 1}
          </span>
        )}
      </div>
    </div>
  );
}

export default App;