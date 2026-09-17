"""Pure ESP/boot path heuristics (Phase 3). Never deletes foreign EFI files."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

# Relative to an ESP root (or a synthetic tree used in tests).
LINUX_EFI_CANDIDATES: tuple[str, ...] = (
    "EFI/ubuntu/shimx64.efi",
    "EFI/ubuntu/grubx64.efi",
    "EFI/debian/shimx64.efi",
    "EFI/debian/grubx64.efi",
    "EFI/fedora/shimx64.efi",
    "EFI/centos/shimx64.efi",
    "EFI/BOOT/BOOTX64.EFI",
    "EFI/systemd/systemd-bootx64.efi",
    "EFI/Limine/BOOTX64.EFI",
    "EFI/limine/BOOTX64.EFI",
)

WINDOWS_BOOTMGFW = "EFI/Microsoft/Boot/bootmgfw.efi"

_ID_SAFE = re.compile(r"[^a-z0-9]+")


def _slug(title: str, path: str) -> str:
    base = _ID_SAFE.sub("-", title.lower()).strip("-") or "entry"
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:8]
    return f"{base[:48]}-{digest}"


def classify_efi_path(rel: str) -> tuple[str, str, str]:
    """Return (type, title, icon) for a relative EFI path."""
    norm = rel.replace("\\", "/")
    lower = norm.lower()
    if lower.endswith("bootmgfw.efi") or "/microsoft/boot/" in lower:
        return "efi_chainload", "Windows Boot Manager", "windows"
    if "shim" in lower or "grub" in lower or "/ubuntu/" in lower or "/debian/" in lower:
        return "efi_chainload", "Linux", "linux"
    if "systemd-boot" in lower:
        return "efi_chainload", "systemd-boot", "linux"
    if "limine" in lower:
        return "efi_chainload", "Limine", "linux"
    if lower.endswith("bootx64.efi"):
        return "efi_chainload", "UEFI default", "firmware"
    return "efi_chainload", Path(norm).stem, "linux"


def discover_candidates(esp_root: Path) -> list[dict[str, Any]]:
    """Walk known heuristic paths under esp_root; never mutate the tree."""
    root = esp_root.resolve()
    found: list[dict[str, Any]] = []
    seen: set[str] = set()

    ordered = (WINDOWS_BOOTMGFW, *LINUX_EFI_CANDIDATES)
    for rel in ordered:
        candidate = root / Path(rel)
        if not candidate.is_file():
            continue
        key = rel.replace("\\", "/")
        if key in seen:
            continue
        seen.add(key)
        entry_type, title, icon = classify_efi_path(key)
        found.append(
            {
                "id": _slug(title, key),
                "title": title[:64],
                "subtitle": key[:128],
                "type": entry_type,
                "path": f"boot():/{key}",
                "icon": icon,
                "source": "scanned",
            }
        )
    return found


def entries_document(discovered: list[dict[str, Any]]) -> dict[str, Any]:
    """Build an entries.json document from discovered rows (manual fields stripped)."""
    entries: list[dict[str, Any]] = []
    for row in discovered:
        item = {
            "id": row["id"],
            "title": row["title"],
            "type": row["type"],
            "path": row["path"],
        }
        if row.get("subtitle"):
            item["subtitle"] = row["subtitle"]
        if row.get("icon"):
            item["icon"] = row["icon"]
        if row.get("source"):
            item["source"] = row["source"]
        entries.append(item)
    return {"schema_version": 1, "entries": entries}
