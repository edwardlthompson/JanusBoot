"""Linux Mint-friendly GUI: CLI façade (Tk launch in gui_tk)."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Any


@dataclass(frozen=True)
class CliResult:
    ok: bool
    stdout: str
    stderr: str
    code: int


def run_janusbootctl(args: list[str], *, esp: Path | None = None) -> CliResult:
    """Invoke janusbootctl as a subprocess (no direct toolkit imports)."""
    exe = which("janusbootctl")
    prefix = [exe] if exe else [sys.executable, "-m", "janusbootctl"]
    cmd = [*prefix]
    if esp is not None:
        cmd.extend(["--esp", str(esp)])
    cmd.extend(args)
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    return CliResult(
        ok=proc.returncode == 0,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
        code=proc.returncode,
    )


def list_entries_via_cli(esp: Path) -> list[dict[str, Any]]:
    result = run_janusbootctl(["validate"], esp=esp)
    if not result.ok:
        raise RuntimeError(result.stderr or "validate failed")
    raw = json.loads((esp / "EFI" / "JanusBoot" / "entries.json").read_text(encoding="utf-8"))
    entries = raw.get("entries")
    return [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else []


def set_timeout_via_cli(esp: Path, seconds: int) -> CliResult:
    return run_janusbootctl(["set", "timeout", str(seconds)], esp=esp)


def set_theme_via_cli(esp: Path, theme_dir: Path) -> CliResult:
    return run_janusbootctl(["theme-apply", str(theme_dir)], esp=esp)


def install_dry_run_via_cli(esp: Path) -> CliResult:
    return run_janusbootctl(["install", "--dry-run"], esp=esp)


def launch_linux_gui(esp: Path) -> None:
    from janusbootctl.gui_tk import launch_linux_gui as _launch

    _launch(esp)
