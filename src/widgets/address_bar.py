"""
Address Bar Widget - Shows current path and allows navigation
"""

import os
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QCompleter
from PySide6.QtCore import Qt, Signal, QStringListModel
from PySide6.QtGui import QFont, QKeySequence

class AddressBar(QWidget):
    """Address bar widget for showing and editing current path"""
    
    path_changed = Signal(str)  # Signal emitted when path changes
    
    def __init__(self):
        super().__init__()
        self.current_path = ""
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the address bar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Path input
        self.path_input = QLineEdit()
        self.path_input.setFont(QFont("Segoe UI", 9))
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                color: #000000;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
        """)
        self.path_input.returnPressed.connect(self.on_path_entered)
        layout.addWidget(self.path_input)
        
        # Go button
        self.go_button = QPushButton("Go")
        self.go_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.go_button.clicked.connect(self.on_go_clicked)
        layout.addWidget(self.go_button)
        
        # Setup completer for path suggestions
        self.setup_completer()
        
    def setup_completer(self):
        """Setup path completion"""
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.path_input.setCompleter(self.completer)
        
    def set_path(self, path):
        """Set the current path"""
        self.current_path = str(Path(path).resolve())
        self.path_input.setText(self.current_path)
        self.update_completer()
        
    def on_path_entered(self):
        """Handle path input when Enter is pressed"""
        path = self.path_input.text().strip()
        if path and path != self.current_path:
            self.path_changed.emit(path)
            
    def on_go_clicked(self):
        """Handle Go button click"""
        self.on_path_entered()
        
    def update_completer(self):
        """Update path completion suggestions"""
        try:
            # Get parent directories
            path = Path(self.current_path)
            suggestions = []
            
            # Add current path and its parents
            while path != path.parent:
                suggestions.append(str(path))
                path = path.parent
                
            # Add common directories
            common_dirs = [
                str(Path.home()),
                str(Path.home() / "Desktop"),
                str(Path.home() / "Documents"),
                str(Path.home() / "Downloads"),
                str(Path.home() / "Pictures"),
                str(Path.home() / "Music"),
                str(Path.home() / "Videos"),
            ]
            
            suggestions.extend(common_dirs)
            
            # Add drive letters on Windows
            if os.name == 'nt':
                import string
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        suggestions.append(drive)
                        
            # Remove duplicates and sort
            suggestions = sorted(list(set(suggestions)))
            
            # Update completer
            model = QStringListModel(suggestions)
            self.completer.setModel(model)
            
        except Exception:
            pass
            
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            # Cancel editing and restore current path
            self.path_input.setText(self.current_path)
            self.path_input.clearFocus()
        else:
            super().keyPressEvent(event)