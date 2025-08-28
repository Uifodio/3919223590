const { app, BrowserWindow, Menu, dialog, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs-extra');
const Store = require('electron-store');
const isDev = require('electron').app.isPackaged ? false : true;

// Initialize persistent storage
const store = new Store({
  name: 'anora_editor_session',
  defaults: {
    recentFiles: [],
    openTabs: [],
    windowBounds: { width: 800, height: 600 },
    alwaysOnTop: false,
    fullscreen: false
  }
});

let mainWindow;
let isAlwaysOnTop = false;
let isFullscreen = false;

function createWindow() {
  const savedBounds = store.get('windowBounds');
  
  mainWindow = new BrowserWindow({
    width: savedBounds.width || 800,
    height: savedBounds.height || 600,
    minWidth: 400,
    minHeight: 300,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'),
    show: false,
    titleBarStyle: 'default',
    backgroundColor: '#1e1e1e'
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../build/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    createMenu();
  });

  // Save window bounds
  mainWindow.on('resize', () => {
    const bounds = mainWindow.getBounds();
    store.set('windowBounds', bounds);
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle file open requests
  mainWindow.webContents.on('will-navigate', (event) => {
    event.preventDefault();
  });
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New',
          accelerator: 'CmdOrCtrl+N',
          click: () => mainWindow.webContents.send('menu-action', 'new-file')
        },
        {
          label: 'Open',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openFile'],
              filters: [
                { name: 'All Files', extensions: ['*'] },
                { name: 'C# Files', extensions: ['cs'] },
                { name: 'Python Files', extensions: ['py'] },
                { name: 'JavaScript Files', extensions: ['js'] },
                { name: 'HTML Files', extensions: ['html', 'htm'] },
                { name: 'CSS Files', extensions: ['css'] },
                { name: 'JSON Files', extensions: ['json'] },
                { name: 'C/C++ Files', extensions: ['c', 'cpp', 'h', 'hpp'] },
                { name: 'Text Files', extensions: ['txt'] }
              ]
            });
            
            if (!result.canceled && result.filePaths.length > 0) {
              mainWindow.webContents.send('menu-action', 'open-file', result.filePaths[0]);
            }
          }
        },
        {
          label: 'Save',
          accelerator: 'CmdOrCtrl+S',
          click: () => mainWindow.webContents.send('menu-action', 'save-file')
        },
        {
          label: 'Save As',
          accelerator: 'CmdOrCtrl+Shift+S',
          click: async () => {
            const result = await dialog.showSaveDialog(mainWindow, {
              filters: [
                { name: 'All Files', extensions: ['*'] },
                { name: 'C# Files', extensions: ['cs'] },
                { name: 'Python Files', extensions: ['py'] },
                { name: 'JavaScript Files', extensions: ['js'] },
                { name: 'HTML Files', extensions: ['html'] },
                { name: 'CSS Files', extensions: ['css'] },
                { name: 'JSON Files', extensions: ['json'] },
                { name: 'C/C++ Files', extensions: ['c', 'cpp', 'h'] },
                { name: 'Text Files', extensions: ['txt'] }
              ]
            });
            
            if (!result.canceled) {
              mainWindow.webContents.send('menu-action', 'save-as', result.filePath);
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Open Recent',
          submenu: []
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        {
          label: 'Undo',
          accelerator: 'CmdOrCtrl+Z',
          click: () => mainWindow.webContents.send('menu-action', 'undo')
        },
        {
          label: 'Redo',
          accelerator: 'CmdOrCtrl+Y',
          click: () => mainWindow.webContents.send('menu-action', 'redo')
        },
        { type: 'separator' },
        {
          label: 'Cut',
          accelerator: 'CmdOrCtrl+X',
          click: () => mainWindow.webContents.send('menu-action', 'cut')
        },
        {
          label: 'Copy',
          accelerator: 'CmdOrCtrl+C',
          click: () => mainWindow.webContents.send('menu-action', 'copy')
        },
        {
          label: 'Paste',
          accelerator: 'CmdOrCtrl+V',
          click: () => mainWindow.webContents.send('menu-action', 'paste')
        },
        {
          label: 'Select All',
          accelerator: 'CmdOrCtrl+A',
          click: () => mainWindow.webContents.send('menu-action', 'select-all')
        },
        { type: 'separator' },
        {
          label: 'Find',
          accelerator: 'CmdOrCtrl+F',
          click: () => mainWindow.webContents.send('menu-action', 'find')
        },
        {
          label: 'Replace',
          accelerator: 'CmdOrCtrl+H',
          click: () => mainWindow.webContents.send('menu-action', 'replace')
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Always on Top',
          type: 'checkbox',
          checked: isAlwaysOnTop,
          click: () => {
            isAlwaysOnTop = !isAlwaysOnTop;
            mainWindow.setAlwaysOnTop(isAlwaysOnTop);
            store.set('alwaysOnTop', isAlwaysOnTop);
            mainWindow.webContents.send('menu-action', 'always-on-top', isAlwaysOnTop);
          }
        },
        {
          label: 'Fullscreen',
          accelerator: 'F11',
          click: () => {
            isFullscreen = !isFullscreen;
            mainWindow.setFullScreen(isFullscreen);
            store.set('fullscreen', isFullscreen);
            mainWindow.webContents.send('menu-action', 'fullscreen', isFullscreen);
          }
        }
      ]
    },
    {
      label: 'Window',
      submenu: [
        {
          label: 'New Tab',
          accelerator: 'CmdOrCtrl+T',
          click: () => mainWindow.webContents.send('menu-action', 'new-tab')
        },
        {
          label: 'Close Tab',
          accelerator: 'CmdOrCtrl+W',
          click: () => mainWindow.webContents.send('menu-action', 'close-tab')
        },
        {
          label: 'Close Others',
          click: () => mainWindow.webContents.send('menu-action', 'close-others')
        },
        {
          label: 'Reopen Closed Tab',
          accelerator: 'CmdOrCtrl+Shift+T',
          click: () => mainWindow.webContents.send('menu-action', 'reopen-closed-tab')
        }
      ]
    },
    {
      label: 'Navigate',
      submenu: [
        {
          label: 'Go to Line',
          accelerator: 'CmdOrCtrl+G',
          click: () => mainWindow.webContents.send('menu-action', 'go-to-line')
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC handlers
ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const content = await fs.readFile(filePath, 'utf8');
    return { success: true, content, filePath };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    await fs.writeFile(filePath, content, 'utf8');
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-recent-files', () => {
  return store.get('recentFiles', []);
});

ipcMain.handle('add-recent-file', (event, filePath) => {
  const recentFiles = store.get('recentFiles', []);
  const newRecentFiles = [filePath, ...recentFiles.filter(f => f !== filePath)].slice(0, 10);
  store.set('recentFiles', newRecentFiles);
  return newRecentFiles;
});

ipcMain.handle('save-session', (event, sessionData) => {
  store.set('openTabs', sessionData);
  return true;
});

ipcMain.handle('load-session', () => {
  return store.get('openTabs', []);
});

// App event handlers
app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  // Save current session before quitting
  if (mainWindow) {
    mainWindow.webContents.send('save-session');
  }
});