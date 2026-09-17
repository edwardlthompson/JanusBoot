#!/usr/bin/env bash
# Detect (and optionally install) JanusBoot LOCAL host deps: QEMU, OVMF, FAT tools.
# Dry-run by default. Use --apply for apt install (tries passwordless sudo first).
#
# Usage:
#   scripts/janusboot-host-deps.sh           # detect only
#   scripts/janusboot-host-deps.sh --apply   # apt install if needed
#   scripts/janusboot-host-deps.sh --check   # exit 1 if anything missing
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APPLY=0
CHECK=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --check) CHECK=1 ;;
    -h|--help)
      sed -n '2,10p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $arg (use --apply, --check, or --help)" >&2
      exit 2
      ;;
  esac
done

PKGS_NEEDED=()
MISSING_MSGS=()

have_qemu() { command -v qemu-system-x86_64 >/dev/null 2>&1; }

find_ovmf_code() {
  local f
  for f in \
    /usr/share/OVMF/OVMF_CODE_4M.fd \
    /usr/share/OVMF/OVMF_CODE.fd \
    /usr/share/qemu/OVMF.fd \
    /usr/share/edk2/x64/OVMF_CODE.fd \
    /usr/share/edk2-ovmf/x64/OVMF_CODE.fd; do
    if [ -f "$f" ]; then
      printf '%s' "$f"
      return 0
    fi
  done
  return 1
}

find_ovmf_vars() {
  local f
  for f in \
    /usr/share/OVMF/OVMF_VARS_4M.fd \
    /usr/share/OVMF/OVMF_VARS.fd \
    /usr/share/edk2/x64/OVMF_VARS.fd \
    /usr/share/edk2-ovmf/x64/OVMF_VARS.fd; do
    if [ -f "$f" ]; then
      printf '%s' "$f"
      return 0
    fi
  done
  return 1
}

find_mkfs_fat() {
  local f
  for f in /usr/sbin/mkfs.fat /sbin/mkfs.fat /usr/bin/mkfs.fat; do
    if [ -x "$f" ]; then
      printf '%s' "$f"
      return 0
    fi
  done
  return 1
}

echo "=== JanusBoot host deps (detect) ==="
echo "Root: $ROOT"

if have_qemu; then
  echo "FOUND:   qemu-system-x86_64 ($(qemu-system-x86_64 --version | head -1))"
else
  echo "MISSING: qemu-system-x86_64"
  PKGS_NEEDED+=(qemu-system-x86)
  MISSING_MSGS+=("qemu-system-x86 (provides qemu-system-x86_64)")
fi

OVMF_CODE=""
OVMF_VARS=""
if OVMF_CODE="$(find_ovmf_code)"; then
  echo "FOUND:   OVMF_CODE=$OVMF_CODE"
else
  echo "MISSING: OVMF_CODE"
  PKGS_NEEDED+=(ovmf)
  MISSING_MSGS+=("ovmf (OVMF_CODE*.fd)")
fi

if OVMF_VARS="$(find_ovmf_vars)"; then
  echo "FOUND:   OVMF_VARS=$OVMF_VARS"
else
  echo "MISSING: OVMF_VARS"
  # ovmf already queued if CODE missing; ensure package listed once
  if [[ ! " ${PKGS_NEEDED[*]} " =~ " ovmf " ]]; then
    PKGS_NEEDED+=(ovmf)
  fi
  MISSING_MSGS+=("ovmf (OVMF_VARS*.fd)")
fi

if MKFS="$(find_mkfs_fat)"; then
  echo "FOUND:   mkfs.fat=$MKFS"
else
  echo "MISSING: mkfs.fat"
  PKGS_NEEDED+=(dosfstools)
  MISSING_MSGS+=("dosfstools")
fi

if command -v mcopy >/dev/null 2>&1 && command -v mmd >/dev/null 2>&1; then
  echo "FOUND:   mcopy / mmd"
else
  echo "MISSING: mcopy and/or mmd"
  PKGS_NEEDED+=(mtools)
  MISSING_MSGS+=("mtools")
fi

if command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1; then
  echo "FOUND:   curl or wget"
else
  echo "MISSING: curl/wget"
  PKGS_NEEDED+=(curl)
  MISSING_MSGS+=("curl")
fi

if command -v uv >/dev/null 2>&1; then
  echo "FOUND:   uv"
else
  echo "WARN:    uv not on PATH (validate/test need it; install via https://astral.sh/uv)"
fi

# Deduplicate packages
if [ "${#PKGS_NEEDED[@]}" -gt 0 ]; then
  mapfile -t PKGS_NEEDED < <(printf '%s\n' "${PKGS_NEEDED[@]}" | awk 'NF && !seen[$0]++')
fi

if [ "${#PKGS_NEEDED[@]}" -eq 0 ]; then
  echo ""
  echo "PASS: all required host packages present."
  exit 0
fi

echo ""
echo "Need packages: ${PKGS_NEEDED[*]}"
echo "Mint/Ubuntu install:"
echo "  sudo apt update"
echo "  sudo DEBIAN_FRONTEND=noninteractive apt install -y ${PKGS_NEEDED[*]}"
echo "Or: scripts/janusboot-host-deps.sh --apply"
echo "See docs/qemu.md"

if [ "$APPLY" -eq 0 ]; then
  if [ "$CHECK" -eq 1 ]; then
    exit 1
  fi
  echo ""
  echo "Dry-run only (no install). Re-run with --apply to attempt apt."
  exit 0
fi

# --- --apply ---
if ! command -v apt-get >/dev/null 2>&1; then
  echo "ERROR: apt-get not found; install packages manually for this distro." >&2
  echo "Hints: docs/qemu.md" >&2
  exit 1
fi

run_sudo() {
  if sudo -n true 2>/dev/null; then
    sudo -n "$@"
    return $?
  fi
  echo "" >&2
  echo "BLOCKED: sudo requires a password (passwordless sudo not available)." >&2
  echo "Run this yourself in a terminal, then re-run smoke:" >&2
  echo "" >&2
  echo "  sudo apt update" >&2
  echo "  sudo DEBIAN_FRONTEND=noninteractive apt install -y ${PKGS_NEEDED[*]}" >&2
  echo "  scripts/janusboot-qemu-smoke.sh" >&2
  echo "" >&2
  exit 3
}

echo ""
echo "=== Applying apt install (noninteractive) ==="
export DEBIAN_FRONTEND=noninteractive
run_sudo apt-get update -y
run_sudo apt-get install -y "${PKGS_NEEDED[@]}"

echo ""
echo "Re-checking after install…"
# Re-exec as detect+check
exec "$0" --check
