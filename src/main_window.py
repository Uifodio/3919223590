"""
Main Window for Perfect File Manager
"""

import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QMenuBar, QStatusBar, QToolBar, QMessageBox, QFileDialog,
    QApplication, QMenu, QAction, QShortcut
)
from PySide6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PySide6.QtGui import QKeySequence, QIcon, QFont

from .widgets.file_tree import FileTreeWidget
from .widgets.file_list import FileListWidget
from .widgets.editor_widget import EditorWidget
from .widgets.address_bar import AddressBar
from .utils.file_operations import FileOperations
from .utils.clipboard_manager import ClipboardManager
from .utils.zip_handler import ZipHandler

class MainWindow(QMainWindow):
    """Main window of the Perfect File Manager"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.current_path = str(Path.home())
        self.clipboard_manager = ClipboardManager()
        self.file_operations = FileOperations()
        self.zip_handler = ZipHandler()
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_shortcuts()
        self.setup_connections()
        
        # Load initial directory
        self.navigate_to(self.current_path)
        
        # Apply theme
        self.apply_theme()
        
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("Perfect File Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Address bar
        self.address_bar = AddressBar()
        main_layout.addWidget(self.address_bar)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # File tree (left panel)
        self.file_tree = FileTreeWidget()
        self.file_tree.setMaximumWidth(300)
        main_splitter.addWidget(self.file_tree)
        
        # File list (right panel)
        self.file_list = FileListWidget()
        main_splitter.addWidget(self.file_list)
        
        # Set splitter proportions
        main_splitter.setSizes([250, 950])
        
        # Editor widget (hidden by default)
        self.editor_widget = EditorWidget()
        self.editor_widget.hide()
        
    def setup_menus(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_window_action = QAction("&New Window", self)
        new_window_action.setShortcut(QKeySequence("Ctrl+N"))
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(self.copy_selected)
        edit_menu.addAction(copy_action)
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence("Ctrl+X"))
        cut_action.triggered.connect(self.cut_selected)
        edit_menu.addAction(cut_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        paste_action.triggered.connect(self.paste_files)
        edit_menu.addAction(paste_action)
        
        delete_action = QAction("&Delete", self)
        delete_action.setShortcut(QKeySequence("Delete"))
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        show_hidden_action = QAction("Show &Hidden Files", self)
        show_hidden_action.setCheckable(True)
        show_hidden_action.setChecked(self.config.get('show_hidden', False))
        show_hidden_action.triggered.connect(self.toggle_hidden_files)
        view_menu.addAction(show_hidden_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Navigation buttons
        back_action = QAction("← Back", self)
        back_action.triggered.connect(self.go_back)
        toolbar.addAction(back_action)
        
        forward_action = QAction("Forward →", self)
        forward_action.triggered.connect(self.go_forward)
        toolbar.addAction(forward_action)
        
        up_action = QAction("↑ Up", self)
        up_action.triggered.connect(self.go_up)
        toolbar.addAction(up_action)
        
        toolbar.addSeparator()
        
        # File operations
        new_folder_action = QAction("New Folder", self)
        new_folder_action.triggered.connect(self.new_folder)
        toolbar.addAction(new_folder_action)
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh)
        toolbar.addAction(refresh_action)
        
    def setup_statusbar(self):
        """Setup the status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # F2 for rename
        rename_shortcut = QShortcut(QKeySequence("F2"), self)
        rename_shortcut.activated.connect(self.rename_selected)
        
        # F5 for refresh
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh)
        
        # Ctrl+R for refresh
        refresh_shortcut2 = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut2.activated.connect(self.refresh)
        
    def setup_connections(self):
        """Setup signal connections"""
        # File tree connections
        self.file_tree.itemClicked.connect(self.on_tree_item_clicked)
        
        # File list connections
        self.file_list.itemDoubleClicked.connect(self.on_list_item_double_clicked)
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Address bar connections
        self.address_bar.path_changed.connect(self.navigate_to)
        
    def apply_theme(self):
        """Apply the current theme"""
        if self.config.get('theme', 'dark') == 'dark':
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #4a4a4a;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QMenu::item:selected {
                    background-color: #4a4a4a;
                }
                QToolBar {
                    background-color: #3c3c3c;
                    border: none;
                }
                QStatusBar {
                    background-color: #3c3c3c;
                    color: #ffffff;
                }
            """)
        
    def navigate_to(self, path):
        """Navigate to a specific path"""
        try:
            path = str(Path(path).resolve())
            if os.path.exists(path) and os.path.isdir(path):
                self.current_path = path
                self.file_list.load_directory(path)
                self.address_bar.set_path(path)
                self.statusbar.showMessage(f"Navigated to: {path}")
            else:
                QMessageBox.warning(self, "Error", f"Path does not exist: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate: {str(e)}")
            
    def on_tree_item_clicked(self, item, column):
        """Handle tree item click"""
        path = item.data(0, Qt.UserRole)
        if path:
            self.navigate_to(path)
            
    def on_list_item_double_clicked(self, item):
        """Handle list item double click"""
        file_path = item.data(Qt.UserRole)
        if file_path:
            if os.path.isdir(file_path):
                self.navigate_to(file_path)
            else:
                self.open_file(file_path)
                
    def on_selection_changed(self):
        """Handle file selection change"""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            self.statusbar.showMessage(f"Selected {len(selected_items)} item(s)")
        else:
            self.statusbar.showMessage("Ready")
            
    def open_file(self, file_path):
        """Open a file in the built-in editor"""
        try:
            # Check if it's a text file
            text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', 
                             '.md', '.log', '.ini', '.cfg', '.conf', '.sh', '.bat',
                             '.cpp', '.c', '.h', '.cs', '.java', '.php', '.rb', '.go'}
            
            if Path(file_path).suffix.lower() in text_extensions:
                self.editor_widget.open_file(file_path)
                self.editor_widget.show()
                self.editor_widget.raise_()
                self.editor_widget.activateWindow()
            else:
                # Open with default system application
                os.startfile(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
            
    def new_window(self):
        """Open a new window"""
        from .main_window import MainWindow
        new_window = MainWindow(self.config)
        new_window.show()
        
    def go_back(self):
        """Go back in history"""
        # TODO: Implement back/forward history
        pass
        
    def go_forward(self):
        """Go forward in history"""
        # TODO: Implement back/forward history
        pass
        
    def go_up(self):
        """Go up one directory"""
        parent = str(Path(self.current_path).parent)
        if parent != self.current_path:
            self.navigate_to(parent)
            
    def new_folder(self):
        """Create a new folder"""
        name, ok = QFileDialog.getSaveFileName(
            self, "New Folder", 
            os.path.join(self.current_path, "New Folder"),
            "Folder"
        )
        if ok and name:
            try:
                os.makedirs(name, exist_ok=True)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {str(e)}")
                
    def refresh(self):
        """Refresh the current view"""
        self.navigate_to(self.current_path)
        
    def copy_selected(self):
        """Copy selected files to clipboard"""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            files = [item.data(Qt.UserRole) for item in selected_items]
            self.clipboard_manager.copy_files(files)
            self.statusbar.showMessage(f"Copied {len(files)} item(s)")
            
    def cut_selected(self):
        """Cut selected files to clipboard"""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            files = [item.data(Qt.UserRole) for item in selected_items]
            self.clipboard_manager.cut_files(files)
            self.statusbar.showMessage(f"Cut {len(files)} item(s)")
            
    def paste_files(self):
        """Paste files from clipboard"""
        try:
            files = self.clipboard_manager.get_files()
            if files:
                self.file_operations.paste_files(files, self.current_path)
                self.refresh()
                self.statusbar.showMessage(f"Pasted {len(files)} item(s)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to paste files: {str(e)}")
            
    def delete_selected(self):
        """Delete selected files"""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            files = [item.data(Qt.UserRole) for item in selected_items]
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete {len(files)} item(s)?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    self.file_operations.delete_files(files)
                    self.refresh()
                    self.statusbar.showMessage(f"Deleted {len(files)} item(s)")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete files: {str(e)}")
                    
    def rename_selected(self):
        """Rename selected file"""
        selected_items = self.file_list.selectedItems()
        if len(selected_items) == 1:
            item = selected_items[0]
            old_path = item.data(Qt.UserRole)
            old_name = os.path.basename(old_path)
            
            new_name, ok = QFileDialog.getSaveFileName(
                self, "Rename", 
                os.path.join(self.current_path, old_name),
                "All Files (*.*)"
            )
            if ok and new_name:
                try:
                    new_path = os.path.join(self.current_path, os.path.basename(new_name))
                    os.rename(old_path, new_path)
                    self.refresh()
                    self.statusbar.showMessage("File renamed")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to rename file: {str(e)}")
                    
    def select_all(self):
        """Select all files"""
        self.file_list.selectAll()
        
    def toggle_hidden_files(self, checked):
        """Toggle hidden files visibility"""
        self.config['show_hidden'] = checked
        self.file_list.set_show_hidden(checked)
        self.file_tree.set_show_hidden(checked)
        
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet.")
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Perfect File Manager",
            "Perfect File Manager v1.0.0\n\n"
            "A powerful file manager for Windows 11\n"
            "Combining File Explorer and Visual Studio Code functionality\n\n"
            "Features:\n"
            "• Built-in code editor with syntax highlighting\n"
            "• Multi-window support\n"
            "• Drag & drop to other applications\n"
            "• ZIP archive support\n"
            "• Unity integration\n\n"
            "© 2024 Perfect File Manager"
        )
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save configuration
        from .utils.config_manager import ConfigManager
        config_manager = ConfigManager()
        config_manager.save_config(self.config)
        
        # Close editor if open
        if self.editor_widget.isVisible():
            self.editor_widget.close()
            
        event.accept()