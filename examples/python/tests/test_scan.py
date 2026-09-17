"""Phase 3 scanner heuristics."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from janusbootctl.cli import main
from janusbootctl.paths import schema_dir
from janusbootctl.scan import classify_efi_path, discover_candidates, entries_document


def test_classify_windows_and_linux() -> None:
    entry_type, title, icon = classify_efi_path("EFI/Microsoft/Boot/bootmgfw.efi")
    assert entry_type == "efi_chainload" and icon == "windows" and "Windows" in title
    entry_type2, _, icon2 = classify_efi_path("EFI/ubuntu/shimx64.efi")
    assert entry_type2 == "efi_chainload" and icon2 == "linux"


def test_discover_on_synthetic_esp(tmp_path: Path) -> None:
    win = tmp_path / "EFI" / "Microsoft" / "Boot" / "bootmgfw.efi"
    linux = tmp_path / "EFI" / "ubuntu" / "shimx64.efi"
    win.parent.mkdir(parents=True)
    linux.parent.mkdir(parents=True)
    win.write_bytes(b"MZ")
    linux.write_bytes(b"MZ")
    found = discover_candidates(tmp_path)
    paths = {e["path"] for e in found}
    assert "boot():/EFI/Microsoft/Boot/bootmgfw.efi" in paths
    assert "boot():/EFI/ubuntu/shimx64.efi" in paths
    doc = entries_document(found)
    assert doc["schema_version"] == 1
    assert all(e.get("source") == "scanned" for e in doc["entries"])


def test_cli_scan_print(tmp_path: Path, repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    esp = tmp_path / "esp"
    efi = esp / "EFI" / "Microsoft" / "Boot"
    efi.mkdir(parents=True)
    (efi / "bootmgfw.efi").write_bytes(b"MZ")
    main(["--esp", str(esp), "--schema-dir", str(schema_dir(repo)), "scan", "--root", str(esp)])
    doc = json.loads(capsys.readouterr().out)
    assert doc["entries"]
