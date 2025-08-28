import { useEffect } from 'react';

export const useKeyboardShortcuts = (shortcuts) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Don't handle shortcuts when typing in input fields
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
      }
      
      const { ctrlKey, shiftKey, key } = event;
      
      // File operations
      if (ctrlKey && !shiftKey && key === 'n') {
        event.preventDefault();
        shortcuts.onNewFile?.();
      } else if (ctrlKey && !shiftKey && key === 'o') {
        event.preventDefault();
        shortcuts.onOpenFile?.();
      } else if (ctrlKey && !shiftKey && key === 's') {
        event.preventDefault();
        shortcuts.onSaveFile?.();
      } else if (ctrlKey && shiftKey && key === 'S') {
        event.preventDefault();
        shortcuts.onSaveAs?.();
      }
      
      // Tab operations
      else if (ctrlKey && !shiftKey && key === 't') {
        event.preventDefault();
        shortcuts.onNewTab?.();
      } else if (ctrlKey && !shiftKey && key === 'w') {
        event.preventDefault();
        shortcuts.onCloseTab?.();
      } else if (ctrlKey && shiftKey && key === 'T') {
        event.preventDefault();
        shortcuts.onReopenTab?.();
      }
      
      // Search operations
      else if (ctrlKey && !shiftKey && key === 'f') {
        event.preventDefault();
        shortcuts.onFind?.();
      } else if (ctrlKey && !shiftKey && key === 'h') {
        event.preventDefault();
        shortcuts.onReplace?.();
      }
      
      // Navigation
      else if (ctrlKey && !shiftKey && key === 'g') {
        event.preventDefault();
        shortcuts.onGoToLine?.();
      }
      
      // Exit
      else if (ctrlKey && !shiftKey && key === 'q') {
        event.preventDefault();
        shortcuts.onExit?.();
      }
      
      // F3 for next search result
      else if (key === 'F3' && !shiftKey) {
        event.preventDefault();
        shortcuts.onNextSearch?.();
      }
      
      // Shift+F3 for previous search result
      else if (key === 'F3' && shiftKey) {
        event.preventDefault();
        shortcuts.onPrevSearch?.();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [shortcuts]);
};