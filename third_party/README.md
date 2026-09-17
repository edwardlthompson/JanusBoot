# third_party (LOCAL lane)

Host-downloaded artifacts only. Do not commit Limine binaries or disk images.

```bash
make deps    # pins Limine BOOTX64.EFI into third_party/limine/
```

Guest cloud images for `.deb` / GUI smoke land under **`build/vm/`** (gitignored via `build/`), not here — see [`docs/vm-guest-smoke.md`](../docs/vm-guest-smoke.md).

See `docs/qemu.md`.

Windows elevation / BCD dry-run: [`WINDOWS_ELEVATION.md`](WINDOWS_ELEVATION.md).
