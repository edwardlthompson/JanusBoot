"""Theme pack apply with atomic themes/.next/ + last-good rollback."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from janusbootctl.theme_image import compile_background, render_preview
from janusbootctl.validate import ValidationError, validate_theme


def load_theme(theme_json: Path) -> dict[str, Any]:
    data = json.loads(theme_json.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValidationError(["theme.json must be an object"])
    return data


def preview_theme(
    theme_json: Path,
    schemas: Path | None = None,
    *,
    out: Path | None = None,
    width: int = 1920,
    height: int = 1080,
) -> dict[str, Any]:
    """Validate + optional raster preview (1080p/4K)."""
    validate_theme(theme_json, schemas=schemas)
    data = load_theme(theme_json)
    result: dict[str, Any] = {
        "id": data.get("id") or theme_json.parent.name,
        "name": data.get("name") or theme_json.parent.name,
        "background": data.get("background"),
        "valid": True,
    }
    if out is not None:
        bg = None
        bg_meta = data.get("background")
        if isinstance(bg_meta, dict) and isinstance(bg_meta.get("path"), str):
            candidate = theme_json.parent / bg_meta["path"]
            if candidate.is_file():
                bg = candidate
        result["preview"] = str(render_preview(data, bg, out, width=width, height=height))
    return result


def apply_theme_to_esp(
    theme_dir: Path,
    esp_root: Path,
    *,
    schemas: Path | None = None,
    dry_run: bool = False,
) -> Path:
    """Compile into themes/.next/<id>/ then atomically promote; keep last-good."""
    theme_json = theme_dir / "theme.json"
    if not theme_json.is_file():
        raise ValidationError([f"missing theme.json under {theme_dir}"])
    validate_theme(theme_json, schemas=schemas)
    data = load_theme(theme_json)
    theme_id = str(data.get("id") or theme_dir.name)
    themes_root = esp_root / "EFI" / "JanusBoot" / "themes"
    live = themes_root / theme_id
    staging = themes_root / ".next" / theme_id
    last_good = themes_root / "last-good" / theme_id
    if dry_run:
        return live

    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    shutil.copy2(theme_json, staging / "theme.json")

    bg = data.get("background") if isinstance(data.get("background"), dict) else {}
    src_name = bg.get("path") if isinstance(bg, dict) else None
    source = theme_dir / str(src_name) if src_name else None
    # Prefer larger source if present
    alt = theme_dir / "background.source.png"
    if alt.is_file():
        source = alt
    if source is not None and source.is_file():
        compile_background(
            source,
            staging / "background.boot.jpg",
            max_width=int(bg.get("max_source_width") or 3840) if isinstance(bg, dict) else 3840,
            max_height=int(bg.get("max_source_height") or 2160) if isinstance(bg, dict) else 2160,
            max_bytes=int(bg.get("max_store_bytes") or 2_097_152)
            if isinstance(bg, dict)
            else 2_097_152,
        )
    icons_src = theme_dir / "icons"
    if icons_src.is_dir():
        shutil.copytree(icons_src, staging / "icons")

    if live.exists():
        if last_good.exists():
            shutil.rmtree(last_good)
        last_good.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(live), str(last_good))
    live.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staging), str(live))
    next_root = themes_root / ".next"
    if next_root.exists() and not any(next_root.iterdir()):
        next_root.rmdir()
    return live
