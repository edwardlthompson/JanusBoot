# NVRAM / repair on VM ESP (LOCAL Phase 7)

Generated QEMU images live under `build/` (gitignored). Dry-run first:

```bash
make repair-plan
# uv run janusbootctl --esp fixtures/esp repair-plan --kind nvram
```

On a real or VM ESP (human confirm only):

```bash
# Example — adjust disk/part; never run blindly:
# efibootmgr -c -d /dev/diskX -p N -l '\\EFI\\JanusBoot\\BOOTX64.EFI' -L JanusBoot
```

Restore JanusBoot JSON from `EFI/JanusBoot/backup/latest/` only after
`repair-plan --kind janus` shows `restore_file` and the user confirms.
