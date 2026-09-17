"""Dry-run / confirm write planner for rescue ISO → removable USB."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from janusbootctl.usb_media import WRITE_TOOL_ALLOWLIST, BlockDevice, classify_device


@dataclass(frozen=True)
class WritePlan:
    iso_path: str
    iso_sha256: str
    iso_bytes: int
    device_path: str
    device_size_bytes: int
    device_model: str
    device_vendor: str
    dry_run: bool
    tool: str
    steps: tuple[str, ...]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def plan_write(
    iso: Path,
    device: BlockDevice,
    *,
    dry_run: bool = True,
    tool: str = "dd",
    confirm: bool = False,
    iso_sha256: str | None = None,
) -> WritePlan:
    if tool not in WRITE_TOOL_ALLOWLIST:
        raise ValueError(f"tool {tool!r} not in allowlist {sorted(WRITE_TOOL_ALLOWLIST)}")
    if not iso.is_file():
        raise FileNotFoundError(f"ISO missing: {iso}")
    cls = classify_device(device)
    if not cls.allowed:
        raise PermissionError(cls.reason)
    if not dry_run and not confirm:
        raise PermissionError("destructive write requires confirm=True")
    digest = iso_sha256 or sha256_file(iso)
    verb = "DRY-RUN: would write" if dry_run else "WRITE"
    steps = (
        f"verify ISO sha256={digest}",
        f"confirm target {cls.path} ({cls.size_bytes} B) model={cls.model} vendor={cls.vendor}",
        f"{verb} {iso.name} → {cls.path} via {tool}",
        "skip verify (dry-run)" if dry_run else "verify first/last blocks after write",
    )
    return WritePlan(
        iso_path=str(iso),
        iso_sha256=digest,
        iso_bytes=iso.stat().st_size,
        device_path=cls.path,
        device_size_bytes=cls.size_bytes,
        device_model=cls.model,
        device_vendor=cls.vendor,
        dry_run=dry_run,
        tool=tool,
        steps=steps,
    )


def plan_to_dict(plan: WritePlan) -> dict[str, Any]:
    data = asdict(plan)
    data["steps"] = list(plan.steps)
    return data
