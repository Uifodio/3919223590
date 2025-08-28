const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');

const store = new Store();

let mainWindow;
let isDev = process.env.NODE_ENV === 'development';

function getSettings() {
  return {
    alwaysOnTop: !!store.get('view.alwaysOnTop', false),
    fullscreen: !!store.get('view.fullscreen', false),
    recentFiles: store.get('recent.files', [])
  };
}

function pushRecentFile(filePath) {
  if (!filePath) return;
  const existing = store.get('recent.files', []);
  const filtered = existing.filter(f => f !== filePath);
  filtered.unshift(filePath);
  const trimmed = filtered.slice(0, 10);
  store.set('recent.files', trimmed);
  buildMenu();
}

function createWindow() {
  const settings = getSettings();
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 400,
    minHeight: 300,
    alwaysOnTop: settings.alwaysOnTop,
    fullscreen: settings.fullscreen,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'),
    titleBarStyle: 'default',
    show: false
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
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external file opening
  mainWindow.webContents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });

  buildMenu();
}

function buildMenu() {
  const settings = getSettings();
  const recent = settings.recentFiles || [];

  const recentSubmenu = recent.length > 0
    ? recent.map(file => ({
        label: file,
        click: () => {
          if (mainWindow) mainWindow.webContents.send('open-file-path', file);
        }
      }))
    : [{ label: 'No Recent Files', enabled: false }];

  const template = [
    {
      label: 'File',
      submenu: [
        { label: 'New', accelerator: 'CmdOrCtrl+N', click: () => mainWindow.webContents.send('menu-new-file') },
        { label: 'Open', accelerator: 'CmdOrCtrl+O', click: () => mainWindow.webContents.send('menu-open-file') },
        { label: 'Save', accelerator: 'CmdOrCtrl+S', click: () => mainWindow.webContents.send('menu-save-file') },
        { label: 'Save As', accelerator: 'CmdOrCtrl+Shift+S', click: () => mainWindow.webContents.send('menu-save-as') },
        { type: 'separator' },
        { label: 'Open Recent', submenu: [
          ...recentSubmenu,
          { type: 'separator' },
          { label: 'Clear Recent', click: () => { store.set('recent.files', []); buildMenu(); } }
        ] },
        { type: 'separator' },
        { label: 'Exit', accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q', click: () => app.quit() }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { label: 'Undo', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: 'Redo', accelerator: 'CmdOrCtrl+Y', role: 'redo' },
        { type: 'separator' },
        { label: 'Cut', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: 'Copy', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: 'Paste', accelerator: 'CmdOrCtrl+V', role: 'paste' },
        { type: 'separator' },
        { label: 'Select All', accelerator: 'CmdOrCtrl+A', role: 'selectAll' },
        { type: 'separator' },
        { label: 'Find', accelerator: 'CmdOrCtrl+F', click: () => mainWindow.webContents.send('menu-find') },
        { label: 'Replace', accelerator: 'CmdOrCtrl+H', click: () => mainWindow.webContents.send('menu-replace') }
      ]
    },
    {
      label: 'View',
      submenu: [
        { label: 'Always on Top', type: 'checkbox', checked: settings.alwaysOnTop, click: (mi) => { mainWindow.setAlwaysOnTop(mi.checked); store.set('view.alwaysOnTop', mi.checked); mainWindow.webContents.send('view-always-on-top-changed', mi.checked); } },
        { label: 'Fullscreen', accelerator: 'F11', type: 'checkbox', checked: settings.fullscreen, click: (mi) => { const val = !!mi.checked; mainWindow.setFullScreen(val); store.set('view.fullscreen', val); mainWindow.webContents.send('view-fullscreen-changed', val); } }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { label: 'New Tab', accelerator: 'CmdOrCtrl+T', click: () => mainWindow.webContents.send('menu-new-tab') },
        { label: 'Close Tab', accelerator: 'CmdOrCtrl+W', click: () => mainWindow.webContents.send('menu-close-tab') },
        { label: 'Close Others', click: () => mainWindow.webContents.send('menu-close-others') },
        { label: 'Reopen Closed Tab', accelerator: 'CmdOrCtrl+Shift+T', click: () => mainWindow.webContents.send('menu-reopen-tab') }
      ]
    },
    {
      label: 'Navigate',
      submenu: [
        { label: 'Go to Line', accelerator: 'CmdOrCtrl+G', click: () => mainWindow.webContents.send('menu-go-to-line') }
      ]
    }
  ];

  if (isDev) {
    template.push({ label: 'Developer', submenu: [
      { label: 'Toggle DevTools', accelerator: 'F12', click: () => mainWindow.webContents.toggleDevTools() },
      { label: 'Reload', accelerator: 'CmdOrCtrl+R', click: () => mainWindow.reload() }
    ]});
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event handlers
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers for file dialogs and IO
ipcMain.handle('open-file-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'All Files', extensions: ['*'] },
      { name: 'C#', extensions: ['cs'] },
      { name: 'JavaScript', extensions: ['js', 'jsx', 'ts', 'tsx'] },
      { name: 'Python', extensions: ['py'] },
      { name: 'HTML', extensions: ['html', 'htm'] },
      { name: 'CSS', extensions: ['css'] },
      { name: 'JSON', extensions: ['json'] },
      { name: 'C/C++', extensions: ['c', 'cpp', 'h', 'hpp'] },
      { name: 'Text', extensions: ['txt'] }
    ]
  });
  if (result.canceled || !result.filePaths || result.filePaths.length === 0) return result;
  pushRecentFile(result.filePaths[0]);
  return result;
});

