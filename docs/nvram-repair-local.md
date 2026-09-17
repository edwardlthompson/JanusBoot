# NVRAM / repair on VM ESP (LOCAL Must gaps)

Cloud API: `janusbootctl backup --with-nvram` writes `EFI/JanusBoot/backup/nvram-<stamp>/`
(`meta.json` + `dump.txt`). LOCAL fills `dump.txt` from the host tool.

## Dry-run first (fixtures / build tree)

```bash
make repair-plan
make repair-apply-smoke    # repair-apply --dry-run on fixtures
make nvram-backup          # efibootmgr -v → build/nvram-esp backup (never real ESP)
```

## Lab VM only (HUMAN confirm)

On a disposable QEMU/VM ESP — **never** production laptops without explicit approval:

```bash
# 1) Dump + backup
make nvram-backup
# or: efibootmgr -v | tee /tmp/nvram.txt
#     uv run janusbootctl --esp /path/to/esp backup --with-nvram --nvram-text "$(cat /tmp/nvram.txt)"

# 2) Show plan
uv run janusbootctl --esp /path/to/esp repair-plan --kind nvram

# 3) Apply NVRAM only after confirm (example — adjust disk/part):
# efibootmgr -c -d /dev/diskX -p N -l '\\EFI\\JanusBoot\\BOOTX64.EFI' -L JanusBoot
```

Restore JanusBoot JSON from `EFI/JanusBoot/backup/<stamp>/` only after
`repair-plan --kind janus` shows `restore_file` and the user confirms.
`repair-undo --confirm` uses `settings.repair_history[].undo_backup`.
