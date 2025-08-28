import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodeEditor.css';

const CodeEditor = ({ content, language, onChange, onCursorPositionChange }) => {
  const [text, setText] = useState(content || '');
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const [selection, setSelection] = useState({ start: 0, end: 0 });
  
  const textareaRef = useRef(null);
  const lineNumbersRef = useRef(null);
  const syntaxHighlighterRef = useRef(null);
  const containerRef = useRef(null);

  // Update text when content prop changes
  useEffect(() => {
    if (content !== text) {
      setText(content || '');
    }
  }, [content]);

  // Perfect scrolling synchronization
  const syncScroll = useCallback((sourceElement, targetElement) => {
    if (!sourceElement || !targetElement) return;
    
    // Get scroll position
    const scrollTop = sourceElement.scrollTop;
    const scrollLeft = sourceElement.scrollLeft;
    
    // Apply to target element
    targetElement.scrollTop = scrollTop;
    targetElement.scrollLeft = scrollLeft;
  }, []);

  // Handle textarea scroll - sync with line numbers and syntax highlighter
  const handleTextareaScroll = useCallback((e) => {
    const textarea = e.target;
    syncScroll(textarea, lineNumbersRef.current);
    syncScroll(textarea, syntaxHighlighterRef.current);
  }, [syncScroll]);

  // Handle line numbers scroll - sync with textarea and syntax highlighter
  const handleLineNumbersScroll = useCallback((e) => {
    const lineNumbers = e.target;
    syncScroll(lineNumbers, textareaRef.current);
    syncScroll(lineNumbers, syntaxHighlighterRef.current);
  }, [syncScroll]);

  // Handle syntax highlighter scroll - sync with textarea and line numbers
  const handleSyntaxHighlighterScroll = useCallback((e) => {
    const syntaxHighlighter = e.target;
    syncScroll(syntaxHighlighter, textareaRef.current);
    syncScroll(syntaxHighlighter, lineNumbersRef.current);
  }, [syncScroll]);

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

  // Handle key events
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
        textarea.focus();
      }, 0);
      
      if (onChange) {
        onChange(newText);
      }
    } else if (e.key === 'Enter') {
      // Auto-indent on Enter
      const textarea = e.target;
      const cursorPos = textarea.selectionStart;
      const textBeforeCursor = text.substring(0, cursorPos);
      const lines = textBeforeCursor.split('\n');
      const currentLine = lines[lines.length - 1];
      const indent = currentLine.match(/^(\s*)/)[0];
      
      setTimeout(() => {
        const newText = text.substring(0, cursorPos) + '\n' + indent + text.substring(cursorPos);
        setText(newText);
        textarea.selectionStart = textarea.selectionEnd = cursorPos + 1 + indent.length;
        textarea.focus();
        
        if (onChange) {
          onChange(newText);
        }
      }, 0);
    }
  }, [text, onChange]);

  // Handle cursor position and selection changes
  const handleSelect = useCallback((e) => {
    const textarea = e.target;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    
    setSelection({ start, end });
    
    // Calculate cursor position
    const textBeforeCursor = text.substring(0, start);
    const lines = textBeforeCursor.split('\n');
    const line = lines.length;
    const column = lines[lines.length - 1].length + 1;
    
    setCursorPosition({ line, column });
    
    if (onCursorPositionChange) {
      onCursorPositionChange({ line, column });
    }
  }, [text, onCursorPositionChange]);

  // Render line numbers with proper synchronization
  const renderLineNumbers = () => {
    const lines = text.split('\n');
    const totalLines = Math.max(lines.length, 1);
    
    return (
      <div 
        className="line-numbers" 
        ref={lineNumbersRef}
        onScroll={handleLineNumbersScroll}
      >
        {Array.from({ length: totalLines }, (_, i) => (
          <div 
            key={i + 1} 
            className={`line-number ${cursorPosition.line === i + 1 ? 'current-line' : ''}`}
          >
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

  // Calculate total lines
  const totalLines = text.split('\n').length;

  return (
    <div className="code-editor" ref={containerRef}>
      <div className="editor-container">
        {renderLineNumbers()}
        <div className="editor-content">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleChange}
            onScroll={handleTextareaScroll}
            onKeyDown={handleKeyDown}
            onSelect={handleSelect}
            className="editor-textarea"
            placeholder="Start typing your code here..."
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            wrap="off"
          />
          <div 
            className="syntax-highlighting"
            ref={syntaxHighlighterRef}
            onScroll={handleSyntaxHighlighterScroll}
          >
            <SyntaxHighlighter
              language={getLanguageForHighlighting(language)}
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                padding: '8px 12px',
                background: 'transparent',
                fontSize: '14px',
                lineHeight: '21px',
                fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
                overflow: 'auto',
                height: '100%'
              }}
              showLineNumbers={false}
              wrapLines={false}
              useInlineStyles={true}
            >
              {text || ' '}
            </SyntaxHighlighter>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;