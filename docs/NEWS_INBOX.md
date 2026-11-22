# News Inbox

Auto-collected inbox of news, upstream updates, security fixes, and ideas relevant to this repo, appended daily by News Bot.
A Cursor planning agent should review these items and fold the useful ones into BUILD_PLAN; entries are append-only, newest at the bottom.


## 2026-11-13

**News and updates**

- Pillow heap overflow when saving TIFF via libtiff (CVE-2026-128067, high); affects <= 12.3.0, fixed in 13.0.0. [source](https://github.com/advisories/GHSA-xcvg-w56q-r89m)

**Tasks for the planning agent**

- [x] Bump pillow floor to >=13.0.0 in janusbootctl — pyproject allows pillow>=10.0.0, which includes the vulnerable versions. Label: `[AGENT][LOCAL]` · Priority: P1 · https://github.com/advisories/GHSA-xcvg-w56q-r89m (synced to BUILD_PLAN)

## 2026-11-14

**News and updates**

- Libreboot 26.11 goes UEFI-only (MrChromebox EDK2 payload on almost all boards; GRUB/legacy payloads dropped). [source](https://libreboot.org/news/libreboot2611.html)

**Tasks for the planning agent**

- [ ] Add Libreboot/MrChromebox EDK2 UEFI firmware to compatibility notes and smoke tests — Libreboot users are now all on UEFI, a new target for JanusBoot. Label: `[AGENT][LOCAL]` · Priority: P3 · https://libreboot.org/news/libreboot2611.html

## 2026-11-15

**News and updates**

- Limine 12.10.0: UEFI disk reads now retry with smaller transfers on picky disks, firmware-reserved/non-WB memory is reported as reserved, the menu auto-rotates on known rotated panels (e.g. Steam Deck; `interface_rotation` still overrides), misreported GOP framebuffer geometry is corrected, and APIC ID, VT-d/AMD-Vi handoff and TSC calibration bugs are fixed. [source](https://github.com/Limine-Bootloader/Limine/releases/tag/v12.10.0) ([changelog](https://raw.githubusercontent.com/Limine-Bootloader/Limine/v12.10.0/ChangeLog))

**Tasks for the planning agent**

- [x] Bump Limine to v12.10.0 and re-run the QEMU/OVMF smoke — The new framebuffer-geometry and auto-rotation fixes can change how JanusBoot themes render, and the UEFI disk-read fix helps on picky hardware; verify the release signature when bumping. Label: `[AGENT][LOCAL]` · Priority: P2 · https://github.com/Limine-Bootloader/Limine/releases/tag/v12.10.0 (synced to BUILD_PLAN)
