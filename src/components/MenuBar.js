import React, { useState } from 'react';
import './MenuBar.css';

const MenuBar = () => {
  const [activeMenu, setActiveMenu] = useState(null);
  
  const menuItems = [
    {
      label: 'File',
      items: [
        { label: 'New', shortcut: 'Ctrl+N', action: 'new' },
        { label: 'Open', shortcut: 'Ctrl+O', action: 'open' },
        { label: 'Save', shortcut: 'Ctrl+S', action: 'save' },
        { label: 'Save As', shortcut: 'Ctrl+Shift+S', action: 'saveAs' },
        { type: 'separator' },
        { label: 'Open Recent', action: 'recent', submenu: true },
        { type: 'separator' },
        { label: 'Exit', shortcut: 'Ctrl+Q', action: 'exit' }
      ]
    },
    {
      label: 'Edit',
      items: [
        { label: 'Undo', shortcut: 'Ctrl+Z', action: 'undo' },
        { label: 'Redo', shortcut: 'Ctrl+Y', action: 'redo' },
        { type: 'separator' },
        { label: 'Cut', shortcut: 'Ctrl+X', action: 'cut' },
        { label: 'Copy', shortcut: 'Ctrl+C', action: 'copy' },
        { label: 'Paste', shortcut: 'Ctrl+V', action: 'paste' },
        { type: 'separator' },
        { label: 'Select All', shortcut: 'Ctrl+A', action: 'selectAll' },
        { type: 'separator' },
        { label: 'Find', shortcut: 'Ctrl+F', action: 'find' },
        { label: 'Replace', shortcut: 'Ctrl+H', action: 'replace' }
      ]
    },
    {
      label: 'View',
      items: [
        { label: 'Always on Top', action: 'alwaysOnTop', type: 'checkbox' },
        { label: 'Fullscreen', shortcut: 'F11', action: 'fullscreen' }
      ]
    },
    {
      label: 'Window',
      items: [
        { label: 'New Tab', shortcut: 'Ctrl+T', action: 'newTab' },
        { label: 'Close Tab', shortcut: 'Ctrl+W', action: 'closeTab' },
        { label: 'Close Others', action: 'closeOthers' },
        { label: 'Reopen Closed Tab', shortcut: 'Ctrl+Shift+T', action: 'reopenTab' }
      ]
    },
    {
      label: 'Navigate',
      items: [
        { label: 'Go to Line', shortcut: 'Ctrl+G', action: 'goToLine' }
      ]
    }
  ];
  
  const handleMenuClick = (menuLabel) => {
    setActiveMenu(activeMenu === menuLabel ? null : menuLabel);
  };
  
  const handleMenuItemClick = (action) => {
    // Menu actions are handled by the main App component through menu events
    setActiveMenu(null);
  };
  
  const handleClickOutside = () => {
    setActiveMenu(null);
  };
  
  return (
    <div className="menu-bar" onClick={handleClickOutside}>
      {menuItems.map((menu) => (
        <div key={menu.label} className="menu-item">
          <button
            className={`menu-button ${activeMenu === menu.label ? 'active' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              handleMenuClick(menu.label);
            }}
          >
            {menu.label}
          </button>
          
          {activeMenu === menu.label && (
            <div className="menu-dropdown" onClick={(e) => e.stopPropagation()}>
              {menu.items.map((item, index) => (
                <div key={index}>
                  {item.type === 'separator' ? (
                    <div className="menu-separator" />
                  ) : (
                    <button
                      className={`menu-option ${item.type === 'checkbox' ? 'checkbox' : ''}`}
                      onClick={() => handleMenuItemClick(item.action)}
                    >
                      <span className="menu-option-label">{item.label}</span>
                      {item.shortcut && (
                        <span className="menu-option-shortcut">{item.shortcut}</span>
                      )}
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default MenuBar;