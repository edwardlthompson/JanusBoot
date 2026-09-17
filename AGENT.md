# AGENT.md — original product brief (Sacred)

Copy this file to `AGENT.md` after clone and **before** `init-project`. Paste the
human’s original prompt **verbatim**. Bootstrap stamps `AGENTS.md` only and will
not overwrite this file. Later sessions: read this before any BUILD_PLAN sprint row.

<!-- agent-brief:one-liner -->
A UEFI-first graphical boot manager that feels like BURG, scans like rEFInd, can repair a broken OS path like Super GRUB, and stores one settings/theme contract on the ESP that you can change from the boot menu, from Linux, and from Windows.
<!-- /agent-brief:one-liner -->

<!-- agent-brief:keywords -->
limine, uefi, janusbootctl, EFI/JanusBoot, qemu, ovmf
<!-- /agent-brief:keywords -->

---

# JanusBoot — Cursor agent brief

**Product name:** JanusBoot  
**CLI / package:** `janusbootctl`  
**EFI binary (target):** `JANUSBOOT.EFI` (or Limine as the loader plus JanusBoot assets)  
**ESP layout:** `EFI/JanusBoot/`  
**Spoken name:** works in English and Spanish (Jano / Janus; keep the English product string **JanusBoot** everywhere in UI/docs).

Do **not** revive BURG as the core. BURG is the *look* (icons, themes, last-used, skip countdown). Engine: **Limine** (UEFI, maintained) + a small repair/settings layer. Steal *ideas* from rEFInd (scan, icons), Super GRUB (rescue when an OS will not boot), Grub Customizer / grub-editor / rEFInd (edit from the OS). Do not vendor BURG source.

---

## One-sentence vision

A UEFI-first graphical boot manager that feels like BURG, scans like rEFInd, can repair a broken OS path like Super GRUB, and stores **one** settings/theme contract on the ESP that you can change **from the boot menu, from Linux, and from Windows**.

---

## Non-goals

- Do not fork or ship unmaintained BURG as the bootloader.
- Do not replace Windows Boot Manager in a hostile way.
- Do not run user theme scripts in EFI (JSON + images only).
- Do not implement exploit PoCs, malware, or unsigned “kernel patching.”
- No network phone-home from EFI.
- v1 is **UEFI x86_64** only (QEMU+OVMF first). ARM64 later.
- Secure Boot: **document** signing / shim; do not fake signed boot in v1 unless keys exist.
- BitLocker/LUKS: detect and leave unlocking to firmware/OS.

---

## Architecture

1. **Loader + boot UI:** Limine (generate `limine.conf` from our JSON). Do not invent a new boot protocol in v1.
2. **Config on ESP (single source of truth):**
   - `EFI/JanusBoot/settings.json`
   - `EFI/JanusBoot/entries.json`
   - `EFI/JanusBoot/themes//` (compiled boot assets + manifest)
   - `EFI/JanusBoot/icons/`
   - backups: `EFI/JanusBoot/backup/`
3. **Userspace:** `janusbootctl` (validate, get/set, theme apply, backup, generate Limine conf, install to ESP).
4. **Linux GUI (Mint-friendly):** Grub Customizer–like; talks only to `janusbootctl`.
5. **Windows GUI:** same operations; require elevation; warn before NVRAM/BCD/ESP writes.
6. **Repair:** userspace first (safer). EFI-side file picker is later. Super GRUB is a reference for flows, not something to fork as the product.
7. **Scanner:** Linux (ESP + os-prober-style paths) and Windows (`bootmgfw.efi`). Never delete foreign EFI files.

---

## UX

### Boot screen
- Full-screen theme, not a tiny GRUB box.
- OS **cards**: large icon + short name + subtitle (`Windows 11`, `Linux Mint`, `Firmware setup`).
- Keyboard: arrows, Enter, Esc, digits 1–9. Mouse optional (nice, not v1 must).
- Visible but quiet timeout bar. Hold Shift or tap Esc to cancel timeout (BURG “skip countdown”).
- **Last used** highlighted; pin icon if default is locked.
- Hidden entries (recovery, memtest, firmware) behind “More…” so the main screen stays clean.
- Empty disk: calm state + Scan again + Repair tools + Firmware setup. Never a black panic screen.

