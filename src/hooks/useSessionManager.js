import { useCallback } from 'react';

const SESSION_KEY = 'nexus_editor_session';
const RECENT_FILES_KEY = 'nexus_editor_recent_files';
const MAX_RECENT_FILES = 10;

export const useSessionManager = () => {
  const saveSession = useCallback((tabs, activeTabIndex) => {
    try {
      const sessionData = {
        tabs: tabs.map(tab => ({
          id: tab.id,
          title: tab.title,
          content: tab.content,
          filePath: tab.filePath,
          language: tab.language,
          modified: tab.modified
        })),
        activeTabIndex,
        timestamp: Date.now()
      };
      
      localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
      
      // Update recent files
      const recentFiles = JSON.parse(localStorage.getItem(RECENT_FILES_KEY) || '[]');
      const newRecentFiles = tabs
        .filter(tab => tab.filePath)
        .map(tab => ({
          path: tab.filePath,
          title: tab.title,
          timestamp: Date.now()
        }));
      
      // Merge and deduplicate
      const allFiles = [...newRecentFiles, ...recentFiles];
      const uniqueFiles = allFiles.filter((file, index, self) => 
        index === self.findIndex(f => f.path === file.path)
      );
      
      // Keep only the most recent MAX_RECENT_FILES
      const updatedRecentFiles = uniqueFiles
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, MAX_RECENT_FILES);
      
      localStorage.setItem(RECENT_FILES_KEY, JSON.stringify(updatedRecentFiles));
    } catch (error) {
      console.error('Error saving session:', error);
    }
  }, []);
  
  const loadSession = useCallback(() => {
    try {
      const sessionData = localStorage.getItem(SESSION_KEY);
      if (!sessionData) return null;
      
      const parsed = JSON.parse(sessionData);
      
      // Check if session is not too old (24 hours)
      const maxAge = 24 * 60 * 60 * 1000; // 24 hours
      if (Date.now() - parsed.timestamp > maxAge) {
        localStorage.removeItem(SESSION_KEY);
        return null;
      }
      
      return parsed;
    } catch (error) {
      console.error('Error loading session:', error);
      return null;
    }
  }, []);
  
  const getRecentFiles = useCallback(() => {
    try {
      const recentFiles = localStorage.getItem(RECENT_FILES_KEY);
      return recentFiles ? JSON.parse(recentFiles) : [];
    } catch (error) {
      console.error('Error loading recent files:', error);
      return [];
    }
  }, []);
  
  const clearSession = useCallback(() => {
    try {
      localStorage.removeItem(SESSION_KEY);
      localStorage.removeItem(RECENT_FILES_KEY);
    } catch (error) {
      console.error('Error clearing session:', error);
    }
  }, []);
  
  return {
    saveSession,
    loadSession,
    getRecentFiles,
    clearSession
  };
};