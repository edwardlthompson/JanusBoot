#!/usr/bin/env bash
# Monitored full LOCAL smoke entrypoint:
#   host deps (prompt install if missing) → validate → test → esp-image → qemu-smoke
# Logs to build/smoke.log (tee). Prefer a real TTY so sudo can prompt.
#
# Usage:
#   scripts/janusboot-smoke-all.sh
#   scripts/janusboot-smoke-all.sh --timeout 40
#   scripts/janusboot-smoke-all.sh --skip-apt
#   make smoke-all
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SKIP_APT=0
TIMEOUT_SEC=30
while [ $# -gt 0 ]; do
  case "$1" in
    --skip-apt) SKIP_APT=1; shift ;;
    --timeout)
      TIMEOUT_SEC="${2:?}"
      shift 2
      ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

mkdir -p build
SMOKE_LOG="$ROOT/build/smoke.log"
STARTED_AT="$(date -Is)"

{
  echo "======== JanusBoot smoke-all ========"
  echo "started:  $STARTED_AT"
  echo "root:     $ROOT"
  echo "timeout:  ${TIMEOUT_SEC}s"
  echo "skip_apt: $SKIP_APT"
  echo "tty0:     $( [ -t 0 ] && echo yes || echo no )"
  echo "tty1:     $( [ -t 1 ] && echo yes || echo no )"
  echo "DISPLAY:  ${DISPLAY:-}"
  echo "====================================="
} | tee "$SMOKE_LOG"

fail() {
  echo "" | tee -a "$SMOKE_LOG"
  echo "FAIL: $*" | tee -a "$SMOKE_LOG"
  echo "Log: $SMOKE_LOG" | tee -a "$SMOKE_LOG"
  exit 1
}

pass() {
  echo "" | tee -a "$SMOKE_LOG"
  echo "PASS: $*" | tee -a "$SMOKE_LOG"
  echo "Log: $SMOKE_LOG" | tee -a "$SMOKE_LOG"
}

run_step() {
  local title="$1"
  shift
  echo "" | tee -a "$SMOKE_LOG"
  echo "--- $title ---" | tee -a "$SMOKE_LOG"
  set +e
  # Preserve exit code while teeing
  "$@" 2>&1 | tee -a "$SMOKE_LOG"
  local rc=${PIPESTATUS[0]}
  set -e
  echo "(exit $rc)" | tee -a "$SMOKE_LOG"
  return "$rc"
}

# 1) Host packages
if [ "$SKIP_APT" -eq 0 ]; then
  if ! run_step "host-deps --check" bash scripts/janusboot-host-deps.sh --check; then
    echo "Host packages incomplete — attempting --apply (sudo TTY or pkexec)…" | tee -a "$SMOKE_LOG"
    if [ ! -t 0 ] || [ ! -t 1 ]; then
      echo "NOTE: this shell has no TTY. Prefer: Terminal → New Terminal, then:" | tee -a "$SMOKE_LOG"
      echo "  cd \"$ROOT\" && scripts/janusboot-smoke-all.sh" | tee -a "$SMOKE_LOG"
      echo "Will try pkexec GUI auth if DISPLAY is set…" | tee -a "$SMOKE_LOG"
    else
      echo ">>> Enter your sudo password in this terminal when prompted <<<" | tee -a "$SMOKE_LOG"
    fi
    set +e
    run_step "host-deps --apply" bash scripts/janusboot-host-deps.sh --apply
    rc=$?
    set -e
    if [ "$rc" -eq 3 ]; then
      fail "host packages need a password prompt (run in integrated terminal; see log)"
    elif [ "$rc" -ne 0 ]; then
      fail "host deps install/check failed (exit $rc)"
    fi
  fi
else
  run_step "host-deps --check (--skip-apt)" bash scripts/janusboot-host-deps.sh --check \
    || fail "host packages missing (--skip-apt set; install manually)"
fi

# 2) Make pipeline
run_step "make deps" make deps || fail "make deps"
run_step "make validate" make validate || fail "make validate"
run_step "make test" make test || fail "make test"
run_step "make esp-image" make esp-image || fail "make esp-image"

# 3) Headless QEMU
run_step "make qemu-smoke (${TIMEOUT_SEC}s)" \
  make qemu-smoke "QEMU_SMOKE_TIMEOUT=${TIMEOUT_SEC}" \
  || fail "make qemu-smoke"

echo "" | tee -a "$SMOKE_LOG"
echo "finished: $(date -Is)" | tee -a "$SMOKE_LOG"
if [ -f "$ROOT/build/qemu-smoke.log" ]; then
  echo "qemu serial: $ROOT/build/qemu-smoke.log ($(wc -c < "$ROOT/build/qemu-smoke.log" | tr -d ' ') bytes)" | tee -a "$SMOKE_LOG"
fi

pass "deps + validate + test + esp-image + qemu-smoke"
echo "Interactive GUI boot: make qemu  (see docs/qemu.md)" | tee -a "$SMOKE_LOG"
