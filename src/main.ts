import { app, BrowserWindow, Menu, ipcMain, dialog, shell, clipboard, globalShortcut, screen } from 'electron';
import * as path from 'path';
import * as fs from 'fs-extra';
import Store from 'electron-store';

// Initialize persistent storage
const store = new Store();

// Global reference to window objects
const windows = new Map<number, BrowserWindow>();

// App configuration
const isDev = process.env.NODE_ENV === 'development';
const isMac = process.platform === 'darwin';

interface AppConfig {
  theme: 'dark' | 'light';
  fontSize: number;
  autoSave: boolean;
  showHiddenFiles: boolean;
  defaultPath: string;
  recentPaths: string[];
  maxRecentPaths: number;
}

const defaultConfig: AppConfig = {
  theme: 'dark',
  fontSize: 14,
  autoSave: true,
  showHiddenFiles: false,
  defaultPath: process.env.USERPROFILE || process.env.HOME || 'C:\\',
  recentPaths: [],
  maxRecentPaths: 10
};

// Load or create config
let config: AppConfig = store.get('config', defaultConfig) as AppConfig;

function createWindow(filePath?: string): BrowserWindow {
  // Get primary display size
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  // Create the browser window
  const mainWindow = new BrowserWindow({
    width: Math.min(1400, width * 0.9),
    height: Math.min(900, height * 0.9),
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      webSecurity: false // Allow file:// URLs for local development
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    show: false,
    titleBarStyle: isMac ? 'hiddenInset' : 'default',
    backgroundColor: config.theme === 'dark' ? '#1e1e1e' : '#ffffff'
  });

  // Load the app
  if (isDev) {
    mainWindow.loadFile(path.join(__dirname, '../src/renderer/index.html'));
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../src/renderer/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Send initial config to renderer
    mainWindow.webContents.send('config-loaded', config);
    
    // Send initial path if provided
    if (filePath) {
      mainWindow.webContents.send('navigate-to', filePath);
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    windows.delete(mainWindow.id);
  });

  // Store window reference
  windows.set(mainWindow.id, mainWindow);

  return mainWindow;
}

