import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                             QTreeWidgetItem, QListWidget, QListWidgetItem,
                             QSplitter, QLineEdit, QPushButton, QLabel, 
                             QMenu, QMessageBox, QFileDialog, QProgressBar,
                             QApplication, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QMimeData, QUrl
from PyQt6.QtGui import QFont, QIcon, QPixmap, QDrag, QDropEvent, QAction

from .utils import FileUtils, config_manager, clipboard_manager

class FileSystemWatcher(QThread):
    """Thread for watching file system changes"""
    
    file_changed = pyqtSignal(str)
    directory_changed = pyqtSignal(str)
    
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.running = True
    
    def run(self):
        """Watch for file system changes"""
        # This would use watchdog in a real implementation
        pass
    
    def stop(self):
        """Stop watching"""
        self.running = False

class FileTreeWidget(QTreeWidget):
    """Tree widget for file system navigation"""
    
    path_changed = pyqtSignal(str)
    item_double_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_tree()
        self.current_path = ""
        self.setup_connections()
    
    def setup_tree(self):
        """Setup tree widget appearance and behavior"""
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        # Load drives
        self.load_drives()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.itemExpanded.connect(self.on_item_expanded)
        self.itemCollapsed.connect(self.on_item_collapsed)
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def load_drives(self):
        """Load all available drives"""
        self.clear()
        drives = FileUtils.get_drives()
        
        for drive in drives:
            item = QTreeWidgetItem(self)
            item.setText(0, drive)
            item.setIcon(0, self.get_icon_for_path(drive))
            item.setData(0, Qt.ItemDataRole.UserRole, drive)
            
            # Add a dummy item to show expand arrow
            dummy = QTreeWidgetItem(item)
            dummy.setText(0, "Loading...")
    
    def get_icon_for_path(self, path: str) -> QIcon:
        """Get appropriate icon for path"""
        # In a real implementation, this would load actual icons
        return QIcon()
    
    def on_item_expanded(self, item: QTreeWidgetItem):
        """Handle item expansion"""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and os.path.isdir(path):
            self.load_directory(item, path)
    
    def on_item_collapsed(self, item: QTreeWidgetItem):
        """Handle item collapse"""
        # Clear children to save memory
        item.takeChildren()
        dummy = QTreeWidgetItem(item)
        dummy.setText(0, "Loading...")
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            self.current_path = path
            self.path_changed.emit(path)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click"""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            self.item_double_clicked.emit(path)
    
    def load_directory(self, parent_item: QTreeWidgetItem, path: str):
        """Load directory contents into tree"""
        try:
            # Remove loading item
            if parent_item.childCount() > 0:
                parent_item.takeChildren()
            
            # Get directory contents
            items = os.listdir(path)
            items.sort(key=str.lower)
            
            for item_name in items:
                item_path = os.path.join(path, item_name)
                
                # Skip hidden files if not showing them
                if not config_manager.get("show_hidden_files", False) and FileUtils.is_hidden(item_path):
                    continue
                
                # Create tree item
                item = QTreeWidgetItem(parent_item)
                item.setText(0, item_name)
                item.setIcon(0, self.get_icon_for_path(item_path))
                item.setData(0, Qt.ItemDataRole.UserRole, item_path)
                
                # If it's a directory, add dummy child for expansion
                if os.path.isdir(item_path):
                    dummy = QTreeWidgetItem(item)
                    dummy.setText(0, "Loading...")
        
        except PermissionError:
            # Handle permission denied
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, "Access Denied")
            error_item.setIcon(0, QIcon())
        except Exception as e:
            # Handle other errors
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, f"Error: {str(e)}")
            error_item.setIcon(0, QIcon())
    
    def navigate_to_path(self, path: str):
        """Navigate to specific path"""
        if not os.path.exists(path):
            return
        
        # Expand the path in the tree
        path_parts = Path(path).parts
        current_item = self.invisibleRootItem()
        
        for part in path_parts:
            found = False
            for i in range(current_item.childCount()):
                child = current_item.child(i)
                if child.text(0) == part:
                    current_item = child
                    found = True
                    break
            
            if not found:
                break
        
        if current_item != self.invisibleRootItem():
            self.setCurrentItem(current_item)
            self.scrollToItem(current_item)
            self.current_path = path
            self.path_changed.emit(path)

class FileListWidget(QListWidget):
    """List widget for displaying files in current directory"""
    
    file_selected = pyqtSignal(str)
    file_double_clicked = pyqtSignal(str)
    files_selected = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_list()
        self.current_path = ""
        self.setup_connections()
    
    def setup_list(self):
        """Setup list widget appearance and behavior"""
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(QPixmap(48, 48).size())
        self.setSpacing(10)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_directory(self, path: str):
        """Load directory contents into list"""
        self.current_path = path
        self.clear()
        
        try:
            if not os.path.exists(path):
                return
            
            # Get directory contents
            items = os.listdir(path)
            items.sort(key=str.lower)
            
            for item_name in items:
                item_path = os.path.join(path, item_name)
                
                # Skip hidden files if not showing them
                if not config_manager.get("show_hidden_files", False) and FileUtils.is_hidden(item_path):
                    continue
                
                # Create list item
                item = QListWidgetItem(self)
                item.setText(item_name)
                item.setIcon(self.get_icon_for_path(item_path))
                item.setData(Qt.ItemDataRole.UserRole, item_path)
                
                # Set tooltip with file info
                tooltip = self.get_file_tooltip(item_path)
                item.setToolTip(tooltip)
        
        except PermissionError:
            # Handle permission denied
            error_item = QListWidgetItem(self)
            error_item.setText("Access Denied")
            error_item.setIcon(QIcon())
        except Exception as e:
            # Handle other errors
            error_item = QListWidgetItem(self)
            error_item.setText(f"Error: {str(e)}")
            error_item.setIcon(QIcon())
    
    def get_icon_for_path(self, path: str) -> QIcon:
        """Get appropriate icon for path"""
        # In a real implementation, this would load actual icons
        return QIcon()
    
    def get_file_tooltip(self, path: str) -> str:
        """Get tooltip text for file"""
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                size_str = FileUtils.get_file_size_str(size)
                modified = os.path.getmtime(path)
                return f"Size: {size_str}\nModified: {modified}"
            elif os.path.isdir(path):
                return "Folder"
        except:
            pass
        return ""
    
    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click"""
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.file_selected.emit(path)
    
    def on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double click"""
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.file_double_clicked.emit(path)
    
    def on_selection_changed(self):
        """Handle selection change"""
        selected_files = []
        for item in self.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                selected_files.append(path)
        self.files_selected.emit(selected_files)
    
    def show_context_menu(self, position):
        """Show context menu for selected items"""
        menu = QMenu(self)
        
        # Get selected items
        selected_items = self.selectedItems()
        if not selected_items:
            return
        
        # File operations
        if len(selected_items) == 1:
            item = selected_items[0]
            path = item.data(Qt.ItemDataRole.UserRole)
            
            if os.path.isfile(path):
                open_action = QAction("Open", self)
                open_action.triggered.connect(lambda: self.file_double_clicked.emit(path))
                menu.addAction(open_action)
                
                open_with_action = QAction("Open With...", self)
                open_with_action.triggered.connect(lambda: self.open_with_application(path))
                menu.addAction(open_with_action)
                
                menu.addSeparator()
        
        # Copy/Cut actions
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_selected)
        menu.addAction(copy_action)
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut_selected)
        menu.addAction(cut_action)
        
        menu.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        # Rename action (single item only)
        if len(selected_items) == 1:
            rename_action = QAction("Rename", self)
            rename_action.setShortcut("F2")
            rename_action.triggered.connect(self.rename_selected)
            menu.addAction(rename_action)
        
        menu.addSeparator()
        
        # Properties action
        properties_action = QAction("Properties", self)
        properties_action.triggered.connect(self.show_properties)
        menu.addAction(properties_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def copy_selected(self):
        """Copy selected files to clipboard"""
        selected_files = []
        for item in self.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                selected_files.append(path)
        
        if selected_files:
            clipboard_manager.add_to_clipboard(selected_files, "copy")
    
    def cut_selected(self):
        """Cut selected files to clipboard"""
        selected_files = []
        for item in self.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                selected_files.append(path)
        
        if selected_files:
            clipboard_manager.add_to_clipboard(selected_files, "cut")
    
    def delete_selected(self):
        """Delete selected files"""
        selected_files = []
        for item in self.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                selected_files.append(path)
        
        if not selected_files:
            return
        
        # Confirm deletion
        if config_manager.get("file_operations.confirm_delete", True):
            count = len(selected_files)
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete {count} item(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Delete files
        for file_path in selected_files:
            try:
                if config_manager.get("file_operations.use_recycle_bin", True):
                    # Move to recycle bin
                    import send2trash
                    send2trash.send2trash(file_path)
                else:
                    # Permanent delete
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete {file_path}: {e}")
        
        # Refresh the view
        self.load_directory(self.current_path)
    
    def rename_selected(self):
        """Rename selected item"""
        selected_items = self.selectedItems()
        if len(selected_items) != 1:
            return
        
        item = selected_items[0]
        old_path = item.data(Qt.ItemDataRole.UserRole)
        old_name = item.text()
        
        # Get new name
        new_name, ok = QFileDialog.getSaveFileName(
            self, "Rename", old_name,
            "All Files (*)"
        )
        
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.load_directory(self.current_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to rename: {e}")
    
    def open_with_application(self, file_path: str):
        """Open file with default application"""
        try:
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open file: {e}")
    
    def show_properties(self):
        """Show properties of selected items"""
        selected_files = []
        for item in self.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                selected_files.append(path)
        
        if not selected_files:
            return
        
        # Show properties dialog
        # This would be implemented with a proper properties dialog
        pass

class FileExplorer(QWidget):
    """Main file explorer widget"""
    
    path_changed = pyqtSignal(str)
    file_selected = pyqtSignal(str)
    files_selected = pyqtSignal(list)
    file_double_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.current_path = ""
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QHBoxLayout(self)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Tree widget (left panel)
        self.tree_widget = FileTreeWidget()
        splitter.addWidget(self.tree_widget)
        
        # List widget (right panel)
        self.list_widget = FileListWidget()
        splitter.addWidget(self.list_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
        
        # Set initial path
        self.navigate_to_path(os.path.expanduser("~"))
    
    def setup_connections(self):
        """Setup signal connections"""
        self.tree_widget.path_changed.connect(self.on_tree_path_changed)
        self.tree_widget.item_double_clicked.connect(self.on_tree_item_double_clicked)
        
        self.list_widget.file_selected.connect(self.on_list_file_selected)
        self.list_widget.files_selected.connect(self.on_list_files_selected)
        self.list_widget.file_double_clicked.connect(self.on_list_file_double_clicked)
    
    def on_tree_path_changed(self, path: str):
        """Handle tree path change"""
        self.current_path = path
        self.list_widget.load_directory(path)
        self.path_changed.emit(path)
    
    def on_tree_item_double_clicked(self, path: str):
        """Handle tree item double click"""
        if os.path.isdir(path):
            self.navigate_to_path(path)
        else:
            self.file_double_clicked.emit(path)
    
    def on_list_file_selected(self, path: str):
        """Handle list file selection"""
        self.file_selected.emit(path)
    
    def on_list_files_selected(self, paths: List[str]):
        """Handle list files selection"""
        self.files_selected.emit(paths)
    
    def on_list_file_double_clicked(self, path: str):
        """Handle list file double click"""
        if os.path.isdir(path):
            self.navigate_to_path(path)
        else:
            self.file_double_clicked.emit(path)
    
    def navigate_to_path(self, path: str):
        """Navigate to specific path"""
        self.current_path = path
        self.tree_widget.navigate_to_path(path)
        self.list_widget.load_directory(path)
        self.path_changed.emit(path)
    
    def get_current_path(self) -> str:
        """Get current path"""
        return self.current_path
    
    def get_selected_files(self) -> List[str]:
        """Get currently selected files"""
        return [item.data(Qt.ItemDataRole.UserRole) for item in self.list_widget.selectedItems()]
    
    def refresh(self):
        """Refresh the current view"""
        if self.current_path:
            self.list_widget.load_directory(self.current_path)