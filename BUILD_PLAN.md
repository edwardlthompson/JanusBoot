# Build Plan

<!-- remaining-tally -->
**Remaining:** AGENT 34 · LOCAL 9 · CLOUD 25 · AUTO 0 · HUMAN 4 · ADB 0 · **38 open**
<!-- /remaining-tally -->

**Progress (not zero):** Sprint 0 ✅ archived · Phase 0–2 ✅ archived · Template upgrade 1.6.0→1.8.0 ✅ archived · Phase 3–8 stubs ✅ archived · **Must gaps + Nice-later + Bootable USB 🔲 open**. The “Remaining” line counts only 🔲/❌ — Phase stubs shipped CLI/schema/QEMU depth, not brief-complete Must (v1). Archive: [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md). Gap analysis tip: `f1a191d`.

Live board for **JanusBoot**. Lane contract: [`docs/JANUSBOOT_AGENT_LANES.md`](docs/JANUSBOOT_AGENT_LANES.md) · lock: [`.cursor/janusboot-lane-lock.json`](.cursor/janusboot-lane-lock.json).

**Who:** `AGENT` code · `HUMAN` person · `ADB` device · `AUTO` CI/scripts

**Venue (template):** `[LOCAL]` / `[CLOUD]` + optional `— scope:` — see [`docs/adr/0008-agent-venue.md`](docs/adr/0008-agent-venue.md). JanusBoot product rows also use the lane table below.

**Lane (required on JanusBoot product rows):**

| Label | Who | Meaning |
|-------|-----|---------|
| `[LOCAL]` | This Computer / local Agent | Host tools, QEMU+OVMF, workspace bind, real ESP later, or merges integration |
| `[CLOUD]` | Cursor Cloud Agent | Text/code/tests only on an isolated `cloud/*` branch; no host firmware, no real disks |

**State:** 🔲 open · ✅ done · ❌ blocked — reason

Format: `🔲 [AGENT][CLOUD] Short task — scope: path/` or `🔲 [AGENT][LOCAL] Short task — scope: path/`. Sequential first. Parallel scopes: [`docs/PARALLEL_AGENT_SCOPES.md`](docs/PARALLEL_AGENT_SCOPES.md). `/build` tries HUMAN/ADB after automation; failures go to `HUMAN_BACKLOG.md`.

## Smoke gate (hard stop)

After every `[AGENT]` row: `python3 scripts/agent-run.py watch-agent-gates --once --autofix --scope auto`

After the **last** `[AGENT]`/`[AUTO]` row in a sprint is ✅, do **not** start the next sprint until this exits 0:

```bash
python3 scripts/agent-run.py smoke-sprint --require

```

That command re-smokes **every** ✅ row: no errors or crashes, plus startup time and load order. Details: [`docs/SPRINT_SMOKE.md`](docs/SPRINT_SMOKE.md). Fail → leave the last row open or ❌; fix; re-run. `/gates` wrap-up includes the same check.

---

## Agent venues (standing queues)

### Local agent (This Computer)

Standing queue for This Computer. Product sprint rows below carry venue tags; keep markers empty unless a venue row is parked here.

<!-- local-agent-lane:begin -->
_No local agent items._
<!-- local-agent-lane:end -->

### Cloud agent (Cursor Cloud)

Standing queue for Cursor Cloud Agents. Product sprint rows below carry venue tags; keep markers empty unless a venue row is parked here.

<!-- cloud-agent-lane:begin -->
_No cloud agent items._
<!-- cloud-agent-lane:end -->

---

## Product

### Product (do not drift)

> Auto-managed from `AGENT.md` after init. Do not hand-edit inside markers. Read `AGENT.md` before any sprint row.

<!-- product-brief-sync:begin -->
> Read `AGENT.md` before any sprint row.

**One-liner:** A UEFI-first graphical boot manager that feels like BURG, scans like rEFInd, can repair a broken OS path like Super GRUB, and stores one settings/theme contract on the ESP that you can change from the boot menu, from Linux, and from Windows.
**Do not drift:** limine, uefi, janusbootctl, efi/janusboot, qemu, ovmf
<!-- product-brief-sync:end -->

### Completed so far (visible progress)

