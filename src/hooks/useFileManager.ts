import { useState, useCallback } from 'react'
import { RecentFile } from '../types'

export function useFileManager() {
  const [recentFiles, setRecentFiles] = useState<RecentFile[]>([])

  const openFile = useCallback(async () => {
    if (window.electronAPI) {
      try {
        const filePath = await window.electronAPI.openFile()
        if (filePath) {
          const content = await window.electronAPI.readFile(filePath)
          const fileName = filePath.split('/').pop() || filePath.split('\\').pop() || 'Unknown'
          
          // Add to recent files
          const newRecentFile: RecentFile = {
            path: filePath,
            name: fileName,
            lastOpened: new Date()
          }
          
          setRecentFiles(prev => {
            const filtered = prev.filter(f => f.path !== filePath)
            return [newRecentFile, ...filtered].slice(0, 10)
          })
          
          return { filePath, content, fileName }
        }
      } catch (error) {
        console.error('Failed to open file:', error)
      }
    }
    return null
  }, [])

  const saveFile = useCallback(async () => {
    if (window.electronAPI) {
      try {
        const filePath = await window.electronAPI.saveFile()
        return filePath
      } catch (error) {
        console.error('Failed to save file:', error)
      }
    }
    return null
  }, [])

  const saveFileAs = useCallback(async () => {
    if (window.electronAPI) {
      try {
        const filePath = await window.electronAPI.saveFile()
        return filePath
      } catch (error) {
        console.error('Failed to save file as:', error)
      }
    }
    return null
  }, [])

  const writeFile = useCallback(async (filePath: string, content: string) => {
    if (window.electronAPI) {
      try {
        await window.electronAPI.writeFile(filePath, content)
        return true
      } catch (error) {
        console.error('Failed to write file:', error)
        return false
      }
    }
    return false
  }, [])

  // Load recent files from localStorage
  useState(() => {
    const saved = localStorage.getItem('anora_recent_files')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setRecentFiles(parsed.map((f: any) => ({
          ...f,
          lastOpened: new Date(f.lastOpened)
        })))
      } catch (error) {
        console.error('Failed to parse recent files:', error)
      }
    }
  })

  // Save recent files to localStorage
  useState(() => {
    localStorage.setItem('anora_recent_files', JSON.stringify(recentFiles))
  })

  return {
    openFile,
    saveFile,
    saveFileAs,
    writeFile,
    recentFiles
  }
}