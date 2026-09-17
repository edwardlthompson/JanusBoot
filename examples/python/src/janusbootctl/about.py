"""CLI About slice: version + donate URL + update stub (no crash payload)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import TypedDict

from janusbootctl import __version__ as _FALLBACK_VERSION

DONATE_URL = "https://github.com/sponsors/edwardlthompson"


def _package_version() -> str:
    try:
        return version("janusbootctl")
    except PackageNotFoundError:
        return _FALLBACK_VERSION


APP_VERSION = _package_version()


class AboutUpdate(TypedDict):
    status: str
    version: str | None
    url: str | None


class AboutPayload(TypedDict):
    version: str
    donate: str
    summary: str
    update: AboutUpdate


def about_summary() -> str:
    """Return a one-line About string."""
    return f"JanusBoot {APP_VERSION} donate {DONATE_URL}"


def about_payload() -> AboutPayload:
    """Return the shared About/donate/update JSON object."""
    return {
        "version": APP_VERSION,
        "donate": DONATE_URL,
        "summary": about_summary(),
        "update": {"status": "current", "version": None, "url": None},
    }
