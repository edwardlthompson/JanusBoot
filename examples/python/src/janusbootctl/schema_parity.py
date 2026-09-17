"""Linux/Windows consumers must agree on shared ESP schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Shared keys both GUIs/CLIs are allowed to mutate via janusbootctl.
SHARED_SETTINGS_KEYS: frozenset[str] = frozenset(
    {
        "timeout",
        "default",
        "theme",
        "wallpaper",
        "last_boot",
        "features",
    }
)

CONSUMERS: tuple[str, ...] = ("linux_gui", "windows_gui", "cli")


def load_settings_schema(schema_path: Path) -> dict[str, Any]:
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("settings schema must be object")
    return data


def assert_consumer_parity(schema_dir: Path) -> list[str]:
    """Return list of divergence errors (empty = OK)."""
    errors: list[str] = []
    settings = load_settings_schema(schema_dir / "settings.schema.json")
    props = settings.get("properties")
    if not isinstance(props, dict):
        return ["settings.schema.json missing properties"]
    for key in SHARED_SETTINGS_KEYS:
        if key not in props:
            errors.append(f"missing shared settings key in schema: {key}")
    entries = json.loads((schema_dir / "entries.schema.json").read_text(encoding="utf-8"))
    theme = json.loads((schema_dir / "theme.schema.json").read_text(encoding="utf-8"))
    if entries.get("$id") == theme.get("$id"):
        errors.append("entries and theme schemas must not share $id")
    # Manifest records which consumers must stay schema-aligned.
    manifest = schema_dir / "parity.manifest.json"
    if manifest.is_file():
        doc = json.loads(manifest.read_text(encoding="utf-8"))
        listed = doc.get("consumers")
        if not isinstance(listed, list) or set(listed) != set(CONSUMERS):
            errors.append(f"parity.manifest consumers must equal {sorted(CONSUMERS)}")
    else:
        errors.append("missing parity.manifest.json")
    return errors