### Repair (product, not a live USB)
- Badge on a card if last boot failed.
- Actions: Try again | Repair | Skip this OS.
- Wizard: Diagnose → Suggested fix → Apply / Revert. Max ~3 steps.
- Always show what will be written (ESP files, BootOrder, BCD pointers, limine.conf). Confirm.
- **Undo last repair** stored on ESP.

### In-boot settings
- Gear: timeout, default/last-used, theme (validated packs only), language, extra scan paths, mouse on/off, show hidden.
- Persist on ESP so Linux/Windows tools use the **same** files.
- Theme cannot hide Firmware setup or Repair.
- Hardware-key **safe mode**: built-in high-contrast theme if user theme fails.

### Desktop tools
- List/reorder entries, icons, default, timeout, theme pack, install/update EFI, NVRAM entry.
- Windows: admin, never silent-write ESP.
- Linux: Mint-friendly GUI; CLI underneath for headless tests.

---

## UI

- Icons: PNG per entry; fallback glyphs (Windows, Tux, gear, firmware).
- Themes: folder on ESP; ship 2–3 built-ins (dark elegant, mint-ish, high-contrast).
- Type: one readable sans, 1080p and 4K scale.
- Motion: short fade only. No heavy 3D.
- Accessibility: high-contrast theme; timeout floor unless user opts in; firmware always reachable.
- UTF-8 labels.

---

## Features

### Must (v1)
- UEFI x86_64.
- Scan ESP + common paths: Windows Boot Manager, systemd-boot, GRUB, Limine, Linux EFI stubs.
- Graphical cards + custom icons (within constraints).
- Last-used + saved default + timeout 0 / N / infinite.
- Settings from boot UI (minimum: OS tools if Limine cannot edit in-menu — call that out, do not stall forever).
- Linux app + Windows app sharing schema.
- Repair lite:
  - Fix/create EFI boot entry (efibootmgr-equivalent from OS tools).
  - Conservative Windows: restore known-good `bootmgfw.efi` copies you backed up; dry-run before `bcdboot`-style actions.
  - Restore JanusBoot/Limine/GRUB EFI files if present on ESP.
  - Reorder NVRAM BootOrder.
  - Reinstall EFI binary + config from ESP backup.
- Super GRUB-like: generate a one-shot Limine entry from picked vmlinuz+initrd (userspace in v1).
- Backup `settings.json` and NVRAM dump before changes.

### Nice (later)
- Mouse, theme zip “shop,” HiDPI native res, btrfs/Timeshift cards, settings PIN, ARM64, icon atlas, reduce-motion / fast-boot (no background).

---

## User themes and icons (size and speed)

EFI is slow. **Desktop compiles; EFI only loads capped assets.**

### Theme pack
Folder, not loose junk:
- `theme.json` — name, author, version, schema version, dark/light, layout (row vs list), colors (text, muted, accent, danger, focus), padding, radius, timeout bar.
- Background: still image or solid/gradient. **No video. No scripts.**
- Optional chrome: selection frame, card background, gear/repair glyphs.
- **Fonts in v1:** bundled UI font only, or one TTF ≤ 200 KB if you add it later. Do not ship huge font families to ESP in v1.

### Icons
- Square **64 / 128 / 256 px** only. Reject huge web logos.
- PNG (transparency OK). JPEG for photos/backgrounds.
- Fallback if missing or rejected.

### Hard limits (enforce in schema + `janusbootctl theme apply`)
- Theme uncompressed on ESP: warn ~4 MB, max ~8–12 MB.
- Background: max source 3840×2160; **store** ~1920×1080 (or 2560×1440) JPEG/PNG, file ~1.5–2 MB cap.
- Icon file ~64–128 KB each.
- Max ~24 custom icons; max ~8 extra chrome images per theme.
- Formats: PNG and baseline JPEG. No WebP/AVIF/SVG **at runtime**. SVG may be **rasterized at apply** on Linux/Windows.
- No animation in v1 (or a tiny capped strip later).
- Max file counts and no path escape (`../`).
- Quota: leave ESP room for Microsoft boot files and Limine.
- Strip EXIF where practical.

### Apply pipeline (`janusbootctl theme apply`)
1. Validate schema, dimensions, sizes, paths.
2. Resize/compress → `background.boot.jpg`, `icon.128.png`, etc.
3. Manifest with hashes and byte sizes.
4. Atomic swap: write `themes/.next/`, then rename; keep previous / last-good.
5. Optional icon **atlas** at apply-time (one read).
6. EFI never resizes images. Hash mismatch → fallback theme + badge.

