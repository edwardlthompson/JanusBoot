"""Read and write settings / entries JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from janusbootctl.paths import entries_path, settings_path
from janusbootctl.validate import load_json, validate_esp


def _dotted_get(data: dict[str, Any], key: str) -> Any:
    cur: Any = data
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(key)
        cur = cur[part]
    return cur


def _dotted_set(data: dict[str, Any], key: str, value: Any) -> None:
    parts = key.split(".")
    cur: dict[str, Any] = data
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            raise KeyError(key)
        cur = nxt
    cur[parts[-1]] = value


def get_value(esp_root: Path, key: str, *, document: str = "settings") -> Any:
    path = settings_path(esp_root) if document == "settings" else entries_path(esp_root)
    return _dotted_get(load_json(path), key)


def set_value(
    esp_root: Path,
    key: str,
    value: Any,
    *,
    document: str = "settings",
    schemas: Path | None = None,
) -> None:
    path = settings_path(esp_root) if document == "settings" else entries_path(esp_root)
    data = load_json(path)
    if not isinstance(data, dict):
        raise TypeError(f"{path} root must be an object")
    _dotted_set(data, key, value)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    validate_esp(esp_root, schemas=schemas)


def parse_cli_value(raw: str) -> Any:
    """Parse set values: JSON literals, else string."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw
