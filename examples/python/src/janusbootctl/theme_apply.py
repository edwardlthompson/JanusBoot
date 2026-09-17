"""Theme pack apply (Phase 8). Compiles theme data; EFI never runs theme code."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from janusbootctl.validate import ValidationError, validate_theme


def load_theme(theme_json: Path) -> dict[str, Any]:
    data = json.loads(theme_json.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValidationError(["theme.json must be an object"])
    return data


def preview_theme(theme_json: Path, schemas: Path | None = None) -> dict[str, Any]:
    """Validate and return a small preview dict (no image resize)."""
    validate_theme(theme_json, schemas=schemas)
    data = load_theme(theme_json)
    return {
        "id": data.get("id") or theme_json.parent.name,
        "name": data.get("name") or theme_json.parent.name,
        "background": data.get("background"),
        "valid": True,
    }


def apply_theme_to_esp(
    theme_dir: Path,
    esp_root: Path,
    *,
    schemas: Path | None = None,
    dry_run: bool = False,
) -> Path:
    """Copy validated theme pack into EFI/JanusBoot/themes/<id>/."""
    theme_json = theme_dir / "theme.json"
    if not theme_json.is_file():
        raise ValidationError([f"missing theme.json under {theme_dir}"])
    validate_theme(theme_json, schemas=schemas)
    data = load_theme(theme_json)
    theme_id = str(data.get("id") or theme_dir.name)
    dest = esp_root / "EFI" / "JanusBoot" / "themes" / theme_id
    if dry_run:
        return dest
    dest.mkdir(parents=True, exist_ok=True)
    for item in theme_dir.iterdir():
        target = dest / item.name
        if item.is_file():
            shutil.copy2(item, target)
        elif item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
    return dest
