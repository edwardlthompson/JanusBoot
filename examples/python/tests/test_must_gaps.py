"""Must-gap depth: repair apply/undo, oneshot, backup nvram, install, parity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from janusbootctl.backup import backup_with_nvram
from janusbootctl.cli import main
from janusbootctl.install_esp import apply_install, plan_nvram_entry
from janusbootctl.oneshot import build_oneshot_entry, clear_oneshot_entry, write_oneshot_entry
from janusbootctl.paths import schema_dir
from janusbootctl.repair import plan_restore_janus_files
from janusbootctl.repair_apply import apply_plans, undo_last_repair
from janusbootctl.scan import discover_candidates, entries_document
from janusbootctl.scan_host import discover_linux_kernels, windows_host_scan_plan
from janusbootctl.schema_parity import assert_consumer_parity
from janusbootctl.theme_apply import preview_theme
from janusbootctl.windows_gui import ELEVATION_WARNING, windows_gui_snapshot


def test_deep_scan_finds_nested_efi(tmp_path: Path) -> None:
    nested = tmp_path / "EFI" / "vendor" / "nested"
    nested.mkdir(parents=True)
    (nested / "custom.efi").write_bytes(b"MZ")
    found = discover_candidates(tmp_path, deep=True)
    assert any("vendor/nested/custom.efi" in e["path"] for e in found)
    shallow = discover_candidates(tmp_path, deep=False)
    assert not shallow


def test_empty_disk_calm_entries() -> None:
    doc = entries_document([])
    assert any(e["id"] == "empty-scan" for e in doc["entries"])


def test_repair_apply_undo(esp_copy: Path) -> None:
    backup = esp_copy / "EFI" / "JanusBoot" / "backup" / "latest"
    backup.mkdir(parents=True, exist_ok=True)
    settings = esp_copy / "EFI" / "JanusBoot" / "settings.json"
    original = settings.read_text(encoding="utf-8")
    (backup / "settings.json").write_text(original, encoding="utf-8")
    (backup / "entries.json").write_text(
        (esp_copy / "EFI" / "JanusBoot" / "entries.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    settings.write_text(original.replace('"timeout": 5', '"timeout": 99'), encoding="utf-8")
    plans = plan_restore_janus_files(esp_copy)
    applied = apply_plans(esp_copy, plans, confirm=True, dry_run=False)
    assert any(r.get("status") == "applied" for r in applied)
    assert '"timeout": 5' in settings.read_text(encoding="utf-8")
    # mutate again then undo
    settings.write_text(original.replace('"timeout": 5', '"timeout": 77'), encoding="utf-8")
    undone = undo_last_repair(esp_copy, confirm=True, dry_run=False)
    assert undone
    with pytest.raises(ValueError, match="confirm"):
        apply_plans(esp_copy, plans, confirm=False, dry_run=False)


def test_oneshot_and_clear(esp_copy: Path, tmp_path: Path) -> None:
    vmlinuz = tmp_path / "vmlinuz-6.1"
    initrd = tmp_path / "initrd.img-6.1"
    vmlinuz.write_bytes(b"k")
    initrd.write_bytes(b"i")
    entry = build_oneshot_entry(vmlinuz, initrd=initrd)
    write_oneshot_entry(esp_copy, entry)
    doc = json.loads((esp_copy / "EFI" / "JanusBoot" / "entries.json").read_text(encoding="utf-8"))
    assert doc["entries"][0]["id"] == "oneshot-linux"
    assert clear_oneshot_entry(esp_copy) is True


def test_backup_nvram_and_install(esp_copy: Path, tmp_path: Path, repo: Path) -> None:
    paths = backup_with_nvram(esp_copy, nvram_dump="BootOrder: 0001\n")
    assert Path(paths["nvram_backup"]).joinpath("dump.txt").is_file()
    efi = tmp_path / "BOOTX64.EFI"
    efi.write_bytes(b"MZ")
    dry = apply_install(esp_copy, efi_binary=efi, schemas=schema_dir(repo), dry_run=True)
    assert all(r["status"] == "dry_run" for r in dry)
    plan = plan_nvram_entry()
    assert plan["dry_run"] is True and "efibootmgr" in plan["command_example"]


def test_theme_raster_preview(repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "preview.png"
    preview = preview_theme(
        repo / "themes" / "mint-dark" / "theme.json",
        schemas=schema_dir(repo),
        out=out,
        width=1920,
        height=1080,
    )
    assert preview["valid"] and out.is_file() and out.stat().st_size > 100


def test_schema_parity(repo: Path) -> None:
    errors = assert_consumer_parity(schema_dir(repo))
    assert errors == []


def test_windows_gui_snapshot_warns(esp_copy: Path) -> None:
    snap = windows_gui_snapshot(esp_copy)
    assert ELEVATION_WARNING in snap.warning
    assert len(snap.entries) >= 1


def test_linux_kernel_and_windows_plan(tmp_path: Path) -> None:
    (tmp_path / "vmlinuz-6").write_bytes(b"k")
    (tmp_path / "initrd.img-6").write_bytes(b"i")
    rows = discover_linux_kernels(tmp_path)
    assert rows and rows[0]["type"] == "linux"
    plan = windows_host_scan_plan()
    assert plan["dry_run"] is True


def test_cli_repair_apply_dry(esp_copy: Path, repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    backup = esp_copy / "EFI" / "JanusBoot" / "backup" / "latest"
    backup.mkdir(parents=True, exist_ok=True)
    for name in ("settings.json", "entries.json"):
        (backup / name).write_text(
            (esp_copy / "EFI" / "JanusBoot" / name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    main(
        [
            "--esp",
            str(esp_copy),
            "--schema-dir",
            str(schema_dir(repo)),
            "repair-apply",
            "--kind",
            "janus",
            "--dry-run",
        ]
    )
    data = json.loads(capsys.readouterr().out)
    assert data and data[0]["status"] in {"dry_run", "skipped"}
