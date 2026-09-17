"""Repair dry-run helpers (Phase 7). Never writes NVRAM/BCD without confirm."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RepairPlan:
    """Proposed repair steps; apply only after explicit confirm (out of scope here)."""

    action: str
    target: str
    risk: str
    dry_run: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def plan_restore_janus_files(esp_root: Path, backup_name: str = "latest") -> list[RepairPlan]:
    """Plan restore of JanusBoot-owned JSON from EFI/JanusBoot/backup/."""
    janus = esp_root / "EFI" / "JanusBoot"
    backup = janus / "backup" / backup_name
    plans: list[RepairPlan] = []
    for name in ("settings.json", "entries.json"):
        src = backup / name
        dest = janus / name
        if src.is_file():
            plans.append(
                RepairPlan(
                    action="restore_file",
                    target=f"{src} → {dest}",
                    risk="overwrites current JanusBoot contract file",
                )
            )
        else:
            plans.append(
                RepairPlan(
                    action="skip_missing_backup",
                    target=str(src),
                    risk="none",
                )
            )
    return plans


def plan_windows_bootmgfw_restore(esp_root: Path) -> list[RepairPlan]:
    """Conservative plan: restore bootmgfw.efi only from our backup copy if present."""
    janus = esp_root / "EFI" / "JanusBoot"
    backup_efi = janus / "backup" / "bootmgfw.efi"
    live = esp_root / "EFI" / "Microsoft" / "Boot" / "bootmgfw.efi"
    if not backup_efi.is_file():
        return [
            RepairPlan(
                action="skip_no_backup",
                target=str(backup_efi),
                risk="none",
            )
        ]
    return [
        RepairPlan(
            action="restore_bootmgfw",
            target=f"{backup_efi} → {live}",
            risk="touches Windows Boot Manager path; requires elevation + confirm",
        )
    ]


def plan_efibootmgr_nvram(
    label: str = "JanusBoot", disk: str = "/dev/diskX", part: int = 1
) -> list[RepairPlan]:
    """Document-only NVRAM plan; LOCAL applies with efibootmgr on a real/VM ESP."""
    loader = r"\\EFI\\JanusBoot\\BOOTX64.EFI"
    return [
        RepairPlan(
            action="efibootmgr_create",
            target=f"label={label} disk={disk} part={part} loader={loader}",
            risk="writes NVRAM BootOrder; LOCAL only with confirm/dry-run",
        )
    ]
