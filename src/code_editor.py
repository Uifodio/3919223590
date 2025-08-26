import os
import sys
from pathlib import Path
from typing import Optional, Callable
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QSplitter, 
                             QScrollBar, QMenu, QMessageBox, QFileDialog,
                             QApplication, QMainWindow, QToolBar, QStatusBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import (QFont, QFontMetrics, QPainter, QColor, QTextCursor,
                         QKeySequence, QAction, QPixmap, QIcon, QTextCharFormat,
                         QSyntaxHighlighter, QTextBlockFormat, QTextDocument)
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
import pygments.lexers
import pygments.styles

from .utils import config_manager, FileUtils

class LineNumberArea(QWidget):
    """Widget for displaying line numbers"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setFixedWidth(50)
        
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)
        
    def sizeHint(self):
        return self.size()

class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for code editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        self.setup_highlighting()
    
    def setup_highlighting(self):
        """Setup highlighting rules"""
        # This will be overridden by the specific language highlighter
        pass
    
    def highlightBlock(self, text):
        """Highlight a block of text"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

class CodeEditor(QTextEdit):
    """Advanced code editor with syntax highlighting and line numbers"""
    
    textChanged = pyqtSignal()
    fileSaved = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.is_modified = False
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.setup_editor()
        self.setup_highlighter()
        
    def setup_editor(self):
        """Setup editor appearance and behavior"""
        # Font setup
        font = QFont("Consolas", config_manager.get("font_size", 12))
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        
        # Editor settings
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(QFontMetrics(self.font()).horizontalAdvance(' ') * 
                               config_manager.get("editor.tab_size", 4))
        
        # Auto-save
        if config_manager.get("auto_save", True):
            self.auto_save_timer.start(30000)  # 30 seconds
        
        # Connect signals
        self.textChanged.connect(self.on_text_changed)
        
    def setup_highlighter(self):
        """Setup syntax highlighter"""
        self.highlighter = None
        self.update_syntax_highlighting()
    
    def update_syntax_highlighting(self):
        """Update syntax highlighting based on file extension"""
        if not self.file_path:
            return
            
        ext = Path(self.file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.csv': 'csv',
            '.md': 'markdown',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.java': 'java',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'ini',
            '.log': 'text',
            '.txt': 'text'
        }
        
        language = language_map.get(ext, 'text')
        
        try:
            if self.highlighter:
                self.highlighter.setDocument(None)
            
            if language != 'text':
                self.highlighter = PygmentsHighlighter(self.document(), language)
            else:
                self.highlighter = None
        except:
            self.highlighter = None
    
    def line_number_area_width(self):
        """Calculate width needed for line numbers"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """Update line number area width"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Update line number area"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def lineNumberAreaPaintEvent(self, event):
        """Paint line numbers"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(53, 53, 53))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(150, 150, 150))
                painter.drawText(0, top, self.line_number_area.width() - 5, 
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlight_current_line(self):
        """Highlight the current line"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(45, 45, 45)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def on_text_changed(self):
        """Handle text changes"""
        self.is_modified = True
        self.textChanged.emit()
    
    def load_file(self, file_path: str):
        """Load a file into the editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.setPlainText(content)
            self.file_path = file_path
            self.is_modified = False
            self.update_syntax_highlighting()
            
            # Add to recent files
            recent_files = config_manager.get("recent_files", [])
            if file_path in recent_files:
                recent_files.remove(file_path)
            recent_files.insert(0, file_path)
            recent_files = recent_files[:10]  # Keep only 10 recent files
            config_manager.set("recent_files", recent_files)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {e}")
    
    def save_file(self, file_path: str = None):
        """Save the current file"""
        if file_path is None:
            file_path = self.file_path
        
        if not file_path:
            return self.save_file_as()
        
        try:
            # Create backup if enabled
            if config_manager.get("backup_on_edit", True) and os.path.exists(file_path):
                FileUtils.create_backup(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
            
            self.file_path = file_path
            self.is_modified = False
            self.fileSaved.emit(file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
            return False
        
        return True
    
    def save_file_as(self):
        """Save file with new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", self.file_path or "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py);;C# Files (*.cs)"
        )
        
        if file_path:
            return self.save_file(file_path)
        return False
    
    def auto_save(self):
        """Auto-save the current file"""
        if self.is_modified and self.file_path:
            self.save_file()
    
    def find_text(self, text: str, case_sensitive: bool = False):
        """Find text in the document"""
        cursor = self.textCursor()
        cursor.clearSelection()
        
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        
        if self.find(text, flags):
            self.ensureCursorVisible()
        else:
            # Wrap around
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.setTextCursor(cursor)
            if self.find(text, flags):
                self.ensureCursorVisible()
    
    def replace_text(self, find_text: str, replace_text: str, case_sensitive: bool = False):
        """Replace text in the document"""
        cursor = self.textCursor()
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        
        if cursor.hasSelection() and cursor.selectedText() == find_text:
            cursor.insertText(replace_text)
        
        if self.find(find_text, flags):
            self.ensureCursorVisible()
    
    def replace_all(self, find_text: str, replace_text: str, case_sensitive: bool = False):
        """Replace all occurrences of text"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(cursor)
        
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        
        count = 0
        while self.find(find_text, flags):
            cursor = self.textCursor()
            cursor.insertText(replace_text)
            count += 1
        
        return count

class PygmentsHighlighter(SyntaxHighlighter):
    """Pygments-based syntax highlighter"""
    
    def __init__(self, document, language):
        super().__init__(document)
        self.language = language
        self.setup_highlighting()
    
    def setup_highlighting(self):
        """Setup highlighting using Pygments"""
        try:
            if self.language == 'text':
                self.lexer = TextLexer()
            else:
                self.lexer = get_lexer_by_name(self.language)
            
            self.formatter = HtmlFormatter(style='monokai')
        except:
            self.lexer = TextLexer()
            self.formatter = HtmlFormatter(style='monokai')
    
    def highlightBlock(self, text):
        """Highlight a block of text using Pygments"""
        try:
            highlighted = highlight(text, self.lexer, self.formatter)
            # Parse the HTML and apply formatting
            # This is a simplified version - in a full implementation,
            # you would parse the HTML and apply QTextCharFormat
            pass
        except:
            pass

class CodeEditorWindow(QMainWindow):
    """Standalone code editor window"""
    
    def __init__(self, file_path: str = None, parent=None):
        super().__init__(parent)
        self.setup_ui()
        if file_path:
            self.editor.load_file(file_path)
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Code Editor - Unity File Manager Pro")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        self.setup_toolbar()
        
        # Editor
        self.editor = CodeEditor()
        layout.addWidget(self.editor)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connect signals
        self.editor.textChanged.connect(self.update_status)
        self.editor.fileSaved.connect(self.on_file_saved)
        
        # Setup menu
        self.setup_menu()
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Save action
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        # Save As action
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        toolbar.addAction(save_as_action)
        
        toolbar.addSeparator()
        
        # Find action
        find_action = QAction("Find", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.show_find_dialog)
        toolbar.addAction(find_action)
        
        # Replace action
        replace_action = QAction("Replace", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        replace_action.triggered.connect(self.show_replace_dialog)
        toolbar.addAction(replace_action)
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("Find", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        replace_action = QAction("Replace", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        replace_action.triggered.connect(self.show_replace_dialog)
        edit_menu.addAction(replace_action)
    
    def new_file(self):
        """Create a new file"""
        if self.editor.is_modified:
            reply = QMessageBox.question(self, "Save Changes", 
                                       "Do you want to save the current file?",
                                       QMessageBox.StandardButton.Save | 
                                       QMessageBox.StandardButton.Discard | 
                                       QMessageBox.StandardButton.Cancel)
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.editor.clear()
        self.editor.file_path = ""
        self.editor.is_modified = False
        self.setWindowTitle("Code Editor - Unity File Manager Pro")
    
    def open_file(self):
        """Open a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py);;C# Files (*.cs)"
        )
        
        if file_path:
            self.editor.load_file(file_path)
            self.setWindowTitle(f"Code Editor - {Path(file_path).name} - Unity File Manager Pro")
    
    def save_file(self):
        """Save the current file"""
        return self.editor.save_file()
    
    def save_file_as(self):
        """Save file with new name"""
        return self.editor.save_file_as()
    
    def show_find_dialog(self):
        """Show find dialog"""
        # This would be implemented with a proper find dialog
        pass
    
    def show_replace_dialog(self):
        """Show replace dialog"""
        # This would be implemented with a proper replace dialog
        pass
    
    def update_status(self):
        """Update status bar"""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.status_bar.showMessage(f"Line {line}, Column {col}")
    
    def on_file_saved(self, file_path: str):
        """Handle file saved event"""
        self.setWindowTitle(f"Code Editor - {Path(file_path).name} - Unity File Manager Pro")
        self.status_bar.showMessage(f"File saved: {file_path}", 3000)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.editor.is_modified:
            reply = QMessageBox.question(self, "Save Changes", 
                                       "Do you want to save the current file?",
                                       QMessageBox.StandardButton.Save | 
                                       QMessageBox.StandardButton.Discard | 
                                       QMessageBox.StandardButton.Cancel)
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        event.accept()