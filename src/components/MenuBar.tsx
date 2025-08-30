import React, { useState } from 'react'
import { RecentFile } from '../types'
import './MenuBar.css'

interface MenuBarProps {
  onNew: () => void
  onOpen: () => void
  onSave: () => void
  onSaveAs: () => void
  onFind: () => void
  onReplace: () => void
  onAlwaysOnTop: () => void
  onFullscreen: () => void
  isAlwaysOnTop: boolean
  isFullscreen: boolean
  recentFiles: RecentFile[]
}

const MenuBar: React.FC<MenuBarProps> = ({
  onNew,
  onOpen,
  onSave,
  onSaveAs,
  onFind,
  onReplace,
  onAlwaysOnTop,
  onFullscreen,
  isAlwaysOnTop,
  isFullscreen,
  recentFiles
}) => {
  const [activeMenu, setActiveMenu] = useState<string | null>(null)

  const handleMenuClick = (menuName: string) => {
    setActiveMenu(activeMenu === menuName ? null : menuName)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.ctrlKey) {
      switch (e.key.toLowerCase()) {
        case 'n':
          e.preventDefault()
          onNew()
          break
        case 'o':
          e.preventDefault()
          onOpen()
          break
        case 's':
          e.preventDefault()
          if (e.shiftKey) {
            onSaveAs()
          } else {
            onSave()
          }
          break
        case 'f':
          e.preventDefault()
          onFind()
          break
        case 'h':
          e.preventDefault()
          onReplace()
          break
        case 'q':
          e.preventDefault()
          window.close()
          break
        case 'w':
          e.preventDefault()
          onAlwaysOnTop()
          break
        case 't':
          e.preventDefault()
          onNew()
          break
        case 'g':
          e.preventDefault()
          // Go to line functionality
          break
      }
    }
  }

  return (
    <div className="menu-bar" onKeyDown={handleKeyDown} tabIndex={0}>
      <div className="menu-item" onClick={() => handleMenuClick('file')}>
        File
        {activeMenu === 'file' && (
          <div className="dropdown-menu">
            <div className="menu-option" onClick={onNew}>
              New <span className="shortcut">Ctrl+N</span>
            </div>
            <div className="menu-option" onClick={onOpen}>
              Open <span className="shortcut">Ctrl+O</span>
            </div>
            <div className="menu-option" onClick={onSave}>
              Save <span className="shortcut">Ctrl+S</span>
            </div>
            <div className="menu-option" onClick={onSaveAs}>
              Save As <span className="shortcut">Ctrl+Shift+S</span>
            </div>
            <div className="menu-separator"></div>
            {recentFiles.length > 0 && (
              <div className="menu-submenu">
                Open Recent
                <div className="submenu">
                  {recentFiles.slice(0, 10).map((file, index) => (
                    <div key={index} className="menu-option">
                      {file.name}
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="menu-separator"></div>
            <div className="menu-option" onClick={() => window.close()}>
              Exit <span className="shortcut">Ctrl+Q</span>
            </div>
          </div>
        )}
      </div>

      <div className="menu-item" onClick={() => handleMenuClick('edit')}>
        Edit
        {activeMenu === 'edit' && (
          <div className="dropdown-menu">
            <div className="menu-option">
              Undo <span className="shortcut">Ctrl+Z</span>
            </div>
            <div className="menu-option">
              Redo <span className="shortcut">Ctrl+Y</span>
            </div>
            <div className="menu-separator"></div>
            <div className="menu-option">
              Cut <span className="shortcut">Ctrl+X</span>
            </div>
            <div className="menu-option">
              Copy <span className="shortcut">Ctrl+C</span>
            </div>
            <div className="menu-option">
              Paste <span className="shortcut">Ctrl+V</span>
            </div>
            <div className="menu-separator"></div>
            <div className="menu-option">
              Select All <span className="shortcut">Ctrl+A</span>
            </div>
            <div className="menu-separator"></div>
            <div className="menu-option" onClick={onFind}>
              Find <span className="shortcut">Ctrl+F</span>
            </div>
            <div className="menu-option" onClick={onReplace}>
              Replace <span className="shortcut">Ctrl+H</span>
            </div>
          </div>
        )}
      </div>

      <div className="menu-item" onClick={() => handleMenuClick('view')}>
        View
        {activeMenu === 'view' && (
          <div className="dropdown-menu">
            <div className="menu-option" onClick={onAlwaysOnTop}>
              Always on Top <span className="shortcut">Ctrl+W</span>
              {isAlwaysOnTop && <span className="checkmark">✓</span>}
            </div>
            <div className="menu-option" onClick={onFullscreen}>
              Fullscreen <span className="shortcut">Ctrl+F</span>
              {isFullscreen && <span className="checkmark">✓</span>}
            </div>
          </div>
        )}
      </div>

      <div className="menu-item" onClick={() => handleMenuClick('window')}>
        Window
        {activeMenu === 'window' && (
          <div className="dropdown-menu">
            <div className="menu-option" onClick={onNew}>
              New Tab <span className="shortcut">Ctrl+T</span>
            </div>
            <div className="menu-option">
              Close Tab <span className="shortcut">Ctrl+W</span>
            </div>
            <div className="menu-option">
              Close Others
            </div>
            <div className="menu-option">
              Reopen Closed Tab <span className="shortcut">Ctrl+Shift+T</span>
            </div>
          </div>
        )}
      </div>

      <div className="menu-item" onClick={() => handleMenuClick('navigate')}>
        Navigate
        {activeMenu === 'navigate' && (
          <div className="dropdown-menu">
            <div className="menu-option">
              Go to Line <span className="shortcut">Ctrl+G</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MenuBar