| Milestone | Status | Where to look |
|-----------|--------|---------------|
| **Sprint 0 — Customize** | ✅ Done (archived) | [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md) — *Sprint 0 — Customize (JanusBoot, 2026-09-17)* |
| **Phase 0–2 — Contracts + QEMU smoke** | ✅ Done (archived) | [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md) — *Sprint / Phase 0–2 — Contracts + QEMU smoke (2026-09-17)* |
| **Template upgrade 1.6.0 → 1.8.0** | ✅ Done (archived) | [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md) — *Template upgrade 1.6.0 → 1.8.0 (2026-09-17)* |
| **Phase 3–8 — Scanner through Polish** | ✅ Stub depth archived | [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md) — *Sprint / Phase 3–8 (2026-09-17)* — **not** brief-complete Must (v1) |
| **Must gaps (v1 depth)** | 🔲 Open | Sprint below |
| **Nice-later + Bootable USB** | 🔲 Open | Sprint below · [`docs/features/bootable-usb.md`](docs/features/bootable-usb.md) |

> **Sprint / Phase 0–2** archived in COMPLETED_TASKS.md @ `a337d62`.
> **Sprint — Template upgrade 1.6.0 → 1.8.0** archived in COMPLETED_TASKS.md @ `a337d62`.
> **Sprint / Phase 3–8** archived in COMPLETED_TASKS.md @ `837199b` (stubs).

Agents **do** flip 🔲 → ✅ on this file as work lands. Status uses emoji markers (✅/🔲), not GitHub `- [ ]` checkboxes. Live tip: `.cursor/worktrees/local-phase-0-2` on `local/phase-0-2` (keep root `BUILD_PLAN.md` in sync for the IDE).

Next open work: **Must gaps (v1 depth)** then **Nice-later + Bootable USB**. Do not mark gaps ✅ until acceptance checks pass. `v1.0.0` ≠ brief-complete Must (v1).

### Waiting on a person

_None blocking for Sprint 0 / Phase 0–2 process._ Optional IDE: pin `docs/help/BATCH_COMMANDS.md`; set Cursor mode in the UI. Optional GitHub: Actions bot approval + `AUTOMERGE_TOKEN` (notes from `setup-github-repo.sh`). Re-check: `scripts/janusboot-human-checklist.sh`. Sacred UPG-71…77 waived via `scripts/janusboot-protect-product.sh` (verify-only). Actions `default_workflow_permissions=write` set for Release Please.

Open for new sprints (see rows below): disposable USB for write smoke; Windows GUI elevation UX sign-off when that row is ready.

- ~~`[HUMAN]` Host password / apt install qemu+ovmf~~ → done (`qemu-system-x86` + `ovmf` installed; note: Cursor aptrepo GPG can break bare `apt update` — install packages directly or fix `NO_PUBKEY 42A1772E62E492D6`)
- ~~`[HUMAN]` Create JanusBoot product GitHub remote~~ → done (`edwardlthompson/JanusBoot`; origin retargeted; bootstrap remote kept)
- ~~`[HUMAN]` Approve `local/phase-0-2` → `main` after `qemu-smoke` PASS~~ → done (`make smoke-all` PASS; ff merge to `main`)
- ~~`[HUMAN]` Fill INITIALIZATION_PROMPT / pick mode / bookmark BATCH_COMMANDS~~ → done (fill script + checklist; IDE pin/mode remain optional)
- ~~`[HUMAN]` Sacred UPG-71…77~~ → waived—product retained (`janusboot-protect-product.sh`)
- ~~`[HUMAN]` Actions workflow permissions for Release Please~~ → done (`default_workflow_permissions=write`)

### Open PRs (synced)

> Auto-managed on product repos too. Do not hand-edit rows inside the markers.

<!-- open-prs-sync:begin -->
_No open Dependabot or Release Please PRs._
<!-- open-prs-sync:end -->

### Template gaps (synced)

> Auto-managed Monday cron + `sync-template-gaps-build-plan`. Do not hand-edit inside markers. Plan-only — run `/upgrade` then name item numbers.

<!-- template-gaps-sync:begin -->
Parent `1.6.0` → `1.8.0` (edwardlthompson/agent-project-bootstrap).

Named gaps **1–79** applied and archived — see COMPLETED_TASKS.md *Template upgrade 1.6.0 → 1.8.0 (2026-09-17)*. This sync block is a pointer only.
<!-- template-gaps-sync:end -->

### UX & UI inventory

Complete list from construction gaps and `/ux-review`. Status is only planned / in_progress / done. `/build` does not execute these until `/ux-apply UX-NNN` (or a Sequential row). Follow [`docs/ux-ui-guidelines.md`](docs/ux-ui-guidelines.md) when shipping UI.

