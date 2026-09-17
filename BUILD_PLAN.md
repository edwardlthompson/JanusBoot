# Build Plan

<!-- remaining-tally -->
**Remaining:** AGENT 12 · LOCAL 6 · CLOUD 6 · AUTO 0 · HUMAN 0 · ADB 0 · **12 open**
<!-- /remaining-tally -->

**Progress (not zero):** Sprint 0 ✅ done (archived) · Phase 0–2 ✅ **15/15** rows done · **12** Phase 3–8 stubs still open · Template upgrade 1.6.0→1.8.0: Canon+Mixed applied; Sacred UPG-71…77 ✅ waived—product retained; Golden UPG-78/79 ✅ About+crash alongside janusbootctl. The “Remaining” line counts only 🔲/❌ — it does **not** mean nothing shipped. Archive: [`COMPLETED_TASKS.md`](COMPLETED_TASKS.md).

Live board for **JanusBoot**. Lane contract: [`docs/JANUSBOOT_AGENT_LANES.md`](docs/JANUSBOOT_AGENT_LANES.md) · lock: [`.cursor/janusboot-lane-lock.json`](.cursor/janusboot-lane-lock.json).

**Who:** `AGENT` code · `HUMAN` person · `ADB` device · `AUTO` CI/scripts

**Venue (template):** `[LOCAL]` / `[CLOUD]` + optional `— scope:` — see [`docs/adr/0008-agent-venue.md`](docs/adr/0008-agent-venue.md). JanusBoot product rows also use the lane table below.

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

## Agent venues (standing queues)

### Local agent (This Computer)

Standing queue for This Computer. Product Phase stubs carry venue tags in sprint sections below.

<!-- local-agent-lane:begin -->
_No local agent items._
<!-- local-agent-lane:end -->

### Cloud agent (Cursor Cloud)

Standing queue for Cursor Cloud Agents. Product Phase stubs carry venue tags in sprint sections below.

<!-- cloud-agent-lane:begin -->
_No cloud agent items._
<!-- cloud-agent-lane:end -->


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

Next open work: **Phase 3–8** stubs (template upgrade 1.6.0→1.8.0 Canon+Mixed+Sacred-waived+Golden About/crash applied).

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

1. 🔲 [AGENT][CLOUD] Linux path heuristics as pure functions + tests; entries schema tweaks — scope: schema/

#### Local lane

1. 🔲 [AGENT][LOCAL] Live ESP mount scan on host; Windows `bootmgfw.efi` discovery — scope: Makefile

### Sprint / Phase 4 — Boot settings (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] VISION/docs + settings UX copy — scope: docs/VISION.md

#### Local lane

1. 🔲 [AGENT][LOCAL] Confirm Limine in-menu limits on QEMU — scope: docs/qemu.md

### Sprint / Phase 5 — Linux GUI (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] UI code talking only to CLI — scope: examples/python/

#### Local lane

1. 🔲 [AGENT][LOCAL] Mint packaging / Polkit / real ESP install — scope: scripts/janusboot-host-deps.sh

### Sprint / Phase 6 — Windows GUI (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] C#/WinUI structure + mocks — scope: docs/spec.md

#### Local lane

1. 🔲 [AGENT][LOCAL] Elevation, real ESP/BCD dry-run on Windows host — scope: third_party/

### Sprint / Phase 7 — Repair (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] Repair wizards, dry-run logic, tests — scope: fixtures/esp/

#### Local lane

1. 🔲 [AGENT][LOCAL] efibootmgr/NVRAM, backup restore on real/VM ESP — scope: build/

### Sprint / Phase 8 — Polish (stub)

<!-- parallel_exception: board stub only; dual-lane CLOUD/LOCAL when opened -->

#### Cloud lane

1. 🔲 [AGENT][CLOUD] Theme pack JSON, apply pipeline code, preview — scope: themes/

#### Local lane

1. 🔲 [AGENT][LOCAL] QEMU visual check; Secure Boot doc against real shim if keys exist — scope: scripts/janusboot-qemu-smoke.sh

