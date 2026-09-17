"""Execute / undo repair plans on JanusBoot-owned ESP paths only."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from janusbootctl.backup import backup_esp
from janusbootctl.paths import janus_dir, settings_path
from janusbootctl.repair import RepairPlan
from janusbootctl.validate import load_json


_OWNED_PREFIX = "EFI/JanusBoot/"


def _is_owned_dest(esp_root: Path, dest: Path) -> bool:
    try:
        rel = dest.resolve().relative_to(esp_root.resolve()).as_posix()
    except ValueError:
        return False
    return rel.startswith(_OWNED_PREFIX) or rel == "EFI/Microsoft/Boot/bootmgfw.efi"


def _append_history(esp_root: Path, record: dict[str, Any]) -> None:
    path = settings_path(esp_root)
    data = load_json(path)
    assert isinstance(data, dict)
    history = list(data.get("repair_history") or [])
    history.append(record)
    data["repair_history"] = history[-32:]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def apply_plans(
    esp_root: Path,
    plans: list[RepairPlan],
    *,
    confirm: bool,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Apply restore_* plans. Requires confirm=True unless dry_run."""
    if not dry_run and not confirm:
        raise ValueError("refusing repair apply without --confirm (or use --dry-run)")
    results: list[dict[str, Any]] = []
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    if not dry_run:
        backup_esp(esp_root, stamp=f"pre-repair-{stamp}")
    for plan in plans:
        if plan.action.startswith("skip_"):
            results.append({"action": plan.action, "status": "skipped", "target": plan.target})
            continue
        if plan.action == "efibootmgr_create":
            results.append(
                {
                    "action": plan.action,
                    "status": "deferred_local",
                    "target": plan.target,
                    "note": "NVRAM write is LOCAL-only",
                }
            )
            continue
        if plan.src is None or plan.dest is None:
            results.append({"action": plan.action, "status": "invalid", "target": plan.target})
            continue
        src, dest = Path(plan.src), Path(plan.dest)
        if not _is_owned_dest(esp_root, dest):
            raise ValueError(f"refusing write outside owned paths: {dest}")
        if dry_run:
            results.append({"action": plan.action, "status": "dry_run", "src": str(src), "dest": str(dest)})
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        results.append({"action": plan.action, "status": "applied", "src": str(src), "dest": str(dest)})
    if not dry_run:
        _append_history(
            esp_root,
            {"id": stamp, "when": stamp, "results": results, "undo_backup": f"pre-repair-{stamp}"},
        )
    return results


def undo_last_repair(esp_root: Path, *, confirm: bool, dry_run: bool = False) -> list[dict[str, Any]]:
    """Restore files from the backup named in the last repair_history entry."""
    if not dry_run and not confirm:
        raise ValueError("refusing undo without --confirm (or use --dry-run)")
    data = load_json(settings_path(esp_root))
    assert isinstance(data, dict)
    history = list(data.get("repair_history") or [])
    if not history:
        return [{"status": "empty", "note": "no repair_history"}]
    last = history[-1]
    backup_name = str(last.get("undo_backup") or "")
    backup = janus_dir(esp_root) / "backup" / backup_name
    plans = []
    for name in ("settings.json", "entries.json"):
        src = backup / name
        dest = janus_dir(esp_root) / name
        if src.is_file():
            plans.append(
                RepairPlan(
                    action="restore_file",
                    target=f"{src} → {dest}",
                    risk="undo last repair",
                    src=str(src),
                    dest=str(dest),
                    dry_run=dry_run,
                )
            )
    return apply_plans(esp_root, plans, confirm=confirm, dry_run=dry_run)
