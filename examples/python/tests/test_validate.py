"""Validation tests for janusbootctl."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from janusbootctl.paths import schema_dir, settings_path
from janusbootctl.validate import ValidationError, validate_esp, validate_theme


def test_validate_fixtures(repo: Path) -> None:
    validate_esp(repo / "fixtures" / "esp", schemas=schema_dir(repo))


def test_validate_theme(repo: Path) -> None:
    validate_theme(repo / "themes" / "high-contrast" / "theme.json", schemas=schema_dir(repo))


def test_validate_rejects_bad_timeout(esp_copy: Path, repo: Path) -> None:
    set_path = settings_path(esp_copy)
    data = json.loads(set_path.read_text(encoding="utf-8"))
    data["timeout"] = -1
    set_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValidationError):
        validate_esp(esp_copy, schemas=schema_dir(repo))


def test_validate_bad_json(esp_copy: Path, repo: Path) -> None:
    settings_path(esp_copy).write_text("{not-json", encoding="utf-8")
    with pytest.raises(ValidationError):
        validate_esp(esp_copy, schemas=schema_dir(repo))


def test_validate_theme_rejects(tmp_path: Path, repo: Path) -> None:
    bad = tmp_path / "theme.json"
    bad.write_text('{"name": "x"}', encoding="utf-8")
    with pytest.raises(ValidationError):
        validate_theme(bad, schemas=schema_dir(repo))
