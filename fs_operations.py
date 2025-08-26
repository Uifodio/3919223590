"""
File System Operations Module
Handles all file and directory operations
"""

import os
import shutil
import send2trash
from pathlib import Path
from typing import List, Dict, Optional
import threading
import time

class FileOperations:
    """File operations manager"""
    
    @staticmethod
    def copy_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """Copy a file"""
        try:
            if os.path.exists(destination) and not overwrite:
                return False
            
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    @staticmethod
    def move_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """Move a file"""
        try:
            if os.path.exists(destination) and not overwrite:
                return False
            
            shutil.move(source, destination)
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str, use_trash: bool = True) -> bool:
        """Delete a file"""
        try:
            if use_trash:
                send2trash.send2trash(file_path)
            else:
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    @staticmethod
    def delete_directory(dir_path: str, use_trash: bool = True) -> bool:
        """Delete a directory"""
        try:
            if use_trash:
                send2trash.send2trash(dir_path)
            else:
                shutil.rmtree(dir_path)
            return True
        except Exception as e:
            print(f"Error deleting directory: {e}")
            return False
    
    @staticmethod
    def create_directory(dir_path: str) -> bool:
        """Create a directory"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
    
    @staticmethod
    def rename_file(old_path: str, new_path: str) -> bool:
        """Rename a file or directory"""
        try:
            os.rename(old_path, new_path)
            return True
        except Exception as e:
            print(f"Error renaming file: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """Get file information"""
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'is_dir': os.path.isdir(file_path),
                'is_file': os.path.isfile(file_path),
                'is_link': os.path.islink(file_path),
                'permissions': oct(stat.st_mode)[-3:]
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {}
    
    @staticmethod
    def list_directory(dir_path: str, show_hidden: bool = False) -> List[Dict]:
        """List directory contents"""
        try:
            items = []
            for item in os.listdir(dir_path):
                if not show_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(dir_path, item)
                if os.path.exists(item_path):
                    items.append(FileOperations.get_file_info(item_path))
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            return items
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []
    
    @staticmethod
    def copy_directory(source: str, destination: str, overwrite: bool = False) -> bool:
        """Copy a directory"""
        try:
            if os.path.exists(destination) and not overwrite:
                return False
            
            shutil.copytree(source, destination, dirs_exist_ok=overwrite)
            return True
        except Exception as e:
            print(f"Error copying directory: {e}")
            return False
    
    @staticmethod
    def get_directory_size(dir_path: str) -> int:
        """Get directory size in bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size
        except Exception as e:
            print(f"Error getting directory size: {e}")
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def is_text_file(file_path: str) -> bool:
        """Check if file is a text file"""
        try:
            text_extensions = {
                '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md',
                '.c', '.cpp', '.h', '.java', '.cs', '.php', '.rb', '.pl',
                '.sh', '.bat', '.ps1', '.sql', '.log', '.ini', '.cfg', '.conf'
            }
            
            ext = Path(file_path).suffix.lower()
            if ext in text_extensions:
                return True
            
            # Try to read first few bytes to check if it's text
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                try:
                    chunk.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        except Exception:
            return False
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = '.bak') -> bool:
        """Create a backup of a file"""
        try:
            backup_path = file_path + backup_suffix
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    @staticmethod
    def restore_backup(backup_path: str, original_path: str) -> bool:
        """Restore a file from backup"""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, original_path)
                return True
            return False
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

class FileWatcher:
    """File system watcher for monitoring changes"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.watching = False
        self.thread = None
    
    def start_watching(self, path: str):
        """Start watching a directory"""
        if self.watching:
            self.stop_watching()
        
        self.watching = True
        self.thread = threading.Thread(target=self._watch_directory, args=(path,))
        self.thread.daemon = True
        self.thread.start()
    
    def stop_watching(self):
        """Stop watching"""
        self.watching = False
        if self.thread:
            self.thread.join()
    
    def _watch_directory(self, path: str):
        """Watch directory for changes"""
        last_modified = {}
        
        while self.watching:
            try:
                current_files = {}
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            current_files[file_path] = os.path.getmtime(file_path)
                        except:
                            pass
                
                # Check for changes
                for file_path, mtime in current_files.items():
                    if file_path not in last_modified:
                        if self.callback:
                            self.callback('created', file_path)
                    elif last_modified[file_path] != mtime:
                        if self.callback:
                            self.callback('modified', file_path)
                
                # Check for deletions
                for file_path in last_modified:
                    if file_path not in current_files:
                        if self.callback:
                            self.callback('deleted', file_path)
                
                last_modified = current_files
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Error watching directory: {e}")
                time.sleep(5)  # Wait longer on error