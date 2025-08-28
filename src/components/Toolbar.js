import React from 'react';
import './Toolbar.css';

const Toolbar = ({ onAction, alwaysOnTop, fullscreen }) => {
  const toolbarItems = [
    { id: 'new', icon: '✚', label: 'New File', action: 'new' },
    { id: 'open', icon: '📁', label: 'Open File', action: 'open' },
    { id: 'save', icon: '💾', label: 'Save', action: 'save' },
    { type: 'separator' },
    { id: 'find', icon: '🔍', label: 'Find', action: 'find' },
    { id: 'replace', icon: '🔄', label: 'Replace', action: 'replace' },
    { type: 'separator' },
    { id: 'pin', icon: '📌', label: 'Always on Top', action: 'pin', active: alwaysOnTop },
    { id: 'full', icon: '⛶', label: 'Fullscreen', action: 'full', active: fullscreen }
  ];
  
  const handleAction = (action) => {
    onAction(action);
  };
  
  return (
    <div className="toolbar">
      {toolbarItems.map((item, index) => (
        <div key={index} className="toolbar-item">
          {item.type === 'separator' ? (
            <div className="toolbar-separator" />
          ) : (
            <button
              className={`toolbar-button ${item.active ? 'active' : ''}`}
              onClick={() => handleAction(item.action)}
              title={item.label}
            >
              <span className="toolbar-icon">{item.icon}</span>
            </button>
          )}
        </div>
      ))}
    </div>
  );
};

export default Toolbar;