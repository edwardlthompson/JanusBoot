"""Guard: janusboot-host-dry-run.sh refuses destructive argv."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "janusboot-host-dry-run.sh"


@pytest.mark.parametrize(
    "bad_args",
    [
        ["--write"],
        ["--confirm"],
        ["repair-apply"],
        ["install"],
        ["write"],
        ["efibootmgr"],
    ],
)
def test_host_dry_run_refuses_destructive_args(bad_args: list[str]) -> None:
    assert SCRIPT.is_file()
    proc = subprocess.run(
        ["bash", str(SCRIPT), *bad_args],
        cwd=str(ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "REFUSE" in (proc.stderr + proc.stdout)


def test_host_dry_run_script_never_invokes_write_paths() -> None:
    src = SCRIPT.read_text(encoding="utf-8")
    assert "scan --write" not in src
    assert "usb write --" not in src
    assert "install --confirm" not in src
    assert "repair-apply --" not in src
    assert "efibootmgr -" not in src
    assert "janusbootctl" in src
    assert "validate" in src
    assert "REFUSE" in src