### UX for creators
- Starter kit: duplicate a built-in theme.
- **Desktop preview** at 1080p/4K **before** writing ESP (mandatory).
- Import folder/zip. Drag-drop icons onto OS rows; crop-to-square in GUI.
- Checklist errors in plain language (“background 8 MB → resized to 1920×1080”).
- Safe mode key + last-good theme if decode fails.
- Boot-time picker lists **validated** packs only.

### Guardrails
- Theme cannot hide Firmware or Repair.
- No writes outside `EFI/JanusBoot/` except documented Limine/ESP install paths.
- Optional PIN to change theme from boot UI (later).

---

## Settings schema (conceptual)

`settings.json` fields (refine in `schema/settings.schema.json`):
- `timeout`, `timeout_style` (menu / hidden)
- `default` (`saved` | entry id)
- `save_default`
- `theme`
- `scan_paths[]`
- `hidden[]`
- `icons{}` (entry id → icon id)
- `last_boot`, `last_boot_ok`
- `repair_history[]`
- feature flags: `repair`, `mouse`, `secureboot`

Linux, Windows, and boot UI CRUD the same files. If they diverge, fail CI.

---

## Phased execution (one PR per phase)

### Phase 0 — Repo
- Layout: `docs/VISION.md` (short vision), `schema/settings.schema.json`, `esp/layout.md`, `.cursorrules`.
- License. No BURG code.
- Limine as submodule or “install Limine, we generate conf.”
- Target: QEMU + OVMF.

### Phase 1 — Config contract
- `janusbootctl`: `get`, `set`, `validate`, `backup`.
- Unit tests. No GUI.

### Phase 2 — Limine
- JSON → `limine.conf` (timeout, default, wallpaper path).
- Makefile: QEMU image, two fake entries.
- `docs/qemu.md` checklist.

### Phase 3 — Scanner
- Linux ESP + Windows `bootmgfw.efi`.
- Write `entries.json` (id, title, path, icon, type).
- Never delete foreign EFI files.

### Phase 4 — Boot-time settings (minimum)
- If Limine cannot edit in-menu: settings from OS tools + regenerate conf. Document in VISION. Do not block the rest.

### Phase 5 — Linux GUI
- Entries, icons, default, timeout, theme picker, install to ESP, NVRAM.
- Only via `janusbootctl`.

### Phase 6 — Windows GUI
- Same; elevation; warnings.

### Phase 7 — Repair v1 (userspace)
- Missing EFI / wrong BootOrder; restore from ESP backup; `efibootmgr`.
- Windows: restore backed-up `bootmgfw.efi`; dry-run flag for BCD tools.
- File-boot: pick kernel+initrd → one-shot Limine entry.

### Phase 8 — Polish
- 2–3 themes, icon set, last-boot-failed, undo, Secure Boot docs.
- Theme apply pipeline + preview + fallback theme.

---

## `.cursorrules` (put in repo)

- QEMU+OVMF for every boot change; never tell the user to `dd` blindly.
- Repair only touches ESP files we own + explicit backups + documented NVRAM/BCD with confirm/dry-run.
- Generate Limine config; do not fork bootloaders in v1.
- Linux and Windows share schema; divergence fails CI.
- Features behind flags: `repair`, `mouse`, `secureboot`.
- One PR per phase.
- User themes are data: compile with `janusbootctl theme apply`; EFI does not run code or resize huge images.
- Product name is **JanusBoot**; CLI **janusbootctl**; ESP **EFI/JanusBoot/**.

---

## First Cursor prompt

Create the repo layout, `settings.schema.json`, `janusbootctl validate/get/set` with tests, ESP directory layout docs, theme schema stubs (limits for background/icons), and a Makefile that builds a Limine UEFI image in QEMU with two fake entries and timeout/default from JSON. Brand as JanusBoot. Do not vendor BURG. Do not implement Windows GUI or real disk repair yet.

---

## Reference links (ideas only)

- https://github.com/kphillisjr/burg
- https://github.com/eyed3v/burg-x86_64-efi
- https://github.com/Limine-Bootloader/Limine
- https://github.com/supergrub/supergrub
- https://sourceforge.net/projects/refind/
- https://launchpad.net/~danielrichter2007/+archive/ubuntu/grub-customizer
- https://github.com/Thenujan-0/grub-editor