### Waiting on a person

_None blocking for Sprint 0 / Phase 0–2 process._ Optional IDE: pin `docs/help/BATCH_COMMANDS.md`; set Cursor mode in the UI. Optional GitHub: Actions bot approval + `AUTOMERGE_TOKEN` (notes from `setup-github-repo.sh`). Re-check: `scripts/janusboot-human-checklist.sh`. Sacred UPG-71…77 waived via `scripts/janusboot-protect-product.sh` (verify-only). Actions `default_workflow_permissions=write` set for Release Please.

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

Named gaps **1–79** boarded under **Sprint — Template upgrade 1.6.0 → 1.8.0** (UPG-01…79) below — apply gated separately; this sync block is a pointer only (avoids double-counting).
<!-- template-gaps-sync:end -->

### Sprint — Template upgrade 1.6.0 → 1.8.0

Named gaps from `/upgrade` (parent `edwardlthompson/agent-project-bootstrap` **1.8.0**). Apply executed 2026-09-16: Canon ✅ copy; Mixed ✅ merge (JanusBoot board/branding/history kept); Sacred ✅ waived—product retained (`janusboot-protect-product.sh`); Golden ✅ About+crash alongside janusbootctl (no template hello restore).

<!-- parallel_exception: template catch-up board; Sequential apply when numbers named for copy -->

#### Canon (1–42) — `[AGENT]` copy from parent

