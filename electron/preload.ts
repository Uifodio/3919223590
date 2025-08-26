import { contextBridge } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
	ping: () => 'pong'
})

declare global {
	interface Window {
		electronAPI: {
			ping: () => string
		}
	}
}