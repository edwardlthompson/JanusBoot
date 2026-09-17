# JanusBoot agent lanes

Isolation for dual-lane Phase 0–2 work. Full contract: `.cursor/janusboot-lane-lock.json` and `.cursor/rules/janusboot.mdc`.

## Lanes

| Label | Who | Branch prefix | Meaning |
|-------|-----|---------------|---------|
| `[LOCAL]` | This Computer / local Agent | `local/<phase-slug>` | Host tools, QEMU+OVMF, ESP image, integration merges |
| `[CLOUD]` | Cursor Cloud Agent | `cloud/<phase-slug>` | Text/code/tests only; no host firmware, no real disks |
| Sequential | LOCAL orchestrator chat | (edits lock + board) | Schema locks, BUILD_PLAN, merge order, lane contract files |

## Active branches (Must gaps v1)

- Cloud: `cloud/must-gaps-v1` (prior: `cloud/phase-3-8`, `cloud/phase-0-2`)
- Local: `local/phase-0-2`
- Merge order: cloud PR → `local/phase-0-2` → (human) `main`. Never cloud → `main` directly.

## Phase 0–2 branches (archived)

- Cloud: `cloud/phase-0-2`
- Local: `local/phase-0-2`

## Path ownership (hard)

| Owner | Paths |
|-------|-------|
| **CLOUD** | `schema/**`, `fixtures/esp/**`, `themes/**`, `docs/VISION.md`, `docs/spec.md`, `esp/**`, `examples/python/**` |
| **LOCAL** | `Makefile`, `third_party/**`, `build/**`, `*.img`, `docs/qemu.md`, `scripts/janusboot-qemu*` |
| **SEQUENTIAL** | `BUILD_PLAN.md`, `COMPLETED_TASKS.md`, `AGENT.md`, `AGENTS.md`, `.cursor/rules/janusboot.mdc`, `.cursorrules`, `docs/JANUSBOOT_AGENT_LANES.md`, `docs/PARALLEL_AGENT_SCOPES.md`, `bootstrap.config.json`, branding stamps init owns |

Before any edit: read the lane lock. If the path is not owned by your lane → **stop**.

## Anti-clobber rules

1. Cloud: no `make qemu`, no writes under `third_party/` or `build/`, no `dd`, no real ESP.
2. Local: no rewriting `schema/` or `examples/python/src/` while a cloud PR for that phase is open; merge cloud first.
3. Neither lane force-pushes the other’s branch.
4. Only Sequential marks BUILD_PLAN rows ✅ after the owning lane’s acceptance checks.
5. Shared schemas are authored on CLOUD then frozen; LOCAL consumes them. Schema bugs → open a `[CLOUD]` follow-up (or Sequential fix), do not silently patch on `local/*`.

## Acceptance

- Cloud: pytest green on `cloud/phase-0-2` (no QEMU).
- Local: after cloud merge, `make qemu` shows two fake entries driven by JSON; no edits to cloud paths except via merge.
- No BURG source trees.
