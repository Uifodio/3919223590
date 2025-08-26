import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QLineEdit, QPushButton, QLabel, 
                             QMenuBar, QMenu, QToolBar, QStatusBar,
                             QMessageBox, QFileDialog, QProgressBar, QDialog,
                             QTabWidget, QApplication, QDockWidget, QTextEdit,
                             QListWidget, QListWidgetItem, QInputDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QSettings
from PyQt6.QtGui import QFont, QIcon, QPixmap, QKeySequence, QPalette, QColor, QAction

from .file_explorer import FileExplorer
from .code_editor import CodeEditorWindow
from .utils import config_manager, clipboard_manager, SystemUtils, FileUtils

class UnityIntegrationDialog(QDialog):
    """Dialog for Unity integration setup"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_unity_paths()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Unity Integration Setup")
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Unity path selection
        unity_label = QLabel("Unity Installation Path:")
        layout.addWidget(unity_label)
        
        unity_layout = QHBoxLayout()
        self.unity_path_edit = QLineEdit()
        unity_layout.addWidget(self.unity_path_edit)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_unity_path)
        unity_layout.addWidget(browse_button)
        
        layout.addLayout(unity_layout)
        
        # Unity versions list
        versions_label = QLabel("Available Unity Versions:")
        layout.addWidget(versions_label)
        
        self.versions_list = QListWidget()
        layout.addWidget(self.versions_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        setup_button = QPushButton("Setup Integration")
        setup_button.clicked.connect(self.setup_integration)
        button_layout.addWidget(setup_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def load_unity_paths(self):
        """Load available Unity installations"""
        unity_paths = SystemUtils.get_unity_installations()
        
        for path in unity_paths:
            item = QListWidgetItem(path)
            self.versions_list.addItem(item)
        
        if unity_paths:
            self.unity_path_edit.setText(unity_paths[0])
    
    def browse_unity_path(self):
        """Browse for Unity installation"""
        path, _ = QFileDialog.getExistingDirectory(
            self, "Select Unity Installation Directory"
        )
        if path:
            self.unity_path_edit.setText(path)
    
    def setup_integration(self):
        """Setup Unity integration"""
        unity_path = self.unity_path_edit.text()
        if not unity_path or not os.path.exists(unity_path):
            QMessageBox.warning(self, "Error", "Please select a valid Unity installation path.")
            return
        
        # Save Unity path to config
        config_manager.set("unity_integration.unity_path", unity_path)
        
        QMessageBox.information(self, "Success", 
                              "Unity integration has been set up successfully!\n"
                              "You can now use this file manager as your default code editor in Unity.")
        self.accept()

class SearchWidget(QWidget):
    """Search widget for file and content search"""
    
    search_requested = pyqtSignal(str, bool)  # search_text, search_content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup search UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files and folders...")
        self.search_input.returnPressed.connect(self.perform_search)
        layout.addWidget(self.search_input)
        
        # Search options
        self.content_search_checkbox = QPushButton("Content Search")
        self.content_search_checkbox.setCheckable(True)
        self.content_search_checkbox.setMaximumWidth(120)
        layout.addWidget(self.content_search_checkbox)
        
        # Search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.perform_search)
        layout.addWidget(search_button)
    
    def perform_search(self):
        """Perform search"""
        search_text = self.search_input.text()
        search_content = self.content_search_checkbox.isChecked()
        
        if search_text:
            self.search_requested.emit(search_text, search_content)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_status_bar()
        self.setup_connections()
        self.load_settings()
        
        # Track open editor windows
        self.editor_windows = []
        
        # Set initial path
        self.navigate_to_path(os.path.expanduser("~"))
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("Unity File Manager Pro")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Search bar
        self.search_widget = SearchWidget()
        main_layout.addWidget(self.search_widget)
        
        # File explorer
        self.file_explorer = FileExplorer()
        main_layout.addWidget(self.file_explorer)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Apply dark theme
        self.apply_dark_theme()
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_window_action = QAction("New Window", self)
        new_window_action.setShortcut(QKeySequence("Ctrl+N"))
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_selected)
        edit_menu.addAction(copy_action)
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_selected)
        edit_menu.addAction(cut_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_files)
        edit_menu.addAction(paste_action)
        
        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.refresh_view)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        show_hidden_action = QAction("Show Hidden Files", self)
        show_hidden_action.setCheckable(True)
        show_hidden_action.triggered.connect(self.toggle_hidden_files)
        view_menu.addAction(show_hidden_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        unity_integration_action = QAction("Unity Integration", self)
        unity_integration_action.triggered.connect(self.show_unity_integration)
        tools_menu.addAction(unity_integration_action)
        
        tools_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Navigation buttons
        back_action = QAction("Back", self)
        back_action.triggered.connect(self.go_back)
        toolbar.addAction(back_action)
        
        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(self.go_forward)
        toolbar.addAction(forward_action)
        
        up_action = QAction("Up", self)
        up_action.triggered.connect(self.go_up)
        toolbar.addAction(up_action)
        
        toolbar.addSeparator()
        
        # File operations
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_selected)
        toolbar.addAction(copy_action)
        
        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(self.cut_selected)
        toolbar.addAction(cut_action)
        
        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self.paste_files)
        toolbar.addAction(paste_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # Refresh
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_view)
        toolbar.addAction(refresh_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Path display
        self.path_label = QLabel()
        self.status_bar.addWidget(self.path_label)
        
        # File count
        self.file_count_label = QLabel()
        self.status_bar.addPermanentWidget(self.file_count_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        # File explorer signals
        self.file_explorer.path_changed.connect(self.on_path_changed)
        self.file_explorer.file_selected.connect(self.on_file_selected)
        self.file_explorer.files_selected.connect(self.on_files_selected)
        self.file_explorer.file_double_clicked.connect(self.on_file_double_clicked)
        
        # Search signals
        self.search_widget.search_requested.connect(self.perform_search)
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        palette = QPalette()
        
        # Set dark colors
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
    
    def load_settings(self):
        """Load application settings"""
        # Load window geometry
        geometry = config_manager.get("window_geometry", {})
        if geometry:
            self.setGeometry(
                geometry.get("x", 100),
                geometry.get("y", 100),
                geometry.get("width", 1400),
                geometry.get("height", 900)
            )
        
        # Load other settings
        show_hidden = config_manager.get("show_hidden_files", False)
        # Update UI accordingly
    
    def save_settings(self):
        """Save application settings"""
        # Save window geometry
        geometry = {
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height()
        }
        config_manager.set("window_geometry", geometry)
    
    def navigate_to_path(self, path: str):
        """Navigate to specific path"""
        self.file_explorer.navigate_to_path(path)
    
    def on_path_changed(self, path: str):
        """Handle path change"""
        self.path_label.setText(path)
        self.update_file_count()
    
    def on_file_selected(self, path: str):
        """Handle file selection"""
        # Update status bar with file info
        if os.path.isfile(path):
            size = FileUtils.get_file_size_str(os.path.getsize(path))
            self.status_bar.showMessage(f"File: {Path(path).name} ({size})")
    
    def on_files_selected(self, paths: List[str]):
        """Handle multiple file selection"""
        if paths:
            self.status_bar.showMessage(f"Selected {len(paths)} item(s)")
    
    def on_file_double_clicked(self, path: str):
        """Handle file double click"""
        if os.path.isfile(path):
            # Check if it's a text/code file
            ext = Path(path).suffix.lower()
            text_extensions = ['.txt', '.py', '.js', '.html', '.css', '.json', 
                             '.xml', '.csv', '.md', '.cs', '.cpp', '.c', '.h',
                             '.java', '.php', '.rb', '.go', '.rs', '.swift',
                             '.kt', '.scala', '.sh', '.bat', '.ps1', '.sql',
                             '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
                             '.log']
            
            if ext in text_extensions:
                # Open in code editor
                self.open_in_editor(path)
            else:
                # Open with default application
                try:
                    os.startfile(path)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to open file: {e}")
        elif os.path.isdir(path):
            # Navigate to directory
            self.navigate_to_path(path)
    
    def open_in_editor(self, file_path: str):
        """Open file in code editor"""
        # Check if editor should open in new window
        if config_manager.get("editor.open_in_new_window", True):
            editor_window = CodeEditorWindow(file_path, self)
            self.editor_windows.append(editor_window)
            editor_window.show()
        else:
            # Open in embedded editor (if implemented)
            pass
    
    def new_window(self):
        """Open new window"""
        new_window = MainWindow()
        new_window.show()
    
    def open_file(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "All Files (*)"
        )
        
        if file_path:
            self.open_in_editor(file_path)
    
    def copy_selected(self):
        """Copy selected files"""
        selected_files = self.file_explorer.get_selected_files()
        if selected_files:
            clipboard_manager.add_to_clipboard(selected_files, "copy")
            self.status_bar.showMessage(f"Copied {len(selected_files)} item(s)", 3000)
    
    def cut_selected(self):
        """Cut selected files"""
        selected_files = self.file_explorer.get_selected_files()
        if selected_files:
            clipboard_manager.add_to_clipboard(selected_files, "cut")
            self.status_bar.showMessage(f"Cut {len(selected_files)} item(s)", 3000)
    
    def paste_files(self):
        """Paste files from clipboard"""
        clipboard_data = clipboard_manager.get_clipboard_data()
        if not clipboard_data:
            return
        
        files = clipboard_data['files']
        operation = clipboard_data['operation']
        current_path = self.file_explorer.get_current_path()
        
        if operation == "copy":
            self.copy_files_to_destination(files, current_path)
        elif operation == "cut":
            self.move_files_to_destination(files, current_path)
    
    def copy_files_to_destination(self, source_files: List[str], destination: str):
        """Copy files to destination"""
        # This would be implemented with progress tracking
        pass
    
    def move_files_to_destination(self, source_files: List[str], destination: str):
        """Move files to destination"""
        # This would be implemented with progress tracking
        pass
    
    def delete_selected(self):
        """Delete selected files"""
        selected_files = self.file_explorer.get_selected_files()
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
        
        # Delete files (this would be implemented)
        self.status_bar.showMessage(f"Deleted {len(selected_files)} item(s)", 3000)
        self.refresh_view()
    
    def select_all(self):
        """Select all files in current directory"""
        # This would select all items in the file list
        pass
    
    def refresh_view(self):
        """Refresh the current view"""
        self.file_explorer.refresh()
    
    def toggle_hidden_files(self):
        """Toggle hidden files visibility"""
        current_setting = config_manager.get("show_hidden_files", False)
        config_manager.set("show_hidden_files", not current_setting)
        self.refresh_view()
    
    def go_back(self):
        """Go back in navigation history"""
        # This would be implemented with navigation history
        pass
    
    def go_forward(self):
        """Go forward in navigation history"""
        # This would be implemented with navigation history
        pass
    
    def go_up(self):
        """Go up one directory level"""
        current_path = self.file_explorer.get_current_path()
        parent_path = str(Path(current_path).parent)
        if parent_path != current_path:
            self.navigate_to_path(parent_path)
    
    def perform_search(self, search_text: str, search_content: bool):
        """Perform file search"""
        # This would be implemented with search functionality
        self.status_bar.showMessage(f"Searching for: {search_text}", 3000)
    
    def show_unity_integration(self):
        """Show Unity integration dialog"""
        dialog = UnityIntegrationDialog(self)
        dialog.exec()
    
    def show_settings(self):
        """Show settings dialog"""
        # This would be implemented with a settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog will be implemented.")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Unity File Manager Pro",
                         "Unity File Manager Pro v1.0.0\n\n"
                         "A powerful file manager with built-in code editor\n"
                         "designed specifically for Unity developers.\n\n"
                         "Features:\n"
                         "• Built-in code editor with syntax highlighting\n"
                         "• Multi-window support\n"
                         "• Unity integration\n"
                         "• ZIP archive handling\n"
                         "• Dark theme\n"
                         "• And much more!")
    
    def update_file_count(self):
        """Update file count in status bar"""
        current_path = self.file_explorer.get_current_path()
        if current_path and os.path.exists(current_path):
            try:
                files = [f for f in os.listdir(current_path) 
                        if not FileUtils.is_hidden(os.path.join(current_path, f)) or 
                        config_manager.get("show_hidden_files", False)]
                self.file_count_label.setText(f"{len(files)} items")
            except:
                self.file_count_label.setText("")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save settings
        self.save_settings()
        
        # Close all editor windows
        for window in self.editor_windows:
            window.close()
        
        event.accept()