"""Local theme zip shop: browse/import validated packs (no network phone-home)."""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from janusbootctl.validate import ValidationError, validate_theme


def list_theme_packs(root: Path) -> list[dict[str, Any]]:
    """List theme directories under root that contain theme.json."""
    if not root.is_dir():
        return []
    packs: list[dict[str, Any]] = []
    for child in sorted(root.iterdir()):
        theme_json = child / "theme.json"
        if not child.is_dir() or not theme_json.is_file():
            continue
        try:
            data = json.loads(theme_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        packs.append(
            {
                "id": str(data.get("id") or child.name),
                "name": str(data.get("name") or child.name),
                "path": str(child),
                "appearance": data.get("appearance"),
            }
        )
    return packs


def import_theme_zip(
    zip_path: Path,
    dest_root: Path,
    *,
    schemas: Path | None = None,
) -> Path:
    """Import a local .zip theme pack after schema validation. No network."""
    if not zip_path.is_file() or zip_path.suffix.lower() != ".zip":
        raise ValidationError([f"expected local .zip theme pack: {zip_path}"])
    dest_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="janus-theme-") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                name = info.filename.replace("\\", "/")
                if name.startswith("/") or ".." in name.split("/"):
                    raise ValidationError([f"unsafe zip member: {info.filename}"])
            zf.extractall(tmp_path)
        theme_json = _find_theme_json(tmp_path)
        validate_theme(theme_json, schemas=schemas)
        data = json.loads(theme_json.read_text(encoding="utf-8"))
        theme_id = str(data.get("id") or theme_json.parent.name)
        if not re_safe_id(theme_id):
            raise ValidationError([f"invalid theme id: {theme_id}"])
        target = dest_root / theme_id
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(theme_json.parent, target)
        return target


def re_safe_id(theme_id: str) -> bool:
    return bool(theme_id) and all(c.isalnum() or c in "-_" for c in theme_id)


def _find_theme_json(root: Path) -> Path:
    direct = root / "theme.json"
    if direct.is_file():
        return direct
    matches = list(root.rglob("theme.json"))
    if len(matches) != 1:
        raise ValidationError(["zip must contain exactly one theme.json"])
    return matches[0]
