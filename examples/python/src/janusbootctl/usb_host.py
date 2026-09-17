"""Linux host removable disk probe (sysfs). Never returns non-removable disks."""

from __future__ import annotations

from pathlib import Path

from janusbootctl.usb_media import BlockDevice, classify_device


def enumerate_linux_devices(sys_block: Path | None = None) -> list[BlockDevice]:
    """Read /sys/block; return only devices that classify as removable."""
    root = sys_block or Path("/sys/block")
    if not root.is_dir():
        return []
    found: list[BlockDevice] = []
    for entry in sorted(root.iterdir()):
        name = entry.name
        if name.startswith(("loop", "ram", "dm-", "zram", "md")):
            continue
        rem_file = entry / "removable"
        try:
            removable = rem_file.read_text(encoding="utf-8").strip() == "1"
        except OSError:
            continue
        tran = _transport(entry)
        model = (_read(entry / "device" / "model") or name).strip()
        vendor = _read(entry / "device" / "vendor").strip()
        try:
            size_bytes = int(_read(entry / "size") or "0") * 512
        except ValueError:
            size_bytes = 0
        found.append(
            BlockDevice(
                path=f"/dev/{name}",
                size_bytes=size_bytes,
                model=model,
                vendor=vendor,
                removable=removable,
                tran=tran,
            )
        )
    return [d for d in found if classify_device(d).allowed]


def _transport(entry: Path) -> str:
    tran_file = entry / "device" / "transport"
    if tran_file.is_file():
        return _read(tran_file).strip().lower()
    text = _read(entry / "device" / "uevent").upper()
    return "usb" if "USB" in text else ""


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else ""
    except OSError:
        return ""
