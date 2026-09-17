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
- **Userspace:** `janusbootctl` validates, gets/sets, backs up, applies themes
  (later), and generates Limine config.
- **GUIs (later):** Linux and Windows talk only to `janusbootctl` and share the
  same JSON schemas.

## Phase 0–2 (this deliverable)

1. Schemas + ESP layout docs + fixtures (two fake OS entries).
2. `janusbootctl`: `validate`, `get`, `set`, `backup`, `generate-limine`.
3. Host QEMU+OVMF smoke (LOCAL lane): FAT image boots Limine with timeout,
   default, and wallpaper driven by JSON.

## Phase 4 note — boot-time settings (minimum)

If Limine cannot edit settings in-menu, JanusBoot still ships: change timeout,
default, and theme from **OS tools** (`janusbootctl` / desktop GUIs), then
regenerate `limine.conf` and write the ESP. Document that path; do not block
Phases 3–8 waiting for a full in-boot settings UI.

## Non-goals (v1)

No BURG core, no hostile Windows Boot Manager replacement, no theme scripts in
EFI, no network phone-home from EFI, no fake Secure Boot signing without keys.

## Expected host targets (LOCAL owns Makefile)

Cloud documents intent only — see `docs/limine-gen.md`. LOCAL implements
`validate`, `esp-image`, `qemu`, and test wrappers.
