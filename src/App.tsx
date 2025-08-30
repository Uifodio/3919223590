import React, { useState, useEffect } from 'react'
import MenuBar from './components/MenuBar'
import Toolbar from './components/Toolbar'
import EditorTabs from './components/EditorTabs'
import SearchReplacePanel from './components/SearchReplacePanel'
import StatusBar from './components/StatusBar'
import { useEditorStore } from './hooks/useEditorStore'
import { useFileManager } from './hooks/useFileManager'
import { useSearchReplace } from './hooks/useSearchReplace'
import './App.css'

function App() {
  const {
    tabs,
    activeTabId,
    addTab,
    closeTab,
    updateTabContent,
    setActiveTab,
    reopenClosedTab
  } = useEditorStore()

  const {
    openFile,
    saveFile,
    saveFileAs,
    recentFiles
  } = useFileManager()

  const {
    isSearchVisible,
    searchQuery,
    replaceQuery,
    showSearch,
    hideSearch,
    findNext,
    findPrevious,
    replace,
    replaceAll
  } = useSearchReplace()

  const [isAlwaysOnTop, setIsAlwaysOnTop] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  const handleNewTab = () => {
    addTab('Untitled', '')
  }

  const handleCloseTab = (tabId: string) => {
    closeTab(tabId)
  }

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId)
  }

  const handleContentChange = (content: string) => {
    if (activeTabId) {
      updateTabContent(activeTabId, content)
    }
  }

  const handleCloseOthers = () => {
    if (activeTabId) {
      tabs.forEach(tab => {
        if (tab.id !== activeTabId) {
          closeTab(tab.id)
        }
      })
    }
  }

  const handleReopenClosedTab = () => {
    reopenClosedTab()
  }

  const handleAlwaysOnTop = () => {
    const newValue = !isAlwaysOnTop
    setIsAlwaysOnTop(newValue)
    if (window.electronAPI) {
      window.electronAPI.setAlwaysOnTop(newValue)
    }
  }

  const handleFullscreen = () => {
    const newValue = !isFullscreen
    setIsFullscreen(newValue)
    if (window.electronAPI) {
      window.electronAPI.setFullscreen(newValue)
    }
  }

  useEffect(() => {
    if (tabs.length === 0) {
      addTab('Untitled', '')
    }
  }, [])

  return (
    <div className="app">
      <MenuBar
        onNew={handleNewTab}
        onOpen={openFile}
        onSave={saveFile}
        onSaveAs={saveFileAs}
        onFind={showSearch}
        onReplace={showSearch}
        onAlwaysOnTop={handleAlwaysOnTop}
        onFullscreen={handleFullscreen}
        isAlwaysOnTop={isAlwaysOnTop}
        isFullscreen={isFullscreen}
        recentFiles={recentFiles}
      />
      
      <Toolbar
        onNew={handleNewTab}
        onOpen={openFile}
        onSave={saveFile}
        onFind={showSearch}
        onReplace={showSearch}
        onPin={handleAlwaysOnTop}
        onFull={handleFullscreen}
        isPinned={isAlwaysOnTop}
        isFullscreen={isFullscreen}
      />

      <div className="main-content">
        <EditorTabs
          tabs={tabs}
          activeTabId={activeTabId}
          onTabChange={handleTabChange}
          onTabClose={handleCloseTab}
          onContentChange={handleContentChange}
          onNewTab={handleNewTab}
          onCloseOthers={handleCloseOthers}
          onReopenClosedTab={handleReopenClosedTab}
        />
      </div>

      {isSearchVisible && (
        <SearchReplacePanel
          searchQuery={searchQuery}
          replaceQuery={replaceQuery}
          onSearchChange={(query) => {}}
          onReplaceChange={(query) => {}}
          onFindNext={findNext}
          onFindPrevious={findPrevious}
          onReplace={replace}
          onReplaceAll={replaceAll}
          onClose={hideSearch}
        />
      )}

      <StatusBar />
    </div>
  )
}

export default App