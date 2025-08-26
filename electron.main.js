const { app, BrowserWindow, ipcMain, dialog, Menu, shell, clipboard } = require('electron');
const path = require('path');
const fs = require('fs-extra');
const { v4: uuidv4 } = require('uuid');

let mainWindow;
let windows = new Map();

function createWindow(windowId = 'main') {
  const isDev = process.env.NODE_ENV === 'development';
  const window = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'public/favicon.ico'),
    show: false,
    titleBarStyle: 'default',
    backgroundColor: '#1a1a1a'
  });

  window.webContents.on('did-finish-load', () => {
    window.show();
  });

  if (isDev) {
    window.loadURL('http://localhost:5173');
    window.webContents.openDevTools();
  } else {
    window.loadFile(path.join(__dirname, 'dist/index.html'));
  }

  // Handle window closed
  window.on('closed', () => {
    windows.delete(windowId);
    if (windowId === 'main' && windows.size === 0) {
      app.quit();
    }
  });

  // Enable drag and drop
  window.webContents.on('will-navigate', (event) => {
    event.preventDefault();
  });

  windows.set(windowId, window);
  return window;
}

// App event handlers
app.whenReady().then(() => {
  createWindow();
  createMenu();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Window',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            const windowId = uuidv4();
            createWindow(windowId);
          }
        },
        {
          label: 'Open Folder',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openDirectory']
            });
            if (!result.canceled) {
              mainWindow.webContents.send('open-folder', result.filePaths[0]);
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectall' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC handlers for file operations
ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const content = await fs.readFile(filePath, 'utf8');
    return { success: true, content };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    // Create backup before writing
    if (await fs.pathExists(filePath)) {
      const backupPath = `${filePath}.bak`;
      await fs.copy(filePath, backupPath);
    }
    
    await fs.writeFile(filePath, content, 'utf8');
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('read-directory', async (event, dirPath) => {
  try {
    const items = await fs.readdir(dirPath, { withFileTypes: true });
    const files = [];
    const folders = [];

    for (const item of items) {
      const fullPath = path.join(dirPath, item.name);
      const stats = await fs.stat(fullPath);
      
      const fileInfo = {
        name: item.name,
        path: fullPath,
        size: stats.size,
        modified: stats.mtime,
        isDirectory: item.isDirectory(),
        isHidden: item.name.startsWith('.')
      };

      if (item.isDirectory()) {
        folders.push(fileInfo);
      } else {
        files.push(fileInfo);
      }
    }

    return {
      success: true,
      folders: folders.sort((a, b) => a.name.localeCompare(b.name)),
      files: files.sort((a, b) => a.name.localeCompare(b.name))
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('copy-file', async (event, source, destination) => {
  try {
    await fs.copy(source, destination);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('move-file', async (event, source, destination) => {
  try {
    await fs.move(source, destination);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('delete-file', async (event, filePath) => {
  try {
    await fs.remove(filePath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('create-directory', async (event, dirPath) => {
  try {
    await fs.ensureDir(dirPath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('rename-file', async (event, oldPath, newPath) => {
  try {
    await fs.move(oldPath, newPath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-drives', async () => {
  try {
    if (process.platform === 'win32') {
      const { exec } = require('child_process');
      return new Promise((resolve) => {
        exec('wmic logicaldisk get size,freespace,caption', (error, stdout) => {
          if (error) {
            resolve({ success: false, error: error.message });
            return;
          }
          
          const lines = stdout.trim().split('\n').slice(1);
          const drives = lines.map(line => {
            const parts = line.trim().split(/\s+/);
            return {
              letter: parts[0],
              freeSpace: parseInt(parts[1]) || 0,
              totalSize: parseInt(parts[2]) || 0
            };
          });
          
          resolve({ success: true, drives });
        });
      });
    } else {
      // For Linux/Mac, return root directory
      return { success: true, drives: [{ letter: '/', freeSpace: 0, totalSize: 0 }] };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('open-external', async (event, filePath) => {
  try {
    await shell.openPath(filePath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('show-in-folder', async (event, filePath) => {
  try {
    await shell.showItemInFolder(filePath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Cross-window clipboard
ipcMain.handle('set-clipboard', async (event, data) => {
  try {
    clipboard.writeText(JSON.stringify(data));
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-clipboard', async () => {
  try {
    const text = clipboard.readText();
    if (text) {
      return { success: true, data: JSON.parse(text) };
    }
    return { success: true, data: null };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Settings management
ipcMain.handle('load-settings', async () => {
  try {
    const settingsPath = path.join(app.getPath('userData'), 'settings.json');
    if (await fs.pathExists(settingsPath)) {
      const settings = await fs.readJson(settingsPath);
      return { success: true, settings };
    }
    return { success: true, settings: getDefaultSettings() };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('save-settings', async (event, settings) => {
  try {
    const settingsPath = path.join(app.getPath('userData'), 'settings.json');
    await fs.writeJson(settingsPath, settings, { spaces: 2 });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

function getDefaultSettings() {
  return {
    theme: 'dark',
    fontSize: 14,
    showHiddenFiles: false,
    autoSave: true,
    autoSaveInterval: 30000,
    editor: {
      fontSize: 14,
      theme: 'vs-dark',
      wordWrap: 'on',
      minimap: { enabled: true },
      lineNumbers: 'on'
    },
    fileManager: {
      viewMode: 'list',
      sortBy: 'name',
      sortOrder: 'asc'
    }
  };
}