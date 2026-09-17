# Host dry-run (read-only ESP scan)

Safe next step after QEMU smokes: **read-only** scan and validate on a real machine. No ESP writes, no NVRAM, no install.

Full QEMU path: [`docs/qemu.md`](qemu.md). Next tier (real apply) stays `[HUMAN]` — see [`HUMAN_BACKLOG.md`](../HUMAN_BACKLOG.md).

## Prerequisites

1. **Backup** — know how you recover if firmware or boot order ever changes later (this dry-run does not change them).
2. **Firmware escape hatch** — know your vendor key for the UEFI boot menu (F12 / Esc / F10 / Del, etc.) so you can pick Windows/Linux or firmware setup without JanusBoot.
3. Prefer a **mounted ESP** you can read as your user (often `/boot/efi` or `/boot/EFI`). Do not unmount or remount as writable for this checklist.

## Step 1 — Read-only scan only

Fixtures (no real ESP):

```bash
make host-dry-run
# or
scripts/janusboot-host-dry-run.sh
```

Real mount (read-only scan; never passes `--write`):

```bash
export JANUSBOOT_ESP_ROOT=/boot/efi   # or your ESP mount
make host-dry-run
# or
JANUSBOOT_ESP_ROOT=/boot/efi scripts/janusboot-host-dry-run.sh
```

## Step 2 — Validate fixtures/settings without writing ESP

The same script runs `janusbootctl validate` against the chosen root (fixtures or `JANUSBOOT_ESP_ROOT`). It may also run `usb list` in **classify-only** mode (no write / no `--confirm`).

## Do not

- `janusbootctl scan --write` (or `janusboot-scan-esp.sh --write`)
- `repair-apply` without an explicit lab plan (and never with `--confirm` here)
- `install --confirm` onto a live ESP
- `efibootmgr` create/delete/BootOrder changes
- NVRAM / BCD mutating commands
- `usb write --confirm` unless the stick is **disposable** and a HUMAN backlog item covers it
- `dd` / raw block writes of `build/esp.img` or rescue images to internal disks

## When it’s OK to proceed to the next tier

Only after this dry-run is green **and** a HUMAN item is explicitly approved:

| Next tier | Where |
|-----------|--------|
| First real-ESP or NVRAM apply outside QEMU (lab only) | [`HUMAN_BACKLOG.md`](../HUMAN_BACKLOG.md) — “Approve first real-ESP or NVRAM apply…” |
| Disposable USB write smoke | HUMAN backlog / Bootable USB notes in [`docs/qemu.md`](qemu.md) |
| NVRAM repair on VM/lab | [`docs/nvram-repair-local.md`](nvram-repair-local.md) |

Until then: stay on QEMU + this host dry-run.