<!-- ux-inventory:begin -->
_No UX inventory items._
<!-- ux-inventory:end -->

---

## Sprint — Must gaps (v1 depth)

Close the gap between Phase 3–8 **stubs** and AGENT.md **Must (v1)**. Severity in each row. Do **not** flip ✅ until Cloud tests (and Local smoke where tagged) pass. Scope trailer is a single path token (venue gate).

### Sequential

1. 🔲 [AGENT][LOCAL] Lock scopes for Must gaps: one PR stream per lane; Sequential owns board flips only after acceptance — scope: BUILD_PLAN.md

### Parallel — CLOUD

2. 🔲 [AGENT][CLOUD] **blocker** Boot UI cards path: Limine-facing assets + conf for large icons, timeout bar, last-used highlight, More…, empty-disk calm copy; document honest floor if Limine cannot do full BURG cards — scope: themes/
3. 🔲 [AGENT][CLOUD] **important** Deep scan: os-prober-style / recursive ESP walk beyond fixed heuristics; Windows-host scan plan + tests; never delete foreign EFI — scope: examples/python/
4. 🔲 [AGENT][CLOUD] **blocker** Repair apply + undo + repair_history: execute plans with confirm/dry-run; ESP-owned files only; unit tests — scope: examples/python/
5. 🔲 [AGENT][CLOUD] **blocker** Super GRUB-like one-shot: pick vmlinuz+initrd → one-shot Limine entry (userspace CLI) + tests — scope: examples/python/
6. 🔲 [AGENT][CLOUD] **important** Backup NVRAM dump + settings before changes (API + fixtures; host dump wired by Local) — scope: examples/python/
7. 🔲 [AGENT][CLOUD] **blocker** Linux GUI (Mint-friendly): real app (not subprocess façade only); entries/icons/default/timeout/theme/install via janusbootctl only — scope: examples/python/
8. 🔲 [AGENT][CLOUD] **blocker** Windows GUI + elevation warnings: same ops as Linux; never silent ESP/NVRAM/BCD write; docs ↔ code — scope: docs/spec.md
9. 🔲 [AGENT][CLOUD] **important** Theme pipeline real depth: resize/compress, hashes, atomic themes/.next/, last-good; desktop 1080p/4K preview (not metadata-only) — scope: examples/python/
10. 🔲 [AGENT][CLOUD] **important** Built-in theme assets: 2–3 packs with real PNG/JPEG + icons/ fallbacks; wallpaper path resolves in fixtures — scope: fixtures/esp/
11. 🔲 [AGENT][CLOUD] **important** In-boot settings gear or ship OS-tools floor with Linux/Windows GUIs covering timeout/default/theme (Phase 4 escape hatch OK only once GUIs exist) — scope: docs/VISION.md
12. 🔲 [AGENT][CLOUD] **important** janusbootctl install (EFI binary + conf to ESP layout) + NVRAM entry planner (dry-run first) — scope: esp/
13. 🔲 [AGENT][CLOUD] **polish** Linux/Windows schema divergence CI gate (fail when consumers disagree) — scope: schema/

### Parallel — LOCAL

14. 🔲 [AGENT][LOCAL] **blocker** QEMU smoke for boot-UI assets (icons/wallpaper/timeout) after Cloud lands — scope: Makefile
15. 🔲 [AGENT][LOCAL] **important** Live scan smoke (make scan-live / host ESP read-only) for deep-scan behavior — scope: Makefile
16. 🔲 [AGENT][LOCAL] **blocker** Repair apply host smoke: efibootmgr/NVRAM dry-run on lab VM only; document confirm — scope: docs/qemu.md
17. 🔲 [AGENT][LOCAL] **important** Wire real NVRAM dump into backup path (Cloud API + Local host tool) — scope: docs/nvram-repair-local.md
18. 🔲 [AGENT][LOCAL] **important** Install-to-ESP smoke on QEMU ESP image (not real disk) — scope: build/

### HUMAN

19. 🔲 [HUMAN] Approve first real-ESP or NVRAM apply outside QEMU (lab machine only) when Local smoke is ready
20. 🔲 [HUMAN] Windows GUI elevation UX sign-off (admin prompt copy) before tagging Must-complete

---

## Sprint — Nice-later + Bootable USB

Nice items from AGENT.md brief plus new **Bootable USB / rescue ISO** feature. Spec: [`docs/features/bootable-usb.md`](docs/features/bootable-usb.md). Steal UX/security ideas from FOSS writers only (USBImager, Etcher, Fedora Media Writer, Popsicle, Ventoy ideas, Mint/usb-creator) — do not vendor proprietary code.

