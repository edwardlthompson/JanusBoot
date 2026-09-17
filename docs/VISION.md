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

## Phase 0–2 (shipped)

1. Schemas + ESP layout docs + fixtures (two fake OS entries).
2. `janusbootctl`: `validate`, `get`, `set`, `backup`, `generate-limine`.
3. Host QEMU+OVMF smoke (LOCAL lane): FAT image boots Limine with timeout,
   default, and wallpaper driven by JSON.

## Phase 3 — Scanner

`janusbootctl scan` walks known EFI paths (Linux shim/GRUB/systemd-boot/Limine +
Windows `bootmgfw.efi`) as pure heuristics. It never deletes foreign EFI files.
Optional `--write` updates `entries.json` with `source: scanned`.

## Phase 4 — Boot-time settings (minimum)

Limine in-menu editing is limited (timeout/default may be conf-only). JanusBoot
ships settings UX copy for OS tools:

| Setting | Boot menu (if Limine allows) | Linux / Windows via `janusbootctl` |
|---------|------------------------------|-------------------------------------|
| Timeout | Prefer in-menu; else OS tools | `set timeout` → regenerate conf |
| Default / last-used | Prefer in-menu; else OS tools | `set default` |
| Theme pack | Validated packs only | `theme-apply` then regenerate |
| Language / scan paths / mouse / hidden | OS tools first | settings.json keys |

Document Limine limits on QEMU (LOCAL). Do not block Phases 5–8 waiting for a
full in-boot settings UI — OS tools + regenerate is the supported path.

## Phase 5–6 — Desktop GUIs

Linux and Windows GUIs talk **only** to `janusbootctl` (same schemas). Windows
requires elevation before ESP/NVRAM/BCD writes; dry-run first.

## Phase 7–8 — Repair + polish

Repair plans are dry-run JSON (`repair-plan`). Theme packs are data; `theme-apply`
copies validated assets onto the ESP. EFI never executes theme code.

## Non-goals (v1)

No BURG core, no hostile Windows Boot Manager replacement, no theme scripts in
EFI, no network phone-home from EFI, no fake Secure Boot signing without keys.

## Expected host targets (LOCAL owns Makefile)

Cloud documents intent only — see `docs/limine-gen.md`. LOCAL implements
`validate`, `esp-image`, `qemu`, and test wrappers.
