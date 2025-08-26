"""
Settings Manager
Handles application settings and configuration
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class SettingsManager:
    """Manages application settings"""
    
    def __init__(self, config_file: str = 'config/settings.json'):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(exist_ok=True)
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        default_settings = {
            'theme': 'dark',
            'font_size': 14,
            'auto_save': True,
            'auto_save_interval': 30,
            'show_hidden_files': False,
            'default_path': str(Path.home()),
            'recent_paths': [],
            'max_recent_paths': 10,
            'editor': {
                'tab_size': 4,
                'word_wrap': False,
                'line_numbers': True,
                'syntax_highlighting': True,
                'auto_indent': True
            },
            'file_operations': {
                'use_trash': True,
                'create_backups': True,
                'backup_suffix': '.bak',
                'confirm_deletions': True
            },
            'window': {
                'width': 1200,
                'height': 800,
                'x': None,
                'y': None,
                'maximized': False
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all settings exist
                    return self._merge_settings(default_settings, loaded_settings)
            else:
                # Create default config file
                self.save_settings(default_settings)
                return default_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings
    
    def save_settings(self, settings: Optional[Dict[str, Any]] = None):
        """Save settings to file"""
        if settings is None:
            settings = self.settings
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.settings = settings
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        keys = key.split('.')
        current = self.settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        self.save_settings()
    
    def add_recent_path(self, path: str):
        """Add a path to recent paths"""
        recent_paths = self.get_setting('recent_paths', [])
        max_paths = self.get_setting('max_recent_paths', 10)
        
        # Remove if already exists
        if path in recent_paths:
            recent_paths.remove(path)
        
        # Add to beginning
        recent_paths.insert(0, path)
        
        # Limit the number of recent paths
        recent_paths = recent_paths[:max_paths]
        
        self.set_setting('recent_paths', recent_paths)
    
    def get_recent_paths(self) -> list:
        """Get recent paths"""
        return self.get_setting('recent_paths', [])
    
    def clear_recent_paths(self):
        """Clear recent paths"""
        self.set_setting('recent_paths', [])
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.load_settings()
        self.save_settings()
    
    def _merge_settings(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded settings with defaults"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def export_settings(self, export_path: str):
        """Export settings to a file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error exporting settings: {e}")
    
    def import_settings(self, import_path: str):
        """Import settings from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Merge with current settings
            self.settings = self._merge_settings(self.settings, imported_settings)
            self.save_settings()
        except Exception as e:
            print(f"Error importing settings: {e}")
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get theme colors"""
        theme = self.get_setting('theme', 'dark')
        
        if theme == 'dark':
            return {
                'background': '#1e1e1e',
                'foreground': '#ffffff',
                'accent': '#007acc',
                'secondary': '#2d2d30',
                'border': '#3e3e42',
                'selection': '#264f78',
                'error': '#f44747',
                'warning': '#ffcc02',
                'success': '#4ec9b0'
            }
        else:  # light theme
            return {
                'background': '#ffffff',
                'foreground': '#000000',
                'accent': '#0078d4',
                'secondary': '#f3f2f1',
                'border': '#e1dfdd',
                'selection': '#add6ff',
                'error': '#d13438',
                'warning': '#ffb900',
                'success': '#107c10'
            }
    
    def get_editor_config(self) -> Dict[str, Any]:
        """Get editor configuration"""
        return self.get_setting('editor', {})
    
    def get_file_operations_config(self) -> Dict[str, Any]:
        """Get file operations configuration"""
        return self.get_setting('file_operations', {})
    
    def get_window_config(self) -> Dict[str, Any]:
        """Get window configuration"""
        return self.get_setting('window', {})
    
    def save_window_state(self, width: int, height: int, x: Optional[int] = None, y: Optional[int] = None, maximized: bool = False):
        """Save window state"""
        window_config = {
            'width': width,
            'height': height,
            'x': x,
            'y': y,
            'maximized': maximized
        }
        self.set_setting('window', window_config)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()