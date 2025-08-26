"""
Configuration Manager - Handles application settings
"""

import os
import json
from pathlib import Path

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        
    def ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(exist_ok=True)
        
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            'theme': 'dark',
            'font_size': 12,
            'font_family': 'Segoe UI',
            'auto_save': True,
            'auto_save_interval': 30,
            'show_hidden': False,
            'show_line_numbers': True,
            'syntax_highlighting': True,
            'recent_files': [],
            'recent_folders': [],
            'window_width': 1200,
            'window_height': 800,
            'tree_width': 250,
            'list_width': 950,
            'editor_width': 1000,
            'editor_height': 700,
            'backup_on_edit': True,
            'confirm_delete': True,
            'show_toolbar': True,
            'show_statusbar': True,
            'language': 'en',
            'file_associations': {
                '.py': 'editor',
                '.js': 'editor',
                '.html': 'editor',
                '.css': 'editor',
                '.json': 'editor',
                '.xml': 'editor',
                '.md': 'editor',
                '.txt': 'editor',
                '.log': 'editor',
                '.ini': 'editor',
                '.cfg': 'editor',
                '.conf': 'editor',
                '.sh': 'editor',
                '.bat': 'editor',
                '.cpp': 'editor',
                '.c': 'editor',
                '.h': 'editor',
                '.cs': 'editor',
                '.java': 'editor',
                '.php': 'editor',
                '.rb': 'editor',
                '.go': 'editor'
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Merge with default config to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                        
                return config
            except Exception as e:
                print(f"Failed to load config: {e}")
                return default_config
        else:
            # Create default config file
            self.save_config(default_config)
            return default_config
            
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")
            
    def get_setting(self, key, default=None):
        """Get a specific setting"""
        config = self.load_config()
        return config.get(key, default)
        
    def set_setting(self, key, value):
        """Set a specific setting"""
        config = self.load_config()
        config[key] = value
        self.save_config(config)
        
    def add_recent_file(self, file_path):
        """Add a file to recent files list"""
        config = self.load_config()
        recent_files = config.get('recent_files', [])
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
            
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Keep only last 20 files
        recent_files = recent_files[:20]
        
        config['recent_files'] = recent_files
        self.save_config(config)
        
    def add_recent_folder(self, folder_path):
        """Add a folder to recent folders list"""
        config = self.load_config()
        recent_folders = config.get('recent_folders', [])
        
        # Remove if already exists
        if folder_path in recent_folders:
            recent_folders.remove(folder_path)
            
        # Add to beginning
        recent_folders.insert(0, folder_path)
        
        # Keep only last 20 folders
        recent_folders = recent_folders[:20]
        
        config['recent_folders'] = recent_folders
        self.save_config(config)
        
    def get_recent_files(self):
        """Get list of recent files"""
        config = self.load_config()
        return config.get('recent_files', [])
        
    def get_recent_folders(self):
        """Get list of recent folders"""
        config = self.load_config()
        return config.get('recent_folders', [])
        
    def clear_recent_files(self):
        """Clear recent files list"""
        config = self.load_config()
        config['recent_files'] = []
        self.save_config(config)
        
    def clear_recent_folders(self):
        """Clear recent folders list"""
        config = self.load_config()
        config['recent_folders'] = []
        self.save_config(config)
        
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        default_config = {
            'theme': 'dark',
            'font_size': 12,
            'font_family': 'Segoe UI',
            'auto_save': True,
            'auto_save_interval': 30,
            'show_hidden': False,
            'show_line_numbers': True,
            'syntax_highlighting': True,
            'recent_files': [],
            'recent_folders': [],
            'window_width': 1200,
            'window_height': 800,
            'tree_width': 250,
            'list_width': 950,
            'editor_width': 1000,
            'editor_height': 700,
            'backup_on_edit': True,
            'confirm_delete': True,
            'show_toolbar': True,
            'show_statusbar': True,
            'language': 'en',
            'file_associations': {
                '.py': 'editor',
                '.js': 'editor',
                '.html': 'editor',
                '.css': 'editor',
                '.json': 'editor',
                '.xml': 'editor',
                '.md': 'editor',
                '.txt': 'editor',
                '.log': 'editor',
                '.ini': 'editor',
                '.cfg': 'editor',
                '.conf': 'editor',
                '.sh': 'editor',
                '.bat': 'editor',
                '.cpp': 'editor',
                '.c': 'editor',
                '.h': 'editor',
                '.cs': 'editor',
                '.java': 'editor',
                '.php': 'editor',
                '.rb': 'editor',
                '.go': 'editor'
            }
        }
        
        self.save_config(default_config)
        return default_config