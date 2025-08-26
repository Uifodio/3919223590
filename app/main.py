import os
import sys
import json
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional
import traceback
import logging

from PySide6 import QtCore, QtGui, QtWidgets
from send2trash import send2trash

APP_NAME = "AuroraFileManager"

# --------------------------- Settings & Persistence ---------------------------

APPDATA_DIR = Path(os.environ.get("APPDATA", str(Path.home() / ".config"))) / APP_NAME
APPDATA_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_PATH = APPDATA_DIR / "settings.json"
RECENTS_PATH = APPDATA_DIR / "recents.json"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "font_family": "Consolas",
    "font_size": 12,
    "editor_autosave": True,
    "editor_autosave_ms": 2500,
}


def load_json(path: Path, default: dict) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default.copy()
    return default.copy()


def save_json(path: Path, data: dict) -> None:
    try:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


SETTINGS = load_json(SETTINGS_PATH, DEFAULT_SETTINGS)
RECENTS = load_json(RECENTS_PATH, {"folders": []})

# Logging setup
LOG_PATH = APPDATA_DIR / "aurora.log"
try:
    logging.basicConfig(filename=str(LOG_PATH), level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Aurora starting up")
except Exception:
    pass


# --------------------------- Theming ---------------------------

def apply_dark_theme(app: QtWidgets.QApplication) -> None:
    app.setStyle("Fusion")
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(37, 37, 38))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(30, 30, 30))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(37, 37, 38))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(45, 45, 48))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(0, 122, 204))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(0, 122, 204))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(dark_palette)


# --------------------------- Utilities ---------------------------

def human_readable_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def ensure_backup(path: Path) -> None:
    try:
        if path.exists():
            bak = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, bak)
    except Exception:
        pass


class ProgressDialog(QtWidgets.QProgressDialog):
    def __init__(self, title: str, label: str, parent=None):
        super().__init__(label, "Cancel", 0, 100, parent)
        self.setWindowTitle(title)
        self.setAutoClose(True)
        self.setAutoReset(True)
        self.setMinimumDuration(400)


class NavigationHistory(QtCore.QObject):
    changed = QtCore.Signal(Path)

    def __init__(self, start: Path):
        super().__init__()
        self._back: List[Path] = []
        self._forward: List[Path] = []
        self._current: Path = start

    @property
    def current(self) -> Path:
        return self._current

    def can_back(self) -> bool:
        return len(self._back) > 0

    def can_forward(self) -> bool:
        return len(self._forward) > 0

    def push(self, path: Path):
        if path == self._current:
            return
        self._back.append(self._current)
        self._current = path
        self._forward.clear()
        self.changed.emit(path)

    def back(self):
        if not self._back:
            return
        self._forward.append(self._current)
        self._current = self._back.pop()
        self.changed.emit(self._current)

    def forward(self):
        if not self._forward:
            return
        self._back.append(self._current)
        self._current = self._forward.pop()
        self.changed.emit(self._current)


class Breadcrumbs(QtWidgets.QWidget):
    pathClicked = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._path = Path.home()
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(4)

    def set_path(self, path: Path):
        self._path = path
        # Clear
        while self.layout().count():
            item = self.layout().takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        # Windows drive handling and root
        parts: List[Path] = []
        p = path
        while True:
            parts.insert(0, p)
            parent = p.parent
            if parent == p:
                break
            p = parent
        for i, part in enumerate(parts):
            btn = QtWidgets.QToolButton()
            btn.setText(part.drive if part.drive else (part.name if part.name else str(part)))
            btn.setAutoRaise(True)
            btn.clicked.connect(lambda _=False, pp=part: self.pathClicked.emit(pp))
            self.layout().addWidget(btn)
            if i < len(parts) - 1:
                arrow = QtWidgets.QLabel("›")
                self.layout().addWidget(arrow)


# --------------------------- File Operations ---------------------------

def copy_with_progress(src_paths: List[Path], dst_dir: Path, parent) -> None:
    files: List[Path] = []
    total_size = 0
    roots: List[Path] = []
    for src in src_paths:
        roots.append(src)
        if src.is_file():
            files.append(src)
            total_size += src.stat().st_size
        elif src.is_dir():
            for root, _, filenames in os.walk(src):
                for name in filenames:
                    p = Path(root) / name
                    files.append(p)
                    total_size += p.stat().st_size

    progress = ProgressDialog("Copy", "Copying files...", parent)
    progress.setRange(0, total_size if total_size > 0 else 1)
    copied = 0

    for file_path in files:
        if progress.wasCanceled():
            break
        # Determine relative path against its own root
        base_root = None
        for r in roots:
            try:
                file_path.relative_to(r)
                base_root = r
                break
            except Exception:
                continue
        if base_root is None:
            base_root = file_path.parent
        rel = file_path.relative_to(base_root if base_root.is_dir() else base_root.parent)
        # Destination path
        if len(src_paths) == 1 and src_paths[0].is_file():
            dest_path = dst_dir / src_paths[0].name
        else:
            dest_path = dst_dir / rel
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if dest_path.exists():
            ensure_backup(dest_path)
        with open(file_path, "rb") as rf, open(dest_path, "wb") as wf:
            while True:
                chunk = rf.read(1024 * 1024)
                if not chunk:
                    break
                wf.write(chunk)
                copied += len(chunk)
                progress.setValue(min(copied, total_size))
                QtWidgets.QApplication.processEvents()


