import { useState, useCallback, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';

export const useFileManager = () => {
  const [tabs, setTabs] = useState([]);
  const [activeTabIndex, setActiveTabIndex] = useState(0);
  const closedTabs = useRef([]);
  const initialized = useRef(false);
  
  const createNewTab = useCallback((content = '') => {
    const newTab = {
      id: uuidv4(),
      title: 'Untitled',
      content: content,
      filePath: null,
      modified: false,
      language: 'text',
      line: 1,
      column: 1,
      totalLines: 1
    };
    
    if (!initialized.current) {
      // First tab - replace the array
      setTabs([newTab]);
      setActiveTabIndex(0);
      initialized.current = true;
    } else {
      // Additional tabs - append to array
      setTabs(prev => [...prev, newTab]);
      setActiveTabIndex(prev => prev + 1);
    }
  }, []);
  
  const openFile = useCallback(async (filePath = null) => {
    let path = filePath;
    
    if (!path) {
      try {
        const result = await window.electronAPI.openFileDialog();
        if (result.canceled || result.filePaths.length === 0) return;
        path = result.filePaths[0];
      } catch (error) {
        console.error('Error opening file dialog:', error);
        return;
      }
    }
    
    try {
      const result = await window.electronAPI.readFile(path);
      if (!result.success) {
        console.error('Error reading file:', result.error);
        return;
      }
      
      const content = result.content;
      const extension = path.split('.').pop().toLowerCase();
      const language = getLanguageFromExtension(extension);
      const title = path.split(/[/\\]/).pop();
      
      const newTab = {
        id: uuidv4(),
        title,
        content,
        filePath: path,
        modified: false,
        language,
        line: 1,
        column: 1,
        totalLines: content.split('\n').length
      };
      
      setTabs(prev => [...prev, newTab]);
      setActiveTabIndex(prev => prev + 1);
    } catch (error) {
      console.error('Error opening file:', error);
    }
  }, []);
  
  const saveFile = useCallback(async (tabIndex) => {
    if (tabIndex < 0 || tabIndex >= tabs.length) return;
    
    const tab = tabs[tabIndex];
    if (!tab.modified) return;
    
    let path = tab.filePath;
    
    if (!path) {
      try {
        const result = await window.electronAPI.saveFileDialog(tab.title);
        if (result.canceled || !result.filePath) return;
        path = result.filePath;
      } catch (error) {
        console.error('Error opening save dialog:', error);
        return;
      }
    }
    
    try {
      const result = await window.electronAPI.writeFile(path, tab.content);
      if (!result.success) {
        console.error('Error saving file:', result.error);
        return;
      }
      
      const extension = path.split('.').pop().toLowerCase();
      const language = getLanguageFromExtension(extension);
      const title = path.split(/[/\\]/).pop();
      
      setTabs(prev => prev.map((t, i) => 
        i === tabIndex 
          ? { ...t, filePath: path, title, language, modified: false }
          : t
      ));
    } catch (error) {
      console.error('Error saving file:', error);
    }
  }, [tabs]);
  
  const saveFileAs = useCallback(async (tabIndex) => {
    if (tabIndex < 0 || tabIndex >= tabs.length) return;
    
    const tab = tabs[tabIndex];
    
    try {
      const result = await window.electronAPI.saveFileDialog(tab.title);
      if (result.canceled || !result.filePath) return;
      
      const path = result.filePath;
      const saveResult = await window.electronAPI.writeFile(path, tab.content);
      
      if (!saveResult.success) {
        console.error('Error saving file:', saveResult.error);
        return;
      }
      
      const extension = path.split('.').pop().toLowerCase();
      const language = getLanguageFromExtension(extension);
      const title = path.split(/[/\\]/).pop();
      
      setTabs(prev => prev.map((t, i) => 
        i === tabIndex 
          ? { ...t, filePath: path, title, language, modified: false }
          : t
      ));
    } catch (error) {
      console.error('Error saving file as:', error);
    }
  }, [tabs]);
  
  const closeTab = useCallback((tabIndex) => {
    if (tabIndex < 0 || tabIndex >= tabs.length) return;
    
    const tab = tabs[tabIndex];
    
    // Save to closed tabs history
    closedTabs.current.unshift(tab);
    if (closedTabs.current.length > 10) {
      closedTabs.current.pop();
    }
    
    // Remove tab
    setTabs(prev => prev.filter((_, i) => i !== tabIndex));
    
    // Adjust active tab index
    if (tabs.length === 1) {
      // Last tab closed, create new one
      createNewTab();
      setActiveTabIndex(0);
    } else if (activeTabIndex >= tabs.length - 1) {
      // Active tab was last, move to previous
      setActiveTabIndex(prev => prev - 1);
    } else if (activeTabIndex > tabIndex) {
      // Active tab was after closed tab, adjust index
      setActiveTabIndex(prev => prev - 1);
    }
  }, [tabs, activeTabIndex, createNewTab]);
  
  const closeOtherTabs = useCallback((keepTabIndex) => {
    if (keepTabIndex < 0 || keepTabIndex >= tabs.length) return;
    
    const tabToKeep = tabs[keepTabIndex];
    setTabs([tabToKeep]);
    setActiveTabIndex(0);
  }, [tabs]);
  
  const reopenClosedTab = useCallback(() => {
    if (closedTabs.current.length === 0) return;
    
    const tab = closedTabs.current.shift();
    const newTab = { ...tab, id: uuidv4() };
    
    setTabs(prev => [...prev, newTab]);
    setActiveTabIndex(prev => prev + 1);
  }, []);
  
  const updateTabContent = useCallback((tabIndex, content) => {
    if (tabIndex < 0 || tabIndex >= tabs.length) return;
    
    const totalLines = content.split('\n').length;
    const modified = content !== tabs[tabIndex].content;
    
    setTabs(prev => prev.map((t, i) => 
      i === tabIndex 
        ? { ...t, content, modified, totalLines }
        : t
    ));
  }, [tabs]);
  
  const getLanguageFromExtension = (extension) => {
    const languageMap = {
      'cs': 'csharp',
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'py': 'python',
      'html': 'html',
      'htm': 'html',
      'css': 'css',
      'json': 'json',
      'c': 'c',
      'cpp': 'cpp',
      'h': 'c',
      'hpp': 'cpp',
      'txt': 'text'
    };
    
    return languageMap[extension] || 'text';
  };
  
  return {
    tabs,
    activeTabIndex,
    createNewTab,
    openFile,
    saveFile,
    saveFileAs,
    closeTab,
    closeOtherTabs,
    reopenClosedTab,
    updateTabContent,
    setActiveTab: setActiveTabIndex
  };
};