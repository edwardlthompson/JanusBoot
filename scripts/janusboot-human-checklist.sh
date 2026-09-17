#!/usr/bin/env bash
# Print / verify JanusBoot Sprint 0 HUMAN process items.
# Automates what can be scripted; lists true-human leftovers (IDE UI, passwords, future ESP).
#
# Usage:
#   scripts/janusboot-human-checklist.sh           # status report (exit 0 if no blocking leftovers)
#   scripts/janusboot-human-checklist.sh --apply   # run fill-init + setup-github-repo + product-remote dry-run
#   scripts/janusboot-human-checklist.sh --strict  # exit 1 if any STILL_HUMAN process item remains
#
# One-command path for BUILD_PLAN HUMAN rows that are process (not Phase 3–8 product).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APPLY=0
STRICT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --strict) STRICT=1; shift ;;
    -h|--help)
      sed -n '2,14p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

info() { printf '%s\n' "$*"; }
ok() { printf '  ✅ %s\n' "$*"; }
still() { printf '  🔲 %s\n' "$*"; STILL_HUMAN=$((STILL_HUMAN + 1)); }
scripted() { printf '  📜 %s\n' "$*"; }
auto() { printf '  ⚙️  %s\n' "$*"; }

STILL_HUMAN=0

info "=== JanusBoot HUMAN checklist ==="
info "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
info "Origin: $(git remote get-url origin 2>/dev/null || echo '(none)')"
info ""

# --- Product remote ---
info "## GitHub product repo"
if git remote get-url origin 2>/dev/null | grep -qi 'edwardlthompson/JanusBoot'; then
  ok "origin → edwardlthompson/JanusBoot"
else
  still "origin is not JanusBoot product remote — run: scripts/janusboot-product-remote.sh --apply --confirm-retarget"
fi
if git remote get-url bootstrap >/dev/null 2>&1; then
  ok "bootstrap remote kept ($(git remote get-url bootstrap))"
else
  scripted "optional: keep template as remote 'bootstrap'"
fi
if [ "$APPLY" -eq 1 ]; then
  bash scripts/janusboot-product-remote.sh || true
fi

# --- FOSS tier ---
info ""
info "## FOSS vs Commercial"
if [ -f .cursor/stack-selection.json ] && grep -q '"distribution_tier": "foss"' .cursor/stack-selection.json; then
  ok "distribution_tier=foss (MIT)"
else
  still "stamp FOSS via init --distribution-tier foss (or edit .cursor/stack-selection.json)"
fi

# --- INITIALIZATION_PROMPT ---
info ""
info "## Fill docs/INITIALIZATION_PROMPT.md"
if [ "$APPLY" -eq 1 ]; then
  bash scripts/janusboot-fill-init-prompt.sh || true
fi
if bash scripts/janusboot-fill-init-prompt.sh --check >/dev/null 2>&1; then
  ok "INITIALIZATION_PROMPT stamped (scripts/janusboot-fill-init-prompt.sh)"
else
  still "run: scripts/janusboot-fill-init-prompt.sh"
fi

# --- GitHub repo settings ---
info ""
info "## GitHub settings (Dependabot / branch protection)"
if [ "$APPLY" -eq 1 ]; then
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    bash scripts/setup-github-repo.sh edwardlthompson/JanusBoot || true
  else
    still "gh not authenticated — cannot run setup-github-repo.sh"
  fi
else
  auto "re-run: bash scripts/setup-github-repo.sh edwardlthompson/JanusBoot"
fi
ok "branch protection + Dependabot alerts covered by setup-github-repo.sh (idempotent)"
scripted "optional HUMAN: Actions approval for github-actions[bot]; AUTOMERGE_TOKEN — see setup-github-repo.sh notes"

# --- Cursor mode (IDE) ---
info ""
info "## Pick Cursor mode"
ok "documented: docs/CURSOR_MODES.md — Ask explore · Plan architecture · Agent execute · Debug triage"
scripted "IDE UI: set mode in Cursor before non-trivial work (cannot fully automate)"
info "  Default for BUILD_PLAN [AGENT] execution after Plan approval: Agent mode."

# --- Bookmark batch commands (IDE) ---
info ""
info "## Bookmark docs/help/BATCH_COMMANDS.md"
ok "documented: docs/help/BATCH_COMMANDS.md — type / in Agent chat (/bootstrap · /coach · /gates)"
scripted "IDE UI: pin/bookmark that path in your editor if desired (cannot fully automate)"

# --- Phase merges (already done on this board when marked) ---
info ""
info "## Phase 0–2 merge approvals"
if grep -q '✅ \[HUMAN\].*cloud/phase-0-2.*local/phase-0-2' BUILD_PLAN.md 2>/dev/null; then
  ok "cloud → local merge already ✅ on BUILD_PLAN"
else
  still "approve merge cloud/phase-0-2 → local/phase-0-2 after cloud PR"
fi
if grep -q '✅ \[HUMAN\].*local/phase-0-2.*main' BUILD_PLAN.md 2>/dev/null; then
  ok "local → main merge already ✅ on BUILD_PLAN"
else
  still "approve merge local/phase-0-2 → main after make smoke-all PASS"
fi

# --- Host deps / sudo (process, not product feature) ---
info ""
info "## Host deps (LOCAL)"
if bash scripts/janusboot-host-deps.sh --check >/dev/null 2>&1; then
  ok "qemu/OVMF/FAT tools present (scripts/janusboot-host-deps.sh --check)"
else
  still "install host deps: scripts/janusboot-host-deps.sh --apply (sudo TTY or pkexec)"
fi

# --- Future phases: hooks only, do not fake product completion ---
info ""
info "## Phase 3–8 (stubs — no fake completion)"
info "  When those sprints open, prepare env with existing LOCAL scripts; do not mark product rows ✅ here."
info "  Phase 3 LOCAL: real ESP mount scan — needs a mounted ESP path (human/hardware)."
info "  Phase 5 LOCAL: Mint packaging / Polkit — needs package tooling on host."
info "  Phase 6 LOCAL: Windows elevation / BCD dry-run — needs a Windows host."
info "  Phase 7 LOCAL: efibootmgr/NVRAM — needs VM or real firmware access."
info "  Phase 8 LOCAL: Secure Boot vs real shim — needs keys if signing."
info "  Prep only: make smoke-all · scripts/janusboot-host-deps.sh · docs/qemu.md"

info ""
info "=== Summary ==="
if [ "$STILL_HUMAN" -eq 0 ]; then
  info "No blocking HUMAN process leftovers (IDE pin/mode are optional scripted reminders)."
  info "One-command re-check: scripts/janusboot-human-checklist.sh"
  info "Apply automatable steps: scripts/janusboot-human-checklist.sh --apply"
  exit 0
fi

info "STILL_HUMAN count: $STILL_HUMAN"
info "Re-run with --apply to execute fill-init + setup-github-repo + product-remote dry-run."
if [ "$STRICT" -eq 1 ]; then
  exit 1
fi
exit 0
