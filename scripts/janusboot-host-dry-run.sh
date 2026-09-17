#!/usr/bin/env bash
# LOCAL: host dry-run — read-only ESP scan + validate. Never writes ESP / NVRAM / USB.
#
# Usage:
#   scripts/janusboot-host-dry-run.sh
#   JANUSBOOT_ESP_ROOT=/boot/efi scripts/janusboot-host-dry-run.sh
#   make host-dry-run
#
# Refuses any destructive argv (--write, --confirm, repair-apply, install, efibootmgr, …).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
UV="${UV:-uv}"
PY="${ROOT}/examples/python"

refuse() {
  echo "REFUSE: host-dry-run never runs destructive ops — $*" >&2
  echo "See docs/host-dry-run.md" >&2
  exit 2
}

# Exit non-zero if any destructive flag/subcommand sneaks in (argv or env).
for arg in "$@"; do
  case "$arg" in
    --write|--confirm|-w)
      refuse "destructive flag: $arg"
      ;;
    *efibootmgr*)
      refuse "efibootmgr must not be invoked from host-dry-run"
      ;;
  esac
  # Subcommand tokens as whole args
  case "$arg" in
    repair-apply|install|write)
      refuse "destructive subcommand: $arg"
      ;;
  esac
done

# Also reject if caller stuffed dangerous tokens into JANUSBOOT_DRY_RUN_EXTRA
if [[ -n "${JANUSBOOT_DRY_RUN_EXTRA:-}" ]]; then
  case " ${JANUSBOOT_DRY_RUN_EXTRA} " in
    *" --write "*|*" --confirm "*|*" repair-apply "*|*" install "*|*" usb write "*|*"efibootmgr"*)
      refuse "JANUSBOOT_DRY_RUN_EXTRA contains a forbidden token"
      ;;
  esac
fi

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      refuse "unexpected argument: $1 (set JANUSBOOT_ESP_ROOT for a live mount)"
      ;;
  esac
done

FIXTURES="${ROOT}/fixtures/esp"
if [[ -n "${JANUSBOOT_ESP_ROOT:-}" ]]; then
  ESP_ROOT="${JANUSBOOT_ESP_ROOT}"
  if [[ ! -d "$ESP_ROOT" ]]; then
    echo "FAIL: JANUSBOOT_ESP_ROOT is not a directory: $ESP_ROOT" >&2
    exit 1
  fi
  ESP_ROOT="$(cd "$ESP_ROOT" && pwd)"
  echo "host-dry-run: ESP=$ESP_ROOT (from JANUSBOOT_ESP_ROOT)"
else
  ESP_ROOT="$FIXTURES"
  echo "host-dry-run: ESP=$ESP_ROOT (fixtures)"
  echo "  Tip: point at a real mount read-only with:"
  echo "    export JANUSBOOT_ESP_ROOT=/boot/efi"
  echo "    make host-dry-run"
fi

if [[ ! -d "$PY/src/janusbootctl" ]]; then
  echo "FAIL: janusbootctl sources missing under examples/python" >&2
  exit 1
fi

echo "host-dry-run: scan (no --write)"
(
  cd "$PY"
  # Explicitly omit --write. Do not generate entries.json on the ESP.
  $UV run janusbootctl --esp "$ESP_ROOT" scan --root "$ESP_ROOT"
)

echo "host-dry-run: validate (read-only)"
(
  cd "$PY"
  $UV run janusbootctl --esp "$ESP_ROOT" validate
)

# Optional classify-only USB list (no write). Skip quietly if CLI unavailable.
echo "host-dry-run: usb list (classify-only, if available)"
if (
  cd "$PY"
  $UV run janusbootctl --esp "$ESP_ROOT" usb list
) 2>/dev/null; then
  :
else
  echo "  (usb list skipped or empty — OK for dry-run)"
fi

echo "PASS: host-dry-run (read-only; no ESP/NVRAM/USB write)"
echo "Next tier needs HUMAN approval — see docs/host-dry-run.md and HUMAN_BACKLOG.md"
