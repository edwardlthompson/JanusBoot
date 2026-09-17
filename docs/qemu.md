# JanusBoot QEMU + ESP smoke (LOCAL lane)

Host checklist for Phase 0–2. **QEMU only** — never write the ESP image to a real disk with `dd`, `cp`, or similar. `build/esp.img` is a throwaway FAT image for the emulator.

## Verified host (this machine)

| Item | Status (2026-09-16) | Notes |
|------|---------------------|--------|
| Distro | Linux Mint 22.3 (Ubuntu noble base) | `ID=linuxmint` |
| `qemu-system-x86_64` | Install via script / apt | `scripts/janusboot-host-deps.sh --apply` |
| OVMF | Same package set | `ovmf` → `OVMF_*_4M.fd` |
| `mkfs.fat` (dosfstools) | Present (`/usr/sbin/mkfs.fat`) | OK |
| `mcopy` / `mmd` (mtools) | Present | OK |
| `uv` | Present | Needed for `make validate` / `make test` / `generate-limine` |
| `fixtures/esp` + `janusbootctl` | On `local/phase-0-2` after cloud merge | OK |

After packages are installed on Mint/Ubuntu noble, firmware paths are:

| Variable | Path |
|----------|------|
| `OVMF_CODE` | `/usr/share/OVMF/OVMF_CODE_4M.fd` |
| `OVMF_VARS` | `/usr/share/OVMF/OVMF_VARS_4M.fd` |

Also shipped by the same package (do not use for Secure Boot smoke unless intentional):

- `/usr/share/OVMF/OVMF_CODE_4M.secboot.fd`
- `/usr/share/qemu/OVMF.fd` (combined image; Makefile prefers split 4M CODE/VARS)

Override if needed:

```bash
make qemu OVMF_CODE=/path/to/OVMF_CODE.fd OVMF_VARS=/path/to/OVMF_VARS.fd
```

## Install (Mint / Ubuntu)

Preferred (dry-run first, then apply **in a real terminal** so sudo can prompt):

```bash
scripts/janusboot-host-deps.sh
scripts/janusboot-host-deps.sh --apply
```

`--apply` privilege order:

1. `sudo -n` if credentials are cached / passwordless
2. Interactive `sudo` on a TTY (password prompt — **not** sudo-only `-n`)
3. `pkexec` GUI polkit dialog when `DISPLAY`/`WAYLAND_DISPLAY` is set

Cursor agent shells often have **no TTY**. Open **Terminal → New Terminal** (or any gnome-terminal) and re-run `--apply` / `make smoke-all` there. If neither TTY nor pkexec works, the script prints the exact `apt` commands.

Manual:

```bash
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt install -y qemu-system-x86 ovmf dosfstools mtools curl
```

### Other distros (hints)

| Distro | Packages | Typical OVMF paths |
|--------|----------|--------------------|
| Fedora | `qemu-system-x86 edk2-ovmf dosfstools mtools` | `/usr/share/edk2/ovmf/OVMF_CODE.fd` |
| Arch | `qemu-system-x86 edk2-ovmf dosfstools mtools` | `/usr/share/edk2-ovmf/x64/OVMF_CODE.fd` |
| openSUSE | `qemu-x86 ovmf dosfstools mtools` | under `/usr/share/qemu/` |

Run `make deps` after install; it prints FOUND/MISSING for each tool.

## Makefile targets

| Target | What it does |
|--------|----------------|
| `make deps` | Host probe + download pinned Limine **v12.9.0** → `third_party/limine/BOOTX64.EFI` |
| `make validate` | `uv run janusbootctl --esp fixtures/esp validate` |
| `make test` | `uv run pytest` in `examples/python` |
| `make esp-image` | FAT image `build/esp.img` via `mkfs.fat` + `mcopy` |
| `make qemu` | **Interactive** GTK window + serial on stdio |
| `make qemu-smoke` | **Headless** `-display none`, timeout (default 30s), serial → `build/qemu-smoke.log` |
| `make smoke-all` | Deps check → prompt install → validate → test → esp-image → qemu-smoke; log → `build/smoke.log` |
| `make clean` | Remove `build/` and `third_party/limine/` |

Scripted full chain (deps install attempt + validate + test + esp-image + qemu-smoke):

```bash
make smoke-all
# or
scripts/janusboot-smoke-all.sh
# thinner (no build/smoke.log tee):
scripts/janusboot-qemu-smoke.sh
```

Limine pin URL:

`https://github.com/Limine-Bootloader/Limine/releases/download/v12.9.0/limine-binary.tar.xz`

Bump `LIMINE_VERSION` in the root `Makefile` when upgrading; keep this doc in sync.

`janusbootctl` expects global `--esp` pointing at the ESP root that contains `EFI/JanusBoot/`, and `generate-limine -o PATH`.

## Interactive vs smoke

| Mode | Command | Display | When to use |
|------|---------|---------|-------------|
| Interactive | `make qemu` | GTK window | Human visual check of two fake entries / timeout |
| Smoke / CI / agent | `make qemu-smoke` or `scripts/janusboot-qemu-smoke.sh` | none | No GUI session; pass if QEMU runs until timeout or serial shows boot markers |

Override smoke duration:

```bash
make qemu-smoke QEMU_SMOKE_TIMEOUT=40
scripts/janusboot-qemu-smoke.sh --timeout 40
```

## ESP image layout (expected)

Populated by `make esp-image`:

```text
build/esp.img  (FAT32, label JANUSBOOT)
  EFI/BOOT/BOOTX64.EFI          ← Limine UEFI (from third_party/limine/)
  limine.conf                   ← from janusbootctl generate-limine
  EFI/JanusBoot/settings.json
  EFI/JanusBoot/entries.json
  …themes / other fixture files…
```

## Safety

- **Never** `dd if=build/esp.img of=/dev/sdX` (or any real block device).
- **Never** mount and rewrite a live ESP from these targets in Phase 0–2.
- QEMU uses a **copy** of `OVMF_VARS` under `build/OVMF_VARS.fd` so system firmware files stay read-only.
- No BURG trees; Limine is downloaded, not vendored as a fork.

## Quick sequence

```bash
# In an integrated terminal (sudo password prompt / pkexec):
make smoke-all
# or step-by-step:
scripts/janusboot-host-deps.sh --apply
make deps
make validate
make test
make esp-image
make qemu-smoke    # agent / headless
# make qemu        # interactive GUI when you want to watch the menu
```

Expect two fake boot entries driven by JSON (timeout/default from `settings.json`). For interactive runs, close the QEMU window or Ctrl-C when done.
