import React, { useState, useEffect } from 'react';
import { Folder, FolderOpen, ChevronRight, ChevronDown, HardDrive } from 'lucide-react';
import { cn } from '../utils/cn';

const FileTree = ({ currentPath, onFolderClick, showHiddenFiles }) => {
  const [treeData, setTreeData] = useState([]);
  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDrives();
  }, []);

  const loadDrives = async () => {
    try {
      const result = await window.electronAPI.getDrives();
      if (result.success) {
        const drives = result.drives.map(drive => ({
          name: drive.letter,
          path: drive.letter,
          type: 'drive',
          children: []
        }));
        setTreeData(drives);
      }
    } catch (error) {
      console.error('Failed to load drives:', error);
    }
  };

  const loadFolderChildren = async (folderPath) => {
    try {
      const result = await window.electronAPI.readDirectory(folderPath);
      if (result.success) {
        const children = [
          ...result.folders.map(folder => ({
            name: folder.name,
            path: folder.path,
            type: 'folder',
            children: []
          }))
        ];

        // Filter hidden files if needed
        const filteredChildren = showHiddenFiles 
          ? children 
          : children.filter(item => !item.name.startsWith('.'));

        return filteredChildren;
      }
    } catch (error) {
      console.error('Failed to load folder children:', error);
    }
    return [];
  };

  const toggleFolder = async (folderPath) => {
    const newExpanded = new Set(expandedFolders);
    
    if (newExpanded.has(folderPath)) {
      newExpanded.delete(folderPath);
    } else {
      newExpanded.add(folderPath);
      
      // Load children if not already loaded
      const folder = findFolderInTree(treeData, folderPath);
      if (folder && folder.children.length === 0) {
        setLoading(true);
        const children = await loadFolderChildren(folderPath);
        folder.children = children;
        setTreeData([...treeData]);
        setLoading(false);
      }
    }
    
    setExpandedFolders(newExpanded);
  };

  const findFolderInTree = (items, path) => {
    for (const item of items) {
      if (item.path === path) {
        return item;
      }
      if (item.children) {
        const found = findFolderInTree(item.children, path);
        if (found) return found;
      }
    }
    return null;
  };

  const renderTreeItem = (item, level = 0) => {
    const isExpanded = expandedFolders.has(item.path);
    const isSelected = currentPath === item.path;
    const hasChildren = item.type === 'folder' || item.type === 'drive';

    return (
      <div key={item.path}>
        <div
          className={cn(
            'folder-tree-item',
            isSelected && 'selected',
            'flex items-center gap-2'
          )}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => {
            if (hasChildren) {
              toggleFolder(item.path);
            }
            onFolderClick(item.path);
          }}
        >
          {hasChildren && (
            <div className="w-4 h-4 flex items-center justify-center">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3" />
              ) : (
                <ChevronRight className="w-3 h-3" />
              )}
            </div>
          )}
          
          {item.type === 'drive' ? (
            <HardDrive className="w-4 h-4 text-blue-500" />
          ) : isExpanded ? (
            <FolderOpen className="w-4 h-4 text-yellow-500" />
          ) : (
            <Folder className="w-4 h-4 text-yellow-500" />
          )}
          
          <span className="truncate">{item.name}</span>
        </div>
        
        {isExpanded && hasChildren && (
          <div>
            {item.children.map(child => renderTreeItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-2 border-b border-border">
        <h3 className="text-sm font-medium">Explorer</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2">
        {loading ? (
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="space-y-1">
            {treeData.map(item => renderTreeItem(item))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileTree;