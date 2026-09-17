# Windows host elevation + ESP/BCD dry-run (LOCAL Phase 6)

JanusBoot never silently writes the ESP or BCD from a desktop GUI.

## Elevation

- WinUI / installer must request **Administrator** before any ESP or NVRAM write.
- Show the exact paths and `janusbootctl` argv in a confirm dialog.
- Prefer `janusbootctl repair-plan --kind all` (dry-run JSON) before apply.

## BCD / bootmgfw

- Dry-run only on this machine unless a human confirms.
- Restore `bootmgfw.efi` only from `EFI/JanusBoot/backup/bootmgfw.efi` if present.
- Do not run `bcdboot` automatically in v1 without an explicit `--confirm` flag (future).

## Layout note

Vendor Windows tooling notes and future MSI stubs may live under `third_party/windows/`
(gitignored binaries). Keep this README tracked.

```text
third_party/windows/   # optional local caches (gitignored)
docs/spec.md           # WinUI mock structure (CLOUD)
```
