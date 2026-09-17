# Feature: bootable-usb

> Rescue / reinstall media from the JanusBoot GUI. Steal UX and safety ideas from FOSS writers only — do not vendor proprietary code. Checklist markers: 🔲 open · ✅ done · ❌ blocked.

## Acceptance criteria

- ✅ User-visible behavior: From Linux/Windows GUI, user picks a **JanusBoot rescue ISO** (run / repair / reinstall JanusBoot + common OS boot help), sees **only removable** targets, confirms a clear device preview, then writes the image (or dry-runs)
- ✅ Named primary CTA (one per view): **Write to USB** (destructive); secondary **Preview / dry-run**; never a silent write
- ✅ Empty state: No removable media → explain why empty + “Insert a USB stick and refresh”
- ✅ Error / loading: Permission denied (elevation), target disappeared, write verify failed, non-removable refused — each with an in-place next action
- ✅ Offline/error behavior: ISO missing → link to download/build docs; never fall back to writing an arbitrary disk image without checksum
- ✅ Accessibility: Keyboard focus order through device list → preview → confirm; screen-reader names include device path, size, model; destructive confirm is a separate step
- ✅ i18n: keys under `bootableUsb.*` (Linux GUI + Windows GUI string tables)

## Hard safety rules (non-negotiable)

1. **Never overwrite internal / non-removable disks** (HDD/SSD/NVMe system disks).
2. Device picker shows **removable media only** (USB flash / SD where the OS marks removable).
3. **Confirm** before any destructive write: show device path, size, model/vendor, and ISO name+checksum.
4. **Dry-run / preview** mode always available; default path for CI and first-run demos.
5. **Refuse** write if classification says non-removable, looks like a system disk, or allowlist check fails.
6. Prefer **userspace** tools with explicit allowlists; document Linux (polkit/sudo) vs Windows (UAC) elevation separately.
7. No blind `dd` instructions in end-user docs; QEMU/image smoke for CI, real USB only on `[LOCAL]` with a disposable stick + `[HUMAN]` confirm.

## Elevation + tool allowlist

| Host | Elevation | Notes |
|------|-----------|-------|
| Linux | polkit (`pkexec`) or sudo **only** for the write helper | Listing removable disks is userspace (`/sys/block/*/removable`). Preview needs no root. |
| Windows | UAC elevation for raw disk write | GUI shows elevation warning; dry-run/list do not require admin. |
**Userspace allowlist** (`WRITE_TOOL_ALLOWLIST` in `usb_media.py`): `dd`, `cp`, `pv`, `usbimager`.
Anything else is refused. FOSS UX references (ideas only): USBImager, Etcher, Fedora Media Writer, Popsicle, Ventoy — do not vendor their code.

## Lane split

| Lane | Owns |
|------|------|
| `[CLOUD]` | Rescue ISO contents/layout docs, dry-run planner, device classification logic + unit tests, GUI picker UX (mock devices), checksum manifest |
| `[LOCAL]` | Real USB write smoke on **removable-only** hardware; Makefile/docs for host tools; never run destructive write in Cloud |
## Smoke scenario

1. _Given_ GUI (or `janusbootctl usb preview`) with a known rescue ISO and zero removable disks
2. _When_ user opens Bootable USB
3. _Then_ empty state with refresh CTA; dry-run against a mocked removable device prints a plan and does not write
4. _Given_ `[LOCAL]` disposable USB + `[HUMAN]` approval
5. _When_ write + verify runs
6. _Then_ only that removable device is touched; verify passes; internal disks untouched

## Container map

| Layer | Path |
|-------|------|
| Logic | `examples/python/src/janusbootctl/usb_media.py` (classify, plan, dry-run) |
| Host probe | `examples/python/src/janusbootctl/usb_host.py` (sysfs removable-only) |
| View | Linux/Windows GUI Bootable USB tab (`gui_tk.py`) — CLI only |
| Tests | `examples/python/tests/test_usb_media.py` |
| Wiring | `janusbootctl usb …` + GUI ≤10 lines each |
| Docs | this file · `docs/rescue-iso.md` · `docs/qemu.md` USB verify |
## Tests

- Automated: yes — classification / allowlist / dry-run planner unit tests (Cloud)
- Coverage: pure logic for “removable vs system” + one dry-run smoke path
- Hardware write: `[LOCAL]` smoke only; document why full write is not in default CI

## Fallback validation

- Why full USB write tests are not in default CI: requires physical removable media and elevation
- Command (Cloud): `uv run pytest examples/python/tests/test_usb_media.py`
- Command (Local): `make usb-smoke` (removable-only; fails closed; dry-run by default)

## Definition of Done

See `docs/FEATURE_MODULES.md` and BUILD_PLAN Sprint — Nice-later + Bootable USB rows. Sequential marks ✅ only after Cloud tests + Local smoke (or explicit ❌ with reason).

## FOSS references (ideas / UX / safety only — do not vendor)

| Project | License (approx.) | Steal |
|---------|-------------------|-------|
| [USBImager](https://codeberg.org/bzt/usbimager) | MIT | Minimal UI; refuse system disk; verify after write |
| [balenaEtcher](https://github.com/balena-io/etcher) | Apache-2.0 | Drive-safety UX; confirm before flash; post-write validation |
| [Fedora Media Writer](https://github.com/FedoraQt/MediaWriter) | GPL-2.0 | Download + write flow; restore USB afterward |
| [Popsicle](https://github.com/pop-os/popsicle) | MIT | Multi-device flash UX; clear progress |
| [Ventoy](https://github.com/ventoy/Ventoy) | GPL-3.0 | Multi-ISO USB *ideas* only — evaluate carefully before any approach copy |
| Ubuntu/`usb-creator`, Linux Mint USB tools | GPL | Distro “make bootable USB” IA |
Prefer MIT/Apache/GPL-compatible approaches documented as references. JanusBoot ships its own planner + allowlist; wrap or shell out to host tools only behind an allowlist.

## Notes

- Product name **JanusBoot**; CLI **janusbootctl**; ESP **EFI/JanusBoot/**
- ISO purpose: run / repair / reinstall JanusBoot and help with common OS boot issues — not a general ISO flasher for arbitrary images in v1
- After each AGENT step: `python3 scripts/agent-run.py watch-agent-gates --once --autofix --scope auto`
