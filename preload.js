const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),
  readDirectory: (dirPath) => ipcRenderer.invoke('read-directory', dirPath),
  copyFile: (source, destination) => ipcRenderer.invoke('copy-file', source, destination),
  moveFile: (source, destination) => ipcRenderer.invoke('move-file', source, destination),
  deleteFile: (filePath) => ipcRenderer.invoke('delete-file', filePath),
  createDirectory: (dirPath) => ipcRenderer.invoke('create-directory', dirPath),
  renameFile: (oldPath, newPath) => ipcRenderer.invoke('rename-file', oldPath, newPath),
  
  // System operations
  getDrives: () => ipcRenderer.invoke('get-drives'),
  openExternal: (filePath) => ipcRenderer.invoke('open-external', filePath),
  showInFolder: (filePath) => ipcRenderer.invoke('show-in-folder', filePath),
  
  // Clipboard operations
  setClipboard: (data) => ipcRenderer.invoke('set-clipboard', data),
  getClipboard: () => ipcRenderer.invoke('get-clipboard'),
  
  // Settings
  loadSettings: () => ipcRenderer.invoke('load-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  
  // Events
  onOpenFolder: (callback) => ipcRenderer.on('open-folder', callback),
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});