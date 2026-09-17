"""Windows GUI helpers + elevation warnings (userspace; CLI-only writes)."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from janusbootctl.linux_gui import CliResult, list_entries_via_cli, run_janusbootctl, set_timeout_via_cli

ELEVATION_WARNING = (
    "JanusBoot Windows tools require an elevated (Administrator) prompt before any "
    "ESP, NVRAM, or BCD write. Dry-run first. Never silent-write."
)


@dataclass(frozen=True)
class WindowsGuiState:
    elevated: bool
    warning: str
    entries: list[dict[str, Any]]


def is_elevated() -> bool:
    """Best-effort admin check (Windows); False on non-Windows."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        return False


def windows_gui_snapshot(esp: Path) -> WindowsGuiState:
    return WindowsGuiState(
        elevated=is_elevated(),
        warning=ELEVATION_WARNING,
        entries=list_entries_via_cli(esp),
    )


def launch_windows_gui(esp: Path) -> None:
    from janusbootctl.gui_tk import launch_windows_gui as _launch

    _launch(esp)


__all__ = [
    "ELEVATION_WARNING",
    "CliResult",
    "WindowsGuiState",
    "is_elevated",
    "launch_windows_gui",
    "list_entries_via_cli",
    "run_janusbootctl",
    "set_timeout_via_cli",
    "windows_gui_snapshot",
]
