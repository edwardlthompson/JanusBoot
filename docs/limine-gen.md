# Limine generation (cloud stub)

`janusbootctl generate-limine` maps `settings.json` + `entries.json` →
`limine.conf`. LOCAL owns the real `Makefile`; this doc lists expected targets
so lanes stay aligned.

## Mapping

| JSON | Limine |
|------|--------|
| `settings.timeout` | `timeout:` (seconds; use `no` only if we add infinite later) |
| `settings.default` (entry id) | `default_entry:` 1-based index among visible entries |
| `settings.wallpaper` | `wallpaper:` path (prefer `boot():/…` ESP-relative) |
| entry `title` | `/Title` menu heading |
| entry `type` `efi_chainload` | `protocol: efi_chainload` |
| entry `path` | `path:` (already Limine-style, e.g. `boot():/EFI/…`) |

## Expected Makefile targets (LOCAL)

| Target | Intent |
|--------|--------|
| `validate` | `uv run janusbootctl validate` against fixtures or ESP mount |
| `test` | `uv run pytest` in `examples/python` |
| `generate-limine` | Write `limine.conf` into the ESP image tree |
| `esp-image` | FAT image with Limine + JanusBoot JSON + generated conf |
| `qemu` | Boot the image with QEMU+OVMF; two fake entries visible |

Do not create the Makefile on the cloud lane.
