const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Example: send a message to the main process
  sendMessage: (message) => ipcRenderer.send('message', message),
  
  // Example: receive a message from the main process
  onMessage: (callback) => ipcRenderer.on('message', callback),
  
  // Example: get app version
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // Example: platform info
  getPlatform: () => process.platform
});