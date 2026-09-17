# JanusBoot QEMU + ESP smoke (LOCAL lane)

Host checklist for Phase 0–2. **QEMU only** — never write the ESP image to a real disk with `dd`, `cp`, or similar. `build/esp.img` is a throwaway FAT image for the emulator.

## Verified host (this machine)

| Item | Status (2026-09-16) | Notes |
|------|---------------------|--------|
| Distro | Linux Mint 22.3 (Ubuntu noble base) | `ID=linuxmint` |
| `qemu-system-x86_64` | **Missing** | Install: `sudo apt install qemu-system-x86` |
| OVMF | **Missing** | Install: `sudo apt install ovmf` |
| `mkfs.fat` (dosfstools) | Present (`/usr/sbin/mkfs.fat`) | OK |
| `mcopy` / `mmd` (mtools) | Present | OK |
| `uv` | Present | Needed for `make validate` / `make test` / `generate-limine` |
| `fixtures/esp` + `janusbootctl` | **Not on `local/phase-0-2` yet** | Waiting on cloud merge (`integrate-pr`) |

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

```bash
sudo apt update
sudo apt install qemu-system-x86 ovmf dosfstools mtools curl
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
| `make validate` | `uv run janusbootctl --esp fixtures/esp validate` (needs cloud merge) |
| `make test` | `uv run pytest` in `examples/python` (needs cloud CLI/tests) |
| `make esp-image` | FAT image `build/esp.img` via `mkfs.fat` + `mcopy` (needs cloud) |
| `make qemu` | Boot `build/esp.img` with QEMU+OVMF (needs cloud + qemu/ovmf) |
| `make clean` | Remove `build/` and `third_party/limine/` |

Limine pin URL:

`https://github.com/Limine-Bootloader/Limine/releases/download/v12.9.0/limine-binary.tar.xz`

Bump `LIMINE_VERSION` in the root `Makefile` when upgrading; keep this doc in sync.

`janusbootctl` (after merge) expects global `--esp` pointing at the ESP root that contains `EFI/JanusBoot/`, and `generate-limine -o PATH`.

## ESP image layout (expected)

Populated by `make esp-image` after cloud assets exist:

```text
build/esp.img  (FAT32, label JANUSBOOT)
  EFI/BOOT/BOOTX64.EFI          ← Limine UEFI (from third_party/limine/)
  limine.conf                   ← from janusbootctl generate-limine
  EFI/JanusBoot/settings.json
  EFI/JanusBoot/entries.json
  …themes / other fixture files…
```

## Blocked until cloud merge

`make esp-image` / `make qemu` / `make validate` **will fail** on this branch until Sequential merges `cloud/phase-0-2` into `local/phase-0-2` with:

1. `fixtures/esp/EFI/JanusBoot/{settings,entries}.json` (two fake entries + timeout/default)
2. `examples/python` `janusbootctl` (`validate`, `generate-limine`, …) + `uv.lock`

Do **not** check out `cloud/*` to copy those files in the LOCAL lane. Integration is `integrate-pr`.

**QEMU smoke status today:** `blocked-on-cloud-merge` (and host still needs `qemu-system-x86` + `ovmf`).

## Safety

- **Never** `dd if=build/esp.img of=/dev/sdX` (or any real block device).
- **Never** mount and rewrite a live ESP from these targets in Phase 0–2.
- QEMU uses a **copy** of `OVMF_VARS` under `build/OVMF_VARS.fd` so system firmware files stay read-only.
- No BURG trees; Limine is downloaded, not vendored as a fork.

## Quick sequence (after cloud merge + apt packages)

```bash
make deps
make validate
make test
make esp-image
make qemu
```

Expect two fake boot entries driven by JSON (timeout/default from `settings.json`). Close the QEMU window or Ctrl-C when done.
