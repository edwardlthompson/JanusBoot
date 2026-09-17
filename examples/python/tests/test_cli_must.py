"""Extra CLI coverage for Must-gap commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from janusbootctl.cli import main
from janusbootctl.install_esp import apply_install
from janusbootctl.limine_gen import generate_limine_conf
from janusbootctl.paths import schema_dir


def _run(esp: Path, repo: Path, *argv: str) -> None:
    main(["--esp", str(esp), "--schema-dir", str(schema_dir(repo)), *argv])


def test_cli_oneshot_backup_install_theme(
    esp_copy: Path, repo: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    vmlinuz = tmp_path / "vmlinuz"
    vmlinuz.write_bytes(b"k")
    _run(esp_copy, repo, "oneshot", str(vmlinuz))
    assert "entries.json" in capsys.readouterr().out
    _run(esp_copy, repo, "oneshot", str(vmlinuz), "--clear")
    assert "cleared" in capsys.readouterr().out
    _run(esp_copy, repo, "backup", "--with-nvram", "--nvram-text", "Boot0001")
    assert "nvram_backup" in json.loads(capsys.readouterr().out)
    efi = tmp_path / "BOOTX64.EFI"
    efi.write_bytes(b"MZ")
    _run(esp_copy, repo, "install", "--efi", str(efi), "--dry-run")
    assert json.loads(capsys.readouterr().out)
    _run(esp_copy, repo, "install", "--plan-nvram")
    assert "efibootmgr" in json.loads(capsys.readouterr().out)["command_example"]
    preview = tmp_path / "p.png"
    theme = str(repo / "themes" / "elegant-dark" / "theme.json")
    _run(esp_copy, repo, "theme-preview", theme, "-o", str(preview), "--width", "1280", "--height", "720")
    assert json.loads(capsys.readouterr().out)["valid"] is True and preview.is_file()
    _run(esp_copy, repo, "theme-apply", str(repo / "themes" / "elegant-dark"))
    assert "elegant-dark" in capsys.readouterr().out
    _run(esp_copy, repo, "scan", "--root", str(esp_copy), "--shallow")
    assert "schema_version" in capsys.readouterr().out


def test_cli_repair_undo_dry(esp_copy: Path, repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _run(esp_copy, repo, "repair-undo", "--dry-run")
    assert json.loads(capsys.readouterr().out)[0]["status"] in {"empty", "dry_run", "skipped"}


def test_install_apply_confirm(esp_copy: Path, repo: Path, tmp_path: Path) -> None:
    efi = tmp_path / "BOOTX64.EFI"
    efi.write_bytes(b"MZ-LIMINE")
    results = apply_install(
        esp_copy, efi_binary=efi, schemas=schema_dir(repo), confirm=True, dry_run=False
    )
    assert any(r["status"] == "applied" for r in results)
    assert (esp_copy / "EFI" / "JanusBoot" / "BOOTX64.EFI").is_file()


def test_hidden_more_menu(esp_copy: Path, repo: Path) -> None:
    path = esp_copy / "EFI" / "JanusBoot" / "entries.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["entries"].append(
        {
            "id": "memtest",
            "title": "Memtest",
            "type": "efi_chainload",
            "path": "boot():/EFI/BOOT/memtest.efi",
            "hidden": True,
            "icon": "gear",
        }
    )
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    conf = generate_limine_conf(esp_copy, schemas=schema_dir(repo))
    assert "/More…" in conf and "Memtest" in conf
