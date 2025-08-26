"""
Zip Handler - Open ZIP archives as folders and save with .bak backup
"""

from __future__ import annotations

import os
import zipfile
import tempfile
import shutil
from pathlib import Path


class ZipHandler:
    """Lightweight ZIP access via temporary extraction and re-pack on save.

    This is a simple implementation to enable browsing/editing. For large zips
    or production-grade performance, consider indexed/streaming implementations.
    """

    def __init__(self) -> None:
        self.temp_root = Path(tempfile.gettempdir()) / "nova_zip_mounts"
        self.temp_root.mkdir(exist_ok=True)

    def mount(self, zip_path: str) -> str:
        """Extract a zip to a temp dir and return the mount path."""
        zip_path = str(Path(zip_path).resolve())
        mount_dir = self.temp_root / (Path(zip_path).stem + "_mount")
        if mount_dir.exists():
            shutil.rmtree(mount_dir, ignore_errors=True)
        mount_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(mount_dir)
        return str(mount_dir)

    def save(self, mount_dir: str, target_zip_path: str) -> None:
        """Repack the mounted dir back into the zip, keeping a .bak backup."""
        target = Path(target_zip_path)
        backup = target.with_suffix(target.suffix + ".bak")
        try:
            if target.exists():
                shutil.copy2(target, backup)
        except Exception:
            pass

        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(mount_dir):
                for file in files:
                    full_path = Path(root) / file
                    arcname = str(Path(root).relative_to(mount_dir) / file)
                    zf.write(full_path, arcname)

