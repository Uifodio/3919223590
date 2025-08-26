import React, { useState } from 'react';
import { Folder, File, FileText, FileImage, FileVideo, FileAudio, Archive, Code } from 'lucide-react';
import { cn } from '../utils/cn';

const FileExplorer = ({
  files,
  folders,
  selectedFiles,
  viewMode,
  showHiddenFiles,
  onFileSelect,
  onFileDoubleClick,
  onContextMenu,
  loading,
  error
}) => {
  const [dragOver, setDragOver] = useState(false);

  const getFileIcon = (fileName) => {
    const ext = fileName.toLowerCase().substring(fileName.lastIndexOf('.'));
    
    // Image files
    if (['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'].includes(ext)) {
      return <FileImage className="w-6 h-6 text-green-500" />;
    }
    
    // Video files
    if (['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'].includes(ext)) {
      return <FileVideo className="w-6 h-6 text-purple-500" />;
    }
    
    // Audio files
    if (['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'].includes(ext)) {
      return <FileAudio className="w-6 h-6 text-orange-500" />;
    }
    
    // Archive files
    if (['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'].includes(ext)) {
      return <Archive className="w-6 h-6 text-red-500" />;
    }
    
    // Code files
    if (['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.sql', '.xml', '.yaml', '.yml', '.json', '.css', '.html', '.md'].includes(ext)) {
      return <Code className="w-6 h-6 text-blue-500" />;
    }
    
    // Text files
    if (['.txt', '.log', '.ini', '.conf'].includes(ext)) {
      return <FileText className="w-6 h-6 text-gray-500" />;
    }
    
    return <File className="w-6 h-6 text-gray-400" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString();
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    // Handle file drop logic here
  };

  const handleKeyDown = (e, item) => {
    if (e.key === 'Enter') {
      onFileDoubleClick(item);
    } else if (e.key === ' ') {
      e.preventDefault();
      onFileSelect(item, e.ctrlKey || e.metaKey);
    }
  };

  const renderListItem = (item) => {
    const isSelected = selectedFiles.some(f => f.path === item.path);
    
    return (
      <div
        key={item.path}
        className={cn(
          'file-list-item',
          isSelected && 'selected'
        )}
        onClick={(e) => onFileSelect(item, e.ctrlKey || e.metaKey)}
        onDoubleClick={() => onFileDoubleClick(item)}
        onContextMenu={(e) => onContextMenu(e, item)}
        onKeyDown={(e) => handleKeyDown(e, item)}
        tabIndex={0}
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {item.isDirectory ? (
            <Folder className="w-5 h-5 text-yellow-500 flex-shrink-0" />
          ) : (
            getFileIcon(item.name)
          )}
          
          <div className="flex-1 min-w-0">
            <div className="truncate font-medium">{item.name}</div>
            {!item.isDirectory && (
              <div className="text-xs text-muted-foreground">
                {formatFileSize(item.size)}
              </div>
            )}
          </div>
          
          <div className="text-xs text-muted-foreground flex-shrink-0">
            {formatDate(item.modified)}
          </div>
        </div>
      </div>
    );
  };

  const renderGridItem = (item) => {
    const isSelected = selectedFiles.some(f => f.path === item.path);
    
    return (
      <div
        key={item.path}
        className={cn(
          'file-grid-item',
          isSelected && 'selected'
        )}
        onClick={(e) => onFileSelect(item, e.ctrlKey || e.metaKey)}
        onDoubleClick={() => onFileDoubleClick(item)}
        onContextMenu={(e) => onContextMenu(e, item)}
        onKeyDown={(e) => handleKeyDown(e, item)}
        tabIndex={0}
      >
        {item.isDirectory ? (
          <Folder className="w-12 h-12 text-yellow-500" />
        ) : (
          getFileIcon(item.name)
        )}
        
        <div className="text-center mt-2">
          <div className="text-sm font-medium truncate max-w-full">
            {item.name}
          </div>
          {!item.isDirectory && (
            <div className="text-xs text-muted-foreground">
              {formatFileSize(item.size)}
            </div>
          )}
        </div>
      </div>
    );
  };

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
          <div className="text-destructive mb-2">Error loading directory</div>
          <div className="text-sm text-muted-foreground">{error}</div>
        </div>
      </div>
    );
  }

  const allItems = [...folders, ...files];
  const filteredItems = showHiddenFiles 
    ? allItems 
    : allItems.filter(item => !item.name.startsWith('.'));

  return (
    <div
      className={cn(
        'flex-1 overflow-auto',
        dragOver && 'bg-accent/20'
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {viewMode === 'list' ? (
        <div className="file-list">
          {filteredItems.map(renderListItem)}
        </div>
      ) : (
        <div className="file-grid">
          {filteredItems.map(renderGridItem)}
        </div>
      )}
      
      {filteredItems.length === 0 && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-muted-foreground">
            <Folder className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <div>No files found</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileExplorer;