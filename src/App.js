import React, { useState, useEffect, useCallback, useRef } from 'react';
import MonacoEditor from 'react-monaco-editor';
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
    window.electronAPI.onMenuAction((event, action, ...args) => {
      handleMenuAction(action, ...args);
    });
    
    window.electronAPI.onSaveSession(() => {
      saveSession();
    });

    return () => {
      window.electronAPI.removeAllListeners('menu-action');
      window.electronAPI.removeAllListeners('save-session');
    };
  }, []);

  const loadSession = async () => {
    try {
      const session = await window.electronAPI.loadSession();
      if (session && session.length > 0) {
        setTabs(session);
        setActiveTab(session[0].id);
      } else {
        // Create default untitled tab
        createNewTab();
      }
    } catch (error) {
      console.error('Failed to load session:', error);
      createNewTab();
    }
  };

  const loadRecentFiles = async () => {
    try {
      const files = await window.electronAPI.getRecentFiles();
      setRecentFiles(files);
    } catch (error) {
      console.error('Failed to load recent files:', error);
    }
  };

  const saveSession = async () => {
    try {
      await window.electronAPI.saveSession(tabs);
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
        editorRef.current?.getAction('undo').run();
        break;
      case 'redo':
        editorRef.current?.getAction('redo').run();
        break;
      case 'cut':
        editorRef.current?.getAction('cut').run();
        break;
      case 'copy':
        editorRef.current?.getAction('copy').run();
        break;
      case 'paste':
        editorRef.current?.getAction('paste').run();
        break;
      case 'select-all':
        editorRef.current?.getAction('selectAll').run();
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
      const result = await window.electronAPI.readFile(filePath);
      if (result.success) {
        const newTab = createNewTab(filePath, result.content);
        await window.electronAPI.addRecentFile(filePath);
        setRecentFiles(prev => [filePath, ...prev.filter(f => f !== filePath)].slice(0, 10));
      } else {
        setStatusMessage(`Error opening file: ${result.error}`);
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
      return;
    }
    
    try {
      await window.electronAPI.writeFile(tab.filePath, tab.content);
      setTabs(prev => prev.map(t => 
        t.id === activeTab ? { ...t, modified: false } : t
      ));
      setStatusMessage(`Saved: ${tab.name}`);
    } catch (error) {
      setStatusMessage(`Error saving file: ${error.message}`);
    }
  };

  const saveFileAs = async (filePath) => {
    if (!activeTab) return;
    
    const tab = tabs.find(t => t.id === activeTab);
    try {
      await window.electronAPI.writeFile(filePath, tab.content);
      setTabs(prev => prev.map(t => 
        t.id === activeTab ? { ...t, filePath, name: filePath.split(/[/\\]/).pop(), modified: false } : t
      ));
      await window.electronAPI.addRecentFile(filePath);
      setStatusMessage(`Saved as: ${filePath.split(/[/\\]/).pop()}`);
    } catch (error) {
      setStatusMessage(`Error saving file: ${error.message}`);
    }
  };

  const handleSearch = (findText, replaceText = '', replaceAll = false) => {
    if (!editorRef.current) return;
    
    const model = editorRef.current.getModel();
    if (!model) return;
    
    const findMatches = model.findMatches(findText, false, false, true, null, false);
    
    if (replaceAll && replaceText !== '') {
      // Replace all matches
      const edits = findMatches.map(match => ({
        range: match.range,
        text: replaceText
      }));
      model.pushEditOperations([], edits, () => null);
      setStatusMessage(`Replaced ${findMatches.length} occurrences`);
    } else if (findMatches.length > 0) {
      // Highlight matches
      editorRef.current.setSelection(findMatches[0].range);
      setStatusMessage(`Found ${findMatches.length} matches`);
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
          <MonacoEditor
            ref={editorRef}
            width="100%"
            height="100%"
            language={currentTab.language}
            theme="vs-dark"
            value={currentTab.content}
            onChange={handleEditorChange}
            options={{
              selectOnLineNumbers: true,
              roundedSelection: false,
              readOnly: false,
              cursorStyle: 'line',
              automaticLayout: true,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              fontSize: 14,
              fontFamily: 'Consolas, "Courier New", monospace',
              lineNumbers: 'on',
              glyphMargin: true,
              folding: true,
              lineDecorationsWidth: 10,
              lineNumbersMinChars: 4,
              renderLineHighlight: 'all',
              bracketPairColorization: { enabled: true },
              guides: {
                bracketPairs: true,
                indentation: true
              }
            }}
          />
        )}
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <span className="status-message">{statusMessage}</span>
        {currentTab && (
          <span className="position-info">
            Line {editorRef.current?.getPosition()?.lineNumber || 1}, 
            Col {editorRef.current?.getPosition()?.column || 1}
          </span>
        )}
      </div>
    </div>
  );
}

export default App;