"""os-prober-style Linux host paths (userspace; never deletes)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def discover_linux_kernels(boot_root: Path, *, max_pairs: int = 32) -> list[dict[str, Any]]:
    """Find vmlinuz + matching initrd under /boot-style trees."""
    root = boot_root.resolve()
    if not root.is_dir():
        return []
    kernels = sorted(root.glob("vmlinuz*")) + sorted(root.glob("vmlinux*"))
    rows: list[dict[str, Any]] = []
    for kernel in kernels:
        if not kernel.is_file() or len(rows) >= max_pairs:
            break
        stem = kernel.name
        initrd = None
        for pattern in (f"initrd.img-{stem.removeprefix('vmlinuz-')}", "initrd.img", "initramfs.img"):
            candidate = root / pattern
            if candidate.is_file():
                initrd = candidate
                break
        rows.append(
            {
                "id": f"linux-{kernel.name}"[:64].replace(".", "-"),
                "title": f"Linux ({kernel.name})"[:64],
                "subtitle": str(kernel)[:128],
                "type": "linux",
                "path": str(kernel),
                "initrd": str(initrd) if initrd else None,
                "icon": "linux",
                "source": "scanned",
            }
        )
    return rows


def windows_host_scan_plan() -> dict[str, Any]:
    """Document Windows-host scan steps (no registry writes here)."""
    return {
        "platform": "windows",
        "steps": [
            {
                "action": "locate_esp",
                "detail": "Find EFI System Partition mount (often ESP letter via mountvol)",
            },
            {
                "action": "find_bootmgfw",
                "detail": r"Look for EFI\Microsoft\Boot\bootmgfw.efi on ESP",
            },
            {
                "action": "never_delete_foreign",
                "detail": "Never delete foreign EFI files; only propose entries.json updates",
            },
        ],
        "dry_run": True,
    }
