"""Pure-logic checks for JanusBoot .deb packaging (LOCAL lane)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "packaging" / "deb" / "debian" / "control"
GUI_BIN = ROOT / "packaging" / "deb" / "bin" / "janusboot-gui"
CTL_BIN = ROOT / "packaging" / "deb" / "bin" / "janusbootctl"
BUILD_DEB = ROOT / "scripts" / "janusboot-build-deb.sh"


def test_control_has_required_fields() -> None:
    text = CONTROL.read_text(encoding="utf-8")
    assert "Package: janusbootctl" in text
    assert re.search(r"^Version:\s+\S+", text, re.M)
    assert "Architecture: all" in text
    assert "python3-tk" in text
    assert "python3-jsonschema" in text


def test_gui_wrapper_supports_smoke_flags() -> None:
    src = GUI_BIN.read_text(encoding="utf-8")
    assert "--smoke" in src
    assert "--self-test" in src
    assert "smoke ok" in src
    assert "JANUSBOOT_SHARE" in src


def test_cli_wrapper_sets_share_path() -> None:
    src = CTL_BIN.read_text(encoding="utf-8")
    assert "JANUSBOOT_SHARE" in src
    assert "janusbootctl.cli" in src


def test_build_deb_script_is_host_safe() -> None:
    src = BUILD_DEB.read_text(encoding="utf-8")
    assert "dpkg-deb" in src
    assert "apt install" not in src
    assert "dpkg -i" not in src
    assert "/usr/share/janusboot" in src


@pytest.mark.skipif(not BUILD_DEB.is_file(), reason="build script missing")
def test_build_deb_produces_artifact(tmp_path: Path) -> None:
    if not (ROOT / "examples" / "python" / "src" / "janusbootctl").is_dir():
        pytest.skip("janusbootctl sources missing")
    out = tmp_path / "dist"
    out.mkdir()
    proc = subprocess.run(
        ["bash", str(BUILD_DEB), "--out", str(out)],
        cwd=str(ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    debs = list(out.glob("janusbootctl_*_all.deb"))
    assert debs, "expected a .deb under out/"
    assert debs[0].stat().st_size > 1000


def test_gui_argparse_smoke_ms_default() -> None:
    """Load argparse without Tk by exec'ing just _parse via subprocess --help."""
    proc = subprocess.run(
        [sys.executable, str(GUI_BIN), "--help"],
        check=False,
        capture_output=True,
        text=True,
        env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "JANUSBOOT_SHARE": str(ROOT)},
    )
    assert proc.returncode == 0
    assert "--smoke" in proc.stdout
    assert "--self-test" in proc.stdout
