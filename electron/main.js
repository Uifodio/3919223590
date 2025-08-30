const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron')
const path = require('path')
const fs = require('fs').promises

let mainWindow
let isAlwaysOnTop = false
let isFullscreen = false

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 400,
    minHeight: 300,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../public/icon.svg'),
    titleBarStyle: 'default',
    backgroundColor: '#1e1e1e',
    show: false
  })

  // Load the app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })
}

// App event handlers
app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// IPC handlers
ipcMain.handle('open-file', async () => {
  try {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'All Files', extensions: ['*'] },
        { name: 'Text Files', extensions: ['txt'] },
        { name: 'Python Files', extensions: ['py'] },
        { name: 'C# Files', extensions: ['cs'] },
        { name: 'JavaScript Files', extensions: ['js', 'jsx'] },
        { name: 'TypeScript Files', extensions: ['ts', 'tsx'] },
        { name: 'HTML Files', extensions: ['html', 'htm'] },
        { name: 'CSS Files', extensions: ['css'] },
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'C/C++ Files', extensions: ['c', 'cpp', 'h', 'hpp'] }
      ]
    })

    if (!result.canceled && result.filePaths.length > 0) {
      return result.filePaths[0]
    }
    return null
  } catch (error) {
    console.error('Error opening file:', error)
    return null
  }
})

ipcMain.handle('save-file', async () => {
  try {
    const result = await dialog.showSaveDialog(mainWindow, {
      filters: [
        { name: 'All Files', extensions: ['*'] },
        { name: 'Text Files', extensions: ['txt'] },
        { name: 'Python Files', extensions: ['py'] },
        { name: 'C# Files', extensions: ['cs'] },
        { name: 'JavaScript Files', extensions: ['js'] },
        { name: 'TypeScript Files', extensions: ['ts'] },
        { name: 'HTML Files', extensions: ['html'] },
        { name: 'CSS Files', extensions: ['css'] },
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'C/C++ Files', extensions: ['c', 'cpp', 'h'] }
      ]
    })

    if (!result.canceled) {
      return result.filePath
    }
    return null
  } catch (error) {
    console.error('Error saving file:', error)
    return null
  }
})

ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const content = await fs.readFile(filePath, 'utf8')
    return content
  } catch (error) {
    console.error('Error reading file:', error)
    throw error
  }
})

ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    await fs.writeFile(filePath, content, 'utf8')
  } catch (error) {
    console.error('Error writing file:', error)
    throw error
  }
})

ipcMain.handle('set-always-on-top', async (event, value) => {
  try {
    isAlwaysOnTop = value
    mainWindow.setAlwaysOnTop(value)
    return true
  } catch (error) {
    console.error('Error setting always on top:', error)
    return false
  }
})

ipcMain.handle('set-fullscreen', async (event, value) => {
  try {
    isFullscreen = value
    mainWindow.setFullScreen(value)
    return true
  } catch (error) {
    console.error('Error setting fullscreen:', error)
    return false
  }
})

ipcMain.handle('get-shortcuts', async () => {
  return {
    'Ctrl+N': 'New file',
    'Ctrl+O': 'Open file',
    'Ctrl+S': 'Save file',
    'Ctrl+Shift+S': 'Save file as',
    'Ctrl+F': 'Find',
    'Ctrl+H': 'Replace',
    'Ctrl+W': 'Always on top',
    'Ctrl+T': 'New tab',
    'Ctrl+G': 'Go to line',
    'Ctrl+Q': 'Exit',
    'F3': 'Find next',
    'Shift+F3': 'Find previous',
    'Esc': 'Close search/replace'
  }
})

// Global shortcuts (if needed)
// const { globalShortcut } = require('electron')
// app.whenReady().then(() => {
//   globalShortcut.register('CommandOrControl+Shift+I', () => {
//     mainWindow.webContents.toggleDevTools()
//   })
// })