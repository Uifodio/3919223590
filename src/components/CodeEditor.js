import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import MiniMap from './MiniMap';
import './CodeEditor.css';

const CodeEditor = ({ content, language, onChange, onCursorPositionChange }) => {
  const [text, setText] = useState(content);
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const textareaRef = useRef(null);
  const lineNumbersRef = useRef(null);
  const editorContainerRef = useRef(null);

  // Update text when content prop changes
  useEffect(() => {
    setText(content);
  }, [content]);

  // Synchronize scrolling between textarea and line numbers
  const handleScroll = useCallback((e) => {
    if (lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = e.target.scrollTop;
    }
    if (onCursorPositionChange) {
      onCursorPositionChange(cursorPosition);
    }
  }, [cursorPosition, onCursorPositionChange]);

  // Handle text changes
  const handleChange = useCallback((e) => {
    const newText = e.target.value;
    setText(newText);
    
    // Calculate cursor position
    const textarea = e.target;
    const cursorPos = textarea.selectionStart;
    const textBeforeCursor = newText.substring(0, cursorPos);
    const lines = textBeforeCursor.split('\n');
    const line = lines.length;
    const column = lines[lines.length - 1].length + 1;
    
    setCursorPosition({ line, column });
    
    if (onChange) {
      onChange(newText);
    }
  }, [onChange]);

  // Handle key events for better navigation
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.target;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      const newText = text.substring(0, start) + '  ' + text.substring(end);
      setText(newText);
      
      // Set cursor position after tab
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      }, 0);
      
      if (onChange) {
        onChange(newText);
      }
    }
  }, [text, onChange]);

  // Handle cursor position changes
  const handleSelect = useCallback((e) => {
    const textarea = e.target;
    const cursorPos = textarea.selectionStart;
    const textBeforeCursor = text.substring(0, cursorPos);
    const lines = textBeforeCursor.split('\n');
    const line = lines.length;
    const column = lines[lines.length - 1].length + 1;
    
    setCursorPosition({ line, column });
    
    if (onCursorPositionChange) {
      onCursorPositionChange({ line, column });
    }
  }, [text, onCursorPositionChange]);

  // Render line numbers
  const renderLineNumbers = () => {
    const lines = text.split('\n');
    const totalLines = lines.length;
    
    return (
      <div className="line-numbers" ref={lineNumbersRef}>
        {Array.from({ length: Math.max(totalLines, 1) }, (_, i) => (
          <div key={i + 1} className="line-number">
            {i + 1}
          </div>
        ))}
      </div>
    );
  };

  // Get language for syntax highlighting
  const getLanguageForHighlighting = (lang) => {
    const languageMap = {
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'py': 'python',
      'cs': 'csharp',
      'cpp': 'cpp',
      'c': 'c',
      'h': 'cpp',
      'hpp': 'cpp',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'xml': 'xml',
      'md': 'markdown',
      'txt': 'text'
    };
    
    return languageMap[lang] || lang || 'text';
  };

  // Calculate total lines for status bar
  const totalLines = text.split('\n').length;

  // Calculate visible range for mini-map
  const calculateVisibleRange = () => {
    if (!textareaRef.current) return { start: 1, end: totalLines };
    
    const textarea = textareaRef.current;
    const lineHeight = 21;
    const visibleLines = Math.ceil(textarea.clientHeight / lineHeight);
    const scrollTop = textarea.scrollTop;
    const start = Math.floor(scrollTop / lineHeight) + 1;
    const end = Math.min(start + visibleLines, totalLines);
    
    return { start, end };
  };

  const handleScrollToLine = useCallback((lineNumber) => {
    if (textareaRef.current) {
      const lineHeight = 21;
      const scrollTop = (lineNumber - 1) * lineHeight;
      textareaRef.current.scrollTop = scrollTop;
    }
  }, []);

  return (
    <div className="code-editor" ref={editorContainerRef}>
      <div className="editor-container">
        {renderLineNumbers()}
        <div className="editor-content">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleChange}
            onScroll={handleScroll}
            onKeyDown={handleKeyDown}
            onSelect={handleSelect}
            className="editor-textarea"
            placeholder="Start typing your code here..."
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
          />
          <div className="syntax-highlighting">
            <SyntaxHighlighter
              language={getLanguageForHighlighting(language)}
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                padding: '8px 12px',
                background: 'transparent',
                fontSize: '14px',
                lineHeight: '21px',
                fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace"
              }}
              showLineNumbers={false}
              wrapLines={false}
            >
              {text || ' '}
            </SyntaxHighlighter>
          </div>
        </div>
      </div>
      
      {/* Mini-map for navigation */}
      <MiniMap
        content={text}
        onScrollToLine={handleScrollToLine}
        visibleRange={calculateVisibleRange()}
      />
    </div>
  );
};

export default CodeEditor;