1. ✅ [AGENT] Canon UPG-01: copy `.cursor/commands/build.md` from parent 1.8.0
2. ✅ [AGENT] Canon UPG-02: copy `.cursor/commands/coach.md` from parent 1.8.0
3. ✅ [AGENT] Canon UPG-03: copy `.cursor/commands/feature.md` from parent 1.8.0
4. ✅ [AGENT] Canon UPG-04: copy `.cursor/commands/gates.md` from parent 1.8.0
5. ✅ [AGENT] Canon UPG-05: copy `.cursor/commands/plan.md` from parent 1.8.0
6. ✅ [AGENT] Canon UPG-06: copy `.cursor/commands/resume.md` from parent 1.8.0
7. ✅ [AGENT] Canon UPG-07: copy `.cursor/commands/scope.md` from parent 1.8.0
8. ✅ [AGENT] Canon UPG-08: copy `.cursor/rules/batch-commands.mdc` from parent 1.8.0
9. ✅ [AGENT] Canon UPG-09: copy `.cursor/rules/brief-replies.mdc` from parent 1.8.0
10. ✅ [AGENT] Canon UPG-10: copy `.cursor/rules/core-directives.mdc` from parent 1.8.0
11. ✅ [AGENT] Canon UPG-11: copy `.cursor/rules/feature-modules.mdc` from parent 1.8.0
12. ✅ [AGENT] Canon UPG-12: copy `.cursor/rules/foss-compliance.mdc` from parent 1.8.0
13. ✅ [AGENT] Canon UPG-13: copy `.cursor/rules/local-compute.mdc` from parent 1.8.0
14. ✅ [AGENT] Canon UPG-14: copy `.cursor/rules/local-deps.mdc` from parent 1.8.0
15. ✅ [AGENT] Canon UPG-15: copy `.cursor/rules/read-before-write.mdc` from parent 1.8.0
16. ✅ [AGENT] Canon UPG-16: copy `.cursor/rules/ux-ui.mdc` from parent 1.8.0
17. ✅ [AGENT] Canon UPG-17: copy `.cursor/rules/windows-encoding.mdc` from parent 1.8.0
18. ✅ [AGENT] Canon UPG-18: copy `BUILD_PLAN_TEMPLATE.md` from parent 1.8.0
19. ✅ [AGENT] Canon UPG-19: copy `docs/CURSOR_MODES.md` from parent 1.8.0
20. ✅ [AGENT] Canon UPG-20: copy `docs/help/BATCH_COMMANDS.md` from parent 1.8.0
21. ✅ [AGENT] Canon UPG-21: copy `docs/help/COACH.md` from parent 1.8.0
22. ✅ [AGENT] Canon UPG-22: copy `docs/help/DONATIONS.md` from parent 1.8.0
23. ✅ [AGENT] Canon UPG-23: copy `docs/help/TOUR.md` from parent 1.8.0
24. ✅ [AGENT] Canon UPG-24: copy `scripts/check-agent-venue.sh` from parent 1.8.0
25. ✅ [AGENT] Canon UPG-25: copy `scripts/lib/agent_venue.py` from parent 1.8.0
26. ✅ [AGENT] Canon UPG-26: copy `scripts/lib/build_plan_tally.py` from parent 1.8.0
27. ✅ [AGENT] Canon UPG-27: copy `scripts/lib/build_sprint.py` from parent 1.8.0
28. ✅ [AGENT] Canon UPG-28: copy `scripts/lib/build_sprint_model.py` from parent 1.8.0
29. ✅ [AGENT] Canon UPG-29: copy `scripts/lib/build_sprint_parse.py` from parent 1.8.0
30. ✅ [AGENT] Canon UPG-30: copy `scripts/lib/build_sprint_resolve.py` from parent 1.8.0
31. ✅ [AGENT] Canon UPG-31: copy `scripts/lib/cursor_feature_radar_io.py` from parent 1.8.0
32. ✅ [AGENT] Canon UPG-32: copy `scripts/lib/cursor_rule_audit.py` from parent 1.8.0
33. ✅ [AGENT] Canon UPG-33: copy `scripts/lib/gate_scope.py` from parent 1.8.0
34. ✅ [AGENT] Canon UPG-34: copy `scripts/lib/gates_canvas.py` from parent 1.8.0
35. ✅ [AGENT] Canon UPG-35: copy `scripts/lib/parallel_scope_model.py` from parent 1.8.0
36. ✅ [AGENT] Canon UPG-36: copy `scripts/lib/resume_digest.py` from parent 1.8.0
37. ✅ [AGENT] Canon UPG-37: copy `scripts/lib/resume_handoff.py` from parent 1.8.0
38. ✅ [AGENT] Canon UPG-38: copy `scripts/lib/sprint_smoke_parse.py` from parent 1.8.0
39. ✅ [AGENT] Canon UPG-39: copy `scripts/lib/sync_open_prs_render.py` from parent 1.8.0
40. ✅ [AGENT] Canon UPG-40: copy `scripts/lib/sync_template_gaps_render.py` from parent 1.8.0
41. ✅ [AGENT] Canon UPG-41: copy `scripts/sync-cursor-features.py` from parent 1.8.0
42. ✅ [AGENT] Canon UPG-42: copy `scripts/validate-bootstrap.sh` from parent 1.8.0

#### Mixed (43–70) — `[AGENT]` merge; keep child; `[HUMAN]` review before ✅

