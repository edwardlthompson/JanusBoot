"""Phase 5 Linux GUI façade + Phase 8 theme apply."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from janusbootctl.cli import main
from janusbootctl.linux_gui import list_entries_via_cli, set_timeout_via_cli
from janusbootctl.paths import schema_dir
from janusbootctl.theme_apply import apply_theme_to_esp, preview_theme


def test_linux_gui_list_and_set(esp_copy: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure subprocess finds this tree's CLI via python -m
    monkeypatch.setenv("PATH", "")
    entries = list_entries_via_cli(esp_copy)
    assert len(entries) >= 1
    result = set_timeout_via_cli(esp_copy, 9)
    assert result.ok


def test_theme_preview_and_apply(
    esp_copy: Path, repo: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    theme_json = repo / "themes" / "high-contrast" / "theme.json"
    preview = preview_theme(theme_json, schemas=schema_dir(repo))
    assert preview["valid"] is True
    dest = apply_theme_to_esp(theme_json.parent, esp_copy, schemas=schema_dir(repo), dry_run=True)
    assert "high-contrast" in str(dest)
    applied = apply_theme_to_esp(theme_json.parent, esp_copy, schemas=schema_dir(repo))
    assert (applied / "theme.json").is_file()
    main(
        [
            "--esp",
            str(esp_copy),
            "--schema-dir",
            str(schema_dir(repo)),
            "theme-preview",
            str(theme_json),
        ]
    )
    assert json.loads(capsys.readouterr().out)["valid"] is True
