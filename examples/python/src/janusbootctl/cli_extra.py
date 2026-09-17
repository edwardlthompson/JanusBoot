"""CLI helpers for usb / theme-shop / snapshot-cards (keeps cli.py slim)."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from janusbootctl.card_stubs import detect_btrfs_snapshots, snapshot_entries_document
from janusbootctl.theme_shop import import_theme_zip, list_theme_packs
from janusbootctl.usb_media import BlockDevice, classify_device, list_removable
from janusbootctl.usb_plan import plan_to_dict, plan_write


def _mock_devices(args: Namespace) -> list[BlockDevice]:
    if args.mock_json is not None:
        raw = json.loads(Path(args.mock_json).read_text(encoding="utf-8"))
        return [
            BlockDevice(
                path=str(d["path"]),
                size_bytes=int(d.get("size_bytes") or 0),
                model=str(d.get("model") or "unknown"),
                vendor=str(d.get("vendor") or ""),
                removable=bool(d.get("removable")),
                tran=str(d.get("tran") or ""),
                is_system=bool(d.get("is_system")),
                mountpoints=tuple(d.get("mountpoints") or ()),
            )
            for d in raw
        ]
    if args.device:
        return [
            BlockDevice(
                path=args.device,
                size_bytes=int(args.size_bytes or 0),
                model=args.model,
                vendor=args.vendor,
                removable=bool(args.removable),
                tran=args.tran,
                is_system=bool(args.system),
            )
        ]
    return []


def run_usb_command(args: Namespace) -> dict[str, Any]:
    devices = _mock_devices(args)
    if args.action == "list":
        allowed = list_removable(devices)
        return {
            "removable": [a.__dict__ for a in allowed],
            "empty": not allowed,
            "hint": "Insert a USB stick and refresh" if not allowed else "ok",
        }
    if args.iso is None:
        raise ValueError("--iso is required for preview/write")
    if not devices:
        raise ValueError("provide --device flags or --mock-json")
    target = devices[0]
    cls = classify_device(target)
    if not cls.allowed:
        raise PermissionError(cls.reason)
    dry = args.action != "write"
    confirm = bool(args.confirm) and args.action == "write"
    # Write action still defaults to dry-run unless --confirm (safety).
    if args.action == "write" and not confirm:
        dry = True
    plan = plan_write(
        Path(args.iso),
        target,
        dry_run=dry,
        tool=args.tool,
        confirm=confirm and not dry,
    )
    return plan_to_dict(plan)


def run_theme_shop(args: Namespace, *, schemas: Path | None) -> Any:
    if args.action == "list":
        return list_theme_packs(Path(args.path))
    dest = args.dest or Path(args.path).parent / "imported"
    return str(import_theme_zip(Path(args.path), dest, schemas=schemas))


def run_snapshot_cards(args: Namespace) -> dict[str, Any]:
    return snapshot_entries_document(detect_btrfs_snapshots(Path(args.root)))
