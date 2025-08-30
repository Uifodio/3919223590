export interface Tab {
  id: string
  title: string
  content: string
  filePath?: string
  isModified: boolean
  language?: string
}

export interface SearchReplaceState {
  isVisible: boolean
  searchQuery: string
  replaceQuery: string
  currentMatchIndex: number
  totalMatches: number
  matches: Array<{ line: number; start: number; end: number }>
}

export interface EditorSettings {
  theme: 'dark' | 'light'
  fontSize: number
  fontFamily: string
  tabSize: number
  insertSpaces: boolean
  wordWrap: boolean
  lineNumbers: boolean
  minimap: boolean
}

export interface RecentFile {
  path: string
  name: string
  lastOpened: Date
}

declare global {
  interface Window {
    electronAPI: {
      openFile: () => Promise<string | null>
      saveFile: () => Promise<string | null>
      readFile: (filePath: string) => Promise<string>
      writeFile: (filePath: string, content: string) => Promise<void>
      setAlwaysOnTop: (value: boolean) => Promise<void>
      setFullscreen: (value: boolean) => Promise<void>
      getShortcuts: () => Promise<any>
      onFileOpened: (callback: (event: any, filePath: string) => void) => void
    }
  }
}