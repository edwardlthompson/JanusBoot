"""CLI entry point for janusbootctl."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from janusbootctl import __version__
from janusbootctl.about import about_payload, about_summary
from janusbootctl.backup import backup_esp
from janusbootctl.config_io import get_value, parse_cli_value, set_value
from janusbootctl.crash import sanitize_crash_payload
from janusbootctl.limine_gen import write_limine_conf
from janusbootctl.paths import default_esp_root, schema_dir
from janusbootctl.validate import ValidationError, validate_esp, validate_theme


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="janusbootctl", description="JanusBoot ESP CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--esp",
        type=Path,
        default=None,
        help="ESP root containing EFI/JanusBoot (default: fixtures/esp)",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=None,
        help="Directory with *.schema.json (default: repo schema/)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate settings.json and entries.json")
    get_p = sub.add_parser("get", help="Get a dotted settings key")
    get_p.add_argument("key")
    set_p = sub.add_parser("set", help="Set a dotted settings key (JSON or string)")
    set_p.add_argument("key")
    set_p.add_argument("value")
    sub.add_parser("backup", help="Copy settings/entries into backup/")
    gen = sub.add_parser("generate-limine", help="Write limine.conf from JSON")
    gen.add_argument("-o", "--output", type=Path, default=None)
    theme = sub.add_parser("validate-theme", help="Validate a theme.json")
    theme.add_argument("path", type=Path)
    about = sub.add_parser("about", help="Print About (version + donate)")
    about.add_argument("--json", action="store_true", help="Emit About JSON payload")
    crash = sub.add_parser("sanitize-crash", help="Sanitize crash message/stack JSON on stdin")
    crash.add_argument(
        "--message",
        default="",
        help="Crash message (default: empty; prefer stdin JSON with message/stack)",
    )
    crash.add_argument("--stack", default="", help="Crash stack text")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
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
            dest = backup_esp(esp)
            print(str(dest))
        elif args.command == "generate-limine":
            path = write_limine_conf(esp, output=args.output, schemas=schemas)
            print(str(path))
        elif args.command == "validate-theme":
            validate_theme(args.path, schemas=schemas)
            print("ok")
        elif args.command == "about":
            if args.json:
                print(json.dumps(about_payload(), sort_keys=True))
            else:
                print(about_summary())
        elif args.command == "sanitize-crash":
            raw = {"message": args.message, "stack": args.stack}
            if not args.message and not args.stack and not sys.stdin.isatty():
                raw = json.load(sys.stdin)
            print(json.dumps(sanitize_crash_payload(raw), sort_keys=True))
    except (ValidationError, KeyError, TypeError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
