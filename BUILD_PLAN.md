# Build Plan

<!-- remaining-tally -->
**Remaining:** AGENT 0 · LOCAL 0 · CLOUD 0 · AUTO 0 · HUMAN 3 · ADB 0 · **3 open**
<!-- /remaining-tally -->

**Progress (not zero):** Sprint 0 ✅ archived · Phase 0–2 ✅ archived · Template upgrade 1.6.0→1.8.0 ✅ archived · Phase 3–8 stubs ✅ archived · Must gaps AGENT ✅ (HUMAN open) · **Nice-later + Bootable USB AGENT ✅ (HUMAN open)**. The “Remaining” line counts only 🔲/❌ — Phase stubs shipped CLI/schema/QEMU depth, not brief-complete Must (v1). Archive: [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md). Gap analysis tip: `f1a191d`.

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
| **Must gaps (v1 depth)** | ✅ AGENT archived · 🔲 HUMAN | [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md) · HUMAN_BACKLOG |
| **Nice-later + Bootable USB** | ✅ AGENT archived · 🔲 HUMAN | [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md) · HUMAN_BACKLOG |
> **Sprint / Phase 0–2** archived in COMPLETED_TASKS.md @ `a337d62`.
> **Sprint — Template upgrade 1.6.0 → 1.8.0** archived in COMPLETED_TASKS.md @ `a337d62`.
> **Sprint / Phase 3–8** archived in COMPLETED_TASKS.md @ `837199b` (stubs).
> **Sprint — Nice-later + Bootable USB** AGENT archived in COMPLETED_TASKS.md @ `346597d`.

Agents **do** flip 🔲 → ✅ on this file as work lands. Status uses emoji markers (✅/🔲), not GitHub `- [ ]` checkboxes. Live tip: `.cursor/worktrees/local-phase-0-2` on `local/phase-0-2` (keep root `BUILD_PLAN.md` in sync for the IDE).

Next open work: Must gaps **HUMAN** (#19–20) + Nice-later **HUMAN** (ISO scope #38) — see HUMAN_BACKLOG.md. Disposable USB write smoke archived. `v1.0.0` ≠ brief-complete Must (v1).

### Waiting on a person

_None blocking for Sprint 0 / Phase 0–2 process._ Optional IDE: pin `docs/help/BATCH_COMMANDS.md`; set Cursor mode in the UI. Optional GitHub: Actions bot approval + `AUTOMERGE_TOKEN` (notes from `setup-github-repo.sh`). Re-check: `scripts/janusboot-human-checklist.sh`. Sacred UPG-71…77 waived via `scripts/janusboot-protect-product.sh` (verify-only). Actions `default_workflow_permissions=write` set for Release Please.

Open for new sprints (see rows below): rescue ISO scope (#38); Windows GUI elevation UX sign-off when that row is ready.

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

<!-- parallel_exception: numbered Parallel CLOUD/LOCAL lists (not markdown tables); AGENT rows archived -->

> **Must gaps (v1 depth)** AGENT/LOCAL/CLOUD archived in COMPLETED_TASKS.md @ `d95c710`. HUMAN sign-offs remain below.

### HUMAN

19. 🔲 [HUMAN] Approve first real-ESP or NVRAM apply outside QEMU (lab machine only) when Local smoke is ready
20. 🔲 [HUMAN] Windows GUI elevation UX sign-off (admin prompt copy) before tagging Must-complete

---

## Sprint — Nice-later + Bootable USB

<!-- parallel_exception: numbered Parallel CLOUD/LOCAL lists (not markdown tables); AGENT archived -->

> **Nice-later + Bootable USB** AGENT/LOCAL/CLOUD archived in COMPLETED_TASKS.md @ `346597d`. HUMAN sign-offs remain below.

### HUMAN

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
| Sprint — Must gaps (v1 depth) | 2026-09-17 | `COMPLETED_TASKS.md` |
| Sprint — Nice-later + Bootable USB | 2026-09-17 | `COMPLETED_TASKS.md` |
