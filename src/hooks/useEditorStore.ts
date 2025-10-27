import { useState, useEffect, useCallback } from 'react'
import { Tab } from '../types'

export function useEditorStore() {
  const [tabs, setTabs] = useState<Tab[]>([])
  const [activeTabId, setActiveTabId] = useState<string | null>(null)
  const [closedTabs, setClosedTabs] = useState<Tab[]>([])

  const addTab = useCallback((title: string, content: string, filePath?: string) => {
    const newTab: Tab = {
      id: `tab-${Date.now()}`,
      title,
      content,
      filePath,
      isModified: false,
      language: filePath ? getLanguageFromPath(filePath) : undefined
    }
    
    setTabs(prev => [...prev, newTab])
    setActiveTabId(newTab.id)
  }, [])

  const closeTab = useCallback((tabId: string) => {
    const tabToClose = tabs.find(tab => tab.id === tabId)
    if (tabToClose) {
      setClosedTabs(prev => [tabToClose, ...prev])
      setTabs(prev => prev.filter(tab => tab.id !== tabId))
      
      if (activeTabId === tabId) {
        const remainingTabs = tabs.filter(tab => tab.id !== tabId)
        if (remainingTabs.length > 0) {
          setActiveTabId(remainingTabs[remainingTabs.length - 1].id)
        } else {
          setActiveTabId(null)
        }
      }
    }
  }, [tabs, activeTabId])

  const updateTabContent = useCallback((tabId: string, content: string) => {
    setTabs(prev => prev.map(tab => 
      tab.id === tabId 
        ? { ...tab, content, isModified: true }
        : tab
    ))
  }, [])

  const setActiveTab = useCallback((tabId: string) => {
    setActiveTabId(tabId)
  }, [])

  const reopenClosedTab = useCallback(() => {
    if (closedTabs.length > 0) {
      const [tabToReopen, ...remainingClosed] = closedTabs
      setClosedTabs(remainingClosed)
      setTabs(prev => [...prev, tabToReopen])
      setActiveTabId(tabToReopen.id)
    }
  }, [closedTabs])

  const getLanguageFromPath = (filePath: string): string => {
    const ext = filePath.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'py': return 'python'
      case 'cs': return 'csharp'
      case 'js': case 'jsx': return 'javascript'
      case 'ts': case 'tsx': return 'typescript'
      case 'html': case 'htm': return 'html'
      case 'css': return 'css'
      case 'json': return 'json'
      case 'c': return 'c'
      case 'cpp': case 'cc': case 'cxx': return 'cpp'
      case 'h': case 'hpp': return 'cpp'
      default: return 'text'
    }
  }

  // Session persistence
  useEffect(() => {
    const savedTabs = localStorage.getItem('anora_editor_tabs')
    const savedActiveTab = localStorage.getItem('anora_editor_active_tab')
    
    if (savedTabs) {
      try {
        const parsedTabs = JSON.parse(savedTabs)
        setTabs(parsedTabs)
        if (savedActiveTab && parsedTabs.find((t: Tab) => t.id === savedActiveTab)) {
          setActiveTabId(savedActiveTab)
        }
      } catch (error) {
        console.error('Failed to parse saved tabs:', error)
      }
    }
  }, [])

  // Autosave
  useEffect(() => {
    const interval = setInterval(() => {
      if (tabs.length > 0) {
        localStorage.setItem('anora_editor_tabs', JSON.stringify(tabs))
        if (activeTabId) {
          localStorage.setItem('anora_editor_active_tab', activeTabId)
        }
      }
    }, 500)

    return () => clearInterval(interval)
  }, [tabs, activeTabId])

  return {
    tabs,
    activeTabId,
    closedTabs,
    addTab,
    closeTab,
    updateTabContent,
    setActiveTab,
    reopenClosedTab
  }
}