"""
File Operations - copy/move/paste/delete/duplicate with progress and recycle bin
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterable, List

from PySide6.QtWidgets import QProgressDialog
from PySide6.QtCore import Qt

try:
    import send2trash  # optional, safer delete
    HAS_TRASH = True
except Exception:
    HAS_TRASH = False


class FileOperations:
    """High-level file operations with basic progress UI."""

    def paste_files(self, payload, destination_dir: str) -> None:
        dest = Path(destination_dir)
        dest.mkdir(parents=True, exist_ok=True)
        file_paths: List[str] = payload.file_paths if hasattr(payload, 'file_paths') else list(payload)
        is_cut = getattr(payload, 'is_cut', False)

        progress = QProgressDialog("Processing files...", "Cancel", 0, len(file_paths))
        progress.setWindowModality(Qt.ApplicationModal)
        progress.show()

        for index, src_str in enumerate(file_paths, start=1):
            progress.setValue(index - 1)
            if progress.wasCanceled():
                break

            src = Path(src_str)
            dst = dest / src.name

            try:
                if src.is_dir():
                    if is_cut:
                        shutil.move(str(src), str(dst))
                    else:
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                else:
                    if is_cut:
                        shutil.move(str(src), str(dst))
                    else:
                        shutil.copy2(str(src), str(dst))
            except Exception:
                # continue other files
                pass

        progress.setValue(len(file_paths))

    def delete_files(self, file_paths: Iterable[str]) -> None:
        for path_str in file_paths:
            path = Path(path_str)
            try:
                if HAS_TRASH:
                    send2trash.send2trash(str(path))
                else:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink(missing_ok=True)
            except Exception:
                pass

    def duplicate(self, path_str: str) -> str:
        path = Path(path_str)
        base = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        while True:
            candidate = parent / f"{base} - Copy{'' if counter == 1 else f' ({counter})'}{suffix}"
            if not candidate.exists():
                break
            counter += 1
        if path.is_dir():
            shutil.copytree(path, candidate)
        else:
            shutil.copy2(path, candidate)
        return str(candidate)

