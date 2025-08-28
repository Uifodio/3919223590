import React, { useState, useEffect, useCallback, useRef } from 'react';
import './styles/App.css';
import Toolbar from './components/Toolbar';
import TabManager from './components/TabManager';
import StatusBar from './components/StatusBar';
import SearchPanel from './components/SearchPanel';
import { useFileManager } from './hooks/useFileManager';
import { useSessionManager } from './hooks/useSessionManager';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

function App() {
  const { tabs, activeTabIndex, createNewTab, openFile, saveFile, saveFileAs, closeTab, closeOtherTabs, reopenClosedTab, updateTabContent, setActiveTab } = useFileManager();
  const [searchPanelVisible, setSearchPanelVisible] = useState(false);
  const [searchMode, setSearchMode] = useState('find');
  const [alwaysOnTop, setAlwaysOnTop] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);

  const editorApiRef = useRef(null);

  const { saveSession, loadSession } = useSessionManager();

  // Load persisted settings from main
  useEffect(() => {
    (async () => {
      if (window.electronAPI?.getSettings) {
        const s = await window.electronAPI.getSettings();
        setAlwaysOnTop(!!s.alwaysOnTop);
        setFullscreen(!!s.fullscreen);
      }
    })();
  }, []);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onNewFile: createNewTab,
    onOpenFile: openFile,
    onSaveFile: () => saveFile(activeTabIndex),
    onSaveAs: () => saveFileAs(activeTabIndex),
    onNewTab: createNewTab,
    onCloseTab: () => closeTab(activeTabIndex),
    onReopenTab: reopenClosedTab,
    onFind: () => setSearchPanelVisible(true),
    onReplace: () => { setSearchMode('replace'); setSearchPanelVisible(true); },
    onGoToLine: () => handleGoToLine(),
    onExit: () => window.close()
  });

  // Menu event handlers
  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.onMenuNewFile(createNewTab);
      window.electronAPI.onMenuOpenFile(openFile);
      window.electronAPI.onMenuSaveFile(() => saveFile(activeTabIndex));
      window.electronAPI.onMenuSaveAs(() => saveFileAs(activeTabIndex));
      window.electronAPI.onMenuNewTab(createNewTab);
      window.electronAPI.onMenuCloseTab(() => closeTab(activeTabIndex));
      window.electronAPI.onMenuCloseOthers(() => closeOtherTabs(activeTabIndex));
      window.electronAPI.onMenuReopenTab(reopenClosedTab);
      window.electronAPI.onMenuFind(() => setSearchPanelVisible(true));
      window.electronAPI.onMenuReplace(() => { setSearchMode('replace'); setSearchPanelVisible(true); });
      window.electronAPI.onMenuGoToLine(() => handleGoToLine());
      window.electronAPI.onAlwaysOnTopChanged((val) => setAlwaysOnTop(!!val));
      window.electronAPI.onFullscreenChanged((val) => setFullscreen(!!val));
    }
    return () => {
      if (window.electronAPI) {
        window.electronAPI.removeAllListeners('menu-new-file');
        window.electronAPI.removeAllListeners('menu-open-file');
        window.electronAPI.removeAllListeners('menu-save-file');
        window.electronAPI.removeAllListeners('menu-save-as');
        window.electronAPI.removeAllListeners('menu-new-tab');
        window.electronAPI.removeAllListeners('menu-close-tab');
        window.electronAPI.removeAllListeners('menu-close-others');
        window.electronAPI.removeAllListeners('menu-reopen-tab');
        window.electronAPI.removeAllListeners('menu-find');
        window.electronAPI.removeAllListeners('menu-replace');
        window.electronAPI.removeAllListeners('menu-go-to-line');
        window.electronAPI.removeAllListeners('view-always-on-top-changed');
        window.electronAPI.removeAllListeners('view-fullscreen-changed');
      }
    };
  }, [createNewTab, openFile, saveFile, saveFileAs, closeTab, closeOtherTabs, reopenClosedTab, activeTabIndex]);

  // Auto-save session
  useEffect(() => {
    const interval = setInterval(() => {
      if (tabs.length > 0) {
        saveSession(tabs, activeTabIndex);
      }
    }, 500);
    return () => clearInterval(interval);
  }, [tabs, activeTabIndex, saveSession]);

  // Load session on startup
  useEffect(() => {
    const savedSession = loadSession();
    if (savedSession && savedSession.tabs && savedSession.tabs.length > 0) {
      savedSession.tabs.forEach(tab => {
        if (tab.filePath) {
          openFile(tab.filePath);
        } else {
          createNewTab(tab.content || '');
        }
      });
      setActiveTab(savedSession.activeTabIndex || 0);
    } else {
      createNewTab('');
    }
  }, []);

  const handleToolbarAction = useCallback((action) => {
    switch (action) {
      case 'new':
        createNewTab();
        break;
      case 'open':
        openFile();
        break;
      case 'save':
        saveFile(activeTabIndex);
        break;
      case 'find':
        setSearchMode('find');
        setSearchPanelVisible(true);
        break;
      case 'replace':
        setSearchMode('replace');
        setSearchPanelVisible(true);
        break;
      case 'pin': {
        const next = !alwaysOnTop;
        setAlwaysOnTop(next);
        window.electronAPI?.setAlwaysOnTop(next);
        window.electronAPI?.setSettings({ alwaysOnTop: next });
        break;
      }
      case 'full': {
        const next = !fullscreen;
        setFullscreen(next);
        window.electronAPI?.setFullscreen(next);
        window.electronAPI?.setSettings({ fullscreen: next });
        break;
      }
      default:
        break;
    }
  }, [createNewTab, openFile, saveFile, activeTabIndex, alwaysOnTop, fullscreen]);

  const handleSearchPanelClose = useCallback(() => {
    setSearchPanelVisible(false);
  }, []);

  const handleTabDrop = useCallback((filePath) => {
    openFile(filePath);
  }, [openFile]);

  const handleGoToLine = useCallback(() => {
    const input = window.prompt('Go to line:');
    if (!input) return;
    const line = Math.max(1, parseInt(input, 10) || 1);
    if (editorApiRef.current && editorApiRef.current.goToLine) {
      editorApiRef.current.goToLine(line, 1);
    }
  }, []);

  return (
    <div className="app">
      <Toolbar onAction={handleToolbarAction} alwaysOnTop={alwaysOnTop} fullscreen={fullscreen} />
      <div className="main-content">
        <TabManager
          tabs={tabs}
          activeTabIndex={activeTabIndex}
          onTabChange={setActiveTab}
          onTabClose={closeTab}
          onTabContentChange={updateTabContent}
          onTabDrop={handleTabDrop}
          editorApiRef={editorApiRef}
        />
        {searchPanelVisible && (
          <SearchPanel
            mode={searchMode}
            onClose={handleSearchPanelClose}
            onFind={() => {}}
            onReplace={() => {}}
            content={tabs[activeTabIndex]?.content || ''}
            onNavigateToLine={(line, column) => {
              if (editorApiRef.current?.goToLine) editorApiRef.current.goToLine(line, column || 1);
            }}
          />
        )}
      </div>
      <StatusBar
        line={tabs[activeTabIndex]?.line || 1}
        column={tabs[activeTabIndex]?.column || 1}
        totalLines={tabs[activeTabIndex]?.totalLines || 1}
      />
    </div>
  );
}

export default App;