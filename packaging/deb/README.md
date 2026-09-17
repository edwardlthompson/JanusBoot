# JanusBoot Debian packaging (LOCAL lane)

Builds a pure-Python `janusbootctl` `.deb` for **guest** install/smoke.
Do **not** `dpkg -i` this on the host during agent/CI runs.

```bash
scripts/janusboot-build-deb.sh          # → dist/janusbootctl_*_all.deb
scripts/janusboot-vm-smoke.sh           # QEMU guest: apt install + GUI --smoke
make deb                                # same as build script
make vm-smoke                           # full guest smoke (+ optional ESP)
make vm-gui                             # interactive guest (GTK + SSH)
```

Layout under `/usr/share/janusboot/` mirrors the repo so
`janusbootctl.paths.repo_root()` finds `schema/` without editing cloud Python.

See [`docs/vm-guest-smoke.md`](../../docs/vm-guest-smoke.md).
