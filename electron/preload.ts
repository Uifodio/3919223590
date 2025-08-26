import { contextBridge, ipcRenderer } from 'electron'

// --------- Expose some APIs to the Renderer process ---------
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  saveFile: (options: any) => ipcRenderer.invoke('dialog:saveFile', options),
  
  // File system operations
  readFile: (filePath: string) => ipcRenderer.invoke('fs:readFile', filePath),
  writeFile: (filePath: string, content: string) => ipcRenderer.invoke('fs:writeFile', filePath, content),
  readDir: (dirPath: string) => ipcRenderer.invoke('fs:readDir', dirPath),
  createDir: (dirPath: string) => ipcRenderer.invoke('fs:createDir', dirPath),
  deleteFile: (filePath: string) => ipcRenderer.invoke('fs:deleteFile', filePath),
  deleteDir: (dirPath: string) => ipcRenderer.invoke('fs:deleteDir', dirPath),
  copyFile: (source: string, dest: string) => ipcRenderer.invoke('fs:copyFile', source, dest),
  moveFile: (source: string, dest: string) => ipcRenderer.invoke('fs:moveFile', source, dest),
  renameFile: (oldPath: string, newPath: string) => ipcRenderer.invoke('fs:renameFile', oldPath, newPath),
  
  // ZIP operations
  extractZip: (zipPath: string, extractPath: string) => ipcRenderer.invoke('zip:extract', zipPath, extractPath),
  createZip: (zipPath: string, sourcePaths: string[]) => ipcRenderer.invoke('zip:create', zipPath, sourcePaths),
  addToZip: (zipPath: string, filePath: string, fileName: string) => ipcRenderer.invoke('zip:add', zipPath, filePath, fileName),
  removeFromZip: (zipPath: string, fileName: string) => ipcRenderer.invoke('zip:remove', zipPath, fileName),
  
  // System operations
  getDrives: () => ipcRenderer.invoke('system:getDrives'),
  getSpecialFolders: () => ipcRenderer.invoke('system:getSpecialFolders'),
  getFileInfo: (filePath: string) => ipcRenderer.invoke('system:getFileInfo', filePath),
  
  // Event listeners
  onFileOpen: (callback: (filePath: string) => void) => {
    ipcRenderer.on('file:open', (_, filePath) => callback(filePath))
  },
  onFolderOpen: (callback: (folderPath: string) => void) => {
    ipcRenderer.on('folder:open', (_, folderPath) => callback(folderPath))
  },
  
  // Remove listeners
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel)
  }
})

// Type definitions for the exposed APIs
declare global {
  interface Window {
    electronAPI: {
      openDirectory: () => Promise<{ canceled: boolean; filePaths: string[] }>
      openFile: () => Promise<{ canceled: boolean; filePaths: string[] }>
      saveFile: (options: any) => Promise<{ canceled: boolean; filePath?: string }>
      readFile: (filePath: string) => Promise<string>
      writeFile: (filePath: string, content: string) => Promise<boolean>
      readDir: (dirPath: string) => Promise<any[]>
      createDir: (dirPath: string) => Promise<boolean>
      deleteFile: (filePath: string) => Promise<boolean>
      deleteDir: (dirPath: string) => Promise<boolean>
      copyFile: (source: string, dest: string) => Promise<boolean>
      moveFile: (source: string, dest: string) => Promise<boolean>
      renameFile: (oldPath: string, newPath: string) => Promise<boolean>
      extractZip: (zipPath: string, extractPath: string) => Promise<boolean>
      createZip: (zipPath: string, sourcePaths: string[]) => Promise<boolean>
      addToZip: (zipPath: string, filePath: string, fileName: string) => Promise<boolean>
      removeFromZip: (zipPath: string, fileName: string) => Promise<boolean>
      getDrives: () => Promise<string[]>
      getSpecialFolders: () => Promise<string[]>
      getFileInfo: (filePath: string) => Promise<any>
      onFileOpen: (callback: (filePath: string) => void) => void
      onFolderOpen: (callback: (folderPath: string) => void) => void
      removeAllListeners: (channel: string) => void
    }
  }
}