import { app, BrowserWindow, Menu, shell, ipcMain, dialog } from 'electron'
import { join } from 'path'
import { fileURLToPath } from 'url'

const isDev = !app.isPackaged

function createWindow(): void {
	const win = new BrowserWindow({
		width: 1280,
		height: 800,
		minWidth: 800,
		minHeight: 600,
		show: false,
		autoHideMenuBar: false,
		webPreferences: {
			preload: join(__dirname, '../preload/index.js'),
			contextIsolation: true,
			nodeIntegration: false,
		}
	})

	win.on('ready-to-show', () => win.show())

	win.webContents.setWindowOpenHandler((details) => {
		shell.openExternal(details.url)
		return { action: 'deny' }
	})

	if (isDev && process.env.VITE_DEV_SERVER_URL) {
		win.loadURL(process.env.VITE_DEV_SERVER_URL)
	} else {
		// In production, Vite outputs index.html to dist
		win.loadFile(join(__dirname, '../../dist/index.html'))
	}

	createMenu(win)
}

app.whenReady().then(() => {
	createWindow()

	app.on('activate', () => {
		if (BrowserWindow.getAllWindows().length === 0) createWindow()
	})
})

app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') app.quit()
})

ipcMain.handle('dialog:openDirectory', async () => {
	return dialog.showOpenDialog({ properties: ['openDirectory'] })
})

ipcMain.handle('dialog:openFile', async () => {
	return dialog.showOpenDialog({ properties: ['openFile'] })
})

function createMenu(win: BrowserWindow): void {
	const template: Electron.MenuItemConstructorOptions[] = [
		{
			label: 'File',
			submenu: [
				{
					label: 'Open File',
					accelerator: 'CmdOrCtrl+O',
					click: async () => {
						const result = await dialog.showOpenDialog(win, { properties: ['openFile'] })
						if (!result.canceled && result.filePaths[0]) {
							win.webContents.send('file:open', result.filePaths[0])
						}
					}
				},
				{ type: 'separator' },
				{ role: 'quit' }
			]
		},
		{
			label: 'View',
			submenu: [
				{ role: 'reload' },
				{ role: 'toggleDevTools' }
			]
		}
	]
	Menu.setApplicationMenu(Menu.buildFromTemplate(template))
}