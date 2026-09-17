"""Limine generation tests for janusbootctl."""

from __future__ import annotations

from pathlib import Path

from janusbootctl.config_io import set_value
from janusbootctl.limine_gen import generate_limine_conf
from janusbootctl.paths import schema_dir


def test_generate_limine_matches_golden(repo: Path) -> None:
    esp = repo / "fixtures" / "esp"
    golden = (esp / "EFI" / "JanusBoot" / "limine.conf.golden").read_text(encoding="utf-8")
    assert generate_limine_conf(esp, schemas=schema_dir(repo)) == golden


def test_default_saved_uses_last_boot(esp_copy: Path, repo: Path) -> None:
    set_value(esp_copy, "default", "saved", schemas=schema_dir(repo))
    set_value(esp_copy, "last_boot", "linux-mint", schemas=schema_dir(repo))
    conf = generate_limine_conf(esp_copy, schemas=schema_dir(repo))
    assert "default_entry: 2" in conf
