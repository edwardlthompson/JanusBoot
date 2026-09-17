"""Optional settings PIN gate (hash only — never store plaintext PIN)."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Any


def hash_pin(pin: str, *, salt: str | None = None) -> dict[str, str]:
    """Return salt + sha256 hex for settings_pin storage."""
    if not pin or len(pin) < 4 or len(pin) > 12 or not pin.isdigit():
        raise ValueError("PIN must be 4–12 digits")
    salt_hex = salt or secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt_hex}:{pin}".encode()).hexdigest()
    return {"salt": salt_hex, "hash": digest}


def verify_pin(pin: str, stored: dict[str, Any]) -> bool:
    """Constant-time compare against settings.settings_pin."""
    salt = stored.get("salt")
    expected = stored.get("hash")
    if not isinstance(salt, str) or not isinstance(expected, str):
        return False
    try:
        got = hash_pin(pin, salt=salt)["hash"]
    except ValueError:
        return False
    return hmac.compare_digest(got, expected)


def pin_blocks_settings(settings: dict[str, Any], pin: str | None) -> bool:
    """True when PIN is enabled and missing/wrong (callers refuse theme/settings)."""
    block = settings.get("settings_pin")
    if not isinstance(block, dict) or not block.get("enabled"):
        return False
    if pin is None:
        return True
    return not verify_pin(pin, block)
