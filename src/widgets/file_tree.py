"""
File Tree Widget - Shows directory structure in left panel
"""

import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox
from PySide6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PySide6.QtGui import QIcon, QFont

class FileTreeWidget(QTreeWidget):
    """Tree widget for displaying file system structure"""
    
    def __init__(self):
        super().__init__()
        self.show_hidden = False
        self.setup_ui()
        self.load_drives()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        self.setHeaderLabel("Folders")
        self.setColumnCount(1)
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set font
        font = QFont("Segoe UI", 9)
        self.setFont(font)
        
    def load_drives(self):
        """Load all available drives"""
        self.clear()
        
        # Get all drives
        if sys.platform == "win32":
            import win32api
            drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
        else:
            drives = ['/']
            
        for drive in drives:
            if drive:
                drive_item = QTreeWidgetItem(self)
                drive_item.setText(0, f"{drive} ({self.get_drive_name(drive)})")
                drive_item.setData(0, Qt.UserRole, drive)
                
                # Set icon based on drive type
                if drive.startswith('C:'):
                    drive_item.setIcon(0, self.style().standardIcon(self.style().SP_ComputerIcon))
                else:
                    drive_item.setIcon(0, self.style().standardIcon(self.style().SP_DriveNetIcon))
                    
                # Add a dummy item to make it expandable
                dummy = QTreeWidgetItem(drive_item)
                dummy.setText(0, "Loading...")
                dummy.setData(0, Qt.UserRole, None)
                
    def get_drive_name(self, drive):
        """Get the name/label of a drive"""
        try:
            if sys.platform == "win32":
                import win32api
                return win32api.GetVolumeInformation(drive)[0] or "Local Disk"
            else:
                return "Drive"
        except:
            return "Drive"
            
    def expand_item(self, item):
        """Expand a tree item and load its children"""
        if item.childCount() == 1 and item.child(0).data(0, Qt.UserRole) is None:
            # Remove loading placeholder
            item.removeChild(item.child(0))
            
            # Load children
            path = item.data(0, Qt.UserRole)
            if path and os.path.isdir(path):
                self.load_directory(item, path)
                
    def load_directory(self, parent_item, path):
        """Load directory contents into tree item"""
        try:
            # Get directory contents
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                
                # Skip hidden files if not showing them
                if not self.show_hidden and item.startswith('.'):
                    continue
                    
                # Only show directories
                if os.path.isdir(item_path):
                    items.append((item, item_path))
                    
            # Sort items
            items.sort(key=lambda x: x[0].lower())
            
            # Add items to tree
            for name, item_path in items:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, name)
                child_item.setData(0, Qt.UserRole, item_path)
                child_item.setIcon(0, self.style().standardIcon(self.style().SP_DirIcon))
                
                # Check if directory has subdirectories
                try:
                    has_subdirs = any(
                        os.path.isdir(os.path.join(item_path, subitem))
                        for subitem in os.listdir(item_path)
                        if not subitem.startswith('.') or self.show_hidden
                    )
                    if has_subdirs:
                        # Add dummy item to make it expandable
                        dummy = QTreeWidgetItem(child_item)
                        dummy.setText(0, "Loading...")
                        dummy.setData(0, Qt.UserRole, None)
                except PermissionError:
                    pass
                    
        except PermissionError:
            # Add a placeholder for inaccessible directories
            placeholder = QTreeWidgetItem(parent_item)
            placeholder.setText(0, "Access Denied")
            placeholder.setData(0, Qt.UserRole, None)
            placeholder.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxWarning))
            
    def set_show_hidden(self, show):
        """Set whether to show hidden files"""
        self.show_hidden = show
        self.load_drives()
        
    def show_context_menu(self, position):
        """Show context menu for tree items"""
        item = self.itemAt(position)
        if not item:
            return
            
        path = item.data(0, Qt.UserRole)
        if not path:
            return
            
        menu = QMenu(self)
        
        # Open in new window
        open_action = menu.addAction("Open in New Window")
        open_action.triggered.connect(lambda: self.open_in_new_window(path))
        
        # Copy path
        copy_action = menu.addAction("Copy Path")
        copy_action.triggered.connect(lambda: self.copy_path(path))
        
        # Properties
        menu.addSeparator()
        properties_action = menu.addAction("Properties")
        properties_action.triggered.connect(lambda: self.show_properties(path))
        
        menu.exec_(self.mapToGlobal(position))
        
    def open_in_new_window(self, path):
        """Open path in new window"""
        # This will be handled by the main window
        pass
        
    def copy_path(self, path):
        """Copy path to clipboard"""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(path)
        
    def show_properties(self, path):
        """Show file properties"""
        try:
            stat = os.stat(path)
            size = stat.st_size
            modified = stat.st_mtime
            
            from datetime import datetime
            modified_str = datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M:%S')
            
            msg = f"Path: {path}\n"
            msg += f"Size: {size:,} bytes\n"
            msg += f"Modified: {modified_str}\n"
            
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
        """Handle mouse press events"""
        super().mousePressEvent(event)
        
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                # Expand item if it has children
                if item.childCount() > 0:
                    self.expand_item(item)
                    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            current_item = self.currentItem()
            if current_item:
                self.expand_item(current_item)
        else:
            super().keyPressEvent(event)