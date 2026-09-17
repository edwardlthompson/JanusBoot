"""Theme image resize/compress + desktop preview (Pillow)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def compile_background(
    source: Path,
    dest: Path,
    *,
    max_width: int = 3840,
    max_height: int = 2160,
    max_bytes: int = 2_097_152,
    quality: int = 85,
) -> Path:
    """Resize/compress wallpaper into dest (JPEG preferred)."""
    img = Image.open(source).convert("RGB")
    img.thumbnail((max_width, max_height))
    dest.parent.mkdir(parents=True, exist_ok=True)
    q = quality
    while q >= 40:
        img.save(dest, format="JPEG", quality=q, optimize=True)
        if dest.stat().st_size <= max_bytes:
            return dest
        q -= 10
    raise ValueError(f"background still exceeds {max_bytes} bytes after compress")


def render_preview(
    theme: dict[str, Any],
    background: Path | None,
    dest: Path,
    *,
    width: int = 1920,
    height: int = 1080,
) -> Path:
    """Raster preview at 1080p or 4K — not metadata-only."""
    colors = theme.get("colors") if isinstance(theme.get("colors"), dict) else {}
    bg_color = "#1A1A1A"
    accent = str(colors.get("accent") or "#92B372")
    text = str(colors.get("text") or "#FFFFFF")
    if background is not None and background.is_file():
        canvas = Image.open(background).convert("RGB").resize((width, height))
    else:
        canvas = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    name = str(theme.get("name") or "theme")
    draw.rectangle([width // 10, height // 3, width * 9 // 10, height // 3 + 120], outline=accent, width=4)
    draw.text((width // 10 + 24, height // 3 + 40), f"{name} preview ({width}x{height})", fill=text, font=font)
    draw.text((width // 10 + 24, height // 3 + 70), "JanusBoot theme pack", fill=accent, font=font)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, format="PNG")
    return dest
