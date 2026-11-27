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

## 2026-11-25

**News and updates**

- Limine 12.11.0 (Nov 21) adds Vim-style menu keys (H/J/K/L), a `qwertz` keyboard layout, and restores 16-color approximations on serial and text mode (24-bit colors had been lost since 12.0.0); 12.11.1 the same day fixes an AArch64 UEFI link failure on toolchains such as Alpine's. JanusBoot is still pinned at 12.9.0, and the open 12.10.0 board row was never applied. [12.11.0 ChangeLog](https://github.com/Limine-Bootloader/Limine/blob/v12.11.1/ChangeLog) · [12.11.1](https://github.com/Limine-Bootloader/Limine/releases/tag/v12.11.1)

**Tasks for the planning agent**

- - [ ] Bump Limine to v12.11.1 and re-run the QEMU/OVMF smoke (retarget the open 12.10.0 board row; Makefile is still 12.9.0) — 12.11 adds menu keybindings and color fixes that can change how JanusBoot themes render, and 12.11.1 is the one to land on. Label: `[AGENT][LOCAL]` · Priority: P2 · https://github.com/Limine-Bootloader/Limine/releases/tag/v12.11.1 (retargeted existing BUILD_PLAN row)

## 2026-11-27

**News and updates**

- systemd [v263-rc1](https://github.com/systemd/systemd/releases/tag/v263-rc1) (Nov 27) leans harder on PE add-ons: Type #1 boot entries can share one UKI and pass different `.addon.efi` files via new "extra" lines (`bootctl link --extra=`), and UKI profiles gain CONDITION_TPM/SECUREBOOT/NETBOOT plus TOFU trust for unsigned add-ons. Add-ons are not bootable on their own, but janusbootctl's `discover_recursive()` (examples/python/src/janusbootctl/scan.py) does an unfiltered `rglob("*.efi")`, so `*.addon.efi`, `*.extra.d/` contents, `EFI/*/drivers/*.efi` and the shim helpers `mmx64.efi` / `fbx64.efi` (present on most Ubuntu/Fedora ESPs today) each become a chainload entry. rEFInd-style scanners skip these by default ([rEFInd scan options](https://www.rodsbooks.com/refind/configfile.html)). This is a scan-quality bug today; v263 is still an RC.

**Tasks for the planning agent**

- [x] Filter non-bootable PE files out of the recursive ESP scan (*.addon.efi, *.extra.d/, EFI/*/drivers/, shim mm*/fb* helpers) and label EFI/Linux/*.efi as UKIs, with a fixture ESP test — Today the deep scan turns MokManager, the shim fallback and any UKI add-on into bogus boot entries that fail or confuse when picked. Label: `[AGENT][LOCAL]` · Priority: P2 · https://github.com/systemd/systemd/releases/tag/v263-rc1 (synced to BUILD_PLAN)
- [ ] Note systemd v263 sd-boot behaviour (Type #1 extra add-on lines, UKI profile CONDITION_*) in the scan design notes — v263 lets several entries share one UKI, so a later BLS loader/entries parser should show one entry per Type #1 file, not per *.efi. Label: `[AGENT][LOCAL]` · Priority: P3 · https://github.com/systemd/systemd/releases/tag/v263-rc1
