"""
Clipboard Manager - Handles cross-window cut/copy state for files
"""

from __future__ import annotations

from typing import List, Optional
from dataclasses import dataclass
from PySide6.QtWidgets import QApplication
import pyperclip


@dataclass
class ClipboardPayload:
    file_paths: List[str]
    is_cut: bool


class ClipboardManager:
    """Process-wide clipboard for file cut/copy/paste across app windows."""

    _KEY = "__nova_explorer_clipboard_payload__"

    def __init__(self) -> None:
        # nothing to init; we store on QApplication instance to be cross-window
        pass

    def _get_app_store(self) -> dict:
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("QApplication instance not available")
        if not hasattr(app, self._KEY):
            setattr(app, self._KEY, {})
        return getattr(app, self._KEY)

    def copy_files(self, file_paths: List[str]) -> None:
        payload = ClipboardPayload(file_paths=list(file_paths), is_cut=False)
        store = self._get_app_store()
        store["payload"] = payload
        # also write plain text for convenience outside the app
        try:
            pyperclip.copy("\n".join(file_paths))
        except Exception:
            pass

    def cut_files(self, file_paths: List[str]) -> None:
        payload = ClipboardPayload(file_paths=list(file_paths), is_cut=True)
        store = self._get_app_store()
        store["payload"] = payload
        try:
            pyperclip.copy("\n".join(file_paths))
        except Exception:
            pass

    def get_files(self) -> Optional[ClipboardPayload]:
        store = self._get_app_store()
        return store.get("payload")

    def clear(self) -> None:
        store = self._get_app_store()
        store.pop("payload", None)

