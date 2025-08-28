import React, { useState, useCallback } from 'react';
import './TabManager.css';
import CodeEditor from './CodeEditor';

const TabManager = ({ tabs, activeTabIndex, onTabChange, onTabClose, onTabContentChange, onTabDrop }) => {
  const [dragOver, setDragOver] = useState(false);
  
  const handleTabClick = (index) => {
    onTabChange(index);
  };
  
  const handleTabClose = (e, index) => {
    e.stopPropagation();
    onTabClose(index);
  };
  
  const handleTabCloseOthers = (e, index) => {
    e.stopPropagation();
    // This will be handled by the parent component
  };
  
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);
  
  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
  }, []);
  
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const filePath = files[0].path;
      onTabDrop(filePath);
    }
  }, [onTabDrop]);
  
  const handleContextMenu = (e, index) => {
    e.preventDefault();
    // Context menu could be implemented here
  };
  
  if (tabs.length === 0) {
    return (
      <div className="tab-manager empty">
        <div className="empty-state">
          <h3>Welcome to Nexus Editor</h3>
          <p>Create a new file or open an existing one to get started</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="tab-manager">
      <div className="tab-bar">
        {tabs.map((tab, index) => (
          <div
            key={tab.id}
            className={`tab ${index === activeTabIndex ? 'active' : ''} ${tab.modified ? 'modified' : ''}`}
            onClick={() => handleTabClick(index)}
            onContextMenu={(e) => handleContextMenu(e, index)}
          >
            <span className="tab-title">{tab.title}</span>
            {tab.modified && <span className="tab-modified-indicator">*</span>}
            <button
              className="tab-close"
              onClick={(e) => handleTabClose(e, index)}
              title="Close tab"
            >
              ×
            </button>
          </div>
        ))}
      </div>
      
      <div
        className={`tab-content ${dragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {tabs[activeTabIndex] && (
          <CodeEditor
            key={tabs[activeTabIndex].id}
            content={tabs[activeTabIndex].content}
            language={tabs[activeTabIndex].language}
            onChange={(content) => 
              onTabContentChange(activeTabIndex, content)
            }
            onCursorPositionChange={(position) => {
              // Update tab with cursor position for status bar
              const updatedTab = { ...tabs[activeTabIndex] };
              updatedTab.line = position.line;
              updatedTab.column = position.column;
              updatedTab.totalLines = content.split('\n').length;
              onTabContentChange(activeTabIndex, content);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default TabManager;