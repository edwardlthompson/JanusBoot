"""Golden Path catalog path: re-export JanusBoot About (do not restore template hello)."""

from __future__ import annotations

from janusbootctl.about import (
    APP_VERSION,
    DONATE_URL,
    AboutPayload,
    AboutUpdate,
    about_payload,
    about_summary,
)

__all__ = [
    "APP_VERSION",
    "DONATE_URL",
    "AboutPayload",
    "AboutUpdate",
    "about_payload",
    "about_summary",
]
