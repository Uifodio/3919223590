const { contextBridge, ipcRenderer } = require('electron')

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  openFile: () => ipcRenderer.invoke('open-file'),
  saveFile: () => ipcRenderer.invoke('save-file'),
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),
  setAlwaysOnTop: (value) => ipcRenderer.invoke('set-always-on-top', value),
  setFullscreen: (value) => ipcRenderer.invoke('set-fullscreen', value),
  getShortcuts: () => ipcRenderer.invoke('get-shortcuts'),
  onFileOpened: (callback) => ipcRenderer.on('file-opened', callback)
})