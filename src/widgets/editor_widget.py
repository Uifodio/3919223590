"""
Built-in Code Editor Widget
"""

import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QSplitter, QListWidget, QListWidgetItem,
    QMenu, QMessageBox, QFileDialog, QProgressBar, QStatusBar,
    QToolBar, QApplication, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSettings
from PySide6.QtGui import (
    QTextCursor, QFont, QSyntaxHighlighter, QTextCharFormat,
    QColor, QKeySequence, QIcon, QTextDocument, QAction
)

class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for code files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_formats()
        
    def setup_formats(self):
        """Setup syntax highlighting formats"""
        # Keywords
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#569CD6"))
        self.keyword_format.setFontWeight(QFont.Bold)
        
        # Strings
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#CE9178"))
        
        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6A9955"))
        self.comment_format.setFontItalic(True)
        
        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#B5CEA8"))
        
        # Functions
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#DCDCAA"))
        
        # Keywords for different languages
        self.keywords = {
            'python': [
                'False', 'None', 'True', 'and', 'as', 'assert', 'break', 'class',
                'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
                'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
                'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
                'while', 'with', 'yield'
            ],
            'javascript': [
                'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
                'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
                'for', 'function', 'if', 'import', 'in', 'instanceof', 'let',
                'new', 'return', 'super', 'switch', 'this', 'throw', 'try',
                'typeof', 'var', 'void', 'while', 'with', 'yield'
            ],
            'cpp': [
                'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
                'do', 'double', 'else', 'enum', 'extern', 'float', 'for',
                'goto', 'if', 'int', 'long', 'register', 'return', 'short',
                'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef',
                'union', 'unsigned', 'void', 'volatile', 'while'
            ]
        }
        
    def highlightBlock(self, text):
        """Highlight a block of text"""
        # Detect language based on file extension
        document = self.document()
        if hasattr(document, 'file_path'):
            ext = Path(document.file_path).suffix.lower()
            if ext == '.py':
                self.highlight_python(text)
            elif ext in ['.js', '.jsx']:
                self.highlight_javascript(text)
            elif ext in ['.cpp', '.c', '.h', '.hpp']:
                self.highlight_cpp(text)
            else:
                self.highlight_generic(text)
        else:
            self.highlight_generic(text)
            
    def highlight_python(self, text):
        """Highlight Python code"""
        # Keywords
        for keyword in self.keywords['python']:
            self.highlight_pattern(f'\\b{keyword}\\b', self.keyword_format)
            
        # Strings
        self.highlight_pattern(r'"[^"]*"', self.string_format)
        self.highlight_pattern(r"'[^']*'", self.string_format)
        
        # Comments
        self.highlight_pattern(r'#.*$', self.comment_format)
        
        # Numbers
        self.highlight_pattern(r'\b\d+\b', self.number_format)
        
        # Functions
        self.highlight_pattern(r'\b\w+(?=\()', self.function_format)
        
    def highlight_javascript(self, text):
        """Highlight JavaScript code"""
        # Keywords
        for keyword in self.keywords['javascript']:
            self.highlight_pattern(f'\\b{keyword}\\b', self.keyword_format)
            
        # Strings
        self.highlight_pattern(r'"[^"]*"', self.string_format)
        self.highlight_pattern(r"'[^']*'", self.string_format)
        
        # Comments
        self.highlight_pattern(r'//.*$', self.comment_format)
        self.highlight_pattern(r'/\*.*?\*/', self.comment_format)
        
        # Numbers
        self.highlight_pattern(r'\b\d+\b', self.number_format)
        
        # Functions
        self.highlight_pattern(r'\b\w+(?=\()', self.function_format)
        
    def highlight_cpp(self, text):
        """Highlight C++ code"""
        # Keywords
        for keyword in self.keywords['cpp']:
            self.highlight_pattern(f'\\b{keyword}\\b', self.keyword_format)
            
        # Strings
        self.highlight_pattern(r'"[^"]*"', self.string_format)
        
        # Comments
        self.highlight_pattern(r'//.*$', self.comment_format)
        self.highlight_pattern(r'/\*.*?\*/', self.comment_format)
        
        # Numbers
        self.highlight_pattern(r'\b\d+\b', self.number_format)
        
        # Functions
        self.highlight_pattern(r'\b\w+(?=\()', self.function_format)
        
    def highlight_generic(self, text):
        """Generic highlighting for unknown file types"""
        # Strings
        self.highlight_pattern(r'"[^"]*"', self.string_format)
        self.highlight_pattern(r"'[^']*'", self.string_format)
        
        # Comments
        self.highlight_pattern(r'#.*$', self.comment_format)
        self.highlight_pattern(r'//.*$', self.comment_format)
        
        # Numbers
        self.highlight_pattern(r'\b\d+\b', self.number_format)
        
    def highlight_pattern(self, pattern, format):
        """Highlight text matching a pattern"""
        import re
        for match in re.finditer(pattern, self.currentBlock().text()):
            self.setFormat(match.start(), match.end() - match.start(), format)

