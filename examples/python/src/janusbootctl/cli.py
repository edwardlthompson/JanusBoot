"""CLI entry point for janusbootctl."""

from __future__ import annotations

import json
import sys

from janusbootctl.about import about_payload, about_summary
from janusbootctl.backup import backup_esp, backup_with_nvram
from janusbootctl.cli_dispatch import crash_payload, dispatch_heavy
from janusbootctl.cli_parser import build_parser
from janusbootctl.config_io import get_value, parse_cli_value, set_value
from janusbootctl.crash import sanitize_crash_payload
from janusbootctl.limine_gen import write_limine_conf
from janusbootctl.paths import default_esp_root, schema_dir
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
            print(json.dumps(sanitize_crash_payload(crash_payload(args)), sort_keys=True))
        elif dispatch_heavy(args, esp, schemas):
            pass
        else:
            raise ValueError(f"unknown command: {args.command}")
    except (ValidationError, KeyError, TypeError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
