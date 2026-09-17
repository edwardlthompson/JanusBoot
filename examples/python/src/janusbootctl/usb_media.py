"""Removable-only USB device classification (never allows system disks)."""

from __future__ import annotations

from dataclasses import dataclass

WRITE_TOOL_ALLOWLIST: frozenset[str] = frozenset({"dd", "cp", "pv", "usbimager"})
_SYSTEM_TRAN = frozenset({"", "sata", "nvme", "ata", "scsi", "virtio", "raid"})
_ROOT_MOUNTS = frozenset({"/", "/boot", "/boot/efi", "/home", "c:", "c:\\"})


@dataclass(frozen=True)
class BlockDevice:
    path: str
    size_bytes: int
    model: str
    vendor: str = ""
    removable: bool = False
    tran: str = ""
    is_system: bool = False
    mountpoints: tuple[str, ...] = ()


@dataclass(frozen=True)
class Classification:
    path: str
    allowed: bool
    reason: str
    size_bytes: int
    model: str
    vendor: str


def _is_device_path(path: str) -> bool:
    return path.startswith("/dev/") or path.startswith("\\\\.\\")


def _looks_system(dev: BlockDevice) -> bool:
    if dev.is_system:
        return True
    for mp in dev.mountpoints:
        key = mp.rstrip("\\/").lower()
        if key in _ROOT_MOUNTS or key.startswith("c:"):
            return True
    return (not dev.removable) and (dev.tran.lower() in _SYSTEM_TRAN)


def classify_device(dev: BlockDevice) -> Classification:
    """Allow only removable/USB media; refuse internal/system-looking disks."""
    model = dev.model or "unknown"
    vendor = dev.vendor or "unknown"

    def refuse(reason: str) -> Classification:
        return Classification(
            path=dev.path,
            allowed=False,
            reason=reason,
            size_bytes=dev.size_bytes,
            model=model,
            vendor=vendor,
        )

    if not _is_device_path(dev.path):
        return refuse("path must be a device node (/dev/… or \\\\.\\…)")
    if _looks_system(dev):
        return refuse("refused: looks like system/internal disk")
    if not (dev.removable or dev.tran.lower() == "usb"):
        return refuse("refused: not removable media")
    if dev.size_bytes <= 0:
        return refuse("refused: unknown size")
    return Classification(
        path=dev.path,
        allowed=True,
        reason="ok: removable media",
        size_bytes=dev.size_bytes,
        model=model,
        vendor=vendor,
    )


def list_removable(devices: list[BlockDevice]) -> list[Classification]:
    return [c for d in devices if (c := classify_device(d)).allowed]
