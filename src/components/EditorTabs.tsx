import React, { useState } from 'react'
import { Tab } from '../types'
import CodeEditor from './CodeEditor'
import './EditorTabs.css'

interface EditorTabsProps {
  tabs: Tab[]
  activeTabId: string | null
  onTabChange: (tabId: string) => void
  onTabClose: (tabId: string) => void
  onContentChange: (content: string) => void
  onNewTab: () => void
  onCloseOthers: () => void
  onReopenClosedTab: () => void
}

const EditorTabs: React.FC<EditorTabsProps> = ({
  tabs,
  activeTabId,
  onTabChange,
  onTabClose,
  onContentChange,
  onNewTab,
  onCloseOthers,
  onReopenClosedTab
}) => {
  const [contextMenu, setContextMenu] = useState<{
    visible: boolean
    x: number
    y: number
    tabId: string | null
  }>({
    visible: false,
    x: 0,
    y: 0,
    tabId: null
  })

  const handleTabClick = (tabId: string) => {
    onTabChange(tabId)
  }

  const handleTabClose = (e: React.MouseEvent, tabId: string) => {
    e.stopPropagation()
    onTabClose(tabId)
  }

  const handleContextMenu = (e: React.MouseEvent, tabId: string) => {
    e.preventDefault()
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      tabId
    })
  }

  const handleContextMenuAction = (action: string) => {
    if (contextMenu.tabId) {
      switch (action) {
        case 'close':
          onTabClose(contextMenu.tabId)
          break
        case 'closeOthers':
          onCloseOthers()
          break
        case 'reopen':
          onReopenClosedTab()
          break
      }
    }
    setContextMenu({ visible: false, x: 0, y: 0, tabId: null })
  }

  const activeTab = tabs.find(tab => tab.id === activeTabId)

  return (
    <div className="editor-tabs">
      <div className="tab-bar">
        {tabs.map(tab => (
          <div
            key={tab.id}
            className={`tab ${tab.id === activeTabId ? 'active' : ''} ${tab.isModified ? 'modified' : ''}`}
            onClick={() => handleTabClick(tab.id)}
            onContextMenu={(e) => handleContextMenu(e, tab.id)}
          >
            <span className="tab-title">{tab.title}</span>
            {tab.isModified && <span className="modified-indicator">*</span>}
            <button
              className="tab-close"
              onClick={(e) => handleTabClose(e, tab.id)}
              title="Close tab (Ctrl+W)"
            >
              ×
            </button>
          </div>
        ))}
        
        <button className="new-tab-button" onClick={onNewTab} title="New Tab (Ctrl+T)">
          +
        </button>
      </div>

      <div className="editor-content">
        {activeTab ? (
          <CodeEditor
            content={activeTab.content}
            language={activeTab.language}
            onChange={onContentChange}
          />
        ) : (
          <div className="no-tabs-message">
            <p>No tabs open</p>
            <button onClick={onNewTab}>Create New Tab</button>
          </div>
        )}
      </div>

      {contextMenu.visible && (
        <>
          <div 
            className="context-menu-overlay" 
            onClick={() => setContextMenu({ visible: false, x: 0, y: 0, tabId: null })}
          />
          <div 
            className="context-menu"
            style={{ left: contextMenu.x, top: contextMenu.y }}
          >
            <div className="context-menu-item" onClick={() => handleContextMenuAction('close')}>
              Close Tab
            </div>
            <div className="context-menu-item" onClick={() => handleContextMenuAction('closeOthers')}>
              Close Others
            </div>
            <div className="context-menu-item" onClick={() => handleContextMenuAction('reopen')}>
              Reopen Closed Tab
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default EditorTabs