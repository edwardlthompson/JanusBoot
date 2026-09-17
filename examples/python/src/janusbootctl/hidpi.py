"""HiDPI preview size presets (1080p → 4K native scale)."""

from __future__ import annotations

PRESETS: dict[str, tuple[int, int]] = {
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4k": (3840, 2160),
}


def resolve_preview_size(
    preset: str | None = None,
    *,
    width: int | None = None,
    height: int | None = None,
) -> tuple[int, int]:
    """Resolve preview dimensions; preset overrides width/height when set."""
    if preset:
        key = preset.lower().strip()
        if key not in PRESETS:
            raise ValueError(f"unknown preset {preset!r}; choose from {sorted(PRESETS)}")
        return PRESETS[key]
    w = 1920 if width is None else width
    h = 1080 if height is None else height
    if w < 640 or h < 480 or w > 3840 or h > 2160:
        raise ValueError("preview size out of range (640x480–3840x2160)")
    return w, h


def scale_factor_for(width: int, height: int) -> float:
    """Scale relative to 1080p short edge (for UI chrome math)."""
    return min(width / 1920.0, height / 1080.0)
