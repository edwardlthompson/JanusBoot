"""Argument parser for janusbootctl (kept separate for file-line budgets)."""

from __future__ import annotations

import argparse
from pathlib import Path

from janusbootctl import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="janusbootctl", description="JanusBoot ESP CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--esp", type=Path, default=None, help="ESP root (default: fixtures/esp)")
    parser.add_argument("--schema-dir", type=Path, default=None, help="schema/ directory")
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
    crash.add_argument("--message", default="", help="Crash message")
    crash.add_argument("--stack", default="", help="Crash stack text")
    scan_p = sub.add_parser("scan", help="Discover EFI loaders (heuristics)")
    scan_p.add_argument("--root", type=Path, default=None, help="ESP root to scan")
    scan_p.add_argument("--write", action="store_true", help="Write entries.json")
    repair_p = sub.add_parser("repair-plan", help="Print dry-run repair plan JSON")
    repair_p.add_argument("--kind", choices=("janus", "bootmgfw", "nvram", "all"), default="all")
    theme_prev = sub.add_parser("theme-preview", help="Validate theme pack; print preview JSON")
    theme_prev.add_argument("theme_json", type=Path)
    theme_app = sub.add_parser("theme-apply", help="Copy validated theme pack onto ESP")
    theme_app.add_argument("theme_dir", type=Path)
    theme_app.add_argument("--dry-run", action="store_true")
    return parser
