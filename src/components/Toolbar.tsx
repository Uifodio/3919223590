import React from 'react'
import './Toolbar.css'

interface ToolbarProps {
  onNew: () => void
  onOpen: () => void
  onSave: () => void
  onFind: () => void
  onReplace: () => void
  onPin: () => void
  onFull: () => void
  isPinned: boolean
  isFullscreen: boolean
}

const Toolbar: React.FC<ToolbarProps> = ({
  onNew,
  onOpen,
  onSave,
  onFind,
  onReplace,
  onPin,
  onFull,
  isPinned,
  isFullscreen
}) => {
  return (
    <div className="toolbar">
      <div className="toolbar-group">
        <button className="toolbar-button" onClick={onNew} title="New (Ctrl+N)">
          <span className="icon">📄</span>
          <span className="text">New</span>
        </button>
        
        <button className="toolbar-button" onClick={onOpen} title="Open (Ctrl+O)">
          <span className="icon">📂</span>
          <span className="text">Open</span>
        </button>
        
        <button className="toolbar-button" onClick={onSave} title="Save (Ctrl+S)">
          <span className="icon">💾</span>
          <span className="text">Save</span>
        </button>
      </div>

      <div className="toolbar-separator"></div>

      <div className="toolbar-group">
        <button className="toolbar-button" onClick={onFind} title="Find (Ctrl+F)">
          <span className="icon">🔍</span>
          <span className="text">Find</span>
        </button>
        
        <button className="toolbar-button" onClick={onReplace} title="Replace (Ctrl+H)">
          <span className="icon">🔄</span>
          <span className="text">Replace</span>
        </button>
      </div>

      <div className="toolbar-separator"></div>

      <div className="toolbar-group">
        <button 
          className={`toolbar-button ${isPinned ? 'active' : ''}`} 
          onClick={onPin} 
          title="Always on Top (Ctrl+W)"
        >
          <span className="icon">📌</span>
          <span className="text">Pin</span>
        </button>
        
        <button 
          className={`toolbar-button ${isFullscreen ? 'active' : ''}`} 
          onClick={onFull} 
          title="Fullscreen (Ctrl+F)"
        >
          <span className="icon">⛶</span>
          <span className="text">Full</span>
        </button>
      </div>
    </div>
  )
}

export default Toolbar