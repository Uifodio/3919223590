import { contextBridge, ipcRenderer } from 'electron';

export type FileEntry = { name: string; fullPath: string; isDirectory: boolean; size: number; mtimeMs: number };

const api = {
  openFolder: () => ipcRenderer.invoke('dialog:openFolder') as Promise<string | null>,
  list: (dir: string) => ipcRenderer.invoke('fs:list', dir) as Promise<FileEntry[]>,
  copy: (sources: string[], targetDir: string) => ipcRenderer.invoke('fs:copy', sources, targetDir) as Promise<boolean>,
  trash: (items: string[]) => ipcRenderer.invoke('fs:trash', items) as Promise<boolean>,
  startDrag: (files: string[]) => ipcRenderer.invoke('drag:start', files) as Promise<void>,
  zipList: (zipPath: string, innerDir: string) => ipcRenderer.invoke('zip:list', zipPath, innerDir) as Promise<FileEntry[]>,
  zipExtractTemp: (zipPath: string, innerPath: string) => ipcRenderer.invoke('zip:extractTemp', zipPath, innerPath) as Promise<string>,
  zipWriteFromFile: (zipPath: string, innerPath: string, sourceFile: string) => ipcRenderer.invoke('zip:writeFromFile', zipPath, innerPath, sourceFile) as Promise<boolean>
};

declare global {
  interface Window { api: typeof api }
}

contextBridge.exposeInMainWorld('api', api);