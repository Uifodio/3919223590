import { useState, useEffect, useCallback } from 'react';

export function useSettings() {
  const [settings, setSettings] = useState({
    theme: 'dark',
    fontSize: 14,
    showHiddenFiles: false,
    autoSave: true,
    autoSaveInterval: 30000,
    editor: {
      fontSize: 14,
      theme: 'vs-dark',
      wordWrap: 'on',
      minimap: { enabled: true },
      lineNumbers: 'on'
    },
    fileManager: {
      viewMode: 'list',
      sortBy: 'name',
      sortOrder: 'asc'
    }
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = useCallback(async () => {
    try {
      const result = await window.electronAPI.loadSettings();
      if (result.success) {
        setSettings(result.settings);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateSettings = useCallback(async (newSettings) => {
    try {
      const updatedSettings = { ...settings, ...newSettings };
      const result = await window.electronAPI.saveSettings(updatedSettings);
      if (result.success) {
        setSettings(updatedSettings);
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }, [settings]);

  return {
    settings,
    updateSettings,
    loading
  };
}