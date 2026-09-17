"""Fail when README hero/stack/owner badges drift from repo truth."""
from __future__ import annotations

import json
from pathlib import Path

OWNER_COLORS = {
    "AGENT": "2ea043",
    "HUMAN": "0969da",
    "ADB": "bf8700",
    "AUTO": "656d76",
}
STACK_COLORS = {
    "web": "646cff",
    "python": "3776AB",
    "android": "3DDC84",
}


def _product_mode(root: Path) -> bool:
    path = root / "branding" / "product.json"
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return str(data.get("mode") or "") == "product"


def _active_stacks(root: Path) -> list[str]:
    sel = root / ".cursor" / "stack-selection.json"
    if sel.is_file():
        try:
            data = json.loads(sel.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        modules = data.get("active_modules")
        if isinstance(modules, list) and modules:
            return [str(m) for m in modules if str(m) in STACK_COLORS]
        stack = str(data.get("stack") or "").strip()
        if stack in STACK_COLORS:
            return [stack]
    return list(STACK_COLORS)


def check_repo(root: Path) -> list[str]:
    readme = (root / "README.md").read_text(encoding="utf-8")
    version = (root / ".template-version").read_text(encoding="utf-8").strip()
    errors: list[str] = []
    product = _product_mode(root)
    if not product and f"badge/template-{version}" not in readme:
        errors.append(f"hero template badge must be template-{version}")
    if "badge/license-MIT" not in readme:
        errors.append("hero license badge must be MIT")
    if "FOSS-no_tracking" not in readme:
        errors.append("hero FOSS badge must say no_tracking")
    if "actions/workflows/ci.yml" not in readme:
        errors.append("CI badge must link ci.yml")
    for label, color in OWNER_COLORS.items():
        needle = f"badge/{label}-"
        if needle not in readme or color not in readme:
            errors.append(f"owner badge {label} / {color} missing")
        elif f"{label}-" not in readme or color.lower() not in readme.lower():
            errors.append(f"owner badge {label} color {color} missing")
    for stack in _active_stacks(root):
        color = STACK_COLORS[stack]
        if f"badge/{stack}-stack-{color}" not in readme:
            errors.append(f"stack badge {stack} must use {color}")
    return errors


def main() -> int:
    errors = check_repo(Path.cwd())
    if errors:
        print("README badge accuracy check failed:")
        for item in errors:
            print(f"  {item}")
        return 1
    print("README badge accuracy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
