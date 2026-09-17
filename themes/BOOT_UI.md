# Boot UI cards path (Limine honest floor)

JanusBoot aims for BURG-like **OS cards** (large icon + title + subtitle). Engine is
**Limine** — we generate `limine.conf` + ESP assets; we do not fork Limine or vendor BURG.

## What Limine gives us (v1 floor)

| UX goal | Limine + JanusBoot path |
|---------|-------------------------|
| Full-screen look | `wallpaper:` → compiled `EFI/JanusBoot/themes/<id>/background.boot.jpg` |
| Timeout bar | Limine countdown; `timeout:` from `settings.json`; quiet bar is Limine chrome |
| Last-used highlight | `default_entry:` from `last_boot` / `default`; regenerate after each boot record |
| Large icons | ESP `icons/*.png` + theme pack icons; Limine list UI shows titles (not true card grid) |
| More… | Hidden entries emitted under `/More…` submenu (`hidden: true` in entries.json) |
| Empty disk | Calm synthetic entries: Scan again (tool), Repair tools, Firmware setup |
| Mouse | Feature flag `mouse` only; not required for v1 |

## Honest gap vs BURG cards

Limine’s graphical menu is still a **branded list / wallpaper shell**, not a free-form
card compositor. JanusBoot therefore:

1. Ships theme packs + icons sized for card-like chrome when/if Limine gains richer layout.
2. Documents this floor in QEMU (`docs/qemu.md`) and VISION Phase 4.
3. Puts full card editing (reorder, icons, timeout, theme) in **Linux/Windows GUIs** via
   `janusbootctl` so Must (v1) is not blocked on in-boot WYSIWYG cards.

## Generated conf markers

`janusbootctl generate-limine` writes:

- `# janusboot:last-used=<id>` comment for operators
- `/More…` directory for hidden recovery/memtest/firmware rows
- Empty-disk calm titles when `entries` is empty after scan
