"""get/set/backup tests for janusbootctl."""

from __future__ import annotations

from pathlib import Path

import pytest

from janusbootctl.backup import backup_esp
from janusbootctl.config_io import get_value, parse_cli_value, set_value
from janusbootctl.paths import schema_dir


def test_get_set_roundtrip(esp_copy: Path, repo: Path) -> None:
    assert get_value(esp_copy, "timeout") == 5
    set_value(esp_copy, "timeout", 10, schemas=schema_dir(repo))
    assert get_value(esp_copy, "timeout") == 10
    set_value(esp_copy, "features.mouse", True, schemas=schema_dir(repo))
    assert get_value(esp_copy, "features.mouse") is True


def test_parse_cli_value() -> None:
    assert parse_cli_value("10") == 10
    assert parse_cli_value("true") is True
    assert parse_cli_value("windows-11") == "windows-11"


def test_backup_copies(esp_copy: Path) -> None:
    dest = backup_esp(esp_copy, stamp="testrun")
    assert (dest / "settings.json").is_file()
    assert (dest / "entries.json").is_file()


def test_get_missing_key(esp_copy: Path) -> None:
    with pytest.raises(KeyError):
        get_value(esp_copy, "no.such.key")


def test_set_rejects_non_object_parent(esp_copy: Path, repo: Path) -> None:
    with pytest.raises(KeyError):
        set_value(esp_copy, "timeout.nested", 1, schemas=schema_dir(repo))