function createMenu(): Menu {
  const template: Electron.MenuItemConstructorOptions[] = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Window',
          accelerator: 'CmdOrCtrl+N',
          click: () => createWindow()
        },
        {
          label: 'Open File',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog({
              properties: ['openFile', 'multiSelections']
            });
            if (!result.canceled && result.filePaths.length > 0) {
              const focusedWindow = BrowserWindow.getFocusedWindow();
              if (focusedWindow) {
                focusedWindow.webContents.send('open-files', result.filePaths);
              }
            }
          }
        },
        {
          label: 'Open Folder',
          accelerator: 'CmdOrCtrl+Shift+O',
          click: async () => {
            const result = await dialog.showOpenDialog({
              properties: ['openDirectory']
            });
            if (!result.canceled && result.filePaths.length > 0) {
              const focusedWindow = BrowserWindow.getFocusedWindow();
              if (focusedWindow) {
                focusedWindow.webContents.send('navigate-to', result.filePaths[0]);
              }
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Save',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            const focusedWindow = BrowserWindow.getFocusedWindow();
            if (focusedWindow) {
              focusedWindow.webContents.send('save-file');
            }
          }
        },
        {
          label: 'Save As',
          accelerator: 'CmdOrCtrl+Shift+S',
          click: () => {
            const focusedWindow = BrowserWindow.getFocusedWindow();
            if (focusedWindow) {
              focusedWindow.webContents.send('save-file-as');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: isMac ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo', label: 'Undo' },
        { role: 'redo', label: 'Redo' },
        { type: 'separator' },
        { role: 'cut', label: 'Cut' },
        { role: 'copy', label: 'Copy' },
        { role: 'paste', label: 'Paste' },
        { role: 'selectall', label: 'Select All' },
        { type: 'separator' },
        {
          label: 'Find',
          accelerator: 'CmdOrCtrl+F',
          click: () => {
            const focusedWindow = BrowserWindow.getFocusedWindow();
            if (focusedWindow) {
              focusedWindow.webContents.send('show-find');
            }
          }
        },
        {
          label: 'Replace',
          accelerator: 'CmdOrCtrl+H',
          click: () => {
            const focusedWindow = BrowserWindow.getFocusedWindow();
            if (focusedWindow) {
              focusedWindow.webContents.send('show-replace');
            }
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload', label: 'Reload' },
        { role: 'forceReload', label: 'Force Reload' },
        { role: 'toggleDevTools', label: 'Toggle Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Actual Size' },
        { role: 'zoomIn', label: 'Zoom In' },
        { role: 'zoomOut', label: 'Zoom Out' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Toggle Full Screen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize', label: 'Minimize' },
        { role: 'close', label: 'Close' },
        { type: 'separator' },
        {
          label: 'New Window',
          accelerator: 'CmdOrCtrl+Shift+N',
          click: () => createWindow()
        }
      ]
    },
    {
      label: 'Tools',
      submenu: [
        {
          label: 'Settings',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            const focusedWindow = BrowserWindow.getFocusedWindow();
            if (focusedWindow) {
              focusedWindow.webContents.send('open-settings');
            }
          }
        },
        {
          label: 'Terminal',
          accelerator: 'Ctrl+`',
          click: () => {
            const focusedWindow = BrowserWindow.getFocusedWindow();
            if (focusedWindow) {
              focusedWindow.webContents.send('toggle-terminal');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Show Hidden Files',
          type: 'checkbox',
          checked: config.showHiddenFiles,
          click: (menuItem) => {
            config.showHiddenFiles = menuItem.checked;
            store.set('config', config);
            const focusedWindow = BrowserWindow.getFocusedWindow();
            if (focusedWindow) {
              focusedWindow.webContents.send('config-updated', config);
            }
          }
        }
      ]
    }
  ];

  // Add Help menu for non-Mac platforms
  if (!isMac) {
    template.push({
      label: 'Help',
      submenu: [
        {
          label: 'About Nova Explorer',
          click: () => {
            dialog.showMessageBox({
              type: 'info',
              title: 'About Nova Explorer',
              message: 'Nova Explorer v1.0.0',
              detail: 'Advanced File Manager with Built-in Editor\n\nLike Windows Explorer + VS Code combined!'
            });
          }
        }
      ]
    });
  }

  return Menu.buildFromTemplate(template);
}

// IPC Handlers
ipcMain.handle('get-config', () => config);

ipcMain.handle('update-config', (event, newConfig: Partial<AppConfig>) => {
  config = { ...config, ...newConfig };
  store.set('config', config);
  
  // Notify all windows of config change
  windows.forEach(window => {
    window.webContents.send('config-updated', config);
  });
  
  return config;
});

ipcMain.handle('add-recent-path', (event, path: string) => {
  if (!config.recentPaths.includes(path)) {
    config.recentPaths.unshift(path);
    config.recentPaths = config.recentPaths.slice(0, config.maxRecentPaths);
    store.set('config', config);
  }
});

ipcMain.handle('get-recent-paths', () => config.recentPaths);

ipcMain.handle('file-operation', async (event, operation: string, ...args: any[]) => {
  try {
    switch (operation) {
      case 'copy':
        return await fs.copy(args[0], args[1]);
      case 'move':
        return await fs.move(args[0], args[1]);
      case 'delete':
        return await fs.remove(args[0]);
      case 'mkdir':
        return await fs.mkdir(args[0], { recursive: true });
      case 'readdir':
        return await fs.readdir(args[0]);
      case 'stat':
        return await fs.stat(args[0]);
      case 'readFile':
        return await fs.readFile(args[0], args[1] || 'utf8');
      case 'writeFile':
        return await fs.writeFile(args[0], args[1], args[2]);
      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
  } catch (error) {
    console.error(`File operation failed: ${operation}`, error);
    throw error;
  }
});

ipcMain.handle('show-save-dialog', async (event, options: Electron.SaveDialogOptions) => {
  const result = await dialog.showSaveDialog(options);
  return result;
});

ipcMain.handle('show-open-dialog', async (event, options: Electron.OpenDialogOptions) => {
  const result = await dialog.showOpenDialog(options);
  return result;
});

ipcMain.handle('show-error-dialog', async (event, title: string, content: string) => {
  await dialog.showErrorBox(title, content);
});

ipcMain.handle('open-external', async (event, url: string) => {
  await shell.openExternal(url);
});

ipcMain.handle('show-in-folder', async (event, filePath: string) => {
  await shell.showItemInFolder(filePath);
});

ipcMain.handle('get-clipboard', () => {
  return clipboard.readText();
});

ipcMain.handle('set-clipboard', (event, text: string) => {
  clipboard.writeText(text);
});

// App event handlers
app.whenReady().then(() => {
  // Create initial window
  createWindow();

  // Set up global shortcuts
  globalShortcut.register('CommandOrControl+N', () => {
    createWindow();
  });

  globalShortcut.register('CommandOrControl+Shift+N', () => {
    createWindow();
  });

  // Set up menu
  Menu.setApplicationMenu(createMenu());

  // macOS specific
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (!isMac) {
    app.quit();
  }
});

app.on('will-quit', () => {
  // Unregister all shortcuts
  globalShortcut.unregisterAll();
});

// Handle file opening on Windows
if (process.platform === 'win32') {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // Someone tried to run a second instance, focus our window instead
    const focusedWindow = BrowserWindow.getFocusedWindow();
    if (focusedWindow) {
      if (focusedWindow.isMinimized()) focusedWindow.restore();
      focusedWindow.focus();
    }

    // Handle file arguments
    const filePath = commandLine.find(arg => !arg.startsWith('-'));
    if (filePath && focusedWindow) {
      focusedWindow.webContents.send('open-file', filePath);
    }
  });
}

// Handle file associations
app.on('open-file', (event, filePath) => {
  event.preventDefault();
  const focusedWindow = BrowserWindow.getFocusedWindow();
  if (focusedWindow) {
    focusedWindow.webContents.send('open-file', filePath);
  } else {
    createWindow(filePath);
  }
});