ipcMain.handle('save-file-dialog', async (event, defaultPath) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultPath || 'untitled.txt',
    filters: [
      { name: 'All Files', extensions: ['*'] },
      { name: 'C#', extensions: ['cs'] },
      { name: 'JavaScript', extensions: ['js'] },
      { name: 'Python', extensions: ['py'] },
      { name: 'HTML', extensions: ['html'] },
      { name: 'CSS', extensions: ['css'] },
      { name: 'JSON', extensions: ['json'] },
      { name: 'C/C++', extensions: ['c', 'cpp', 'h'] },
      { name: 'Text', extensions: ['txt'] }
    ]
  });
  if (!result.canceled && result.filePath) pushRecentFile(result.filePath);
  return result;
});

ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const content = await fs.promises.readFile(filePath, 'utf8');
    pushRecentFile(filePath);
    return { success: true, content };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    await fs.promises.writeFile(filePath, content, 'utf8');
    pushRecentFile(filePath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Settings and window control IPC
ipcMain.handle('settings:get', async () => getSettings());
ipcMain.handle('settings:set', async (event, partial) => {
  if (partial && typeof partial === 'object') {
    if (typeof partial.alwaysOnTop === 'boolean') store.set('view.alwaysOnTop', partial.alwaysOnTop);
    if (typeof partial.fullscreen === 'boolean') store.set('view.fullscreen', partial.fullscreen);
  }
  buildMenu();
  return getSettings();
});

ipcMain.on('window:setAlwaysOnTop', (event, value) => {
  const val = !!value;
  store.set('view.alwaysOnTop', val);
  if (mainWindow) mainWindow.setAlwaysOnTop(val);
  buildMenu();
});

ipcMain.on('window:setFullscreen', (event, value) => {
  const val = !!value;
  store.set('view.fullscreen', val);
  if (mainWindow) mainWindow.setFullScreen(val);
  buildMenu();
});

// Handle file association on Windows
if (process.platform === 'win32') {
  const gotTheLock = app.requestSingleInstanceLock();
  
  if (!gotTheLock) {
    app.quit();
  } else {
    app.on('second-instance', (event, commandLine, workingDirectory) => {
      if (mainWindow) {
        if (mainWindow.isMinimized()) mainWindow.restore();
        mainWindow.focus();
        
        // Handle file argument
        if (commandLine.length > 1) {
          const filePath = commandLine[1];
          mainWindow.webContents.send('open-file-path', filePath);
        }
      }
    });
    
    // Handle file argument on first instance
    if (process.argv.length > 1) {
      const filePath = process.argv[1];
      app.whenReady().then(() => {
        mainWindow.webContents.send('open-file-path', filePath);
      });
    }
  }
}