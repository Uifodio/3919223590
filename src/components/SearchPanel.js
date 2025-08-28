import React, { useState, useEffect, useRef, useCallback } from 'react';
import './SearchPanel.css';

const SearchPanel = ({ mode, onClose, onFind, onReplace, content, onNavigateToLine }) => {
  const [findQuery, setFindQuery] = useState('');
  const [replaceQuery, setReplaceQuery] = useState('');
  const [options, setOptions] = useState({
    caseSensitive: false,
    wholeWord: false,
    regex: false
  });
  const [results, setResults] = useState([]);
  const [currentResultIndex, setCurrentResultIndex] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  
  const findInputRef = useRef(null);
  const replaceInputRef = useRef(null);
  
  // Focus and select find input on mount
  useEffect(() => {
    if (findInputRef.current) {
      findInputRef.current.focus();
      findInputRef.current.select();
    }
  }, []);
  
  // Perform search when query or options change
  useEffect(() => {
    if (findQuery.trim() && content) {
      performSearch();
    } else {
      setResults([]);
      setCurrentResultIndex(0);
    }
  }, [findQuery, options, content]);
  
  // Perform actual search in content
  const performSearch = useCallback(() => {
    if (!findQuery.trim() || !content) return;
    
    setIsSearching(true);
    const searchResults = [];
    const lines = content.split('\n');
    const searchTerm = options.caseSensitive ? findQuery : findQuery.toLowerCase();
    
    lines.forEach((line, lineIndex) => {
      const lineText = options.caseSensitive ? line : line.toLowerCase();
      let searchIndex = 0;
      
      while (true) {
        const index = lineText.indexOf(searchTerm, searchIndex);
        if (index === -1) break;
        
        // Check whole word if option is enabled
        if (options.wholeWord) {
          const before = lineText[index - 1] || ' ';
          const after = lineText[index + searchTerm.length] || ' ';
          const wordBoundary = /[a-zA-Z0-9_]/.test(before) || /[a-zA-Z0-9_]/.test(after);
          if (wordBoundary) {
            searchIndex = index + 1;
            continue;
          }
        }
        
        searchResults.push({
          line: lineIndex + 1,
          column: index + 1,
          text: line.substring(index, index + searchTerm.length),
          fullLine: line
        });
        
        searchIndex = index + 1;
      }
    });
    
    setResults(searchResults);
    setCurrentResultIndex(searchResults.length > 0 ? 0 : -1);
    setIsSearching(false);
  }, [findQuery, options, content]);
  
  // Navigate to specific result
  const navigateToResult = useCallback((result) => {
    if (onNavigateToLine && result) {
      onNavigateToLine(result.line, result.column);
    }
  }, [onNavigateToLine]);
  
  // Handle find action
  const handleFind = useCallback(() => {
    if (findQuery.trim()) {
      performSearch();
    }
  }, [findQuery, performSearch]);
  
  // Handle replace action
  const handleReplace = useCallback(() => {
    if (findQuery.trim() && replaceQuery.trim() && results.length > 0) {
      const currentResult = results[currentResultIndex];
      if (currentResult) {
        onReplace(findQuery, replaceQuery, options, currentResult);
        // Remove the replaced result and update
        const newResults = results.filter((_, index) => index !== currentResultIndex);
        setResults(newResults);
        if (newResults.length > 0) {
          setCurrentResultIndex(Math.min(currentResultIndex, newResults.length - 1));
        } else {
          setCurrentResultIndex(-1);
        }
      }
    }
  }, [findQuery, replaceQuery, options, results, currentResultIndex, onReplace]);
  
  // Handle replace all action
  const handleReplaceAll = useCallback(() => {
    if (findQuery.trim() && replaceQuery.trim() && results.length > 0) {
      onReplace(findQuery, replaceQuery, { ...options, replaceAll: true });
      setResults([]);
      setCurrentResultIndex(-1);
    }
  }, [findQuery, replaceQuery, options, results.length, onReplace]);
  
  // Navigate to next result
  const handleNext = useCallback(() => {
    if (results.length > 0) {
      const nextIndex = (currentResultIndex + 1) % results.length;
      setCurrentResultIndex(nextIndex);
      navigateToResult(results[nextIndex]);
    }
  }, [results, currentResultIndex, navigateToResult]);
  
  // Navigate to previous result
  const handlePrevious = useCallback(() => {
    if (results.length > 0) {
      const prevIndex = currentResultIndex === 0 ? results.length - 1 : currentResultIndex - 1;
      setCurrentResultIndex(prevIndex);
      navigateToResult(results[prevIndex]);
    }
  }, [results, currentResultIndex, navigateToResult]);
  
  // Handle keyboard shortcuts
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (e.shiftKey) {
        handlePrevious();
      } else {
        handleNext();
      }
    } else if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'F3') {
      e.preventDefault();
      if (e.shiftKey) {
        handlePrevious();
      } else {
        handleNext();
      }
    }
  }, [handleNext, handlePrevious, onClose]);
  
  // Handle input changes with debouncing
  const handleFindChange = useCallback((e) => {
    setFindQuery(e.target.value);
  }, []);
  
  const handleReplaceChange = useCallback((e) => {
    setReplaceQuery(e.target.value);
  }, []);
  
  return (
    <div className="search-panel bottom">
      <div className="search-header">
        <div className="search-mode-indicator">
          {mode === 'replace' ? '🔍 Replace' : '🔍 Find'}
        </div>
        <button onClick={onClose} className="search-close-btn" title="Close (Esc)">
          ✕
        </button>
      </div>
      
      <div className="search-content">
        <div className="search-inputs">
          <div className="search-group">
            <label className="search-label">Find:</label>
            <input
              ref={findInputRef}
              type="text"
              value={findQuery}
              onChange={handleFindChange}
              onKeyDown={handleKeyDown}
              placeholder="Enter search term..."
              className="search-input find-input"
            />
          </div>
          
          {mode === 'replace' && (
            <div className="search-group">
              <label className="search-label">Replace:</label>
              <input
                ref={replaceInputRef}
                type="text"
                value={replaceQuery}
                onChange={handleReplaceChange}
                onKeyDown={handleKeyDown}
                placeholder="Enter replacement text..."
                className="search-input replace-input"
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
            <span>Case sensitive</span>
          </label>
          
          <label className="search-checkbox">
            <input
              type="checkbox"
              checked={options.wholeWord}
              onChange={(e) => setOptions(prev => ({ ...prev, wholeWord: e.target.checked }))}
            />
            <span>Whole word</span>
          </label>
          
          <label className="search-checkbox">
            <input
              type="checkbox"
              checked={options.regex}
              onChange={(e) => setOptions(prev => ({ ...prev, regex: e.target.checked }))}
            />
            <span>Regex</span>
          </label>
        </div>
        
        <div className="search-actions">
          <button onClick={handleFind} className="search-button find" disabled={!findQuery.trim()}>
            Find
          </button>
          
          {mode === 'replace' && (
            <>
              <button onClick={handleReplace} className="search-button replace" disabled={!findQuery.trim() || !replaceQuery.trim() || results.length === 0}>
                Replace
              </button>
              <button onClick={handleReplaceAll} className="search-button replace-all" disabled={!findQuery.trim() || !replaceQuery.trim() || results.length === 0}>
                Replace All
              </button>
            </>
          )}
          
          <div className="search-navigation">
            <button onClick={handlePrevious} className="search-button nav" disabled={results.length === 0} title="Previous (Shift+Enter, Shift+F3)">
              ↑
            </button>
            <button onClick={handleNext} className="search-button nav" disabled={results.length === 0} title="Next (Enter, F3)">
              ↓
            </button>
          </div>
        </div>
      </div>
      
      {results.length > 0 && (
        <div className="search-results">
          <div className="results-info">
            <span className="results-count">
              {results.length} result{results.length !== 1 ? 's' : ''}
            </span>
            {currentResultIndex >= 0 && (
              <span className="current-result">
                • Current: {currentResultIndex + 1} of {results.length}
              </span>
            )}
          </div>
          {currentResultIndex >= 0 && results[currentResultIndex] && (
            <div className="current-result-preview">
              Line {results[currentResultIndex].line}: {results[currentResultIndex].fullLine}
            </div>
          )}
        </div>
      )}
      
      {isSearching && (
        <div className="search-loading">
          <div className="loading-spinner"></div>
          Searching...
        </div>
      )}
    </div>
  );
};

export default SearchPanel;