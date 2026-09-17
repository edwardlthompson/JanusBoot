# JanusBoot vision

A UEFI-first graphical boot manager that feels like BURG, scans like rEFInd, can
repair a broken OS path like Super GRUB, and stores **one** settings/theme
contract on the ESP that you can change from the boot menu, from Linux, and
from Windows.

## Engine

- **Loader:** Limine (UEFI x86_64). We generate `limine.conf`; we do not fork
  bootloaders or vendor BURG.
- **Contract on ESP:** `EFI/JanusBoot/` — `settings.json`, `entries.json`,
  themes, icons, backups.
- **Userspace:** `janusbootctl` validates, gets/sets, backs up (incl. NVRAM dump
  folder), applies themes, installs EFI+conf, and generates Limine config.
- **GUIs:** Linux (Mint-friendly Tk) and Windows (elevation-gated Tk) talk only
  to `janusbootctl` and share the same JSON schemas (`schema/parity.manifest.json`).

## Boot UI cards — honest Limine floor

See `themes/BOOT_UI.md`. Limine gives wallpaper + timeout + list/submenu entries
(More… for hidden). True BURG card grids are not Limine’s model; OS tools cover
reorder/icons/timeout/theme. Empty disk emits calm Scan again / Firmware rows.

## In-boot settings vs OS-tools floor (Phase 4 escape hatch — accepted)

Limine in-menu editing cannot CRUD `settings.json`. **Must (v1) ships the OS-tools
floor:** Linux + Windows GUIs + CLI cover timeout, default/last-used, and theme.
QEMU documents the floor in `docs/qemu.md`. Do not block releases waiting for a
full in-boot gear menu.

## Scanner

Deep scan: heuristics + recursive `EFI/**/*.efi` walk + optional Linux
`/boot` vmlinuz pairs (`scan_host`). Windows host plan is documented dry-run.
Never delete foreign EFI files.

## Repair

`repair-plan` / `repair-apply` / `repair-undo` with confirm or dry-run. Owned
paths under `EFI/JanusBoot/` (+ conservative bootmgfw from our backup). History
in `settings.repair_history`. NVRAM create stays LOCAL (`efibootmgr`).

## One-shot rescue

`janusbootctl oneshot <vmlinuz> [--initrd]` writes a temporary linux entry
(userspace), then regenerate Limine conf.

## Themes

Built-in packs: `high-contrast`, `mint-dark`, `elegant-dark` with real
JPEG/PNG + icons. Apply uses `themes/.next/` → live + `last-good/`; preview
renders 1080p/4K PNG (not metadata-only).

## Install

`janusbootctl install [--efi BOOTX64.EFI] --dry-run|--confirm` plus
`--plan-nvram` for BootOrder planner.

## Non-goals (v1)

No BURG core, no hostile Windows Boot Manager replacement, no theme scripts in
EFI, no network phone-home from EFI, no fake Secure Boot signing without keys.
