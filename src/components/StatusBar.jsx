import React from 'react';
import { File, Folder } from 'lucide-react';

const StatusBar = ({ selectedCount, totalCount, currentPath }) => {
  return (
    <div className="status-bar">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs">
            {selectedCount > 0 ? `${selectedCount} selected` : `${totalCount} items`}
          </span>
        </div>
        
        <div className="flex items-center gap-1 text-xs">
          <Folder className="w-3 h-3" />
          <span>Folders</span>
        </div>
        
        <div className="flex items-center gap-1 text-xs">
          <File className="w-3 h-3" />
          <span>Files</span>
        </div>
      </div>
      
      <div className="text-xs truncate max-w-md">
        {currentPath}
      </div>
    </div>
  );
};

export default StatusBar;