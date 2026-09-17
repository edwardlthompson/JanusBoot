"""Command dispatch helpers for janusbootctl (keeps cli.py under line budget)."""

from __future__ import annotations

import json
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

from janusbootctl.cli_extra import run_snapshot_cards, run_theme_shop, run_usb_command
from janusbootctl.install_esp import apply_install, plan_nvram_entry
from janusbootctl.oneshot import build_oneshot_entry, clear_oneshot_entry, write_oneshot_entry
from janusbootctl.repair import (
    plan_efibootmgr_nvram,
    plan_restore_janus_files,
    plan_windows_bootmgfw_restore,
)
from janusbootctl.repair_apply import apply_plans, undo_last_repair
from janusbootctl.scan import discover_candidates, entries_document
from janusbootctl.theme_apply import apply_theme_to_esp, preview_theme
from janusbootctl.validate import validate_esp


def dispatch_heavy(args: Namespace, esp: Path, schemas: Path | None) -> bool:
    """Handle scan/repair/theme/usb/install/gui. Return False if unhandled."""
    cmd = args.command
    if cmd == "scan":
        doc = entries_document(discover_candidates(args.root or esp, deep=not args.shallow))
        if args.write:
            out = Path(esp) / "EFI" / "JanusBoot" / "entries.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            validate_esp(esp, schemas=schemas)
            print(str(out))
        else:
            print(json.dumps(doc, indent=2))
        return True
    if cmd == "repair-plan":
        plans: list[Any] = []
        if args.kind in ("janus", "all"):
            plans.extend(plan_restore_janus_files(esp))
        if args.kind in ("bootmgfw", "all"):
            plans.extend(plan_windows_bootmgfw_restore(esp))
        if args.kind in ("nvram", "all"):
            plans.extend(plan_efibootmgr_nvram())
        print(json.dumps([p.to_dict() for p in plans], indent=2))
        return True
    if cmd == "repair-apply":
        plans = []
        if args.kind in ("janus", "all"):
            plans.extend(plan_restore_janus_files(esp))
        if args.kind in ("bootmgfw", "all"):
            plans.extend(plan_windows_bootmgfw_restore(esp))
        print(
            json.dumps(
                apply_plans(esp, plans, confirm=args.confirm, dry_run=args.dry_run), indent=2
            )
        )
        return True
    if cmd == "repair-undo":
        print(
            json.dumps(undo_last_repair(esp, confirm=args.confirm, dry_run=args.dry_run), indent=2)
        )
        return True
    if cmd == "oneshot":
        if args.clear:
            print("cleared" if clear_oneshot_entry(esp) else "none")
        else:
            entry = build_oneshot_entry(args.vmlinuz, initrd=args.initrd, cmdline=args.cmdline)
            print(str(write_oneshot_entry(esp, entry)))
        return True
    if cmd == "theme-preview":
        print(
            json.dumps(
                preview_theme(
                    args.theme_json,
                    schemas=schemas,
                    out=args.output,
                    width=args.width,
                    height=args.height,
                    preset=args.preset,
                ),
                sort_keys=True,
            )
        )
        return True
    if cmd == "theme-apply":
        print(str(apply_theme_to_esp(args.theme_dir, esp, schemas=schemas, dry_run=args.dry_run)))
        return True
    if cmd == "theme-shop":
        print(json.dumps(run_theme_shop(args, schemas=schemas), indent=2))
        return True
    if cmd == "snapshot-cards":
        print(json.dumps(run_snapshot_cards(args), indent=2))
        return True
    if cmd == "usb":
        print(json.dumps(run_usb_command(args), indent=2))
        return True
    if cmd == "install":
        if args.plan_nvram:
            print(json.dumps(plan_nvram_entry(), indent=2))
        else:
            dry = args.dry_run or not args.confirm
            print(
                json.dumps(
                    apply_install(
                        esp,
                        efi_binary=args.efi,
                        schemas=schemas,
                        confirm=args.confirm,
                        dry_run=dry,
                    ),
                    indent=2,
                )
            )
        return True
    if cmd == "gui":
        if args.platform == "linux":
            from janusbootctl.linux_gui import launch_linux_gui

            launch_linux_gui(esp)
        else:
            from janusbootctl.windows_gui import launch_windows_gui

            launch_windows_gui(esp)
        return True
    return False


def crash_payload(args: Namespace) -> dict[str, Any]:
    raw: dict[str, Any] = {"message": args.message, "stack": args.stack}
    if not args.message and not args.stack and not sys.stdin.isatty():
        raw = json.load(sys.stdin)
    return raw
