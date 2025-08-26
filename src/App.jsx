import React, { useState, useEffect, useCallback } from 'react';
import FileTree from './components/FileTree';
import FileExplorer from './components/FileExplorer';
import FileEditor from './components/FileEditor';
import Toolbar from './components/Toolbar';
import StatusBar from './components/StatusBar';
import SearchBar from './components/SearchBar';
import Breadcrumb from './components/Breadcrumb';
import ContextMenu from './components/ContextMenu';
import ProgressBar from './components/ProgressBar';
import { useFileManager } from './utils/useFileManager';
import { useSettings } from './utils/useSettings';
import { cn } from './utils/cn';

function App() {
  const [currentPath, setCurrentPath] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [editingFile, setEditingFile] = useState(null);
  const [showHiddenFiles, setShowHiddenFiles] = useState(false);
  const [viewMode, setViewMode] = useState('list');
  const [contextMenu, setContextMenu] = useState(null);
  const [progress, setProgress] = useState(null);
  const [clipboard, setClipboard] = useState(null);

  const { settings, updateSettings } = useSettings();
  const {
    files,
    folders,
    loading,
    error,
    refresh,
    navigateTo,
    performOperation
  } = useFileManager();

  // Load initial path
  useEffect(() => {
    const loadInitialPath = async () => {
      try {
        const drives = await window.electronAPI.getDrives();
        if (drives.success && drives.drives.length > 0) {
          setCurrentPath(drives.drives[0].letter);
          navigateTo(drives.drives[0].letter);
        }
      } catch (error) {
        console.error('Failed to load drives:', error);
      }
    };

    loadInitialPath();
  }, [navigateTo]);

  // Handle folder navigation
  const handleFolderClick = useCallback((folderPath) => {
    setCurrentPath(folderPath);
    navigateTo(folderPath);
    setSelectedFiles([]);
  }, [navigateTo]);

  // Handle file selection
  const handleFileSelect = useCallback((file, isMultiSelect = false) => {
    if (isMultiSelect) {
      setSelectedFiles(prev => {
        const isSelected = prev.some(f => f.path === file.path);
        if (isSelected) {
          return prev.filter(f => f.path !== file.path);
        } else {
          return [...prev, file];
        }
      });
    } else {
      setSelectedFiles([file]);
    }
  }, []);

  // Handle file double click
  const handleFileDoubleClick = useCallback(async (file) => {
    if (file.isDirectory) {
      handleFolderClick(file.path);
    } else {
      // Check if it's a text file
      const textExtensions = ['.txt', '.js', '.jsx', '.ts', '.tsx', '.json', '.css', '.html', '.md', '.py', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.sql', '.xml', '.yaml', '.yml', '.ini', '.conf', '.log'];
      const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (textExtensions.includes(ext)) {
        setEditingFile(file);
      } else {
        // Open with default application
        await window.electronAPI.openExternal(file.path);
      }
    }
  }, [handleFolderClick]);

  // Handle context menu
  const handleContextMenu = useCallback((event, file = null) => {
    event.preventDefault();
    setContextMenu({
      x: event.clientX,
      y: event.clientY,
      file
    });
  }, []);

  // Handle file operations
  const handleFileOperation = useCallback(async (operation, source, destination = null) => {
    setProgress({ operation, progress: 0 });
    
    try {
      const result = await performOperation(operation, source, destination);
      if (result.success) {
        refresh();
        setSelectedFiles([]);
      } else {
        console.error('Operation failed:', result.error);
      }
    } catch (error) {
      console.error('Operation error:', error);
    } finally {
      setProgress(null);
    }
  }, [performOperation, refresh]);

  // Handle clipboard operations
  const handleCopy = useCallback(async () => {
    if (selectedFiles.length > 0) {
      const clipboardData = {
        type: 'files',
        files: selectedFiles,
        operation: 'copy'
      };
      await window.electronAPI.setClipboard(clipboardData);
      setClipboard(clipboardData);
    }
  }, [selectedFiles]);

  const handleCut = useCallback(async () => {
    if (selectedFiles.length > 0) {
      const clipboardData = {
        type: 'files',
        files: selectedFiles,
        operation: 'cut'
      };
      await window.electronAPI.setClipboard(clipboardData);
      setClipboard(clipboardData);
    }
  }, [selectedFiles]);

  const handlePaste = useCallback(async () => {
    if (clipboard && clipboard.type === 'files') {
      for (const file of clipboard.files) {
        const fileName = file.name;
        const destination = `${currentPath}/${fileName}`;
        
        if (clipboard.operation === 'copy') {
          await handleFileOperation('copy', file.path, destination);
        } else if (clipboard.operation === 'cut') {
          await handleFileOperation('move', file.path, destination);
        }
      }
      setClipboard(null);
    }
  }, [clipboard, currentPath, handleFileOperation]);

  // Handle search
  const handleSearch = useCallback((query) => {
    // Implement search functionality
    console.log('Search query:', query);
  }, []);

  // Handle breadcrumb navigation
  const handleBreadcrumbClick = useCallback((path) => {
    setCurrentPath(path);
    navigateTo(path);
    setSelectedFiles([]);
  }, [navigateTo]);

  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      {/* Toolbar */}
      <Toolbar
        onNewWindow={() => window.electronAPI.createNewWindow()}
        onOpenFolder={async () => {
          const result = await window.electronAPI.showOpenDialog();
          if (result.success && result.filePaths.length > 0) {
            handleFolderClick(result.filePaths[0]);
          }
        }}
        onCopy={handleCopy}
        onCut={handleCut}
        onPaste={handlePaste}
        onDelete={() => {
          if (selectedFiles.length > 0) {
            handleFileOperation('delete', selectedFiles.map(f => f.path));
          }
        }}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        showHiddenFiles={showHiddenFiles}
        onShowHiddenFilesChange={setShowHiddenFiles}
      />

      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - File Tree */}
        <div className="w-64 border-r border-border bg-card flex flex-col">
          <FileTree
            currentPath={currentPath}
            onFolderClick={handleFolderClick}
            showHiddenFiles={showHiddenFiles}
          />
        </div>

        {/* Right Panel - File Explorer or Editor */}
        <div className="flex-1 flex flex-col">
          {/* Breadcrumb */}
          <Breadcrumb
            currentPath={currentPath}
            onPathClick={handleBreadcrumbClick}
          />

          {/* Content Area */}
          <div className="flex-1 flex overflow-hidden">
            {editingFile ? (
              <FileEditor
                file={editingFile}
                onClose={() => setEditingFile(null)}
                onSave={async (content) => {
                  await window.electronAPI.writeFile(editingFile.path, content);
                  refresh();
                }}
                settings={settings.editor}
              />
            ) : (
              <FileExplorer
                files={files}
                folders={folders}
                selectedFiles={selectedFiles}
                viewMode={viewMode}
                showHiddenFiles={showHiddenFiles}
                onFileSelect={handleFileSelect}
                onFileDoubleClick={handleFileDoubleClick}
                onContextMenu={handleContextMenu}
                loading={loading}
                error={error}
              />
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <StatusBar
        selectedCount={selectedFiles.length}
        totalCount={files.length + folders.length}
        currentPath={currentPath}
      />

      {/* Context Menu */}
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          file={contextMenu.file}
          onClose={() => setContextMenu(null)}
          onOperation={handleFileOperation}
          currentPath={currentPath}
        />
      )}

      {/* Progress Bar */}
      {progress && (
        <ProgressBar
          operation={progress.operation}
          progress={progress.progress}
          onClose={() => setProgress(null)}
        />
      )}
    </div>
  );
}

export default App;