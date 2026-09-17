"""CLI entry point for janusbootctl."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from janusbootctl.about import about_payload, about_summary
from janusbootctl.backup import backup_esp, backup_with_nvram
from janusbootctl.cli_parser import build_parser
from janusbootctl.config_io import get_value, parse_cli_value, set_value
from janusbootctl.crash import sanitize_crash_payload
from janusbootctl.install_esp import apply_install, plan_nvram_entry
from janusbootctl.limine_gen import write_limine_conf
from janusbootctl.oneshot import build_oneshot_entry, clear_oneshot_entry, write_oneshot_entry
from janusbootctl.paths import default_esp_root, schema_dir
from janusbootctl.repair import (
    plan_efibootmgr_nvram,
    plan_restore_janus_files,
    plan_windows_bootmgfw_restore,
)
from janusbootctl.repair_apply import apply_plans, undo_last_repair
from janusbootctl.scan import discover_candidates, entries_document
from janusbootctl.theme_apply import apply_theme_to_esp, preview_theme
from janusbootctl.validate import ValidationError, validate_esp, validate_theme


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    esp = args.esp or default_esp_root()
    schemas = args.schema_dir or schema_dir()

    try:
        if args.command == "validate":
            validate_esp(esp, schemas=schemas)
            print("ok")
        elif args.command == "get":
            print(json.dumps(get_value(esp, args.key)))
        elif args.command == "set":
            set_value(esp, args.key, parse_cli_value(args.value), schemas=schemas)
            print("ok")
        elif args.command == "backup":
            if args.with_nvram:
                print(json.dumps(backup_with_nvram(esp, nvram_dump=args.nvram_text), indent=2))
            else:
                print(str(backup_esp(esp)))
        elif args.command == "generate-limine":
            print(str(write_limine_conf(esp, output=args.output, schemas=schemas)))
        elif args.command == "validate-theme":
            validate_theme(args.path, schemas=schemas)
            print("ok")
        elif args.command == "about":
            print(json.dumps(about_payload(), sort_keys=True) if args.json else about_summary())
        elif args.command == "sanitize-crash":
            raw = {"message": args.message, "stack": args.stack}
            if not args.message and not args.stack and not sys.stdin.isatty():
                raw = json.load(sys.stdin)
            print(json.dumps(sanitize_crash_payload(raw), sort_keys=True))
        elif args.command == "scan":
            doc = entries_document(discover_candidates(args.root or esp, deep=not args.shallow))
            if args.write:
                out = Path(esp) / "EFI" / "JanusBoot" / "entries.json"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
                validate_esp(esp, schemas=schemas)
                print(str(out))
            else:
                print(json.dumps(doc, indent=2))
        elif args.command == "repair-plan":
            plans = []
            if args.kind in ("janus", "all"):
                plans.extend(plan_restore_janus_files(esp))
            if args.kind in ("bootmgfw", "all"):
                plans.extend(plan_windows_bootmgfw_restore(esp))
            if args.kind in ("nvram", "all"):
                plans.extend(plan_efibootmgr_nvram())
            print(json.dumps([p.to_dict() for p in plans], indent=2))
        elif args.command == "repair-apply":
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
        elif args.command == "repair-undo":
            print(
                json.dumps(
                    undo_last_repair(esp, confirm=args.confirm, dry_run=args.dry_run), indent=2
                )
            )
        elif args.command == "oneshot":
            if args.clear:
                print("cleared" if clear_oneshot_entry(esp) else "none")
            else:
                entry = build_oneshot_entry(args.vmlinuz, initrd=args.initrd, cmdline=args.cmdline)
                print(str(write_oneshot_entry(esp, entry)))
        elif args.command == "theme-preview":
            print(
                json.dumps(
                    preview_theme(
                        args.theme_json,
                        schemas=schemas,
                        out=args.output,
                        width=args.width,
                        height=args.height,
                    ),
                    sort_keys=True,
                )
            )
        elif args.command == "theme-apply":
            dest = apply_theme_to_esp(args.theme_dir, esp, schemas=schemas, dry_run=args.dry_run)
            print(str(dest))
        elif args.command == "install":
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
        elif args.command == "gui":
            if args.platform == "linux":
                from janusbootctl.linux_gui import launch_linux_gui

                launch_linux_gui(esp)
            else:
                from janusbootctl.windows_gui import launch_windows_gui

                launch_windows_gui(esp)
    except (ValidationError, KeyError, TypeError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
