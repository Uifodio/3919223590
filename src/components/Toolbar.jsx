import React from 'react';
import { 
  Plus, 
  FolderOpen, 
  Copy, 
  Scissors, 
  Clipboard, 
  Trash2, 
  List, 
  Grid, 
  Eye,
  EyeOff,
  Settings
} from 'lucide-react';
import { cn } from '../utils/cn';

const Toolbar = ({
  onNewWindow,
  onOpenFolder,
  onCopy,
  onCut,
  onPaste,
  onDelete,
  viewMode,
  onViewModeChange,
  showHiddenFiles,
  onShowHiddenFilesChange
}) => {
  return (
    <div className="toolbar">
      <div className="flex items-center gap-1">
        <button
          className="toolbar-button"
          onClick={onNewWindow}
          title="New Window"
        >
          <Plus className="w-4 h-4" />
        </button>
        
        <button
          className="toolbar-button"
          onClick={onOpenFolder}
          title="Open Folder"
        >
          <FolderOpen className="w-4 h-4" />
        </button>
      </div>

      <div className="flex items-center gap-1">
        <button
          className="toolbar-button"
          onClick={onCopy}
          title="Copy (Ctrl+C)"
        >
          <Copy className="w-4 h-4" />
        </button>
        
        <button
          className="toolbar-button"
          onClick={onCut}
          title="Cut (Ctrl+X)"
        >
          <Scissors className="w-4 h-4" />
        </button>
        
        <button
          className="toolbar-button"
          onClick={onPaste}
          title="Paste (Ctrl+V)"
        >
          <Clipboard className="w-4 h-4" />
        </button>
        
        <button
          className="toolbar-button"
          onClick={onDelete}
          title="Delete"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="flex items-center gap-1">
        <button
          className={cn(
            "toolbar-button",
            viewMode === 'list' && "bg-accent"
          )}
          onClick={() => onViewModeChange('list')}
          title="List View"
        >
          <List className="w-4 h-4" />
        </button>
        
                  <button
            className={cn(
              "toolbar-button",
              viewMode === 'grid' && "bg-accent"
            )}
            onClick={() => onViewModeChange('grid')}
            title="Grid View"
          >
            <Grid className="w-4 h-4" />
          </button>
      </div>

      <div className="flex items-center gap-1">
        <button
          className={cn(
            "toolbar-button",
            showHiddenFiles && "bg-accent"
          )}
          onClick={() => onShowHiddenFilesChange(!showHiddenFiles)}
          title={showHiddenFiles ? "Hide Hidden Files" : "Show Hidden Files"}
        >
          {showHiddenFiles ? (
            <EyeOff className="w-4 h-4" />
          ) : (
            <Eye className="w-4 h-4" />
          )}
        </button>
        
        <button
          className="toolbar-button"
          onClick={() => {/* TODO: Open settings */}}
          title="Settings"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default Toolbar;