"""Nice-later stubs: theme shop, PIN, HiDPI, atlas, snapshots."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from janusbootctl.card_stubs import detect_btrfs_snapshots, snapshot_entries_document
from janusbootctl.cli import main
from janusbootctl.hidpi import resolve_preview_size, scale_factor_for
from janusbootctl.icon_atlas import build_icon_atlas, write_icon_atlas
from janusbootctl.linux_gui import usb_list_via_cli, usb_preview_via_cli
from janusbootctl.pin_gate import hash_pin, pin_blocks_settings, verify_pin
from janusbootctl.theme_shop import import_theme_zip, list_theme_packs
from janusbootctl.validate import ValidationError


def test_cli_theme_shop_and_snapshots(
    tmp_path: Path, repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    themes = repo / "themes"
    main(["theme-shop", "list", str(themes)])
    packs = json.loads(capsys.readouterr().out)
    assert isinstance(packs, list) and packs
    src = themes / "high-contrast"
    zpath = tmp_path / "pack.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        for path in src.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(src).as_posix())
    dest = tmp_path / "imported"
    main(["theme-shop", "import", str(zpath), "--dest", str(dest)])
    imported = Path(json.loads(capsys.readouterr().out))
    assert (imported / "theme.json").is_file()
    snap_root = tmp_path / "timeshift" / "snapshots"
    snap_root.mkdir(parents=True)
    (snap_root / "2026-01-01").mkdir()
    main(["snapshot-cards", "--root", str(tmp_path)])
    assert json.loads(capsys.readouterr().out)["entries"][0]["calm"] is True


def test_theme_shop_rejects_unsafe_zip(tmp_path: Path, repo: Path) -> None:
    zpath = tmp_path / "bad.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("../evil/theme.json", "{}")
    with pytest.raises(ValidationError):
        import_theme_zip(zpath, tmp_path / "out", schemas=repo / "schema")
    assert list_theme_packs(tmp_path / "missing") == []


def test_pin_and_hidpi_and_atlas(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        hash_pin("12")
    stored = {**hash_pin("4242"), "enabled": True}
    assert verify_pin("4242", stored)
    assert not verify_pin("0000", stored)
    assert not verify_pin("4242", {"salt": 1, "hash": "x"})
    assert pin_blocks_settings({"settings_pin": stored}, None)
    assert not pin_blocks_settings({"settings_pin": stored}, "4242")
    assert not pin_blocks_settings({}, None)
    assert resolve_preview_size("4k") == (3840, 2160)
    assert resolve_preview_size(width=1280, height=720) == (1280, 720)
    assert scale_factor_for(3840, 2160) == 2.0
    with pytest.raises(ValueError):
        resolve_preview_size("8k")
    with pytest.raises(ValueError):
        resolve_preview_size(width=100, height=100)
    icons = tmp_path / "icons"
    icons.mkdir()
    (icons / "linux.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    assert build_icon_atlas(icons)["count"] == 1
    write_icon_atlas(icons)
    assert (icons / "atlas.json").is_file()


def test_theme_shop_list_and_snapshots(tmp_path: Path, repo: Path) -> None:
    themes = repo / "themes"
    packs = list_theme_packs(themes) if themes.is_dir() else []
    assert isinstance(packs, list)
    snap_root = tmp_path / "timeshift" / "snapshots"
    snap_root.mkdir(parents=True)
    (snap_root / "2026-01-01").mkdir()
    cards = detect_btrfs_snapshots(tmp_path)
    assert snapshot_entries_document(cards)["entries"][0]["calm"] is True
    assert snapshot_entries_document([])["entries"][0]["id"] == "no-snapshots"


def test_linux_gui_usb_helpers(tmp_path: Path) -> None:
    iso = tmp_path / "r.iso"
    iso.write_bytes(b"iso")
    mocks = tmp_path / "m.json"
    mocks.write_text(
        json.dumps(
            [{"path": "/dev/sdb", "size_bytes": 1000, "model": "M", "removable": True, "tran": "usb"}]
        ),
        encoding="utf-8",
    )
    assert usb_list_via_cli(mock_json=mocks).ok
    assert usb_preview_via_cli(
        iso, device="/dev/sdb", size_bytes=1000, model="M", removable=True, tran="usb"
    ).ok
