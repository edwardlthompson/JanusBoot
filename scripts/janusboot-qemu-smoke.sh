#!/usr/bin/env bash
# Full LOCAL smoke: host deps → make deps → validate → test → esp-image → headless QEMU.
# Clear PASS/FAIL. Does not require a GUI session (--display none).
# Prefer scripts/janusboot-smoke-all.sh for monitored logging to build/smoke.log.
# Phase 8: visual check = make qemu; Secure Boot = docs/qemu.md (no fake signed boot).
#
# Usage:
#   scripts/janusboot-qemu-smoke.sh
#   scripts/janusboot-qemu-smoke.sh --skip-apt     # do not try --apply on host deps
#   scripts/janusboot-qemu-smoke.sh --timeout 40   # QEMU wall-clock seconds (default 30)
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

fail() {
  echo ""
  echo "FAIL: $*"
  exit 1
}

pass() {
  echo ""
  echo "PASS: $*"
}

echo "=== JanusBoot QEMU smoke ==="
echo "Root: $ROOT"
echo "Timeout: ${TIMEOUT_SEC}s"
echo "(monitored log variant: scripts/janusboot-smoke-all.sh → build/smoke.log)"

# 1) Host packages
if [ "$SKIP_APT" -eq 0 ]; then
  if ! bash scripts/janusboot-host-deps.sh --check; then
    echo "Host packages incomplete — attempting --apply (sudo TTY or pkexec)…"
    if [ ! -t 0 ] || [ ! -t 1 ]; then
      echo "NOTE: no TTY here — looking for pkexec GUI, else open Terminal and re-run."
    else
      echo ">>> Enter your sudo password in this terminal when prompted <<<"
    fi
    set +e
    bash scripts/janusboot-host-deps.sh --apply
    rc=$?
    set -e
    if [ "$rc" -eq 3 ]; then
      fail "host packages need sudo/pkexec password (run in integrated terminal)"
    elif [ "$rc" -ne 0 ]; then
      fail "host deps install/check failed (exit $rc)"
    fi
  fi
else
  bash scripts/janusboot-host-deps.sh --check \
    || fail "host packages missing (--skip-apt set; install manually)"
fi

# 2) Make pipeline (non-interactive)
echo ""
echo "--- make deps ---"
make deps

echo ""
echo "--- make validate ---"
make validate

echo ""
echo "--- make test ---"
make test

echo ""
echo "--- make esp-image ---"
make esp-image

# 3) Headless QEMU (Makefile qemu-smoke)
echo ""
echo "--- make qemu-smoke (headless, ${TIMEOUT_SEC}s) ---"
make qemu-smoke QEMU_SMOKE_TIMEOUT="${TIMEOUT_SEC}"

pass "deps + validate + test + esp-image + qemu-smoke"
echo "Interactive GUI boot: make qemu  (see docs/qemu.md)"