def move_with_progress(src_paths: List[Path], dst_dir: Path, parent) -> None:
    # If destination exists, make backup before overwrite
    for src in src_paths:
        target = dst_dir / src.name
        if target.exists():
            ensure_backup(target)
    copy_with_progress(src_paths, dst_dir, parent)
    for src in src_paths:
        if src.is_dir():
            shutil.rmtree(src, ignore_errors=True)
        else:
            try:
                src.unlink()
            except Exception:
                pass


# --------------------------- Editor ---------------------------
class CodeEditor(QtWidgets.QPlainTextEdit):
    requestFindNext = QtCore.Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QtGui.QFont(SETTINGS.get("font_family", "Consolas"), SETTINGS.get("font_size", 12))
        self.setFont(font)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.highlighter = SimpleHighlighter(self.document())
        self._path: Optional[Path] = None
        self._autosave_timer = QtCore.QTimer(self)
        self._autosave_timer.setInterval(int(SETTINGS.get("editor_autosave_ms", 2500)))
        self._autosave_timer.timeout.connect(self._maybe_autosave)
        if SETTINGS.get("editor_autosave", True):
            self._autosave_timer.start()
        # Line numbers
        self._lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def lineNumberAreaWidth(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self._lineNumberArea.scroll(0, dy)
        else:
            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self._lineNumberArea)
        painter.fillRect(event.rect(), QtGui.QColor(45, 45, 48))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QtGui.QColor(120, 120, 120))
                painter.drawText(0, top, self._lineNumberArea.width() - 6, self.fontMetrics().height(), QtCore.Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            lineColor = QtGui.QColor(255, 255, 255, 20)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor: CodeEditor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class SimpleHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        keyword_format = QtGui.QTextCharFormat()
        keyword_format.setForeground(QtGui.QBrush(QtGui.QColor(86, 156, 214)))
        keyword_format.setFontWeight(QtGui.QFont.Bold)
        self.rules = []
        keywords = [
            "def", "class", "return", "if", "elif", "else", "for", "while", "try", "except",
            "import", "from", "as", "with", "pass", "break", "continue", "True", "False", "None",
            "public", "private", "protected", "static", "void", "int", "float", "double", "string",
            "var", "const", "let", "function", "new", "this", "switch", "case", "default",
        ]
        for kw in keywords:
            self.rules.append((QtCore.QRegularExpression(fr"\\b{kw}\\b"), keyword_format))

        comment_format = QtGui.QTextCharFormat()
        comment_format.setForeground(QtGui.QBrush(QtGui.QColor(87, 166, 74)))
        self.rules.append((QtCore.QRegularExpression(r"//.*"), comment_format))
        self.rules.append((QtCore.QRegularExpression(r"#.*"), comment_format))

        string_format = QtGui.QTextCharFormat()
        string_format.setForeground(QtGui.QBrush(QtGui.QColor(214, 157, 133)))
        self.rules.append((QtCore.QRegularExpression(r"\".*\""), string_format))
        self.rules.append((QtCore.QRegularExpression(r"\'.*\'"), string_format))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)


# --------------------------- ZIP Helpers ---------------------------

def zip_list(zip_path: Path) -> List[str]:
    with zipfile.ZipFile(zip_path, 'r') as zf:
        return zf.namelist()


def zip_read(zip_path: Path, internal_path: str) -> str:
    with zipfile.ZipFile(zip_path, 'r') as zf:
        with zf.open(internal_path) as f:
            return f.read().decode('utf-8', errors='replace')


def zip_write_with_backup(zip_path: Path, internal_path: str, text: str) -> None:
    bak = zip_path.with_suffix(zip_path.suffix + ".bak")
    try:
        if zip_path.exists():
            shutil.copy2(zip_path, bak)
    except Exception:
        pass
    tmp_fd, tmp_name = tempfile.mkstemp(suffix=zip_path.suffix)
    os.close(tmp_fd)
    tmp_zip = Path(tmp_name)
    with zipfile.ZipFile(zip_path, 'r') as src, zipfile.ZipFile(tmp_zip, 'w') as dst:
        for item in src.infolist():
            if item.filename == internal_path:
                continue
            dst.writestr(item, src.read(item.filename))
        dst.writestr(internal_path, text)
    shutil.move(str(tmp_zip), str(zip_path))