43. ✅ [AGENT] Mixed UPG-43: merge `.cursor-plugin/plugin.json` (keep JanusBoot values; human review)
44. ✅ [AGENT] Mixed UPG-44: merge `.cursor/hooks/session_start_context.py` (keep JanusBoot values; human review)
45. ✅ [AGENT] Mixed UPG-45: merge `.cursor/skills/validate-bootstrap/SKILL.md` (keep JanusBoot values; human review)
46. ✅ [AGENT] Mixed UPG-46: merge `.pre-commit-config.yaml` (keep JanusBoot values; human review)
47. ✅ [AGENT] Mixed UPG-47: merge `.release-please-manifest.json` (keep JanusBoot values; human review)
48. ✅ [AGENT] Mixed UPG-48: merge `.template-version` (keep JanusBoot values; human review)
49. ✅ [AGENT] Mixed UPG-49: merge `AGENT_MEMORY.md` (keep JanusBoot values; human review)
50. ✅ [AGENT] Mixed UPG-50: merge `BUILD_PLAN.md` (keep JanusBoot values; human review)
51. ✅ [AGENT] Mixed UPG-51: merge `CHANGELOG.md` (keep JanusBoot values; human review)
52. ✅ [AGENT] Mixed UPG-52: merge `CITATION.cff` (keep JanusBoot values; human review)
53. ✅ [AGENT] Mixed UPG-53: merge `COMPLETED_TASKS.md` (keep JanusBoot values; human review)
54. ✅ [AGENT] Mixed UPG-54: merge `DECISION_LOG.md` (keep JanusBoot values; human review)
55. ✅ [AGENT] Mixed UPG-55: merge `KNOWLEDGE_BASE.md` (keep JanusBoot values; human review)
56. ✅ [AGENT] Mixed UPG-56: merge `README.md` (keep JanusBoot values; human review)
57. ✅ [AGENT] Mixed UPG-57: merge `TEMPLATE_INDEX.json` (keep JanusBoot values; human review)
58. ✅ [AGENT] Mixed UPG-58: merge `docs/CURSOR_INTEGRATIONS.md` (keep JanusBoot values; human review)
59. ✅ [AGENT] Mixed UPG-59: merge `docs/PARALLEL_AGENT_SCOPES.md` (keep JanusBoot values; human review)
60. ✅ [AGENT] Mixed UPG-60: merge `docs/START_HERE.md` (keep JanusBoot values; human review)
61. ✅ [AGENT] Mixed UPG-61: merge `docs/adr/0008-agent-venue.md` (keep JanusBoot values; human review)
62. ✅ [AGENT] Mixed UPG-62: merge `docs/adr/0009-cost-diet-brevity.md` (keep JanusBoot values; human review)
63. ✅ [AGENT] Mixed UPG-63: merge `schemas/golden-path/upgrade-policy.json` (keep JanusBoot values; human review)
64. ✅ [AGENT] Mixed UPG-64: merge `tests/test_agent_venue.py` (keep JanusBoot values; human review)
65. ✅ [AGENT] Mixed UPG-65: merge `tests/test_build_plan_tally.py` (keep JanusBoot values; human review)
66. ✅ [AGENT] Mixed UPG-66: merge `tests/test_gate_scope.py` (keep JanusBoot values; human review)
67. ✅ [AGENT] Mixed UPG-67: merge `tests/test_resume_handoff.py` (keep JanusBoot values; human review)
68. ✅ [AGENT] Mixed UPG-68: merge `tests/test_sync_open_prs_build_plan.py` (keep JanusBoot values; human review)
69. ✅ [AGENT] Mixed UPG-69: merge `tests/test_sync_template_gaps_build_plan.py` (keep JanusBoot values; human review)
70. ✅ [AGENT] Mixed UPG-70: merge `tests/test_validate_bootstrap_agent.py` (keep JanusBoot values; human review)

#### Sacred (71–77) — `[HUMAN]` waived—product retained (verify-only; do not overwrite)

71. ✅ [HUMAN] Sacred UPG-71: waived—product retained — AGENTS.md JanusBoot card (`janusboot-protect-product.sh`; sync-adapters OK)
72. ✅ [HUMAN] Sacred UPG-72: waived—product retained — examples/node lock (stack pruned / not JanusBoot app)
73. ✅ [HUMAN] Sacred UPG-73: waived—product retained — examples/node package.json (stack pruned)
74. ✅ [HUMAN] Sacred UPG-74: waived—product retained — examples/python/pyproject.toml (janusbootctl)
75. ✅ [HUMAN] Sacred UPG-75: waived—product retained — examples/python/uv.lock (janusbootctl)
76. ✅ [HUMAN] Sacred UPG-76: waived—product retained — examples/web lock (stack pruned)
77. ✅ [HUMAN] Sacred UPG-77: waived—product retained — examples/web package.json (stack pruned)

#### Golden Path (78–79) — applied alongside janusbootctl (no hello-primary restore)

78. ✅ [AGENT] Golden UPG-78: About payload + `janusbootctl about` (+ `hello.about` catalog re-export)
79. ✅ [AGENT] Golden UPG-79: crash sanitizer + `janusbootctl sanitize-crash` (+ `hello.crash` catalog re-export)


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
