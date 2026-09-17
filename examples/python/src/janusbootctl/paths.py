"""Resolve repo, schema, and ESP fixture paths."""

from __future__ import annotations

from pathlib import Path


def package_root() -> Path:
    """Return examples/python root (parent of src/)."""
    return Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    """Return JanusBoot repository root (parent of examples/)."""
    return package_root().parents[1]


def schema_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "schema"


def default_esp_root(root: Path | None = None) -> Path:
    """Default fixture ESP containing EFI/JanusBoot/."""
    return (root or repo_root()) / "fixtures" / "esp"


def janus_dir(esp_root: Path) -> Path:
    return esp_root / "EFI" / "JanusBoot"


def settings_path(esp_root: Path) -> Path:
    return janus_dir(esp_root) / "settings.json"


def entries_path(esp_root: Path) -> Path:
    return janus_dir(esp_root) / "entries.json"
