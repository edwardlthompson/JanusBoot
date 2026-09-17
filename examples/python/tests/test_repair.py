"""Phase 7 repair dry-run plans."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from janusbootctl.cli import main
from janusbootctl.paths import schema_dir
from janusbootctl.repair import plan_restore_janus_files, plan_windows_bootmgfw_restore


def test_plan_restore_from_backup(esp_copy: Path) -> None:
    backup = esp_copy / "EFI" / "JanusBoot" / "backup" / "latest"
    backup.mkdir(parents=True, exist_ok=True)
    (backup / "settings.json").write_text(
        (esp_copy / "EFI" / "JanusBoot" / "settings.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (backup / "entries.json").write_text(
        (esp_copy / "EFI" / "JanusBoot" / "entries.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    plans = plan_restore_janus_files(esp_copy)
    assert any(p.action == "restore_file" for p in plans)


def test_bootmgfw_skip_without_backup(esp_copy: Path) -> None:
    plans = plan_windows_bootmgfw_restore(esp_copy)
    assert plans[0].action == "skip_no_backup"


def test_cli_repair_plan(esp_copy: Path, repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main(
        [
            "--esp",
            str(esp_copy),
            "--schema-dir",
            str(schema_dir(repo)),
            "repair-plan",
            "--kind",
            "all",
        ]
    )
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list) and data
    assert all(row.get("dry_run") is True for row in data)
