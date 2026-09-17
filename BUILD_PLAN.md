# Build Plan

<!-- remaining-tally -->
**Remaining:** AGENT 12 · AUTO 0 · HUMAN 0 · ADB 0 · **12 open**
<!-- /remaining-tally -->

**Progress (not zero):** Sprint 0 ✅ done (archived) · Phase 0–2 ✅ **15/15** rows done · **12** Phase 3–8 stubs still open. The “Remaining” line counts only 🔲/❌ — it does **not** mean nothing shipped. Archive: [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md).

Live board for **JanusBoot**. Lane contract: [`docs/JANUSBOOT_AGENT_LANES.md`](docs/JANUSBOOT_AGENT_LANES.md) · lock: [`.cursor/janusboot-lane-lock.json`](.cursor/janusboot-lane-lock.json).

**Who:** `AGENT` code · `HUMAN` person · `ADB` device · `AUTO` CI/scripts

**Lane (required on JanusBoot product rows):**

| Label | Who | Meaning |
|-------|-----|---------|
| `[LOCAL]` | This Computer / local Agent | Host tools, QEMU+OVMF, workspace bind, real ESP later, or merges integration |
| `[CLOUD]` | Cursor Cloud Agent | Text/code/tests only on an isolated `cloud/*` branch; no host firmware, no real disks |

**State:** 🔲 open · ✅ done · ❌ blocked — reason

Format: `🔲 [AGENT][CLOUD] Short task` or `🔲 [AGENT][LOCAL] Short task`. Sequential `[AGENT]` (orchestrator) first. Parallel scopes: [`docs/PARALLEL_AGENT_SCOPES.md`](docs/PARALLEL_AGENT_SCOPES.md). `/build` tries HUMAN/ADB after automation; failures go to `HUMAN_BACKLOG.md`.

## Smoke gate (hard stop)

After every `[AGENT]` row: `python3 scripts/agent-run.py watch-agent-gates --once --autofix --scope auto`

After the **last** `[AGENT]`/`[AUTO]` row in a sprint is ✅, do **not** start the next sprint until this exits 0:

```bash
python3 scripts/agent-run.py smoke-sprint --require

```

That command re-smokes **every** ✅ row: no errors or crashes, plus startup time and load order. Details: [`docs/SPRINT_SMOKE.md`](docs/SPRINT_SMOKE.md). Fail → leave the last row open or ❌; fix; re-run. `/gates` wrap-up includes the same check.

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
| **Sprint 0 — Customize** | ✅ Done (archived off this board) | [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md) — section *Sprint 0 — Customize (JanusBoot, 2026-09-17)* |
| **Phase 0–2 — Contracts + QEMU smoke** | ✅ Done (all rows below) | Orchestrator + Cloud + Local lanes — every row ✅; `make smoke-all` PASS |

Agents **do** flip 🔲 → ✅ on this file as work lands. Status uses emoji markers (✅/🔲), not GitHub `- [ ]` checkboxes. If your IDE still shows Sprint 0 open with “30 remaining,” you are on a **stale path** (repo root leftover while the live checkout is `.cursor/worktrees/local-phase-0-2` on `main` / `local/phase-0-2` @ `41c13f0`+). Open the worktree copy or pull `origin/main`.

Next open work starts at **Phase 3** stubs.

### Sprint / Phase 0–2 — Contracts + QEMU smoke

<!-- parallel_exception: dual-lane CLOUD/LOCAL isolation via janusboot-lane-lock; not Parallel table agents -->

#### Orchestrator (sequential only)

1. ✅ [AGENT][LOCAL] Clone bootstrap; write `AGENT.md` (brief verbatim); run init
2. ✅ [AGENT][LOCAL] Create `docs/JANUSBOOT_AGENT_LANES.md`, lane lock, BUILD_PLAN LOCAL/CLOUD sections, `janusboot.mdc` + `.cursorrules`
3. ✅ [AGENT][LOCAL] Create branches `cloud/phase-0-2` and `local/phase-0-2` from post-init main
4. ✅ [HUMAN][LOCAL] Approve merge of `cloud/phase-0-2` into `local/phase-0-2` after cloud PR (Sequential integrate-pr: merge commit `fbf88ea`)
5. ✅ [HUMAN][LOCAL] Approve merge of `local/phase-0-2` → `main` after verify (+ host QEMU smoke) — `make smoke-all` PASS 2026-09-16 (qemu-smoke serial markers; packages via pkexec install after Cursor aptrepo blocked `apt update`)

#### Cloud lane

1. ✅ [AGENT][CLOUD] Write `docs/VISION.md`, `docs/spec.md`, `esp/layout.md` (Phase 4 OS-tools note in VISION)
2. ✅ [AGENT][CLOUD] Write `schema/{settings,entries,theme}.schema.json` with theme size/path limits
3. ✅ [AGENT][CLOUD] Write `fixtures/esp/EFI/JanusBoot/{settings,entries}.json` + `themes/high-contrast/theme.json`
4. ✅ [AGENT][CLOUD] Evolve `examples/python` → `janusbootctl` (`validate` / `get` / `set` / `backup` / `generate-limine`) + `jsonschema` + `uv.lock`
5. ✅ [AGENT][CLOUD] pytest (no QEMU): validate/get/set/backup + golden `limine.conf` from fixtures
6. ✅ [AGENT][CLOUD] Open PR into `local/phase-0-2` (not `main`) — integrated locally; product remote https://github.com/edwardlthompson/JanusBoot now hosts `cloud/phase-0-2` + `local/phase-0-2` + `main`

