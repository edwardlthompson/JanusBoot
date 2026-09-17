"""Golden Path catalog path: re-export JanusBoot crash sanitizer."""

from __future__ import annotations

from janusbootctl.crash import sanitize_crash_payload, sanitize_crash_text

__all__ = ["sanitize_crash_payload", "sanitize_crash_text"]