### Sequential

21. 🔲 [AGENT][LOCAL] Keep board pointers honest as Cloud/Local USB and Must rows land — scope: BUILD_PLAN.md

### Parallel — CLOUD (nice-later)

22. 🔲 [AGENT][CLOUD] **nice** Mouse support behind mouse feature flag (boot UI + settings) — scope: schema/
23. 🔲 [AGENT][CLOUD] **nice** Theme zip shop (browse/import validated packs; no network phone-home from EFI) — scope: examples/python/
24. 🔲 [AGENT][CLOUD] **nice** HiDPI native resolution path (4K scale beyond 1080p preview) — scope: examples/python/
25. 🔲 [AGENT][CLOUD] **nice** btrfs / Timeshift cards (detect + calm entry; no hostile unlock) — scope: examples/python/
26. 🔲 [AGENT][CLOUD] **nice** Settings PIN (optional gate for boot UI theme/settings changes) — scope: schema/
27. 🔲 [AGENT][CLOUD] **nice** ARM64 UEFI target (after x86_64 Must) — scope: docs/VISION.md
28. 🔲 [AGENT][CLOUD] **nice** Icon atlas at theme apply (one read for EFI) — scope: examples/python/
29. 🔲 [AGENT][CLOUD] **nice** Reduce-motion / fast-boot (no background) setting — scope: schema/

### Parallel — CLOUD (bootable USB)

30. 🔲 [AGENT][CLOUD] **must-new** Rescue ISO contents: run / repair / reinstall JanusBoot + common OS boot help; layout + checksum manifest docs — scope: docs/spec.md
31. 🔲 [AGENT][CLOUD] **must-new** Device classification: removable-only allowlist; refuse internal/system disks; unit tests — scope: examples/python/
32. 🔲 [AGENT][CLOUD] **must-new** Dry-run / preview planner: show path, size, model, ISO+checksum; no write — scope: examples/python/
33. 🔲 [AGENT][CLOUD] **must-new** GUI Bootable USB flow: empty state, confirm step, one primary CTA; Linux + Windows panels call CLI only — scope: examples/python/
34. 🔲 [AGENT][CLOUD] **must-new** Elevation docs: Linux polkit/sudo vs Windows UAC; userspace tool allowlist — scope: docs/features/bootable-usb.md

### Parallel — LOCAL (bootable USB)

35. 🔲 [AGENT][LOCAL] **must-new** Removable-only USB write smoke (make usb-smoke or equiv.); fail closed if non-removable — scope: Makefile
36. 🔲 [AGENT][LOCAL] **must-new** Post-write verify path on disposable stick; never document blind dd to internal disks — scope: docs/qemu.md

### HUMAN

37. 🔲 [HUMAN] Provide disposable USB stick and approve first real write smoke (Local)
38. 🔲 [HUMAN] Confirm rescue ISO common OS boot help scope (what is in vs out of v1 ISO)

---

## Ongoing Maintenance

Not a checklist. GitHub Monday cron (`.github/workflows/weekly-health-check.yml`) already runs CI wait, security triage, parent template-gap BUILD_PLAN sync (this child board), radar, `update-deps` dry-run, Dependabot leftover list, open-PR BUILD_PLAN sync, and latest-release SBOM. Upgrade-sim stays on the template maintainer repo. `/ship` owns pre-release and the release tag.

If Monday cron is red: Cursor Automation `weekly-maintain`, then Grok Bot 4–5. Do not put those chores back on this board. [`docs/GROK_BOTS.md`](docs/GROK_BOTS.md) · [`docs/CURSOR_AUTOMATIONS.commercial.md`](docs/CURSOR_AUTOMATIONS.commercial.md)

---

## Archive

Older sprints: [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md).

### Archived Sprints

| Sprint | Complete | Archive |
|--------|----------|---------|
| Sprint 0 — Customize | 2026-09-17 | `COMPLETED_TASKS.md` |
| Sprint / Phase 0–2 — Contracts + QEMU smoke | 2026-09-17 | `COMPLETED_TASKS.md` |
| Sprint — Template upgrade 1.6.0 → 1.8.0 | 2026-09-17 | `COMPLETED_TASKS.md` |
| Sprint / Phase 3–8 — Scanner through Polish (stubs) | 2026-09-17 | `COMPLETED_TASKS.md` |