class LineNumberWidget(QWidget):
    """Widget for displaying line numbers"""
    
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setFixedWidth(50)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the line number widget"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #858585;
                border-right: 1px solid #3e3e3e;
            }
        """)
        
    def paintEvent(self, event):
        """Paint line numbers"""
        from PySide6.QtGui import QPainter, QPen
        
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1e1e1e"))
        
        # Get document info
        document = self.editor.document()
        block_count = document.blockCount()
        
        # Calculate line height
        font_metrics = self.editor.fontMetrics()
        line_height = font_metrics.height()
        
        # Draw line numbers
        painter.setPen(QPen(QColor("#858585")))
        painter.setFont(self.editor.font())
        
        for i in range(block_count):
            y = i * line_height
            painter.drawText(5, y + line_height - 2, str(i + 1))

class EditorWidget(QWidget):
    """Main editor widget with syntax highlighting and features"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.setInterval(30000)  # 30 seconds
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the editor UI"""
        self.setWindowTitle("Perfect File Manager - Editor")
        self.setGeometry(200, 200, 1000, 700)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Toolbar
        self.setup_toolbar()
        layout.addWidget(self.toolbar)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Line number widget
        self.line_numbers = LineNumberWidget(self)
        splitter.addWidget(self.line_numbers)
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 12))
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                selection-background-color: #264f78;
            }
        """)
        splitter.addWidget(self.editor)
        
        # Set splitter proportions
        splitter.setSizes([50, 950])
        
        # Status bar
        self.statusbar = QStatusBar()
        layout.addWidget(self.statusbar)
        
        # Setup syntax highlighter
        self.highlighter = SyntaxHighlighter(self.editor.document())
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
    def setup_toolbar(self):
        """Setup the editor toolbar"""
        self.toolbar = QToolBar()
        
        # File operations
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.new_file)
        self.toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file_dialog)
        self.toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_file)
        self.toolbar.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_file_as)
        self.toolbar.addAction(save_as_action)
        
        self.toolbar.addSeparator()
        
        # Edit operations
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        undo_action.triggered.connect(self.editor.undo)
        self.toolbar.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        redo_action.triggered.connect(self.editor.redo)
        self.toolbar.addAction(redo_action)
        
        self.toolbar.addSeparator()
        
        # Search
        find_action = QAction("Find", self)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        find_action.triggered.connect(self.show_find_dialog)
        self.toolbar.addAction(find_action)
        
        replace_action = QAction("Replace", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        replace_action.triggered.connect(self.show_replace_dialog)
        self.toolbar.addAction(replace_action)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.on_cursor_changed)
        
    def open_file(self, file_path):
        """Open a file in the editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.editor.setPlainText(content)
            self.current_file = file_path
            self.editor.document().file_path = file_path  # For syntax highlighting
            self.is_modified = False
            
            # Update window title
            self.setWindowTitle(f"Perfect File Manager - {os.path.basename(file_path)}")
            
            # Start auto-save
            self.auto_save_timer.start()
            
            # Update status
            self.update_status()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
            
    def save_file(self):
        """Save the current file"""
        if not self.current_file:
            return self.save_file_as()
            
        try:
            # Create backup if auto-backup is enabled
            if self.should_create_backup():
                self.create_backup()
                
            content = self.editor.toPlainText()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.is_modified = False
            self.update_status()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
            
    def save_file_as(self):
        """Save file with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", self.current_file or "",
            "All Files (*.*);;Text Files (*.txt);;Python Files (*.py);;JavaScript Files (*.js)"
        )
        
        if file_path:
            self.current_file = file_path
            self.save_file()
            
    def new_file(self):
        """Create a new file"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Save Changes",
                "Do you want to save changes to the current file?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return
                
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self.setWindowTitle("Perfect File Manager - Editor")
        self.update_status()
        
    def open_file_dialog(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "All Files (*.*);;Text Files (*.txt);;Python Files (*.py);;JavaScript Files (*.js)"
        )
        
        if file_path:
            self.open_file(file_path)
            
    def show_find_dialog(self):
        """Show find dialog"""
        # Simple find dialog
        text, ok = QInputDialog.getText(self, "Find", "Find text:")
        if ok and text:
            self.find_text(text)
            
    def show_replace_dialog(self):
        """Show replace dialog"""
        # Simple replace dialog
        find_text, ok = QInputDialog.getText(self, "Replace", "Find text:")
        if ok and find_text:
            replace_text, ok = QInputDialog.getText(self, "Replace", "Replace with:")
            if ok:
                self.replace_text(find_text, replace_text)
                
    def find_text(self, text):
        """Find text in editor"""
        cursor = self.editor.textCursor()
        cursor = self.editor.document().find(text, cursor)
        
        if not cursor.isNull():
            self.editor.setTextCursor(cursor)
        else:
            QMessageBox.information(self, "Find", "Text not found.")
            
    def replace_text(self, find_text, replace_text):
        """Replace text in editor"""
        cursor = self.editor.textCursor()
        text = self.editor.toPlainText()
        new_text = text.replace(find_text, replace_text)
        self.editor.setPlainText(new_text)
        
    def auto_save(self):
        """Auto-save the current file"""
        if self.current_file and self.is_modified:
            self.save_file()
            
    def should_create_backup(self):
        """Check if backup should be created"""
        # Always create backup for now
        return True
        
    def create_backup(self):
        """Create a backup of the current file"""
        if not self.current_file:
            return
            
        backup_path = f"{self.current_file}.bak"
        try:
            import shutil
            shutil.copy2(self.current_file, backup_path)
        except Exception as e:
            print(f"Failed to create backup: {e}")
            
    def on_text_changed(self):
        """Handle text changes"""
        self.is_modified = True
        self.update_status()
        
    def on_cursor_changed(self):
        """Handle cursor position changes"""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.statusbar.showMessage(f"Line {line}, Column {column}")
        
    def update_status(self):
        """Update status bar"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            modified = " *" if self.is_modified else ""
            self.setWindowTitle(f"Perfect File Manager - {filename}{modified}")
        else:
            self.setWindowTitle("Perfect File Manager - Editor")
            
    def closeEvent(self, event):
        """Handle close event"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Save Changes",
                "Do you want to save changes before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.save_file()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()