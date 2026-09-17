"""Build a single icons/atlas.json at theme apply (one EFI read)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_icon_atlas(icons_dir: Path) -> dict[str, Any]:
    """Index PNG icons into one atlas manifest (paths relative to icons/)."""
    entries: list[dict[str, Any]] = []
    if icons_dir.is_dir():
        for path in sorted(icons_dir.glob("*.png")):
            entries.append(
                {
                    "id": path.stem[:64],
                    "file": path.name,
                    "bytes": path.stat().st_size,
                }
            )
    return {
        "schema_version": 1,
        "count": len(entries),
        "icons": entries,
        "note": "EFI reads atlas.json once; bitmaps stay as separate PNGs in v1",
    }


def write_icon_atlas(icons_dir: Path, *, dry_run: bool = False) -> Path:
    atlas = build_icon_atlas(icons_dir)
    dest = icons_dir / "atlas.json"
    if not dry_run:
        icons_dir.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(atlas, indent=2) + "\n", encoding="utf-8")
    return dest
