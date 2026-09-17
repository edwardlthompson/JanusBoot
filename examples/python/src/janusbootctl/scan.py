"""ESP/boot discovery: heuristics + recursive walk. Never deletes foreign EFI."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

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
    "EFI/JanusBoot/BOOTX64.EFI",
)

WINDOWS_BOOTMGFW = "EFI/Microsoft/Boot/bootmgfw.efi"
_ID_SAFE = re.compile(r"[^a-z0-9]+")


def _slug(title: str, path: str) -> str:
    base = _ID_SAFE.sub("-", title.lower()).strip("-") or "entry"
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:8]
    return f"{base[:48]}-{digest}"


def classify_efi_path(rel: str) -> tuple[str, str, str]:
    """Return (type, title, icon) for a relative EFI path."""
    lower = rel.replace("\\", "/").lower()
    if lower.endswith("bootmgfw.efi") or "/microsoft/boot/" in lower:
        return "efi_chainload", "Windows Boot Manager", "windows"
    if "shim" in lower or "grub" in lower or "/ubuntu/" in lower or "/debian/" in lower:
        return "efi_chainload", "Linux", "linux"
    if "systemd-boot" in lower:
        return "efi_chainload", "systemd-boot", "linux"
    if "limine" in lower or "/janusboot/" in lower:
        return "efi_chainload", "Limine", "linux"
    if lower.endswith("bootx64.efi"):
        return "efi_chainload", "UEFI default", "firmware"
    return "efi_chainload", Path(rel).stem[:64], "linux"


def _row(rel: str) -> dict[str, Any]:
    key = rel.replace("\\", "/")
    entry_type, title, icon = classify_efi_path(key)
    return {
        "id": _slug(title, key),
        "title": title[:64],
        "subtitle": key[:128],
        "type": entry_type,
        "path": f"boot():/{key}",
        "icon": icon,
        "source": "scanned",
    }


def discover_heuristic(esp_root: Path) -> list[dict[str, Any]]:
    """Fixed known paths (rEFInd-style short list)."""
    root = esp_root.resolve()
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rel in (WINDOWS_BOOTMGFW, *LINUX_EFI_CANDIDATES):
        key = rel.replace("\\", "/")
        if key in seen or not (root / Path(rel)).is_file():
            continue
        seen.add(key)
        found.append(_row(key))
    return found


def discover_recursive(esp_root: Path, *, max_files: int = 256) -> list[dict[str, Any]]:
    """Recursive ESP walk for *.efi under EFI/ (never mutates)."""
    root = esp_root.resolve()
    efi = root / "EFI"
    if not efi.is_dir():
        return []
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted({*efi.rglob("*.efi"), *efi.rglob("*.EFI")}):
        if len(found) >= max_files or not path.is_file():
            continue
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if rel not in seen:
            seen.add(rel)
            found.append(_row(rel))
    return found


def discover_candidates(esp_root: Path, *, deep: bool = True) -> list[dict[str, Any]]:
    """Merge heuristics with optional recursive walk; stable unique by path."""
    by_path: dict[str, dict[str, Any]] = {}
    for row in discover_heuristic(esp_root):
        by_path[str(row["path"])] = row
    if deep:
        for row in discover_recursive(esp_root):
            by_path.setdefault(str(row["path"]), row)
    return list(by_path.values())


def empty_disk_entries() -> list[dict[str, Any]]:
    """Calm empty-disk actions (not panic)."""
    return [
        {
            "id": "empty-scan",
            "title": "Scan again",
            "subtitle": "No OS loaders found on this ESP",
            "type": "tool",
            "path": "boot():/EFI/JanusBoot/BOOTX64.EFI",
            "icon": "gear",
            "source": "manual",
        },
        {
            "id": "empty-firmware",
            "title": "Firmware setup",
            "subtitle": "Open UEFI settings",
            "type": "firmware",
            "path": "boot():/EFI/BOOT/BOOTX64.EFI",
            "icon": "firmware",
            "source": "manual",
            "hidden": False,
        },
    ]


def entries_document(discovered: list[dict[str, Any]]) -> dict[str, Any]:
    """Build entries.json from discovered rows; empty → calm placeholders."""
    rows = discovered or empty_disk_entries()
    entries: list[dict[str, Any]] = []
    for row in rows:
        item = {
            "id": row["id"],
            "title": row["title"],
            "type": row["type"],
            "path": row["path"],
        }
        for key in ("subtitle", "icon", "source", "hidden"):
            if key in row and row[key] is not None:
                item[key] = row[key]
        entries.append(item)
    return {"schema_version": 1, "entries": entries}
