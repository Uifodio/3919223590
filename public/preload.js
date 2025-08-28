const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  saveFileDialog: (defaultPath) => ipcRenderer.invoke('save-file-dialog', defaultPath),
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),
  
  // Settings and window controls
  getSettings: () => ipcRenderer.invoke('settings:get'),
  setSettings: (partial) => ipcRenderer.invoke('settings:set', partial),
  setAlwaysOnTop: (value) => ipcRenderer.send('window:setAlwaysOnTop', value),
  setFullscreen: (value) => ipcRenderer.send('window:setFullscreen', value),
  
  // Menu event listeners
  onMenuNewFile: (callback) => ipcRenderer.on('menu-new-file', callback),
  onMenuOpenFile: (callback) => ipcRenderer.on('menu-open-file', callback),
  onMenuSaveFile: (callback) => ipcRenderer.on('menu-save-file', callback),
  onMenuSaveAs: (callback) => ipcRenderer.on('menu-save-as', callback),
  onMenuNewTab: (callback) => ipcRenderer.on('menu-new-tab', callback),
  onMenuCloseTab: (callback) => ipcRenderer.on('menu-close-tab', callback),
  onMenuCloseOthers: (callback) => ipcRenderer.on('menu-close-others', callback),
  onMenuReopenTab: (callback) => ipcRenderer.on('menu-reopen-tab', callback),
  onMenuFind: (callback) => ipcRenderer.on('menu-find', callback),
  onMenuReplace: (callback) => ipcRenderer.on('menu-replace', callback),
  onMenuGoToLine: (callback) => ipcRenderer.on('menu-go-to-line', callback),
  onOpenFilePath: (callback) => ipcRenderer.on('open-file-path', callback),
  onAlwaysOnTopChanged: (callback) => ipcRenderer.on('view-always-on-top-changed', (e, v) => callback(v)),
  onFullscreenChanged: (callback) => ipcRenderer.on('view-fullscreen-changed', (e, v) => callback(v)),
  
  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});