import os
import shutil
import zipfile
import json
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import psutil

# Import winreg only on Windows
try:
    import winreg
except ImportError:
    winreg = None

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def get_drives() -> List[str]:
        """Get all available drives on Windows"""
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives
    
    @staticmethod
    def is_hidden(path: str) -> bool:
        """Check if file or folder is hidden"""
        try:
            return bool(os.stat(path).st_file_attributes & 0x2)
        except:
            return path.startswith('.')
    
    @staticmethod
    def get_file_icon_path(file_path: str) -> str:
        """Get appropriate icon for file type"""
        ext = Path(file_path).suffix.lower()
        icon_map = {
            '.txt': 'text',
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.csv': 'csv',
            '.md': 'markdown',
            '.zip': 'archive',
            '.rar': 'archive',
            '.7z': 'archive',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.bmp': 'image',
            '.mp4': 'video',
            '.avi': 'video',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.pdf': 'pdf',
            '.doc': 'word',
            '.docx': 'word',
            '.xls': 'excel',
            '.xlsx': 'excel',
            '.ppt': 'powerpoint',
            '.pptx': 'powerpoint',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'header',
            '.java': 'java',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'shell',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'config',
            '.cfg': 'config',
            '.conf': 'config',
            '.log': 'log',
            '.exe': 'executable',
            '.msi': 'installer',
            '.dll': 'library',
            '.sys': 'system',
            '.tmp': 'temp',
            '.bak': 'backup'
        }
        return icon_map.get(ext, 'file')
    
    @staticmethod
    def get_file_size_str(size_bytes: int) -> str:
        """Convert bytes to human readable size"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def create_backup(file_path: str) -> str:
        """Create a backup of a file"""
        backup_path = f"{file_path}.bak"
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Failed to create backup: {e}")
            return ""
    
    @staticmethod
    def is_zip_file(file_path: str) -> bool:
        """Check if file is a ZIP archive"""
        return zipfile.is_zipfile(file_path)
    
    @staticmethod
    def get_zip_contents(zip_path: str) -> List[str]:
        """Get list of files in ZIP archive"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                return zip_file.namelist()
        except:
            return []
    
    @staticmethod
    def extract_zip_file(zip_path: str, extract_path: str) -> bool:
        """Extract ZIP file to specified path"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(extract_path)
            return True
        except Exception as e:
            print(f"Failed to extract ZIP: {e}")
            return False

class SystemUtils:
    """Utility class for system operations"""
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Get system information"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    @staticmethod
    def get_unity_installations() -> List[str]:
        """Find Unity installations on the system"""
        unity_paths = []
        
        # Common Unity installation paths
        common_paths = [
            "C:\\Program Files\\Unity\\Hub\\Editor",
            "C:\\Program Files (x86)\\Unity\\Hub\\Editor",
            os.path.expanduser("~\\AppData\\Local\\Unity\\Hub\\Editor")
        ]
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    unity_exe = os.path.join(base_path, item, "Editor", "Unity.exe")
                    if os.path.exists(unity_exe):
                        unity_paths.append(unity_exe)
        
        return unity_paths
    
    @staticmethod
    def get_visual_studio_paths() -> List[str]:
        """Find Visual Studio installations"""
        vs_paths = []
        
        if winreg is None:
            return vs_paths
        
        # Registry keys for Visual Studio
        registry_keys = [
            r"SOFTWARE\Microsoft\VisualStudio\SxS\VS7",
            r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\SxS\VS7"
        ]
        
        for key_path in registry_keys:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            if "devenv.exe" in value.lower():
                                vs_paths.append(value)
                            i += 1
                        except WindowsError:
                            break
            except:
                continue
        
        return vs_paths
    
    @staticmethod
    def get_default_browser() -> str:
        """Get default browser path"""
        if winreg is None:
            return ""
            
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                program_id = winreg.QueryValueEx(key, "ProgId")[0]
                
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{program_id}\\shell\\open\\command") as key:
                command = winreg.QueryValueEx(key, "")[0]
                return command.split('"')[1] if '"' in command else command.split()[0]
        except:
            return ""

class ConfigManager:
    """Configuration manager for application settings"""
    
    def __init__(self, config_path: str = "resources/config/settings.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "theme": "dark",
            "font_size": 12,
            "auto_save": True,
            "backup_on_edit": True,
            "show_hidden_files": False,
            "default_editor": "built_in",
            "unity_integration": {
                "auto_detect": True,
                "unity_path": "",
                "vs_path": ""
            },
            "editor": {
                "syntax_highlighting": True,
                "line_numbers": True,
                "word_wrap": False,
                "tab_size": 4,
                "auto_indent": True
            },
            "file_operations": {
                "confirm_delete": True,
                "use_recycle_bin": True,
                "show_progress": True
            },
            "recent_files": [],
            "recent_folders": [],
            "window_geometry": {
                "width": 1200,
                "height": 800,
                "x": 100,
                "y": 100
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    return self._merge_configs(default_config, loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

class ClipboardManager:
    """Cross-window clipboard manager"""
    
    def __init__(self):
        self.clipboard_data = []
    
    def add_to_clipboard(self, file_paths: List[str], operation: str = "copy"):
        """Add files to clipboard"""
        self.clipboard_data = {
            'files': file_paths,
            'operation': operation,
            'source_window': None  # Will be set by the source window
        }
    
    def get_clipboard_data(self):
        """Get clipboard data"""
        return self.clipboard_data.copy() if self.clipboard_data else None
    
    def clear_clipboard(self):
        """Clear clipboard"""
        self.clipboard_data = []

# Global instances
config_manager = ConfigManager()
clipboard_manager = ClipboardManager()