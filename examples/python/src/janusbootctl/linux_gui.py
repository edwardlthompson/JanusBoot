"""Linux GUI façade (Phase 5): talks only to janusbootctl CLI subprocess."""

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
    prefix: list[str]
    exe = which("janusbootctl")
    if exe:
        prefix = [exe]
    else:
        prefix = [sys.executable, "-m", "janusbootctl"]
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
    """Validate via CLI, then read entries.json (shared schema contract)."""
    result = run_janusbootctl(["validate"], esp=esp)
    if not result.ok:
        raise RuntimeError(result.stderr or "validate failed")
    raw = json.loads((esp / "EFI" / "JanusBoot" / "entries.json").read_text(encoding="utf-8"))
    entries = raw.get("entries")
    if not isinstance(entries, list):
        return []
    return [e for e in entries if isinstance(e, dict)]


def set_timeout_via_cli(esp: Path, seconds: int) -> CliResult:
    return run_janusbootctl(["set", "timeout", str(seconds)], esp=esp)