# --------------------------- Main Window ---------------------------
class FolderTree(QtWidgets.QTreeView):
    pathActivated = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed | QtWidgets.QAbstractItemView.SelectedClicked)

        self.model_fs = QtWidgets.QFileSystemModel(self)
        self.model_fs.setReadOnly(False)
        self.model_fs.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Drives)
        # On Windows, empty string shows drives
        root_path = ""
        self.model_fs.setRootPath(root_path)
        self.setModel(self.model_fs)
        self.setRootIndex(self.model_fs.index(root_path))

        self.doubleClicked.connect(self.on_double_clicked)

    def on_double_clicked(self, idx: QtCore.QModelIndex):
        path = Path(self.model_fs.filePath(idx))
        self.pathActivated.emit(path)

    def selected_paths(self) -> List[Path]:
        paths: List[Path] = []
        for idx in self.selectionModel().selectedRows():
            paths.append(Path(self.model_fs.filePath(idx)))
        return paths

    def startDrag(self, supportedActions):
        indexes = self.selectionModel().selectedRows()
        if not indexes:
            return
        mime_data = QtCore.QMimeData()
        urls = []
        for idx in indexes:
            urls.append(QtCore.QUrl.fromLocalFile(self.model_fs.filePath(idx)))
        mime_data.setUrls(urls)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        idx = self.indexAt(event.position().toPoint()) if hasattr(event, 'position') else self.indexAt(event.pos())
        target_path = Path(self.model_fs.filePath(idx)) if idx.isValid() else Path(self.model_fs.rootPath())
        if target_path.is_file():
            target_path = target_path.parent
        urls = event.mimeData().urls()
        src_paths = [Path(u.toLocalFile()) for u in urls if u.isLocalFile()]
        if src_paths:
            # Back up any targets that would be overwritten
            for s in src_paths:
                dest = target_path / s.name
                if dest.exists():
                    ensure_backup(dest)
            copy_with_progress(src_paths, target_path, self)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class FilesView(QtWidgets.QListView):
    fileActivated = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setIconSize(QtCore.QSize(64, 64))
        self.setSpacing(12)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed | QtWidgets.QAbstractItemView.SelectedClicked)

        self.model_fs = QtWidgets.QFileSystemModel(self)
        self.model_fs.setReadOnly(False)
        self.model_fs.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        self._apply_icon_provider()
        self.setModel(self.model_fs)

        self.doubleClicked.connect(self.on_double_clicked)

    def _apply_icon_provider(self):
        try:
            self.model_fs.setIconProvider(CustomIconProvider())
        except Exception:
            pass

    def set_directory(self, path: Path):
        if not path.exists() or not path.is_dir():
            return
        self.model_fs.setRootPath(str(path))
        self.setRootIndex(self.model_fs.index(str(path)))

    def selected_paths(self) -> List[Path]:
        paths: List[Path] = []
        for idx in self.selectionModel().selectedRows():
            paths.append(Path(self.model_fs.filePath(idx)))
        return paths

    def startDrag(self, supportedActions):
        indexes = self.selectionModel().selectedRows()
        if not indexes:
            return
        mime_data = QtCore.QMimeData()
        urls = []
        for idx in indexes:
            urls.append(QtCore.QUrl.fromLocalFile(self.model_fs.filePath(idx)))
        mime_data.setUrls(urls)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        idx = self.rootIndex()
        target_path = Path(self.model_fs.filePath(idx))
        urls = event.mimeData().urls()
        src_paths = [Path(u.toLocalFile()) for u in urls if u.isLocalFile()]
        if src_paths:
            for s in src_paths:
                dest = target_path / s.name
                if dest.exists():
                    ensure_backup(dest)
            copy_with_progress(src_paths, target_path, self)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def on_double_clicked(self, idx: QtCore.QModelIndex):
        path = Path(self.model_fs.filePath(idx))
        self.fileActivated.emit(path)


class FilesDetailsView(QtWidgets.QTreeView):
    fileActivated = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(True)
        self.setAllColumnsShowFocus(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed | QtWidgets.QAbstractItemView.SelectedClicked)

        self.model_fs = QtWidgets.QFileSystemModel(self)
        self.model_fs.setReadOnly(False)
        self.model_fs.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        try:
            self.model_fs.setIconProvider(CustomIconProvider())
        except Exception:
            pass
        self.setModel(self.model_fs)
        self.setRootIsDecorated(False)
        self.setColumnWidth(0, 300)

        self.doubleClicked.connect(self.on_double_clicked)

    def set_directory(self, path: Path):
        if not path.exists() or not path.is_dir():
            return
        self.model_fs.setRootPath(str(path))
        self.setRootIndex(self.model_fs.index(str(path)))
        # Show columns: Name, Size, Type, Date Modified
        for col, w in [(0, 320), (1, 100), (2, 160), (3, 180)]:
            self.setColumnWidth(col, w)

    def selected_paths(self) -> List[Path]:
        paths: List[Path] = []
        for idx in self.selectionModel().selectedRows():
            paths.append(Path(self.model_fs.filePath(idx)))
        return paths

    def on_double_clicked(self, idx: QtCore.QModelIndex):
        path = Path(self.model_fs.filePath(idx))
        self.fileActivated.emit(path)


