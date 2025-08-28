import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodeEditor.css';

const CodeEditor = ({ content, language, onChange }) => {
  const [text, setText] = useState(content);
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const [selection, setSelection] = useState({ start: 0, end: 0 });
  const textareaRef = useRef(null);
  const lineNumbersRef = useRef(null);
  
  useEffect(() => {
    setText(content);
  }, [content]);
  
  useEffect(() => {
    if (textareaRef.current) {
      const textarea = textareaRef.current;
      const lines = text.split('\n');
      const line = lines.length;
      const column = lines[lines.length - 1].length + 1;
      setCursorPosition({ line, column });
    }
  }, [text]);
  
  const handleChange = (e) => {
    const newText = e.target.value;
    setText(newText);
    
    // Calculate cursor position
    const textarea = e.target;
    const cursorPos = textarea.selectionStart;
    const lines = newText.substring(0, cursorPos).split('\n');
    const line = lines.length;
    const column = lines[lines.length - 1].length + 1;
    
    setCursorPosition({ line, column });
    onChange(newText, line, column);
  };
  
  const handleScroll = useCallback(() => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  }, []);
  
  const handleKeyDown = (e) => {
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
      
      onChange(newText, cursorPosition.line, cursorPosition.column);
    } else if (e.key === 'Enter') {
      // Auto-indent
      const textarea = e.target;
      const cursorPos = textarea.selectionStart;
      const lines = text.substring(0, cursorPos).split('\n');
      const currentLine = lines[lines.length - 1];
      const indent = currentLine.match(/^(\s*)/)[0];
      
      setTimeout(() => {
        const newText = text.substring(0, cursorPos) + '\n' + indent + text.substring(cursorPos);
        setText(newText);
        onChange(newText, cursorPosition.line + 1, indent.length + 1);
      }, 0);
    }
  };
  
  const handleSelect = (e) => {
    const textarea = e.target;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    setSelection({ start, end });
  };
  
  const renderLineNumbers = () => {
    const lines = text.split('\n');
    return (
      <div className="line-numbers" ref={lineNumbersRef}>
        {lines.map((_, index) => (
          <div key={index} className="line-number">
            {String(index + 1).padStart(4, ' ')}
          </div>
        ))}
      </div>
    );
  };
  
  const getLanguageForHighlighting = (lang) => {
    const languageMap = {
      'csharp': 'csharp',
      'javascript': 'javascript',
      'typescript': 'typescript',
      'python': 'python',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'c': 'c',
      'cpp': 'cpp',
      'text': 'text'
    };
    
    return languageMap[lang] || 'text';
  };
  
  return (
    <div className="code-editor">
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
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            wrap="off"
          />
          
          <div className="syntax-highlighting">
            <SyntaxHighlighter
              language={getLanguageForHighlighting(language)}
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                padding: '8px 0',
                background: 'transparent',
                fontSize: '14px',
                lineHeight: '1.5',
                fontFamily: 'Consolas, Monaco, "Courier New", monospace'
              }}
              showLineNumbers={false}
              wrapLines={true}
              lineProps={{
                style: { wordBreak: 'break-all', whiteSpace: 'pre-wrap' }
              }}
            >
              {text}
            </SyntaxHighlighter>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;