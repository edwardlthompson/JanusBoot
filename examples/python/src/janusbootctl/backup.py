"""Backup JanusBoot ESP JSON + optional NVRAM dump artifacts."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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


def write_nvram_dump_stub(
    esp_root: Path,
    *,
    dump_text: str | None = None,
    stamp: str | None = None,
) -> Path:
    """Store an NVRAM dump text under backup/ (host tool fills dump_text)."""
    when = stamp or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    dest = janus_dir(esp_root) / "backup" / f"nvram-{when}"
    dest.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "nvram_dump",
        "when": when,
        "source": "janusbootctl",
        "note": "LOCAL wires efibootmgr -v / firmware export into dump.txt",
    }
    (dest / "meta.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    text = dump_text if dump_text is not None else "# placeholder — LOCAL host dump not attached\n"
    (dest / "dump.txt").write_text(text, encoding="utf-8")
    return dest


def backup_with_nvram(
    esp_root: Path,
    *,
    nvram_dump: str | None = None,
    stamp: str | None = None,
) -> dict[str, str]:
    """Settings/entries backup plus NVRAM dump folder."""
    when = stamp or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_dir = backup_esp(esp_root, stamp=when)
    nvram_dir = write_nvram_dump_stub(esp_root, dump_text=nvram_dump, stamp=when)
    return {"settings_backup": str(json_dir), "nvram_backup": str(nvram_dir)}
