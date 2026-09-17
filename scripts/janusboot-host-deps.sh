#!/usr/bin/env bash
# Detect (and optionally install) JanusBoot LOCAL host deps: QEMU, OVMF, FAT tools.
# Dry-run by default. Use --apply for apt install.
#
# Privilege escalation (apply order):
#   1) sudo -n          (passwordless / cached credentials)
#   2) sudo with TTY    (interactive password prompt on a real terminal)
#   3) pkexec           (GUI polkit dialog on Linux desktop, if available)
# Never use sudo -n as the only path — that skips the password prompt.
#
# Usage:
#   scripts/janusboot-host-deps.sh           # detect only
#   scripts/janusboot-host-deps.sh --apply   # apt install if needed
#   scripts/janusboot-host-deps.sh --check   # exit 1 if anything missing
#   scripts/janusboot-host-deps.sh status    # same as --check (alias)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APPLY=0
CHECK=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --check|status) CHECK=1 ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $arg (use --apply, --check, status, or --help)" >&2
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

have_usable_tty() {
  # stdin/stdout are TTYs, or /dev/tty is a usable controlling terminal
  if [ -t 0 ] && [ -t 1 ]; then
    return 0
  fi
  if [ -c /dev/tty ] && { : >/dev/tty; } 2>/dev/null; then
    return 0
  fi
  return 1
}

print_manual_install() {
  echo "" >&2
  echo "ACTION REQUIRED: run this in an integrated terminal (or any real TTY) so sudo can prompt:" >&2
  echo "" >&2
  echo "  cd \"$ROOT\"" >&2
  echo "  scripts/janusboot-host-deps.sh --apply" >&2
  echo "" >&2
  echo "Or paste these commands:" >&2
  echo "  sudo apt update" >&2
  echo "  sudo DEBIAN_FRONTEND=noninteractive apt install -y ${PKGS_NEEDED[*]}" >&2
  echo "  scripts/janusboot-qemu-smoke.sh" >&2
  echo "" >&2
  echo "If a desktop session is available, --apply will try pkexec (GUI password dialog)." >&2
  echo "Cursor agent shells often have no TTY — prefer Terminal → New Terminal, then re-run." >&2
}

# Run a privileged command. Prefer interactive sudo over silent sudo -n-only.
# Exit codes: 0 ok; 3 = needs human TTY / password; other = command failure.
run_privileged() {
  local label="$1"
  shift

  # 1) Cached / passwordless sudo (fast path, not the only path)
  if sudo -n true 2>/dev/null; then
    echo "auth: sudo -n (cached/passwordless) for: $label" >&2
    sudo -n "$@"
    return $?
  fi

  # 2) Interactive sudo on a real TTY (password prompt)
  if have_usable_tty; then
    echo "" >&2
    echo ">>> SUDO PASSWORD PROMPT — look at this terminal and enter your password <<<" >&2
    echo "auth: interactive sudo for: $label" >&2
    if [ -t 0 ] && [ -t 1 ]; then
      sudo "$@"
      return $?
    fi
    # Agent/non-TTY stdout but /dev/tty works (rare): force prompt onto tty
    sudo "$@" </dev/tty >/dev/tty 2>/dev/tty
    return $?
  fi

  # 3) GUI polkit dialog (Linux desktop)
  if command -v pkexec >/dev/null 2>&1 && { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; }; then
    echo "" >&2
    echo ">>> POLKIT / pkexec — approve the GUI password dialog on your desktop <<<" >&2
    echo "auth: pkexec for: $label" >&2
    # Keep cwd; forward noninteractive apt frontend when set
    if [ -n "${DEBIAN_FRONTEND:-}" ]; then
      pkexec --keep-cwd env DEBIAN_FRONTEND="$DEBIAN_FRONTEND" "$@"
    else
      pkexec --keep-cwd "$@"
    fi
    return $?
  fi

  print_manual_install
  echo "BLOCKED: no TTY for sudo password and pkexec unavailable/unusable." >&2
  return 3
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
  echo "Dry-run only (no install). Re-run with --apply to attempt apt (sudo TTY or pkexec)."
  exit 0
fi

# --- --apply ---
if ! command -v apt-get >/dev/null 2>&1; then
  echo "ERROR: apt-get not found; install packages manually for this distro." >&2
  echo "Hints: docs/qemu.md" >&2
  exit 1
fi

echo ""
echo "=== Applying apt install ==="
export DEBIAN_FRONTEND=noninteractive

set +e
run_privileged "apt-get update" apt-get update -y
rc=$?
set -e
if [ "$rc" -eq 3 ]; then
  exit 3
elif [ "$rc" -ne 0 ]; then
  echo "ERROR: apt-get update failed (exit $rc)" >&2
  exit "$rc"
fi

set +e
run_privileged "apt-get install ${PKGS_NEEDED[*]}" \
  apt-get install -y "${PKGS_NEEDED[@]}"
rc=$?
set -e
if [ "$rc" -eq 3 ]; then
  exit 3
elif [ "$rc" -ne 0 ]; then
  echo "ERROR: apt-get install failed (exit $rc)" >&2
  exit "$rc"
fi

echo ""
echo "Re-checking after install…"
exec "$0" --check

# --- Phase 5 LOCAL notes (Mint packaging / Polkit / real ESP) ---
# Packaging (future .deb): wrap janusbootctl + polkit policy that allows
# org.janusboot.esp.write only after auth; GUI must call CLI, never raw mount.
# Real ESP install: mount ESP, copy EFI/JanusBoot + Limine BOOTX64, then
# efibootmgr (see docs/nvram-repair-local.md). Always dry-run + confirm.
# pkexec is already used above for apt --apply when no TTY.
