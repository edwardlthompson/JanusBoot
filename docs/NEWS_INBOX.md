# News Inbox

Auto-collected inbox of news, upstream updates, security fixes, and ideas relevant to this repo, appended daily by News Bot.
A Cursor planning agent should review these items and fold the useful ones into BUILD_PLAN; entries are append-only, newest at the bottom.


## 2026-11-13

**News and updates**

- Pillow heap overflow when saving TIFF via libtiff (CVE-2026-128067, high); affects <= 12.3.0, fixed in 13.0.0. [source](https://github.com/advisories/GHSA-xcvg-w56q-r89m)

**Tasks for the planning agent**

- [ ] Bump pillow floor to >=13.0.0 in janusbootctl — pyproject allows pillow>=10.0.0, which includes the vulnerable versions. Label: `[AGENT][LOCAL]` · Priority: P1 · https://github.com/advisories/GHSA-xcvg-w56q-r89m

## 2026-11-14

**News and updates**

- Libreboot 26.11 goes UEFI-only (MrChromebox EDK2 payload on almost all boards; GRUB/legacy payloads dropped). [source](https://libreboot.org/news/libreboot2611.html)

**Tasks for the planning agent**

- [ ] Add Libreboot/MrChromebox EDK2 UEFI firmware to compatibility notes and smoke tests — Libreboot users are now all on UEFI, a new target for JanusBoot. Label: `[AGENT][LOCAL]` · Priority: P3 · https://libreboot.org/news/libreboot2611.html
