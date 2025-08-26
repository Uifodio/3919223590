import { app, BrowserWindow, ipcMain, dialog, shell, nativeImage } from 'electron';
import path from 'node:path';
import fs from 'fs-extra';
import os from 'node:os';
import AdmZip from 'adm-zip';

let mainWindow: BrowserWindow | null = null;

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  if (!app.isPackaged) {
    await mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    await mainWindow.loadFile(path.join(__dirname, '../../dist/index.html'));
  }
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC: basic dialogs
ipcMain.handle('dialog:openFolder', async () => {
  const r = await dialog.showOpenDialog({ properties: ['openDirectory'] });
  if (r.canceled || r.filePaths.length === 0) return null;
  return r.filePaths[0];
});

// IPC: list directory entries
ipcMain.handle('fs:list', async (_e, dir: string) => {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const results = await Promise.all(entries.map(async (ent) => {
    const full = path.join(dir, ent.name);
    const stat = await fs.stat(full);
    return {
      name: ent.name,
      fullPath: full,
      isDirectory: ent.isDirectory(),
      size: stat.size,
      mtimeMs: stat.mtimeMs
    };
  }));
  return results.sort((a, b) => (a.isDirectory === b.isDirectory ? a.name.localeCompare(b.name) : a.isDirectory ? -1 : 1));
});

// IPC: copy with progress (simple)
ipcMain.handle('fs:copy', async (_e, sources: string[], targetDir: string) => {
  await fs.ensureDir(targetDir);
  for (const src of sources) {
    const base = path.basename(src);
    const dest = path.join(targetDir, base);
    if (await fs.pathExists(dest)) {
      await fs.copy(dest, dest + '.bak', { overwrite: true });
    }
    await fs.copy(src, dest, { overwrite: true, errorOnExist: false });
  }
  return true;
});

// IPC: delete to recycle bin
ipcMain.handle('fs:trash', async (_e, items: string[]) => {
  for (const it of items) {
    await shell.trashItem(it);
  }
  return true;
});

// IPC: start drag to external apps
ipcMain.handle('drag:start', async (e, filePaths: string[]) => {
  const win = BrowserWindow.fromWebContents(e.sender);
  if (!win) return;
  // Use a small transparent icon
  const icon = nativeImage.createEmpty();
  win.webContents.startDrag({
    file: filePaths[0],
    icon
  });
});

// IPC: ZIP list
ipcMain.handle('zip:list', async (_e, zipPath: string, innerDir: string) => {
  const zip = new AdmZip(zipPath);
  const entries = zip.getEntries();
  const prefix = innerDir.replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
  const results: any[] = [];
  const seen = new Set<string>();
  for (const ent of entries) {
    if (!ent.entryName.startsWith(prefix)) continue;
    const remainder = ent.entryName.slice(prefix.length).replace(/^\//, '');
    if (!remainder) continue;
    const parts = remainder.split('/');
    const first = parts[0];
    if (seen.has(first)) continue;
    seen.add(first);
    const isDir = parts.length > 1 || ent.isDirectory;
    results.push({ name: first.replace(/\/$/, ''), fullPath: path.join(zipPath, first), isDirectory: isDir, size: ent.header.size, mtimeMs: ent.header.time?.getTime?.() ?? Date.now() });
  }
  return results.sort((a, b) => (a.isDirectory === b.isDirectory ? a.name.localeCompare(b.name) : a.isDirectory ? -1 : 1));
});

// IPC: ZIP extract one to temp
ipcMain.handle('zip:extractTemp', async (_e, zipPath: string, innerPath: string) => {
  const zip = new AdmZip(zipPath);
  const tmpDir = path.join(os.tmpdir(), 'AAAFileManager', String(Date.now()));
  await fs.ensureDir(tmpDir);
  const fileName = path.basename(innerPath);
  const out = path.join(tmpDir, fileName);
  const entry = zip.getEntry(innerPath.replace(/\\/g, '/'));
  if (!entry) throw new Error('Entry not found');
  fs.writeFileSync(out, entry.getData());
  return out;
});

// IPC: ZIP write-back
ipcMain.handle('zip:writeFromFile', async (_e, zipPath: string, innerPath: string, sourceFile: string) => {
  await fs.copy(zipPath, zipPath + '.bak', { overwrite: true });
  const zip = new AdmZip(zipPath);
  const normalized = innerPath.replace(/\\/g, '/');
  zip.deleteFile(normalized);
  zip.addLocalFile(sourceFile, path.dirname(normalized), path.basename(normalized));
  zip.writeZip(zipPath);
  return true;
});