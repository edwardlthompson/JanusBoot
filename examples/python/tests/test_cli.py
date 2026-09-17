"""CLI entry tests for janusbootctl."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from janusbootctl.cli import main
from janusbootctl.paths import schema_dir, settings_path


def test_cli_validate(capsys: pytest.CaptureFixture[str], repo: Path) -> None:
    main(
        [
            "--esp",
            str(repo / "fixtures" / "esp"),
            "--schema-dir",
            str(schema_dir(repo)),
            "validate",
        ]
    )
    assert capsys.readouterr().out.strip() == "ok"


def test_cli_get(capsys: pytest.CaptureFixture[str], repo: Path) -> None:
    main(
        [
            "--esp",
            str(repo / "fixtures" / "esp"),
            "--schema-dir",
            str(schema_dir(repo)),
            "get",
            "default",
        ]
    )
    assert json.loads(capsys.readouterr().out) == "windows-11"


def test_cli_set_and_backup(esp_copy: Path, repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    schemas = str(schema_dir(repo))
    esp = str(esp_copy)
    main(["--esp", esp, "--schema-dir", schemas, "set", "timeout", "7"])
    assert capsys.readouterr().out.strip() == "ok"
    main(["--esp", esp, "--schema-dir", schemas, "backup"])
    out = capsys.readouterr().out.strip()
    assert Path(out).is_dir()


def test_cli_generate_limine(
    tmp_path: Path, repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "limine.conf"
    main(
        [
            "--esp",
            str(repo / "fixtures" / "esp"),
            "--schema-dir",
            str(schema_dir(repo)),
            "generate-limine",
            "-o",
            str(out),
        ]
    )
    assert Path(capsys.readouterr().out.strip()) == out
    golden = (repo / "fixtures" / "esp" / "EFI" / "JanusBoot" / "limine.conf.golden").read_text(
        encoding="utf-8"
    )
    assert out.read_text(encoding="utf-8") == golden


def test_cli_validate_theme(capsys: pytest.CaptureFixture[str], repo: Path) -> None:
    theme = repo / "themes" / "high-contrast" / "theme.json"
    main(["--schema-dir", str(schema_dir(repo)), "validate-theme", str(theme)])
    assert capsys.readouterr().out.strip() == "ok"


def test_cli_validate_fails(esp_copy: Path, repo: Path) -> None:
    settings_path(esp_copy).unlink()
    with pytest.raises(SystemExit) as exc:
        main(["--esp", str(esp_copy), "--schema-dir", str(schema_dir(repo)), "validate"])
    assert exc.value.code == 1
