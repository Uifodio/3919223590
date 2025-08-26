import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import MainLayout from '@components/Layout/MainLayout'
import FileManager from '@components/FileManager/FileManager'
import Editor from '@components/Editor/Editor'
import Search from '@components/Search/Search'
import Settings from '@components/Settings/Settings'
import { useFileStore } from '@stores/fileStore'
import { useSettingsStore } from '@stores/settingsStore'
import './App.css'

function App(): React.ReactElement {
  const { initializeFileStore } = useFileStore()
  const { initializeSettings, theme } = useSettingsStore()

  useEffect(() => {
    // Initialize stores
    initializeFileStore()
    initializeSettings()

    // Set up Electron event listeners
    if (window.electronAPI) {
      window.electronAPI.onFileOpen((filePath: string) => {
        // Handle file open from menu
        console.log('File opened from menu:', filePath)
      })

      window.electronAPI.onFolderOpen((folderPath: string) => {
        // Handle folder open from menu
        console.log('Folder opened from menu:', folderPath)
      })
    }

    return () => {
      if (window.electronAPI) {
        window.electronAPI.removeAllListeners('file:open')
        window.electronAPI.removeAllListeners('folder:open')
      }
    }
  }, [initializeFileStore, initializeSettings])

  useEffect(() => {
    // Apply theme
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  return (
    <div className="app" data-theme={theme}>
      <MainLayout>
        <Routes>
          <Route path="/" element={<FileManager />} />
          <Route path="/editor/:filePath?" element={<Editor />} />
          <Route path="/search" element={<Search />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </MainLayout>
      
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'var(--bg-secondary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)'
          }
        }}
      />
    </div>
  )
}

export default App