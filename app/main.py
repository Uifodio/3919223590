import os
import sys
import json
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional

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


class ProgressDialog(QtWidgets.QProgressDialog):
    def __init__(self, title: str, label: str, parent=None):
        super().__init__(label, "Cancel", 0, 100, parent)
        self.setWindowTitle(title)
        self.setAutoClose(True)
        self.setAutoReset(True)
        self.setMinimumDuration(400)


def ensure_backup(path: Path) -> None:
    try:
        if path.exists():
            bak = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, bak)
    except Exception:
        pass


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

    def open_path(self, path: Path, text: Optional[str] = None) -> None:
        self._path = path
        if text is None:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception as ex:
                QtWidgets.QMessageBox.warning(self, "Open Error", str(ex))
                return
        self.setPlainText(text)
        self.document().setModified(False)

    def save(self) -> bool:
        if not self._path:
            return False
        try:
            # Only backup real filesystem files, not virtual zip pseudo-paths
            p = self._path
            if p.exists() and p.is_file():
                ensure_backup(p)
            p.write_text(self.toPlainText(), encoding="utf-8")
            self.document().setModified(False)
            return True
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self, "Save Error", str(ex))
            return False

    def _maybe_autosave(self) -> None:
        if SETTINGS.get("editor_autosave", True) and self.document().isModified():
            self.save()


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
class FileTree(QtWidgets.QTreeView):
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
        self.model_fs.setRootPath(str(Path.home()))
        self.setModel(self.model_fs)
        self.setRootIndex(self.model_fs.index(str(Path.home())))

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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, start_path: Optional[Path] = None):
        super().__init__()
        self.setWindowTitle("Aurora File Manager")
        self.resize(1200, 800)

        self.editor = CodeEditor(self)
        self.find_bar = FindReplaceBar(self)
        self.find_bar.setVisible(False)

        self.file_tree = FileTree(self)
        self.file_tree.pathActivated.connect(self.on_path_activated)

        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(self.file_tree)
        right = QtWidgets.QWidget(self)
        right.setLayout(QtWidgets.QVBoxLayout())
        right.layout().setContentsMargins(0, 0, 0, 0)
        right.layout().addWidget(self.find_bar)
        right.layout().addWidget(self.editor)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self._temp_zip: Optional[tuple[Path, str]] = None  # (zip_path, internal_path)

        self._build_menu()
        self._wire_find_replace()

        if start_path and start_path.exists():
            self._open_initial_path(start_path)

    # ------------------- Menu & Actions -------------------
    def _build_menu(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("File")
        act_new_window = file_menu.addAction("New Window")
        act_open_folder = file_menu.addAction("Open Folder...")
        act_open_zip = file_menu.addAction("Open ZIP...")
        file_menu.addSeparator()
        act_save = file_menu.addAction("Save")
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
        act_find = view_menu.addAction("Find/Replace")
        act_toggle_theme = view_menu.addAction("Toggle Dark/Light")

        tools_menu = mb.addMenu("Tools")
        act_monitor = tools_menu.addAction("Monitor Folder for Quick Replace...")
        act_recent = tools_menu.addAction("Open Recent...")
        act_search = tools_menu.addAction("Search (names + content)...")

        act_new_window.triggered.connect(self._new_window)
        act_open_folder.triggered.connect(self._open_folder)
        act_open_zip.triggered.connect(self._open_zip)
        act_save.triggered.connect(self._save_editor)
        act_quit.triggered.connect(QtWidgets.QApplication.instance().quit)

        act_copy.triggered.connect(lambda: self._clipboard_op("copy"))
        act_cut.triggered.connect(lambda: self._clipboard_op("cut"))
        act_paste.triggered.connect(self._paste_into_current())
        act_rename.triggered.connect(self._rename_selected)
        act_delete.triggered.connect(self._delete_selected)
        act_duplicate.triggered.connect(self._duplicate_selected)

        act_find.triggered.connect(lambda: self.find_bar.setVisible(not self.find_bar.isVisible()))
        act_toggle_theme.triggered.connect(self._toggle_theme)

        act_monitor.triggered.connect(self._monitor_folder)
        act_recent.triggered.connect(self._open_recent)
        act_search.triggered.connect(self._open_search_dialog)

    def _wire_find_replace(self):
        self.find_bar.next_btn.clicked.connect(self._find_next)
        self.find_bar.replace_btn.clicked.connect(self._replace_once)

    def _open_initial_path(self, path: Path):
        if path.is_dir():
            self.file_tree.setRootIndex(self.file_tree.model_fs.index(str(path)))
        elif path.is_file():
            self._open_file(path)

    # ------------------- Actions -------------------
    def _new_window(self):
        w = MainWindow()
        w.show()

    def _open_folder(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", str(Path.home()))
        if d:
            self.file_tree.setRootIndex(self.file_tree.model_fs.index(d))
            self._add_recent(Path(d))

    def _open_zip(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open ZIP", str(Path.home()), "ZIP Files (*.zip)")
        if f:
            self._browse_zip(Path(f))
            self._add_recent(Path(f))

    def _save_editor(self):
        if self._temp_zip:
            zip_path, internal_path = self._temp_zip
            try:
                zip_write_with_backup(zip_path, internal_path, self.editor.toPlainText())
                self.editor.document().setModified(False)
                QtWidgets.QMessageBox.information(self, "Saved", f"Saved into {zip_path.name}:{internal_path}\nBackup created.")
            except Exception as ex:
                QtWidgets.QMessageBox.warning(self, "Save Error", str(ex))
        else:
            if self.editor.save():
                QtWidgets.QMessageBox.information(self, "Saved", "File saved.")

    def _clipboard_op(self, mode: str):
        paths = self.file_tree.selected_paths()
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
            idx = self.file_tree.currentIndex()
            target_dir = Path(self.file_tree.model_fs.filePath(idx))
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
        paths = self.file_tree.selected_paths()
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
        paths = self.file_tree.selected_paths()
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
        paths = self.file_tree.selected_paths()
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
            # A simple notification; drag and drop will handle replacement
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
                self.file_tree.setRootIndex(self.file_tree.model_fs.index(str(p)))

    def _add_recent(self, path: Path):
        items = RECENTS.get("folders", [])
        s = str(path)
        if s in items:
            items.remove(s)
        items.insert(0, s)
        RECENTS["folders"] = items[:12]
        save_json(RECENTS_PATH, RECENTS)

    # ------------------- Open Paths -------------------
    def on_path_activated(self, path: Path):
        if path.is_dir():
            return
        if path.suffix.lower() == ".zip":
            self._browse_zip(path)
            self._add_recent(path)
        else:
            self._open_file(path)

    def _open_file(self, path: Path):
        try:
            self._temp_zip = None
            self.editor.open_path(path)
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self, "Open Error", str(ex))

    def _browse_zip(self, zip_path: Path):
        items = zip_list(zip_path)
        item, ok = QtWidgets.QInputDialog.getItem(self, f"Open in {zip_path.name}", "Select file:", items, 0, False)
        if ok and item:
            content = zip_read(zip_path, item)
            self.editor.open_path(Path(f"{zip_path}:{item}"), content)
            self._temp_zip = (zip_path, item)

    # ------------------- Find/Replace -------------------
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

    # ------------------- Global Search -------------------
    def _open_search_dialog(self):
        dlg = SearchDialog(self)
        dlg.exec()


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
        mw._open_file(path)
        self.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    if SETTINGS.get("theme", "dark") == "dark":
        apply_dark_theme(app)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()