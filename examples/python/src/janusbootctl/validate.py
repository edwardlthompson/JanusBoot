"""Load and validate JanusBoot JSON documents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from janusbootctl.paths import entries_path, schema_dir, settings_path


class ValidationError(Exception):
    """One or more schema validation failures."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _validator(schema_path: Path) -> Draft202012Validator:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_document(data: Any, schema_path: Path) -> list[str]:
    validator = _validator(schema_path)
    return sorted(
        f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}"
        for err in validator.iter_errors(data)
    )


def validate_esp(esp_root: Path, schemas: Path | None = None) -> None:
    """Validate settings.json and entries.json under an ESP root."""
    base = schemas or schema_dir()
    errors: list[str] = []
    pairs = (
        (settings_path(esp_root), base / "settings.schema.json", "settings"),
        (entries_path(esp_root), base / "entries.schema.json", "entries"),
    )
    for path, schema, label in pairs:
        if not path.is_file():
            errors.append(f"{label}: missing file {path}")
            continue
        try:
            data = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{label}: {exc}")
            continue
        for msg in validate_document(data, schema):
            errors.append(f"{label}: {msg}")
    if errors:
        raise ValidationError(errors)


def validate_theme(theme_path: Path, schemas: Path | None = None) -> None:
    base = schemas or schema_dir()
    data = load_json(theme_path)
    errs = validate_document(data, base / "theme.schema.json")
    if errs:
        raise ValidationError([f"theme: {e}" for e in errs])
