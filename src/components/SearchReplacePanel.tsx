import React, { useState, useEffect } from 'react'
import './SearchReplacePanel.css'

interface SearchReplacePanelProps {
  searchQuery: string
  replaceQuery: string
  onSearchChange: (query: string) => void
  onReplaceChange: (query: string) => void
  onFindNext: () => void
  onFindPrevious: () => void
  onReplace: () => void
  onReplaceAll: () => void
  onClose: () => void
}

const SearchReplacePanel: React.FC<SearchReplacePanelProps> = ({
  searchQuery,
  replaceQuery,
  onSearchChange,
  onReplaceChange,
  onFindNext,
  onFindPrevious,
  onReplace,
  onReplaceAll,
  onClose
}) => {
  const [localSearchQuery, setLocalSearchQuery] = useState(searchQuery)
  const [localReplaceQuery, setLocalReplaceQuery] = useState(replaceQuery)

  useEffect(() => {
    setLocalSearchQuery(searchQuery)
    setLocalReplaceQuery(replaceQuery)
  }, [searchQuery, replaceQuery])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setLocalSearchQuery(query)
    onSearchChange(query)
  }

  const handleReplaceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value
    setLocalReplaceQuery(query)
    onReplaceChange(query)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Escape':
        onClose()
        break
      case 'Enter':
        if (e.shiftKey) {
          onFindPrevious()
        } else {
          onFindNext()
        }
        break
      case 'F3':
        if (e.shiftKey) {
          onFindPrevious()
        } else {
          onFindNext()
        }
        e.preventDefault()
        break
    }
  }

  return (
    <div className="search-replace-panel" onKeyDown={handleKeyDown}>
      <div className="search-replace-header">
        <span className="panel-title">Find and Replace</span>
        <button className="close-button" onClick={onClose} title="Close (Esc)">
          ✕
        </button>
      </div>
      
      <div className="search-replace-content">
        <div className="input-group">
          <label htmlFor="search-input">Find:</label>
          <input
            id="search-input"
            type="text"
            value={localSearchQuery}
            onChange={handleSearchChange}
            placeholder="Search query..."
            autoFocus
          />
        </div>
        
        <div className="input-group">
          <label htmlFor="replace-input">Replace:</label>
          <input
            id="replace-input"
            type="text"
            value={localReplaceQuery}
            onChange={handleReplaceChange}
            placeholder="Replace with..."
          />
        </div>
        
        <div className="button-group">
          <button onClick={onFindNext} title="Find Next (Enter)">
            Find Next
          </button>
          <button onClick={onFindPrevious} title="Find Previous (Shift+Enter)">
            Find Previous
          </button>
          <button onClick={onReplace} title="Replace Current">
            Replace
          </button>
          <button onClick={onReplaceAll} title="Replace All">
            Replace All
          </button>
        </div>
        
        <div className="shortcuts-info">
          <span>F3: Next, Shift+F3: Previous, Esc: Close</span>
        </div>
      </div>
    </div>
  )
}

export default SearchReplacePanel