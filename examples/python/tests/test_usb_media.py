"""USB media safety: removable-only classification + dry-run planner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from janusbootctl.cli import main
from janusbootctl.usb_host import enumerate_linux_devices
from janusbootctl.usb_media import BlockDevice, classify_device, list_removable
from janusbootctl.usb_plan import plan_write


def test_refuse_nvme_and_sata_system_disks() -> None:
    nvme = BlockDevice("/dev/nvme0n1", 512_000_000_000, "Samsung SSD", tran="nvme")
    sata = BlockDevice("/dev/sda", 1_000_000_000_000, "WDC HDD", tran="sata", mountpoints=("/",))
    assert classify_device(nvme).allowed is False
    assert "refused" in classify_device(nvme).reason
    assert classify_device(sata).allowed is False


def test_allow_removable_usb_only() -> None:
    stick = BlockDevice(
        "/dev/sdb", 16_000_000_000, "Cruzer", vendor="SanDisk", removable=True, tran="usb"
    )
    cls = classify_device(stick)
    assert cls.allowed is True
    assert list_removable([stick, BlockDevice("/dev/nvme0n1", 1, "SSD", tran="nvme")]) == [cls]


def test_refuse_bad_path_and_unknown_tool(tmp_path: Path) -> None:
    bad = BlockDevice("sdb", 1, "x", removable=True, tran="usb")
    assert classify_device(bad).allowed is False
    iso = tmp_path / "a.iso"
    iso.write_bytes(b"iso")
    stick = BlockDevice("/dev/sdb", 8_000_000_000, "Flash", removable=True, tran="usb")
    with pytest.raises(ValueError, match="allowlist"):
        plan_write(iso, stick, tool="evil-dd")
    with pytest.raises(FileNotFoundError):
        plan_write(tmp_path / "missing.iso", stick)


def test_dry_run_plan_never_writes(tmp_path: Path) -> None:
    iso = tmp_path / "janusboot-rescue.iso"
    iso.write_bytes(b"ISOIMAGE" + b"\0" * 64)
    stick = BlockDevice("/dev/sdc", 8_000_000_000, "VentoyStick", removable=True, tran="usb")
    plan = plan_write(iso, stick, dry_run=True)
    assert plan.dry_run is True and plan.iso_sha256 and "DRY-RUN" in plan.steps[2]
    with pytest.raises(PermissionError, match="confirm"):
        plan_write(iso, stick, dry_run=False, confirm=False)
    with pytest.raises(PermissionError, match="refused"):
        plan_write(iso, BlockDevice("/dev/nvme0n1", 1, "SSD", tran="nvme"), dry_run=True)
    assert plan_write(iso, stick, dry_run=False, confirm=True).dry_run is False


def test_cli_usb_list_and_preview(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    iso = tmp_path / "rescue.iso"
    iso.write_bytes(b"iso")
    mocks = tmp_path / "devices.json"
    mocks.write_text(
        json.dumps(
            [
                {
                    "path": "/dev/sdb",
                    "size_bytes": 8_000_000_000,
                    "model": "Flash",
                    "removable": True,
                    "tran": "usb",
                },
                {"path": "/dev/nvme0n1", "size_bytes": 1, "model": "System", "tran": "nvme"},
            ]
        ),
        encoding="utf-8",
    )
    main(["usb", "list", "--mock-json", str(mocks)])
    listed = json.loads(capsys.readouterr().out)
    assert listed["removable"][0]["path"] == "/dev/sdb"
    args = [
        "usb",
        "preview",
        "--iso",
        str(iso),
        "--device",
        "/dev/sdb",
        "--size-bytes",
        "8000000000",
        "--model",
        "Flash",
        "--removable",
        "--tran",
        "usb",
    ]
    main(args)
    assert json.loads(capsys.readouterr().out)["dry_run"] is True
    args[1] = "write"
    main(args)
    assert json.loads(capsys.readouterr().out)["dry_run"] is True


def test_enumerate_sysfs_mock(tmp_path: Path) -> None:
    block = tmp_path / "block"
    sdb = block / "sdb"
    sdb.mkdir(parents=True)
    (sdb / "removable").write_text("1\n", encoding="utf-8")
    (sdb / "size").write_text("1000\n", encoding="utf-8")
    (sdb / "device").mkdir()
    (sdb / "device" / "model").write_text("MockStick\n", encoding="utf-8")
    (sdb / "device" / "uevent").write_text("DRIVER=usb-storage\n", encoding="utf-8")
    sda = block / "sda"
    sda.mkdir()
    (sda / "removable").write_text("0\n", encoding="utf-8")
    (sda / "size").write_text("999999\n", encoding="utf-8")
    (sda / "device").mkdir()
    (sda / "device" / "transport").write_text("sata\n", encoding="utf-8")
    devices = enumerate_linux_devices(block)
    assert len(devices) == 1 and devices[0].path == "/dev/sdb"
    assert enumerate_linux_devices(tmp_path / "nope") == []
