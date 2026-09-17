"""Calm btrfs / Timeshift card stubs — detect only; never hostile unlock."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def detect_btrfs_snapshots(root: Path) -> list[dict[str, Any]]:
    """Look for common Timeshift / snapper layout markers under root."""
    cards: list[dict[str, Any]] = []
    candidates = (
        root / "timeshift" / "snapshots",
        root / "timeshift-btrfs" / "snapshots",
        root / ".snapshots",
        root / "btrfs" / "snapshots",
    )
    for path in candidates:
        if not path.is_dir():
            continue
        kids = [p for p in path.iterdir() if p.is_dir()]
        label = "Timeshift" if "timeshift" in str(path).lower() else "btrfs snapshot"
        cards.append(
            {
                "id": f"snapshot-{path.name.lower()}",
                "title": f"{label} ({len(kids)} found)",
                "subtitle": "Read-only browse — unlock stays in the OS",
                "type": "tool",
                "path": f"host():/{path.as_posix().lstrip('/')}",
                "icon": "repair",
                "source": "snapshot-stub",
                "calm": True,
            }
        )
    return cards


def snapshot_entries_document(cards: list[dict[str, Any]]) -> dict[str, Any]:
    """Wrap detected cards; empty → calm empty state (no fake unlock CTA)."""
    if not cards:
        return {
            "schema_version": 1,
            "entries": [
                {
                    "id": "no-snapshots",
                    "title": "No snapshots detected",
                    "subtitle": "Insert a Timeshift/btrfs volume and refresh",
                    "type": "tool",
                    "path": "boot():/EFI/JanusBoot/BOOTX64.EFI",
                    "icon": "repair",
                    "source": "snapshot-stub",
                    "calm": True,
                }
            ],
        }
    return {"schema_version": 1, "entries": cards}
