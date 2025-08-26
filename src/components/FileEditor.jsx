import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { X, Save, Undo, Redo, Search, Settings } from 'lucide-react';
import { cn } from '../utils/cn';

const FileEditor = ({ file, onClose, onSave, settings }) => {
  const [content, setContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDirty, setIsDirty] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [autoSaveTimer, setAutoSaveTimer] = useState(null);

  useEffect(() => {
    loadFile();
  }, [file]);

  useEffect(() => {
    // Auto-save functionality
    if (settings.autoSave && isDirty) {
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
      }
      
      const timer = setTimeout(() => {
        handleSave();
      }, settings.autoSaveInterval || 30000);
      
      setAutoSaveTimer(timer);
    }

    return () => {
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
      }
    };
  }, [content, isDirty, settings.autoSave, settings.autoSaveInterval]);

  const loadFile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.readFile(file.path);
      if (result.success) {
        setContent(result.content);
        setOriginalContent(result.content);
        setIsDirty(false);
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await onSave(content);
      setOriginalContent(content);
      setIsDirty(false);
    } catch (error) {
      console.error('Failed to save file:', error);
    }
  };

  const handleContentChange = (value) => {
    setContent(value);
    setIsDirty(value !== originalContent);
  };

  const handleUndo = () => {
    // Monaco Editor handles undo/redo internally
  };

  const handleRedo = () => {
    // Monaco Editor handles undo/redo internally
  };

  const getLanguageFromExtension = (fileName) => {
    const ext = fileName.toLowerCase().substring(fileName.lastIndexOf('.'));
    const languageMap = {
      '.js': 'javascript',
      '.jsx': 'javascript',
      '.ts': 'typescript',
      '.tsx': 'typescript',
      '.json': 'json',
      '.css': 'css',
      '.html': 'html',
      '.md': 'markdown',
      '.py': 'python',
      '.java': 'java',
      '.cpp': 'cpp',
      '.c': 'c',
      '.h': 'cpp',
      '.php': 'php',
      '.rb': 'ruby',
      '.go': 'go',
      '.rs': 'rust',
      '.swift': 'swift',
      '.kt': 'kotlin',
      '.scala': 'scala',
      '.sql': 'sql',
      '.xml': 'xml',
      '.yaml': 'yaml',
      '.yml': 'yaml',
      '.ini': 'ini',
      '.conf': 'ini',
      '.log': 'log',
      '.txt': 'plaintext'
    };
    return languageMap[ext] || 'plaintext';
  };

  const handleBeforeUnload = (e) => {
    if (isDirty) {
      e.preventDefault();
      e.returnValue = '';
    }
  };

  useEffect(() => {
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isDirty]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-destructive mb-2">Error loading file</div>
          <div className="text-sm text-muted-foreground">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Editor Toolbar */}
      <div className="flex items-center justify-between p-2 border-b border-border bg-card">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{file.name}</span>
          {isDirty && <span className="text-xs text-muted-foreground">(modified)</span>}
        </div>
        
        <div className="flex items-center gap-1">
          <button
            className="toolbar-button"
            onClick={() => setShowSearch(!showSearch)}
            title="Search"
          >
            <Search className="w-4 h-4" />
          </button>
          
          <button
            className="toolbar-button"
            onClick={handleUndo}
            title="Undo"
          >
            <Undo className="w-4 h-4" />
          </button>
          
          <button
            className="toolbar-button"
            onClick={handleRedo}
            title="Redo"
          >
            <Redo className="w-4 h-4" />
          </button>
          
          <button
            className="toolbar-button"
            onClick={handleSave}
            disabled={!isDirty}
            title="Save"
          >
            <Save className="w-4 h-4" />
          </button>
          
          <button
            className="toolbar-button"
            onClick={onClose}
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search Bar */}
      {showSearch && (
        <div className="p-2 border-b border-border bg-card">
          <input
            type="text"
            placeholder="Search in file..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      )}

      {/* Monaco Editor */}
      <div className="flex-1">
        <Editor
          height="100%"
          language={getLanguageFromExtension(file.name)}
          theme={settings.theme || 'vs-dark'}
          value={content}
          onChange={handleContentChange}
          options={{
            fontSize: settings.fontSize || 14,
            wordWrap: settings.wordWrap || 'on',
            minimap: settings.minimap || { enabled: true },
            lineNumbers: settings.lineNumbers || 'on',
            automaticLayout: true,
            scrollBeyondLastLine: false,
            folding: true,
            foldingStrategy: 'indentation',
            showFoldingControls: 'always',
            selectOnLineNumbers: true,
            roundedSelection: false,
            readOnly: false,
            cursorStyle: 'line',
            contextmenu: true,
            mouseWheelZoom: true,
            quickSuggestions: true,
            suggestOnTriggerCharacters: true,
            acceptSuggestionOnEnter: 'on',
            tabCompletion: 'on',
            wordBasedSuggestions: true,
            parameterHints: {
              enabled: true
            },
            autoIndent: 'full',
            formatOnPaste: true,
            formatOnType: true,
            dragAndDrop: true,
            find: {
              addExtraSpaceOnTop: false,
              autoFindInSelection: 'never',
              seedSearchStringFromSelection: 'always',
              focusBackOnEditor: true
            }
          }}
        />
      </div>
    </div>
  );
};

export default FileEditor;