class CustomIconProvider(QtWidgets.QFileIconProvider):
    def icon(self, type_or_info):  # type: ignore[override]
        try:
            if isinstance(type_or_info, QtWidgets.QFileIconProvider.IconType):
                return super().icon(type_or_info)
            info = type_or_info
            file_path = Path(info.absoluteFilePath())
            if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif"} and file_path.is_file():
                pix = QtGui.QPixmap(str(file_path))
                if not pix.isNull():
                    return QtGui.QIcon(pix.scaled(128, 128, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            return super().icon(type_or_info)
        except Exception:
            return super().icon(type_or_info)


class FindReplaceBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(4, 4, 4, 4)
        self.find_edit = QtWidgets.QLineEdit(self)
        self.find_edit.setPlaceholderText("Find...")
        self.case_cb = QtWidgets.QCheckBox("Match case")
        self.next_btn = QtWidgets.QPushButton("Find Next")
        self.replace_edit = QtWidgets.QLineEdit(self)
        self.replace_edit.setPlaceholderText("Replace with...")
        self.replace_btn = QtWidgets.QPushButton("Replace")
        self.layout().addWidget(self.find_edit)
        self.layout().addWidget(self.case_cb)
        self.layout().addWidget(self.next_btn)
        self.layout().addWidget(self.replace_edit)
        self.layout().addWidget(self.replace_btn)


class EditorWindow(QtWidgets.QMainWindow):
    def __init__(self, path: Optional[Path] = None, text: Optional[str] = None, zip_ctx: Optional[tuple[Path, str]] = None):
        super().__init__()
        self.setWindowTitle("Aurora Editor")
        self.resize(1000, 700)
        self.editor = CodeEditor(self)
        self.find_bar = FindReplaceBar(self)
        self.find_bar.setVisible(False)
        central = QtWidgets.QWidget(self)
        central.setLayout(QtWidgets.QVBoxLayout())
        central.layout().setContentsMargins(0, 0, 0, 0)
        central.layout().addWidget(self.find_bar)
        central.layout().addWidget(self.editor)
        self.setCentralWidget(central)

        tb = self.addToolBar("Editor")
        act_save = tb.addAction("Save")
        act_find = tb.addAction("Find")
        act_delete = tb.addAction("Delete (Recycle)")
        act_save.triggered.connect(self._save)
        act_find.triggered.connect(lambda: self.find_bar.setVisible(not self.find_bar.isVisible()))
        act_delete.triggered.connect(self._delete_current)

        self.find_bar.next_btn.clicked.connect(self._find_next)
        self.find_bar.replace_btn.clicked.connect(self._replace_once)

        self._temp_zip = zip_ctx
        if path is not None:
            if text is not None:
                self.editor.open_path(path, text)
            else:
                self.editor.open_path(path)

    def _save(self):
        if self._temp_zip:
            zip_path, internal_path = self._temp_zip
            try:
                zip_write_with_backup(zip_path, internal_path, self.editor.toPlainText())
                self.editor.document().setModified(False)
                QtWidgets.QMessageBox.information(self, "Saved", f"Saved into {zip_path.name}:{internal_path}\nBackup created.")
            except Exception as ex:
                QtWidgets.QMessageBox.warning(self, "Save Error", str(ex))
        else:
            self.editor.save()

    def _delete_current(self):
        p = self.editor._path
        if not p:
            return
        if QtWidgets.QMessageBox.question(self, "Delete", f"Send to Recycle Bin?\n{p}") != QtWidgets.QMessageBox.Yes:
            return
        try:
            send2trash(str(p))
            self.close()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self, "Delete Error", str(ex))

    def _find_next(self):
        text = self.find_bar.find_edit.text()
        if not text:
            return
        flags = QtGui.QTextDocument.FindFlags()
        if self.find_bar.case_cb.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if not self.editor.find(text, flags):
            cursor = self.editor.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            self.editor.setTextCursor(cursor)
            self.editor.find(text, flags)

    def _replace_once(self):
        text = self.find_bar.find_edit.text()
        repl = self.find_bar.replace_edit.text()
        if not text:
            return
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == text:
            cursor.insertText(repl)
        self._find_next()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, start_path: Optional[Path] = None):
        super().__init__()
        self.setWindowTitle("Aurora File Manager")
        self.resize(1200, 800)

        self.folder_tree = FolderTree(self)
        self.folder_tree.pathActivated.connect(self.on_folder_activated)
        self.folder_tree.selectionModel().selectionChanged.connect(self._on_folder_selection_changed)

        right = QtWidgets.QWidget(self)
        right.setLayout(QtWidgets.QVBoxLayout())
        right.layout().setContentsMargins(4, 4, 4, 4)
        # Simple navigation bar
        nav = QtWidgets.QHBoxLayout()
        self.back_btn = QtWidgets.QPushButton("◀")
        self.forward_btn = QtWidgets.QPushButton("▶")
        self.up_btn = QtWidgets.QPushButton("⬆")
        self.addr = QtWidgets.QLineEdit()
        self.breadcrumbs = Breadcrumbs(self)
        nav.addWidget(self.back_btn)
        nav.addWidget(self.forward_btn)
        nav.addWidget(self.up_btn)
        nav.addWidget(self.addr)
        right.layout().addLayout(nav)
        right.layout().addWidget(self.breadcrumbs)
        # Stacked views: icons and details
        self.files_icons = FilesView(self)
        self.files_details = FilesDetailsView(self)
        self.files_icons.fileActivated.connect(self.on_file_activated)
        self.files_details.fileActivated.connect(self.on_file_activated)
        self.files_stack = QtWidgets.QStackedWidget(self)
        self.files_stack.addWidget(self.files_icons)
        self.files_stack.addWidget(self.files_details)
        right.layout().addWidget(self.files_stack)

        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(self.folder_tree)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self._temp_zip: Optional[tuple[Path, str]] = None  # (zip_path, internal_path)

        # Initialize history BEFORE any directory set calls
        self.history: Optional[NavigationHistory] = None
        # Wire navigation buttons
        self.back_btn.clicked.connect(self._go_back)
        self.forward_btn.clicked.connect(self._go_forward)
        self.up_btn.clicked.connect(self._go_up)
        self.addr.returnPressed.connect(self._go_address)
        self.breadcrumbs.pathClicked.connect(self._go_breadcrumb)

        try:
            if start_path and start_path.exists():
                self._open_initial_path(start_path)
            else:
                # Default to showing home in files view
                self._set_directory(Path.home(), add_history=True)
        except Exception as ex:
            logging.exception("Failed during initial directory setup")
            QtWidgets.QMessageBox.warning(self, "Startup Error", str(ex))

        self._build_menu()

    # ------------------- Menu & Actions -------------------
    def _build_menu(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("File")
        act_new_window = file_menu.addAction("New Window")
        act_open_folder = file_menu.addAction("Open Folder...")
        act_open_zip = file_menu.addAction("Open ZIP...")
        file_menu.addSeparator()
        act_quit = file_menu.addAction("Quit")

        edit_menu = mb.addMenu("Edit")
        act_copy = edit_menu.addAction("Copy")
        act_cut = edit_menu.addAction("Cut")
        act_paste = edit_menu.addAction("Paste")
        act_rename = edit_menu.addAction("Rename...")
        act_delete = edit_menu.addAction("Delete (Recycle Bin)")
        act_duplicate = edit_menu.addAction("Duplicate")

        view_menu = mb.addMenu("View")
        act_toggle_theme = view_menu.addAction("Toggle Dark/Light")
        view_menu.addSeparator()
        self.act_view_icons = view_menu.addAction("Large Icons")
        self.act_view_details = view_menu.addAction("Details")
        self.act_view_icons.setCheckable(True)
        self.act_view_details.setCheckable(True)
        self.act_view_icons.setChecked(True)
        self.view_group = QtGui.QActionGroup(self)
        self.view_group.setExclusive(True)
        self.view_group.addAction(self.act_view_icons)
        self.view_group.addAction(self.act_view_details)
        self.act_view_icons.triggered.connect(lambda: self._set_view_mode("icons"))
        self.act_view_details.triggered.connect(lambda: self._set_view_mode("details"))
        view_menu.addSeparator()
        sort_menu = view_menu.addMenu("Sort By")
        for label, col in [("Name", 0), ("Size", 1), ("Type", 2), ("Date", 3)]:
            a = sort_menu.addAction(label)
            a.triggered.connect(lambda _=False, c=col: self._sort_by(c))

        tools_menu = mb.addMenu("Tools")
        act_monitor = tools_menu.addAction("Monitor Folder for Quick Replace...")
        act_recent = tools_menu.addAction("Open Recent...")
        act_search = tools_menu.addAction("Search (names + content)...")
        tools_menu.addSeparator()
        act_batch_rename = tools_menu.addAction("Batch Rename...")
        act_split_view = tools_menu.addAction("Toggle Split View")

        act_new_window.triggered.connect(self._new_window)
        act_open_folder.triggered.connect(self._open_folder)
        act_open_zip.triggered.connect(self._open_zip)
        act_quit.triggered.connect(QtWidgets.QApplication.instance().quit)

        act_copy.triggered.connect(lambda: self._clipboard_op("copy"))
        act_cut.triggered.connect(lambda: self._clipboard_op("cut"))
        act_paste.triggered.connect(self._paste_into_current())
        act_rename.triggered.connect(self._rename_selected)
        act_delete.triggered.connect(self._delete_selected)
        act_duplicate.triggered.connect(self._duplicate_selected)

        act_toggle_theme.triggered.connect(self._toggle_theme)

        act_monitor.triggered.connect(self._monitor_folder)
        act_recent.triggered.connect(self._open_recent)
        act_search.triggered.connect(self._open_search_dialog)
        act_batch_rename.triggered.connect(self._batch_rename)
        act_split_view.triggered.connect(self._toggle_split_view)

    # ------------------- Navigation -------------------
    def on_folder_activated(self, path: Path):
        if path.is_dir():
            self._set_directory(path)
            self._add_recent(path)

    def _on_folder_selection_changed(self, selected, deselected):
        # Update files view to current folder of selection
        idxs = self.folder_tree.selectionModel().selectedRows()
        if idxs:
            p = Path(self.folder_tree.model_fs.filePath(idxs[0]))
            if p.exists() and p.is_dir():
                self._set_directory(p)

    def _go_back(self):
        self.history.back()

    def _go_forward(self):
        self.history.forward()

    def _go_up(self):
        current_dir = Path(self.addr.text()).resolve()
        parent = current_dir.parent if current_dir.exists() else Path.home()
        if parent == current_dir:
            return
        self._set_directory(parent)

    def _go_address(self):
        p = Path(self.addr.text()).expanduser()
        if p.exists() and p.is_dir():
            self._set_directory(p)

    def _go_breadcrumb(self, path: Path):
        if path.exists() and path.is_dir():
            self._set_directory(path)

    def _on_history_changed(self, path: Path):
        # Do not push again into history here; just reflect
        self._apply_directory(path)
        try:
            self.back_btn.setEnabled(self.history.can_back())
            self.forward_btn.setEnabled(self.history.can_forward())
        except Exception:
            pass

    def _set_directory(self, path: Path, add_history: bool = True):
        # Lazy init of history on first set
        if self.history is None:
            try:
                self.history = NavigationHistory(path)
                self.history.changed.connect(self._on_history_changed)
            except Exception:
                logging.exception("Failed to initialize navigation history")
            # First apply without pushing back
            self._apply_directory(path)
            self.back_btn.setEnabled(False)
            self.forward_btn.setEnabled(False)
            return
        if add_history:
            try:
                self.history.push(path)
            except Exception:
                logging.exception("History push failed")
        self._apply_directory(path)
        try:
            self.back_btn.setEnabled(self.history.can_back())
            self.forward_btn.setEnabled(self.history.can_forward())
        except Exception:
            pass

    def _apply_directory(self, path: Path):
        self.files_icons.set_directory(path)
        self.files_details.set_directory(path)
        self.addr.setText(str(path))
        self.breadcrumbs.set_path(path)

    # ------------------- Actions -------------------
    def _new_window(self):
        w = MainWindow()
        w.show()

    def _open_folder(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", str(Path.home()))
        if d:
            self._set_directory(Path(d))
            self._add_recent(Path(d))

    def _open_zip(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open ZIP", str(Path.home()), "ZIP Files (*.zip)")
        if f:
            self._browse_zip(Path(f))
            self._add_recent(Path(f))

    def _clipboard_op(self, mode: str):
        paths = self.files_icons.selected_paths() or self.files_details.selected_paths()
        if not paths:
            return
        mime = QtCore.QMimeData()
        urls = [QtCore.QUrl.fromLocalFile(str(p)) for p in paths]
        mime.setUrls(urls)
        mime.setText("\n".join(str(p) for p in paths))
        cb = QtWidgets.QApplication.clipboard()
        cb.setMimeData(mime, cb.Clipboard)
        cb.setText("\n".join(str(p) for p in paths))
        cb.setProperty("aurora_cut", mode == "cut")

    def _paste_into_current(self):
        def handler():
            idx = self.files_icons.rootIndex() if self.files_stack.currentWidget() is self.files_icons else self.files_details.rootIndex()
            model = self.files_icons.model_fs if self.files_stack.currentWidget() is self.files_icons else self.files_details.model_fs
            target_dir = Path(model.filePath(idx))
            if not target_dir.exists() or target_dir.is_file():
                target_dir = target_dir.parent if target_dir.exists() else Path.home()
            cb = QtWidgets.QApplication.clipboard()
            mime = cb.mimeData()
            urls = mime.urls()
            if not urls:
                return
            src_paths = [Path(u.toLocalFile()) for u in urls]
            cut = bool(cb.property("aurora_cut"))
            if cut:
                move_with_progress(src_paths, target_dir, self)
                cb.setProperty("aurora_cut", False)
            else:
                copy_with_progress(src_paths, target_dir, self)
        return handler

    def _rename_selected(self):
        paths = self.files_icons.selected_paths() or self.files_details.selected_paths()
        if len(paths) != 1:
            return
        path = paths[0]
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename", "New name:", text=path.name)
        if ok and new_name:
            target = path.with_name(new_name)
            try:
                path.rename(target)
            except Exception as ex:
                QtWidgets.QMessageBox.warning(self, "Rename Error", str(ex))

    def _delete_selected(self):
        paths = self.files_icons.selected_paths() or self.files_details.selected_paths()
        if not paths:
            return
        if QtWidgets.QMessageBox.question(self, "Delete", f"Send {len(paths)} item(s) to Recycle Bin?") != QtWidgets.QMessageBox.Yes:
            return
        for p in paths:
            try:
                send2trash(str(p))
            except Exception as ex:
                QtWidgets.QMessageBox.warning(self, "Delete Error", f"{p}: {ex}")

    def _duplicate_selected(self):
        paths = self.files_icons.selected_paths() or self.files_details.selected_paths()
        for p in paths:
            dst = p.with_name(f"{p.stem} copy{p.suffix}")
            try:
                if p.is_dir():
                    shutil.copytree(p, dst)
                else:
                    shutil.copy2(p, dst)
            except Exception as ex:
                QtWidgets.QMessageBox.warning(self, "Duplicate Error", f"{p}: {ex}")

    def _toggle_theme(self):
        if SETTINGS.get("theme", "dark") == "dark":
            SETTINGS["theme"] = "light"
            QtWidgets.QApplication.instance().setPalette(QtWidgets.QApplication.style().standardPalette())
        else:
            SETTINGS["theme"] = "dark"
            apply_dark_theme(QtWidgets.QApplication.instance())
        save_json(SETTINGS_PATH, SETTINGS)

    def _monitor_folder(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Monitor Folder", str(Path.home()))
        if not d:
            return
        watcher = QtCore.QFileSystemWatcher(self)
        watcher.addPath(d)
        def on_changed(_):
            QtWidgets.QMessageBox.information(self, "Folder Changed", f"New or updated files in: {d}")
        watcher.directoryChanged.connect(on_changed)
        QtWidgets.QMessageBox.information(self, "Monitoring", f"Now watching: {d}")

    def _open_recent(self):
        items = [str(p) for p in RECENTS.get("folders", [])]
        if not items:
            QtWidgets.QMessageBox.information(self, "Recent", "No recent items")
            return
        item, ok = QtWidgets.QInputDialog.getItem(self, "Open Recent", "Select:", items, 0, False)
        if ok and item:
            p = Path(item)
            if p.suffix.lower() == ".zip":
                self._browse_zip(p)
            elif p.is_dir():
                self._set_directory(p)

    def _add_recent(self, path: Path):
        items = RECENTS.get("folders", [])
        s = str(path)
        if s in items:
            items.remove(s)
        items.insert(0, s)
        RECENTS["folders"] = items[:12]
        save_json(RECENTS_PATH, RECENTS)

    # ------------------- Open Paths -------------------
    def on_file_activated(self, path: Path):
        if path.suffix.lower() == ".zip":
            self._browse_zip(path)
            self._add_recent(path)
        else:
            self._open_file_external(path)

    def _browse_zip(self, zip_path: Path):
        items = zip_list(zip_path)
        item, ok = QtWidgets.QInputDialog.getItem(self, f"Open in {zip_path.name}", "Select file:", items, 0, False)
        if ok and item:
            content = zip_read(zip_path, item)
            ed = EditorWindow(Path(f"{zip_path}:{item}"), content, zip_ctx=(zip_path, item))
            ed.show()

    def _open_file_external(self, path: Path):
        try:
            ed = EditorWindow(path)
            ed.show()
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self, "Open Error", str(ex))

    # ------------------- Global Search -------------------
    def _open_search_dialog(self):
        dlg = SearchDialog(self)
        dlg.exec()

    # ------------------- View & Sorting -------------------
    def _set_view_mode(self, mode: str):
        if mode == "icons":
            self.files_stack.setCurrentWidget(self.files_icons)
            self.act_view_icons.setChecked(True)
        else:
            self.files_stack.setCurrentWidget(self.files_details)
            self.act_view_details.setChecked(True)

    def _sort_by(self, column: int):
        # Sort only affects details view; icons use default order
        self.files_details.sortByColumn(column, QtCore.Qt.AscendingOrder)

    # ------------------- Batch Rename -------------------
    def _batch_rename(self):
        paths = self.files_icons.selected_paths() or self.files_details.selected_paths()
        if not paths:
            QtWidgets.QMessageBox.information(self, "Batch Rename", "Select files to rename in the files view.")
            return
        dlg = BatchRenameDialog(paths, self)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            for old, new in dlg.get_operations():
                try:
                    ensure_backup(old)
                    old.rename(new)
                except Exception as ex:
                    QtWidgets.QMessageBox.warning(self, "Rename Error", f"{old} -> {new}: {ex}")

    # ------------------- Split View -------------------
    def _toggle_split_view(self):
        # Replace right pane with a splitter containing current stack duplicated
        parent = self.files_stack.parent()
        if isinstance(parent, QtWidgets.QSplitter) and parent.count() == 2:
            # Already split
            # Remove second pane
            if hasattr(self, "files_stack2") and self.files_stack2 is not None:
                w = self.files_stack2
                self.files_stack2 = None
                w.setParent(None)
            return
        # Create a new details+icons stack as second pane
        self.files_icons2 = FilesView(self)
        self.files_details2 = FilesDetailsView(self)
        self.files_icons2.fileActivated.connect(self.on_file_activated)
        self.files_details2.fileActivated.connect(self.on_file_activated)
        self.files_stack2 = QtWidgets.QStackedWidget(self)
        self.files_stack2.addWidget(self.files_icons2)
        self.files_stack2.addWidget(self.files_details2)
        # Put into splitter
        splitter: QtWidgets.QSplitter = self.centralWidget()  # left folder + right container
        right_container = splitter.widget(1)
        new_right_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        # Take existing right container's files_stack
        layout = right_container.layout()
        layout.addWidget(new_right_splitter)
        new_right_splitter.addWidget(self.files_stack)
        new_right_splitter.addWidget(self.files_stack2)
        new_right_splitter.setSizes([1, 1])


class BatchRenameDialog(QtWidgets.QDialog):
    def __init__(self, paths: List[Path], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Rename")
        self.resize(700, 500)
        self.paths = paths
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QHBoxLayout()
        self.find_edit = QtWidgets.QLineEdit()
        self.find_edit.setPlaceholderText("Find (supports * wildcard)")
        self.replace_edit = QtWidgets.QLineEdit()
        self.replace_edit.setPlaceholderText("Replace with (use {n} for numbering)")
        self.start_spin = QtWidgets.QSpinBox()
        self.start_spin.setMinimum(1)
        self.start_spin.setPrefix("Start # ")
        go_btn = QtWidgets.QPushButton("Preview")
        form.addWidget(self.find_edit)
        form.addWidget(self.replace_edit)
        form.addWidget(self.start_spin)
        form.addWidget(go_btn)
        layout.addLayout(form)
        self.list = QtWidgets.QTableWidget(0, 2)
        self.list.setHorizontalHeaderLabels(["From", "To"])
        self.list.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.list)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(btns)
        go_btn.clicked.connect(self._preview)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

    def _preview(self):
        self.list.setRowCount(0)
        pattern = self.find_edit.text()
        repl = self.replace_edit.text()
        start = self.start_spin.value()
        counter = start
        from fnmatch import fnmatch
        for p in self.paths:
            name = p.name
            if not pattern or fnmatch(name, pattern):
                new_name = repl.replace("{n}", f"{counter}") if repl else name
                target = p.with_name(new_name)
                row = self.list.rowCount()
                self.list.insertRow(row)
                self.list.setItem(row, 0, QtWidgets.QTableWidgetItem(str(p)))
                self.list.setItem(row, 1, QtWidgets.QTableWidgetItem(str(target)))
                counter += 1

    def get_operations(self) -> List[tuple[Path, Path]]:
        ops: List[tuple[Path, Path]] = []
        for row in range(self.list.rowCount()):
            old = Path(self.list.item(row, 0).text())
            new = Path(self.list.item(row, 1).text())
            if old != new:
                ops.append((old, new))
        return ops


class SearchDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search")
        self.resize(800, 500)
        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QHBoxLayout()
        self.root_edit = QtWidgets.QLineEdit(str(Path.home()))
        browse_btn = QtWidgets.QPushButton("Browse...")
        self.query_edit = QtWidgets.QLineEdit()
        self.query_edit.setPlaceholderText("Search text (leave empty for name-only search)")
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Name includes (e.g., .cs;shader;*.py)")
        self.case_cb = QtWidgets.QCheckBox("Match case")
        self.content_cb = QtWidgets.QCheckBox("Search file contents")
        self.content_cb.setChecked(True)
        go_btn = QtWidgets.QPushButton("Search")
        form.addWidget(QtWidgets.QLabel("Root:"))
        form.addWidget(self.root_edit)
        form.addWidget(browse_btn)
        form.addWidget(QtWidgets.QLabel("Name:"))
        form.addWidget(self.name_edit)
        form.addWidget(QtWidgets.QLabel("Text:"))
        form.addWidget(self.query_edit)
        form.addWidget(self.case_cb)
        form.addWidget(self.content_cb)
        form.addWidget(go_btn)

        layout.addLayout(form)

        self.results = QtWidgets.QListWidget()
        layout.addWidget(self.results)

        browse_btn.clicked.connect(self._browse_root)
        go_btn.clicked.connect(self._run_search)
        self.results.itemDoubleClicked.connect(self._open_result)

    def _browse_root(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Search Root", self.root_edit.text())
        if d:
            self.root_edit.setText(d)

    def _matches_name(self, name: str, pattern_str: str) -> bool:
        if not pattern_str:
            return True
        patterns = [p.strip() for p in pattern_str.split(';') if p.strip()]
        for p in patterns:
            if '*' in p or '?' in p:
                from fnmatch import fnmatch
                if fnmatch(name, p):
                    return True
            else:
                if p.lower() in name.lower():
                    return True
        return False

    def _run_search(self):
        self.results.clear()
        root = Path(self.root_edit.text()).expanduser()
        if not root.exists():
            return
        name_filter = self.name_edit.text()
        text_query = self.query_edit.text()
        match_case = self.case_cb.isChecked()
        search_content = self.content_cb.isChecked()
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if not self._matches_name(fn, name_filter):
                    continue
                full = Path(dirpath) / fn
                display = str(full)
                if search_content and text_query:
                    try:
                        data = full.read_text(encoding='utf-8', errors='ignore')
                        hay = data if match_case else data.lower()
                        needle = text_query if match_case else text_query.lower()
                        if needle in hay:
                            self.results.addItem(display)
                    except Exception:
                        continue
                else:
                    self.results.addItem(display)

    def _open_result(self, item: QtWidgets.QListWidgetItem):
        path = Path(item.text())
        mw: MainWindow = self.parent()  # type: ignore
        mw._open_file_external(path)
        self.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    if SETTINGS.get("theme", "dark") == "dark":
        apply_dark_theme(app)

    # Global exception hook to log and show errors
    def handle_exception(exc_type, exc_value, exc_traceback):
        try:
            traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logging.error("Unhandled exception:\n%s", traceback_str)
            QtWidgets.QMessageBox.critical(None, "Unhandled Error", traceback_str[:2000])
        except Exception:
            pass
    sys.excepthook = handle_exception

    w = MainWindow()
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()