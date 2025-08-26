import React, { useEffect, useRef } from 'react';
import { 
  Copy, 
  Scissors, 
  Trash2, 
  Edit, 
  Download, 
  ExternalLink, 
  FolderOpen,
  FileText,
  Settings
} from 'lucide-react';

const ContextMenu = ({ x, y, file, onClose, onOperation, currentPath }) => {
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const handleOperation = (operation) => {
    if (file) {
      onOperation(operation, file.path);
    }
    onClose();
  };

  const openWithDefault = async () => {
    if (file) {
      await window.electronAPI.openExternal(file.path);
    }
    onClose();
  };

  const showInFolder = async () => {
    if (file) {
      await window.electronAPI.showInFolder(file.path);
    }
    onClose();
  };

  const copyPath = () => {
    if (file) {
      navigator.clipboard.writeText(file.path);
    }
    onClose();
  };

  return (
    <div
      ref={menuRef}
      className="context-menu"
      style={{
        left: x,
        top: y,
        position: 'fixed'
      }}
    >
      {file && (
        <>
          <div className="context-menu-item" onClick={() => handleOperation('copy')}>
            <Copy className="w-4 h-4 mr-2" />
            Copy
          </div>
          
          <div className="context-menu-item" onClick={() => handleOperation('cut')}>
            <Scissors className="w-4 h-4 mr-2" />
            Cut
          </div>
          
          <div className="context-menu-item" onClick={() => handleOperation('delete')}>
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </div>
          
          <div className="border-t border-border my-1"></div>
          
          {!file.isDirectory && (
            <div className="context-menu-item" onClick={() => handleOperation('edit')}>
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </div>
          )}
          
          <div className="context-menu-item" onClick={openWithDefault}>
            <ExternalLink className="w-4 h-4 mr-2" />
            Open with Default
          </div>
          
          <div className="context-menu-item" onClick={showInFolder}>
            <FolderOpen className="w-4 h-4 mr-2" />
            Show in Folder
          </div>
          
          <div className="context-menu-item" onClick={copyPath}>
            <FileText className="w-4 h-4 mr-2" />
            Copy Path
          </div>
        </>
      )}
      
      {!file && (
        <>
          <div className="context-menu-item" onClick={() => handleOperation('paste')}>
            <Copy className="w-4 h-4 mr-2" />
            Paste
          </div>
          
          <div className="border-t border-border my-1"></div>
          
          <div className="context-menu-item" onClick={() => handleOperation('createDirectory')}>
            <FolderOpen className="w-4 h-4 mr-2" />
            New Folder
          </div>
          
          <div className="context-menu-item" onClick={() => handleOperation('createFile')}>
            <FileText className="w-4 h-4 mr-2" />
            New File
          </div>
        </>
      )}
    </div>
  );
};

export default ContextMenu;