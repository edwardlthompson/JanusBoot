"""Backup JanusBoot ESP JSON before destructive writes."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from janusbootctl.paths import entries_path, janus_dir, settings_path


def backup_esp(esp_root: Path, *, stamp: str | None = None) -> Path:
    """Copy settings.json and entries.json into EFI/JanusBoot/backup/."""
    when = stamp or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    dest = janus_dir(esp_root) / "backup" / when
    dest.mkdir(parents=True, exist_ok=True)
    for src in (settings_path(esp_root), entries_path(esp_root)):
        if src.is_file():
            shutil.copy2(src, dest / src.name)
    return dest
