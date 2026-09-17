"""Install JanusBoot/Limine files onto an ESP layout (dry-run first)."""

from __future__ import annotations

import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from janusbootctl.limine_gen import write_limine_conf
from janusbootctl.paths import janus_dir


@dataclass(frozen=True)
class InstallStep:
    action: str
    src: str | None
    dest: str
    risk: str

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


def plan_install(
    esp_root: Path,
    *,
    efi_binary: Path | None = None,
    conf_output: Path | None = None,
) -> list[InstallStep]:
    """Plan EFI binary + limine.conf placement under EFI/JanusBoot/."""
    janus = janus_dir(esp_root)
    steps = [
        InstallStep(
            action="mkdir",
            src=None,
            dest=str(janus),
            risk="none",
        ),
        InstallStep(
            action="write_limine_conf",
            src=None,
            dest=str(conf_output or (janus / "limine.conf")),
            risk="overwrites generated conf",
        ),
    ]
    if efi_binary is not None:
        steps.append(
            InstallStep(
                action="copy_efi",
                src=str(efi_binary),
                dest=str(janus / "BOOTX64.EFI"),
                risk="writes EFI binary we own",
            )
        )
        steps.append(
            InstallStep(
                action="copy_efi_fallback",
                src=str(efi_binary),
                dest=str(esp_root / "EFI" / "BOOT" / "BOOTX64.EFI"),
                risk="may replace EFI/BOOT fallback loader — confirm",
            )
        )
    return steps


def plan_nvram_entry(
    label: str = "JanusBoot",
    disk: str = "/dev/diskX",
    part: int = 1,
) -> dict[str, Any]:
    """Dry-run NVRAM Boot entry planner (LOCAL executes efibootmgr)."""
    return {
        "dry_run": True,
        "label": label,
        "disk": disk,
        "part": part,
        "loader": r"\EFI\JanusBoot\BOOTX64.EFI",
        "command_example": (
            f"efibootmgr -c -d {disk} -p {part} -L {label} -l '\\\\EFI\\\\JanusBoot\\\\BOOTX64.EFI'"
        ),
        "risk": "writes firmware BootOrder",
    }


def apply_install(
    esp_root: Path,
    *,
    efi_binary: Path | None = None,
    schemas: Path | None = None,
    confirm: bool = False,
    dry_run: bool = True,
) -> list[dict[str, Any]]:
    steps = plan_install(esp_root, efi_binary=efi_binary)
    if not dry_run and not confirm:
        raise ValueError("refusing install without --confirm (or use --dry-run)")
    results: list[dict[str, Any]] = []
    for step in steps:
        if dry_run:
            results.append({**step.to_dict(), "status": "dry_run"})
            continue
        dest = Path(step.dest)
        if step.action == "mkdir":
            dest.mkdir(parents=True, exist_ok=True)
        elif step.action == "write_limine_conf":
            write_limine_conf(esp_root, output=dest, schemas=schemas)
        elif step.action.startswith("copy_efi") and step.src:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(step.src, dest)
        results.append({**step.to_dict(), "status": "applied"})
    return results
