# Guest VM smoke — .deb install + Linux GUI (LOCAL)

**Host system packages stay untouched.** Building under `dist/` and `build/` is OK.
All `apt` / `dpkg -i` / GUI runs happen **inside a QEMU guest**.

USB sticks (e.g. host `/dev/sdd`) are **out of scope** — this path never touches block devices other than qcow2 under `build/vm/`.

## Quick run

```bash
# 1) Artifact only on host (no dpkg -i):
make deb
# → dist/janusbootctl_0.1.0_all.deb

# 2) Guest install + GUI smoke (+ Limine ESP qemu-smoke):
make vm-smoke
# or:
scripts/janusboot-vm-smoke.sh
scripts/janusboot-vm-smoke.sh --skip-esp    # .deb/GUI only
scripts/janusboot-vm-smoke.sh --keep        # keep work disk for debug
```

Interactive guest (GTK display; SSH on `127.0.0.1:2222`):

```bash
make vm-gui
# Inside guest after cloud-init:
#   sudo apt-get install -y /path/to/janusbootctl_*.deb
#   janusboot-gui
# Headless proof without VNC:
#   xvfb-run -a janusboot-gui --smoke
```

## What is smoked

| Step | Where | Check |
|------|--------|--------|
| Build `.deb` | Host `dist/` | `dpkg-deb` (or ar/tar fallback) |
| Debian cloudimg | `build/vm/*.qcow2` (gitignored via `build/`) | Downloaded once |
| `apt-get install ./janusbootctl_*.deb` | **Guest only** | CLI `janusbootctl validate` |
| `xvfb-run janusboot-gui --smoke` | **Guest only** | Opens Tk, closes, prints `smoke ok` |
| `make qemu-smoke` | Host QEMU + `build/esp.img` | Limine/OVMF serial markers (optional `--skip-esp`) |
| Host `dpkg -l` | Host | Before/after identical; no `janusboot*` package |

## GUI `--smoke` / `--self-test`

Packaged launcher (LOCAL packaging — does not edit cloud `examples/python`):

```bash
janusboot-gui --smoke
janusboot-gui --self-test --smoke-ms 500
janusboot-gui --esp /usr/share/janusboot/fixtures/esp   # interactive
```

`--smoke` imports `janusbootctl`, opens a short-lived Tk window, exits 0.
Use with `xvfb-run -a` when the guest has no physical display.

## Host requirements (already used for ESP smoke)

| Tool | Role |
|------|------|
| `qemu-system-x86_64`, `qemu-img` | Guest + ESP smoke |
| OVMF | UEFI firmware |
| `dpkg-deb` (usual) or `ar`+`tar` | Build `.deb` |
| `genisoimage` / `mkisofs` | cloud-init NoCloud seed |
| `curl`, `ssh`, `scp`, `ssh-keygen` | Image fetch + guest control |

If QEMU/OVMF are missing: see [`docs/qemu.md`](qemu.md) — **document only** from agents; do not `apt install` on the host as part of this smoke.

## Safety

- Never `dpkg -i dist/janusbootctl_*.deb` on the host during smoke.
- Never `dd` ESP/qcow2 images to real disks or USB.
- Ephemeral SSH key: `build/vm/id_ed25519` (gitignored).

## Proof host was not modified

After `make vm-smoke`, compare:

```bash
diff -u build/vm/host-dpkg-before.txt build/vm/host-dpkg-after.txt
# expect: no differences
dpkg -l | grep -i janus || echo "no janusboot on host"
```
