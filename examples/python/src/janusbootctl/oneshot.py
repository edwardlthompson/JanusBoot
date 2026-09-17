"""Super GRUB-like one-shot: vmlinuz+initrd → temporary Limine linux entry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from janusbootctl.paths import entries_path
from janusbootctl.validate import load_json

ONESHOT_ID = "oneshot-linux"


def build_oneshot_entry(
    vmlinuz: Path,
    *,
    initrd: Path | None = None,
    cmdline: str = "root=UUID=CHANGE_ME ro quiet",
    title: str = "One-shot Linux",
) -> dict[str, Any]:
    if not vmlinuz.is_file():
        raise FileNotFoundError(f"vmlinuz not found: {vmlinuz}")
    entry: dict[str, Any] = {
        "id": ONESHOT_ID,
        "title": title[:64],
        "subtitle": "Temporary rescue entry",
        "type": "linux",
        "path": str(vmlinuz.resolve()),
        "icon": "linux",
        "source": "manual",
        "hidden": False,
    }
    if initrd is not None:
        if not initrd.is_file():
            raise FileNotFoundError(f"initrd not found: {initrd}")
        entry["subtitle"] = f"initrd={initrd.name}; {cmdline}"[:128]
    else:
        entry["subtitle"] = cmdline[:128]
    return entry


def write_oneshot_entry(esp_root: Path, entry: dict[str, Any]) -> Path:
    """Insert/replace oneshot entry in entries.json (userspace only)."""
    path = entries_path(esp_root)
    doc = load_json(path) if path.is_file() else {"schema_version": 1, "entries": []}
    assert isinstance(doc, dict)
    entries = [
        e for e in doc.get("entries", []) if isinstance(e, dict) and e.get("id") != ONESHOT_ID
    ]
    entries.insert(0, entry)
    doc["schema_version"] = 1
    doc["entries"] = entries
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return path


def clear_oneshot_entry(esp_root: Path) -> bool:
    path = entries_path(esp_root)
    if not path.is_file():
        return False
    doc = load_json(path)
    assert isinstance(doc, dict)
    before = doc.get("entries", [])
    entries = [e for e in before if isinstance(e, dict) and e.get("id") != ONESHOT_ID]
    if len(entries) == len(before):
        return False
    doc["entries"] = entries
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return True
