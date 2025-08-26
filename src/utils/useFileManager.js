import { useState, useCallback } from 'react';

export function useFileManager() {
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPath, setCurrentPath] = useState('');

  const loadDirectory = useCallback(async (path) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.readDirectory(path);
      if (result.success) {
        setFiles(result.files);
        setFolders(result.folders);
        setCurrentPath(path);
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const navigateTo = useCallback((path) => {
    loadDirectory(path);
  }, [loadDirectory]);

  const refresh = useCallback(() => {
    if (currentPath) {
      loadDirectory(currentPath);
    }
  }, [currentPath, loadDirectory]);

  const performOperation = useCallback(async (operation, source, destination = null) => {
    try {
      switch (operation) {
        case 'copy':
          return await window.electronAPI.copyFile(source, destination);
        case 'move':
          return await window.electronAPI.moveFile(source, destination);
        case 'delete':
          if (Array.isArray(source)) {
            const results = await Promise.all(
              source.map(path => window.electronAPI.deleteFile(path))
            );
            return { success: results.every(r => r.success) };
          } else {
            return await window.electronAPI.deleteFile(source);
          }
        case 'createDirectory':
          return await window.electronAPI.createDirectory(source);
        case 'rename':
          return await window.electronAPI.renameFile(source, destination);
        default:
          throw new Error(`Unknown operation: ${operation}`);
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  return {
    files,
    folders,
    loading,
    error,
    currentPath,
    navigateTo,
    refresh,
    performOperation
  };
}