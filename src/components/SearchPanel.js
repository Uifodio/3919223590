import React, { useState, useEffect, useRef } from 'react';
import './SearchPanel.css';

const SearchPanel = ({ mode, onClose, onFind, onReplace }) => {
  const [findQuery, setFindQuery] = useState('');
  const [replaceQuery, setReplaceQuery] = useState('');
  const [options, setOptions] = useState({
    caseSensitive: false,
    wholeWord: false,
    regex: false
  });
  const [results, setResults] = useState([]);
  const [currentResultIndex, setCurrentResultIndex] = useState(0);
  
  const findInputRef = useRef(null);
  const replaceInputRef = useRef(null);
  
  useEffect(() => {
    if (findInputRef.current) {
      findInputRef.current.focus();
      findInputRef.current.select();
    }
  }, []);
  
  useEffect(() => {
    if (findQuery) {
      // TODO: Implement actual search functionality
      // For now, just simulate results
      const mockResults = [
        { line: 1, column: 1, text: findQuery },
        { line: 3, column: 5, text: findQuery },
        { line: 7, column: 2, text: findQuery }
      ];
      setResults(mockResults);
      setCurrentResultIndex(0);
    } else {
      setResults([]);
      setCurrentResultIndex(0);
    }
  }, [findQuery, options]);
  
  const handleFind = () => {
    if (findQuery.trim()) {
      onFind(findQuery, options);
    }
  };
  
  const handleReplace = () => {
    if (findQuery.trim() && replaceQuery.trim()) {
      onReplace(findQuery, replaceQuery, options);
    }
  };
  
  const handleReplaceAll = () => {
    if (findQuery.trim() && replaceQuery.trim()) {
      onReplace(findQuery, replaceQuery, { ...options, replaceAll: true });
    }
  };
  
  const handleNext = () => {
    if (results.length > 0) {
      const nextIndex = (currentResultIndex + 1) % results.length;
      setCurrentResultIndex(nextIndex);
      // TODO: Navigate to the result
    }
  };
  
  const handlePrevious = () => {
    if (results.length > 0) {
      const prevIndex = currentResultIndex === 0 ? results.length - 1 : currentResultIndex - 1;
      setCurrentResultIndex(prevIndex);
      // TODO: Navigate to the result
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) {
        handlePrevious();
      } else {
        handleNext();
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  };
  
  return (
    <div className="search-panel">
      <div className="search-inputs">
        <div className="search-group">
          <label>Find:</label>
          <input
            ref={findInputRef}
            type="text"
            value={findQuery}
            onChange={(e) => setFindQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter search term..."
            className="search-input"
          />
        </div>
        
        {mode === 'replace' && (
          <div className="search-group">
            <label>Replace:</label>
            <input
              ref={replaceInputRef}
              type="text"
              value={replaceQuery}
              onChange={(e) => setReplaceQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter replacement text..."
              className="search-input"
            />
          </div>
        )}
      </div>
      
      <div className="search-options">
        <label className="search-checkbox">
          <input
            type="checkbox"
            checked={options.caseSensitive}
            onChange={(e) => setOptions(prev => ({ ...prev, caseSensitive: e.target.checked }))}
          />
          Case sensitive
        </label>
        
        <label className="search-checkbox">
          <input
            type="checkbox"
            checked={options.wholeWord}
            onChange={(e) => setOptions(prev => ({ ...prev, wholeWord: e.target.checked }))}
          />
          Whole word
        </label>
        
        <label className="search-checkbox">
          <input
            type="checkbox"
            checked={options.regex}
            onChange={(e) => setOptions(prev => ({ ...prev, regex: e.target.checked }))}
          />
          Regex
        </label>
      </div>
      
      <div className="search-actions">
        <button onClick={handleFind} className="search-button find">
          Find
        </button>
        
        {mode === 'replace' && (
          <>
            <button onClick={handleReplace} className="search-button replace">
              Replace
            </button>
            <button onClick={handleReplaceAll} className="search-button replace-all">
              Replace All
            </button>
          </>
        )}
        
        <button onClick={handlePrevious} className="search-button nav" title="Previous (Shift+Enter)">
          ↑
        </button>
        <button onClick={handleNext} className="search-button nav" title="Next (Enter)">
          ↓
        </button>
        
        <button onClick={onClose} className="search-button close" title="Close (Esc)">
          ✕
        </button>
      </div>
      
      {results.length > 0 && (
        <div className="search-results">
          <div className="results-info">
            {results.length} result{results.length !== 1 ? 's' : ''}
            {currentResultIndex >= 0 && (
              <span> • Current: {currentResultIndex + 1}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPanel;