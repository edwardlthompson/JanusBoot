# JanusBoot rescue ISO layout

Purpose: **run / repair / reinstall JanusBoot** and help with common OS boot
failures — not a general-purpose ISO flasher.

## Contents (v1 contract)

| Path on ISO | Role |
|-------------|------|
| `EFI/BOOT/BOOTX64.EFI` | Limine (or JanusBoot-wrapped) UEFI loader |
| `EFI/JanusBoot/` | settings/entries/themes stubs for live session |
| `janusboot/rescue/` | repair docs + `janusbootctl` wheel/sdist for the live OS |
| `SHA256SUMS` | Manifest of every shipped payload file |
| `README.txt` | What is in vs out of v1 (HUMAN confirms scope) |

## Checksum manifest

`SHA256SUMS` lists `sha256  path` lines. `janusbootctl usb preview|write` requires
the chosen ISO file’s digest (computed or provided) before any plan is shown.
Never write an arbitrary disk image without a checksum step.

## Common OS boot help (in vs out)

**In (v1 intent):** chainload Windows Boot Manager / shim+GRUB / systemd-boot /
Limine when found on the host ESP; restore JanusBoot ESP files from backup;
regenerate `limine.conf`; calm empty-disk entries.

**Out (until HUMAN expands):** BitLocker/LUKS unlock, hostile BCD rewrite,
arbitrary third-party ISOs, network fetch of images from EFI.

HUMAN row confirms the final in/out list before tagging ISO-complete.

## Build note

Cloud owns layout docs + checksum contract. LOCAL builds the FAT/ISO artifact
and runs `make usb-smoke` (classifier + dry-run). Physical stick write is HUMAN.
