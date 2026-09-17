# JanusBoot QEMU + ESP smoke (LOCAL lane)

Host checklist for Phase 0–2. **QEMU only** — never write the ESP image to a real disk with `dd`, `cp`, or similar. `build/esp.img` is a throwaway FAT image for the emulator. After QEMU is green, the safe real-machine next step is a **read-only** host dry-run: [`docs/host-dry-run.md`](host-dry-run.md) (`make host-dry-run`).

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

## Limine in-menu limits (Phase 4 LOCAL)

Confirmed against Limine **v12.9.0** in QEMU (this host):

| Capability | In Limine menu | JanusBoot path |
|------------|----------------|----------------|
| Timeout | Via `TIMEOUT` in `limine.conf` | `janusbootctl set timeout` → `generate-limine` |
| Default entry | Via `DEFAULT_ENTRY` / order | `janusbootctl set default` |
| Theme / wallpaper | Wallpaper path in conf | `theme-apply` + regenerate |
| Live edit of settings JSON | **Not** available in-menu | OS tools only (VISION Phase 4) |
| Mouse | Limine may ignore | Feature flag `mouse` (off by default) |
Do not block desktop GUIs waiting for full in-boot settings. OS tools + regenerate is supported.

## Visual check + Secure Boot (Phase 8 LOCAL)

Interactive visual check:

```bash
make qemu

```

Expect two cards (Windows 11 + Linux Mint) from fixtures, timeout bar, high-contrast-capable theme path.

## Must-gap LOCAL smokes

```bash
make qemu-boot-ui-smoke   # wallpaper + icons on FAT image + qemu-smoke
make scan-live-deep       # recursive EFI walk (SCAN_ROOT=fixtures/esp by default)
make repair-apply-smoke   # dry-run repair-apply (no NVRAM write)
make nvram-backup         # efibootmgr dump → Cloud backup API under build/
make install-esp-smoke    # install EFI+conf onto build/esp-root (not a real disk)

```

Repair NVRAM apply outside QEMU remains `[HUMAN]` — see `docs/nvram-repair-local.md`.

Secure Boot: document only unless keys exist. OVMF ships `OVMF_CODE_4M.secboot.fd`; JanusBoot does **not** fake signed boot in v1. If shim/keys are present on the host, note the path in a local scratch file — do not commit secrets. Feature flag: `secureboot`.

## Guest Linux .deb + GUI smoke (LOCAL)

Install and open the Linux GUI **only inside a QEMU guest** — never `dpkg -i` on the host during smoke.

```bash
make deb          # → dist/janusbootctl_*.deb (host artifact)
make vm-smoke     # guest apt install + xvfb janusboot-gui --smoke + qemu-smoke
make vm-gui       # interactive guest; leave QEMU running for SSH GUI
```

Full write-up: [`docs/vm-guest-smoke.md`](vm-guest-smoke.md).

## Bootable USB (LOCAL) — removable only

```bash
make usb-smoke          # classifier unit tests + dry-run planner (default)

```

**Never** document `dd` of a JanusBoot image onto an internal HDD/SSD/NVMe. The
planner refuses non-removable / system-looking devices. GUI and CLI default to
**Preview / dry-run**.

### Post-write verify (disposable stick only)

After `[HUMAN]` approves a real write on a **removable** stick:

1. Confirm path, size, model/vendor in the plan JSON (`janusbootctl usb write --confirm …`).
2. Write via an allowlisted tool only (`dd`/`cp`/`pv`/`usbimager`).
3. Verify: re-hash the ISO; compare the first 1 MiB and last 1 MiB on the device
   to the ISO (or tool-native verify). Fail closed if mismatch.
4. If no disposable stick is present, leave the HUMAN backlog item open — do not
   substitute an internal disk.

Elevation: Linux polkit/sudo for the write helper only; Windows UAC for raw disk
access. Listing removable media stays userspace.

### Smoke result (HUMAN #37) — 2026-09-17

- **Device:** `/dev/sdd` (user said `/dev/SDD1` → partition; wrote **whole disk** only)
- **Classify:** `enumerate_linux_devices` → allowed; `ok: removable media`; model=Cruzer vendor=SanDisk size=2000682496; `nvme0n1` refused
- **Dry-run:** `janusbootctl usb preview` + `usb write` (no `--confirm`) → `dry_run: true`
- **Confirm plan:** `janusbootctl usb write --confirm --device /dev/sdd …` → `dry_run: false`
- **Write:** `pkexec dd if=build/usb-rescue-stub.iso of=/dev/sdd` (allowlisted `dd`); unmounted `/dev/sdd1` first
- **Verify:** device head sha256 matched ISO (`adb66558333d125dc44052c09cf06c47ccdc4c903b2153387dadeaa542423af1`); ISO < 1 MiB so last-MiB N/A
- **Result:** PASS — BUILD_PLAN #37 ✅; removed from HUMAN_BACKLOG