#### Local lane

1. ✅ [AGENT][LOCAL] Install/detect host deps (qemu-system-x86_64, OVMF, dosfstools/mtools); write `docs/qemu.md` — qemu-system-x86 + ovmf installed; `scripts/janusboot-host-deps.sh --check` PASS
2. ✅ [AGENT][LOCAL] `Makefile`: pin Limine → `third_party/limine/`, `esp-image`, `qemu`, `qemu-smoke`, wrappers for `validate`/`test` via `uv run`
3. ✅ [AGENT][LOCAL] After cloud PR merge: `make validate`, `make esp-image`, `make qemu` — two fake entries, timeout/default from JSON — `make smoke-all` PASS (`validate` + `test` 21 + `esp-image` + `qemu-smoke` serial markers)
4. ✅ [AGENT][LOCAL] `python3 scripts/agent-run.py verify` (or python feature-gate); mark Phase 0–2 rows ✅ — `feature-gate --stack python` passed; `make test` 21 passed. Golden Path About/hello tests removed with `janusbootctl` replace (expected product gap vs template About-smoke)

### Sprint / Phase 3 — Scanner (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] Linux path heuristics as pure functions + tests; entries schema tweaks

#### Local lane

1. 🔲 [AGENT][LOCAL] Live ESP mount scan on host; Windows `bootmgfw.efi` discovery

### Sprint / Phase 4 — Boot settings (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] VISION/docs + settings UX copy

#### Local lane

1. 🔲 [AGENT][LOCAL] Confirm Limine in-menu limits on QEMU

### Sprint / Phase 5 — Linux GUI (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] UI code talking only to CLI

#### Local lane

1. 🔲 [AGENT][LOCAL] Mint packaging / Polkit / real ESP install

### Sprint / Phase 6 — Windows GUI (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] C#/WinUI structure + mocks

#### Local lane

1. 🔲 [AGENT][LOCAL] Elevation, real ESP/BCD dry-run on Windows host

### Sprint / Phase 7 — Repair (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] Repair wizards, dry-run logic, tests

#### Local lane

1. 🔲 [AGENT][LOCAL] efibootmgr/NVRAM, backup restore on real/VM ESP

### Sprint / Phase 8 — Polish (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] Theme pack JSON, apply pipeline code, preview

#### Local lane

1. 🔲 [AGENT][LOCAL] QEMU visual check; Secure Boot doc against real shim if keys exist

### Waiting on a person

_None blocking for Sprint 0 / Phase 0–2 process._ Optional IDE: pin `docs/help/BATCH_COMMANDS.md`; set Cursor mode in the UI. Optional GitHub: Actions bot approval + `AUTOMERGE_TOKEN` (notes from `setup-github-repo.sh`). Re-check: `scripts/janusboot-human-checklist.sh`.

- ~~`[HUMAN]` Host password / apt install qemu+ovmf~~ → done (`qemu-system-x86` + `ovmf` installed; note: Cursor aptrepo GPG can break bare `apt update` — install packages directly or fix `NO_PUBKEY 42A1772E62E492D6`)
- ~~`[HUMAN]` Create JanusBoot product GitHub remote~~ → done (`edwardlthompson/JanusBoot`; origin retargeted; bootstrap remote kept)
- ~~`[HUMAN]` Approve `local/phase-0-2` → `main` after `qemu-smoke` PASS~~ → done (`make smoke-all` PASS; ff merge to `main`)
- ~~`[HUMAN]` Fill INITIALIZATION_PROMPT / pick mode / bookmark BATCH_COMMANDS~~ → done (fill script + checklist; IDE pin/mode remain optional)

### Open PRs (synced)

> Auto-managed on product repos too. Do not hand-edit rows inside the markers.

<!-- open-prs-sync:begin -->
_No open Dependabot or Release Please PRs._
<!-- open-prs-sync:end -->

### Template gaps (synced)

> Auto-managed Monday cron + `sync-template-gaps-build-plan`. Do not hand-edit inside markers. Plan-only — run `/upgrade` then name item numbers.

<!-- template-gaps-sync:begin -->
_No template gaps; .template-version matches upstream (or template maintainer N/A)._
<!-- template-gaps-sync:end -->

### UX & UI inventory

Complete list from construction gaps and `/ux-review`. Status is only planned / in_progress / done. `/build` does not execute these until `/ux-apply UX-NNN` (or a Sequential row). Follow [`docs/ux-ui-guidelines.md`](docs/ux-ui-guidelines.md) when shipping UI.

<!-- ux-inventory:begin -->
_No UX inventory items._
<!-- ux-inventory:end -->

---

## Ongoing Maintenance

Not a checklist. GitHub Monday cron (`.github/workflows/weekly-health-check.yml`) already runs CI wait, security triage, parent template-gap BUILD_PLAN sync (this child board), radar, `update-deps` dry-run, Dependabot leftover list, open-PR BUILD_PLAN sync, and latest-release SBOM. Upgrade-sim stays on the template maintainer repo. `/ship` owns pre-release and the release tag.

If Monday cron is red: Cursor Automation `weekly-maintain`, then Grok Bot 4–5. Do not put those chores back on this board. [`docs/GROK_BOTS.md`](docs/GROK_BOTS.md) · [`docs/CURSOR_AUTOMATIONS.commercial.md`](docs/CURSOR_AUTOMATIONS.commercial.md)

---

## Archive

Older sprints: [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md).
