"""Golden Path web must ship CSP, Referrer-Policy, and Permissions-Policy."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "examples" / "web"


class WebSecurityHeaderTests(unittest.TestCase):
    def test_index_meta_policies(self) -> None:
        if not (WEB / "index.html").is_file():
            self.skipTest("web example pruned")
        html = (WEB / "index.html").read_text(encoding="utf-8")
        self.assertIn('name="referrer"', html)
        self.assertIn("no-referrer", html)
        self.assertIn("Permissions-Policy", html)
        self.assertIn("camera=()", html)
        self.assertNotIn("Content-Security-Policy", html)

    def test_vite_preview_headers(self) -> None:
        if not (WEB / "vite.config.ts").is_file():
            self.skipTest("web example pruned")
        vite = (WEB / "vite.config.ts").read_text(encoding="utf-8")
        self.assertIn("injectCspMeta", vite)
        self.assertIn("Referrer-Policy", vite)
        self.assertIn("frame-ancestors 'none'", vite)
        self.assertIn("preview: { headers: SECURITY_HEADERS }", vite)


if __name__ == "__main__":
    unittest.main()
