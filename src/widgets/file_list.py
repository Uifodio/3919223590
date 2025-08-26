"""
File List Widget - Shows files and folders in main panel
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QInputDialog,
    QProgressDialog, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal, QMimeData, QTimer, QUrl
from PySide6.QtGui import QIcon, QFont, QDrag, QPixmap

class FileListWidget(QListWidget):
    """List widget for displaying files and folders"""
    
    def __init__(self):
        super().__init__()
        self.current_path = ""
        self.show_hidden = False
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the list widget UI"""
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QPixmap(48, 48).size())
        self.setSpacing(10)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        
        # Set font
        font = QFont("Segoe UI", 9)
        self.setFont(font)
        
    def load_directory(self, path):
        """Load directory contents"""
        self.current_path = path
        self.clear()
        
        try:
            # Get directory contents
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                
                # Skip hidden files if not showing them
                if not self.show_hidden and item.startswith('.'):
                    continue
                    
                items.append((item, item_path))
                
            # Sort items (folders first, then files)
            def sort_key(item_tuple):
                name, item_path = item_tuple
                is_dir = os.path.isdir(item_path)
                return (not is_dir, name.lower())
                
            items.sort(key=sort_key)
            
            # Add items to list
            for name, item_path in items:
                self.add_file_item(name, item_path)
                
        except PermissionError:
            # Show access denied message
            item = QListWidgetItem(self)
            item.setText("Access Denied")
            item.setIcon(self.style().standardIcon(self.style().SP_MessageBoxWarning))
            item.setData(Qt.UserRole, None)
            
    def add_file_item(self, name, path):
        """Add a file or folder item to the list"""
        item = QListWidgetItem(self)
        item.setText(name)
        item.setData(Qt.UserRole, path)
        
        # Set icon based on file type
        if os.path.isdir(path):
            item.setIcon(self.style().standardIcon(self.style().SP_DirIcon))
        else:
            item.setIcon(self.get_file_icon(path))
            
        # Set tooltip with file info
        tooltip = self.get_file_tooltip(path)
        item.setToolTip(tooltip)
        
    def get_file_icon(self, path):
        """Get appropriate icon for file type"""
        ext = Path(path).suffix.lower()
        
        # Common file type icons
        icon_map = {
            '.txt': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.py': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.js': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.html': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.css': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.json': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.xml': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.md': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.zip': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.rar': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.7z': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.jpg': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.jpeg': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.png': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.gif': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.mp4': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.avi': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.mp3': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
            '.wav': self.style().standardIcon(self.style().SP_FileDialogDetailedView),
        }
        
        return icon_map.get(ext, self.style().standardIcon(self.style().SP_FileIcon))
        
    def get_file_tooltip(self, path):
        """Get tooltip text for file"""
        try:
            stat = os.stat(path)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            tooltip = f"Name: {os.path.basename(path)}\n"
            tooltip += f"Path: {path}\n"
            tooltip += f"Size: {self.format_size(size)}\n"
            tooltip += f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}"
            
            if os.path.isdir(path):
                try:
                    file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
                    dir_count = len([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])
                    tooltip += f"\nFiles: {file_count}, Folders: {dir_count}"
                except PermissionError:
                    tooltip += "\nAccess Denied"
                    
            return tooltip
            
        except Exception:
            return f"Path: {path}"
            
    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
        
    def set_show_hidden(self, show):
        """Set whether to show hidden files"""
        self.show_hidden = show
        if self.current_path:
            self.load_directory(self.current_path)
            
    def show_context_menu(self, position):
        """Show context menu for list items"""
        item = self.itemAt(position)
        if not item:
            return
            
        path = item.data(Qt.UserRole)
        if not path:
            return
            
        menu = QMenu(self)
        
        # Open actions
        if os.path.isdir(path):
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda: self.open_folder(path))
        else:
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda: self.open_file(path))
            
        open_with_action = menu.addAction("Open With...")
        open_with_action.triggered.connect(lambda: self.open_with(path))
        
        menu.addSeparator()
        
        # Edit actions
        if not os.path.isdir(path):
            edit_action = menu.addAction("Edit")
            edit_action.triggered.connect(lambda: self.edit_file(path))
            
        menu.addSeparator()
        
        # File operations
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(lambda: self.copy_file(path))
        
        cut_action = menu.addAction("Cut")
        cut_action.triggered.connect(lambda: self.cut_file(path))
        
        menu.addSeparator()
        
        rename_action = menu.addAction("Rename")
        rename_action.triggered.connect(lambda: self.rename_file(item))
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_file(path))
        
        menu.addSeparator()
        
        # Properties
        properties_action = menu.addAction("Properties")
        properties_action.triggered.connect(lambda: self.show_properties(path))
        
        menu.exec_(self.mapToGlobal(position))
        
    def open_folder(self, path):
        """Open folder (signal will be handled by main window)"""
        # This will be handled by the main window
        pass
        
    def open_file(self, path):
        """Open file (signal will be handled by main window)"""
        # This will be handled by the main window
        pass
        
    def open_with(self, path):
        """Open file with default application"""
        try:
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
            
    def edit_file(self, path):
        """Edit file (signal will be handled by main window)"""
        # This will be handled by the main window
        pass
        
    def copy_file(self, path):
        """Copy file to clipboard"""
        # This will be handled by the main window
        pass
        
    def cut_file(self, path):
        """Cut file to clipboard"""
        # This will be handled by the main window
        pass
        
    def rename_file(self, item):
        """Rename file"""
        old_path = item.data(Qt.UserRole)
        old_name = os.path.basename(old_path)
        
        new_name, ok = QInputDialog.getText(
            self, "Rename", "Enter new name:", text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            try:
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                os.rename(old_path, new_path)
                self.load_directory(self.current_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename: {str(e)}")
                
    def delete_file(self, path):
        """Delete file"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{os.path.basename(path)}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.load_directory(self.current_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")
                
    def show_properties(self, path):
        """Show file properties"""
        try:
            stat = os.stat(path)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            msg = f"Name: {os.path.basename(path)}\n"
            msg += f"Path: {path}\n"
            msg += f"Size: {self.format_size(size)}\n"
            msg += f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if os.path.isdir(path):
                try:
                    file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
                    dir_count = len([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])
                    msg += f"Files: {file_count}\n"
                    msg += f"Folders: {dir_count}\n"
                except PermissionError:
                    msg += "Access Denied\n"
                    
            QMessageBox.information(self, "Properties", msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get properties: {str(e)}")
            
    def mousePressEvent(self, event):
        """Handle mouse press events for drag and drop"""
        super().mousePressEvent(event)
        
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events for drag and drop"""
        if not (event.buttons() & Qt.LeftButton):
            return
            
        if ((event.pos() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return
            
        item = self.itemAt(self.drag_start_position)
        if not item:
            return
            
        path = item.data(Qt.UserRole)
        if not path:
            return
            
        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()
        # Provide both URL and text forms
        url = QUrl.fromLocalFile(path)
        mime_data.setUrls([url])
        mime_data.setText(path)
        drag.setMimeData(mime_data)
        
        # Set drag pixmap
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.transparent)
        drag.setPixmap(pixmap)
        
        # Start drag
        drag.exec_(Qt.CopyAction | Qt.MoveAction)
        
    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """Handle drop events"""
        urls = event.mimeData().urls()
        if urls:
            # Handle file drop (will be implemented in main window)
            pass