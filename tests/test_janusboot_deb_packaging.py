"""Pure-logic checks for JanusBoot .deb packaging (LOCAL lane)."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "packaging" / "deb" / "debian" / "control"
GUI_BIN = ROOT / "packaging" / "deb" / "bin" / "janusboot-gui"
CTL_BIN = ROOT / "packaging" / "deb" / "bin" / "janusbootctl"
BUILD_DEB = ROOT / "scripts" / "janusboot-build-deb.sh"


class DebPackagingTests(unittest.TestCase):
    def test_control_has_required_fields(self) -> None:
        text = CONTROL.read_text(encoding="utf-8")
        self.assertIn("Package: janusbootctl", text)
        self.assertIsNotNone(re.search(r"^Version:\s+\S+", text, re.M))
        self.assertIn("Architecture: all", text)
        self.assertIn("python3-tk", text)
        self.assertIn("python3-jsonschema", text)

    def test_gui_wrapper_supports_smoke_flags(self) -> None:
        src = GUI_BIN.read_text(encoding="utf-8")
        self.assertIn("--smoke", src)
        self.assertIn("--self-test", src)
        self.assertIn("smoke ok", src)
        self.assertIn("JANUSBOOT_SHARE", src)

    def test_cli_wrapper_sets_share_path(self) -> None:
        src = CTL_BIN.read_text(encoding="utf-8")
        self.assertIn("JANUSBOOT_SHARE", src)
        self.assertIn("janusbootctl.cli", src)

    def test_build_deb_script_is_host_safe(self) -> None:
        src = BUILD_DEB.read_text(encoding="utf-8")
        self.assertIn("dpkg-deb", src)
        self.assertNotIn("apt install", src)
        self.assertNotIn("dpkg -i", src)
        self.assertIn("/usr/share/janusboot", src)

    def test_build_deb_produces_artifact(self) -> None:
        if not BUILD_DEB.is_file():
            self.skipTest("build script missing")
        if not (ROOT / "examples" / "python" / "src" / "janusbootctl").is_dir():
            self.skipTest("janusbootctl sources missing")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            out.mkdir()
            proc = subprocess.run(
                ["bash", str(BUILD_DEB), "--out", str(out)],
                cwd=str(ROOT),
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            debs = list(out.glob("janusbootctl_*_all.deb"))
            self.assertTrue(debs, "expected a .deb under out/")
            self.assertGreater(debs[0].stat().st_size, 1000)

    def test_gui_argparse_smoke_ms_default(self) -> None:
        """Load argparse without Tk by exec'ing just _parse via subprocess --help."""
        env = dict(os.environ)
        env["JANUSBOOT_SHARE"] = str(ROOT)
        proc = subprocess.run(
            [sys.executable, str(GUI_BIN), "--help"],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--smoke", proc.stdout)
        self.assertIn("--self-test", proc.stdout)


if __name__ == "__main__":
    unittest.main()
