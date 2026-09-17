"""Guard: janusboot-host-dry-run.sh refuses destructive argv."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "janusboot-host-dry-run.sh"


class HostDryRunTests(unittest.TestCase):
    def test_host_dry_run_refuses_destructive_args(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        for bad_args in (
            ["--write"],
            ["--confirm"],
            ["repair-apply"],
            ["install"],
            ["write"],
            ["efibootmgr"],
        ):
            with self.subTest(bad_args=bad_args):
                proc = subprocess.run(
                    ["bash", str(SCRIPT), *bad_args],
                    cwd=str(ROOT),
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
                self.assertIn("REFUSE", proc.stderr + proc.stdout)

    def test_host_dry_run_script_never_invokes_write_paths(self) -> None:
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("scan --write", src)
        self.assertNotIn("usb write --", src)
        self.assertNotIn("install --confirm", src)
        self.assertNotIn("repair-apply --", src)
        self.assertNotIn("efibootmgr -", src)
        self.assertIn("janusbootctl", src)
        self.assertIn("validate", src)
        self.assertIn("REFUSE", src)


if __name__ == "__main__":
    unittest.main()
