#!/usr/bin/env bash
# Guest-only .deb install + GUI smoke in QEMU (does NOT apt-install on the host).
#
# Flow: build deb → download Debian cloudimg → cloud-init seed → boot →
#       apt install .deb inside guest → xvfb-run janusboot-gui --smoke
# Optional: also run Limine ESP qemu-smoke on the host image (no USB devices).
#
# Usage:
#   scripts/janusboot-vm-smoke.sh
#   scripts/janusboot-vm-smoke.sh --skip-esp          # skip make qemu-smoke
#   scripts/janusboot-vm-smoke.sh --keep              # leave VM disk/seed for debug
#   scripts/janusboot-vm-smoke.sh --timeout 600
# Interactive GUI (human VNC/GTK): make vm-gui
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VM_DIR="$ROOT/build/vm"
IMG_NAME="debian-12-generic-amd64.qcow2"
IMG_URL="https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2"
SSH_PORT="${JANUSBOOT_VM_SSH_PORT:-2222}"
TIMEOUT_SEC=900
SKIP_ESP=0
KEEP=0
INTERACTIVE=0
LEAVE_RUNNING=0

while [ $# -gt 0 ]; do
  case "$1" in
    --skip-esp) SKIP_ESP=1; shift ;;
    --keep) KEEP=1; shift ;;
    --leave-running) LEAVE_RUNNING=1; KEEP=1; shift ;;
    --interactive|--gui) INTERACTIVE=1; shift ;;
    --timeout) TIMEOUT_SEC="${2:?}"; shift 2 ;;
    --ssh-port) SSH_PORT="${2:?}"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

fail() { echo ""; echo "FAIL: $*"; exit 1; }
pass() { echo ""; echo "PASS: $*"; }

QEMU="${QEMU:-qemu-system-x86_64}"
command -v "$QEMU" >/dev/null 2>&1 || fail "$QEMU missing (document only — do not apt on host from this script)"
command -v qemu-img >/dev/null 2>&1 || fail "qemu-img missing"
command -v genisoimage >/dev/null 2>&1 || command -v mkisofs >/dev/null 2>&1 \
  || fail "genisoimage/mkisofs missing (needed for cloud-init seed; do not apt from this script)"
MKISO="$(command -v genisoimage || command -v mkisofs)"

mkdir -p "$VM_DIR"
HOST_DPKG_BEFORE="$VM_DIR/host-dpkg-before.txt"
HOST_DPKG_AFTER="$VM_DIR/host-dpkg-after.txt"
dpkg -l >"$HOST_DPKG_BEFORE" 2>/dev/null || true

echo "=== JanusBoot guest VM smoke ==="
echo "Root: $ROOT"
echo "VM dir: $VM_DIR (gitignored via build/)"
echo "SSH port: $SSH_PORT"
echo "Host apt/dpkg installs: FORBIDDEN in this script"

# --- 1) Build .deb on host (artifact only) ---
echo ""
echo "--- build .deb ---"
bash "$ROOT/scripts/janusboot-build-deb.sh" --out "$ROOT/dist"
DEB="$(ls -1 "$ROOT/dist"/janusbootctl_*_all.deb | sort | tail -1)"
[ -f "$DEB" ] || fail "deb not produced"
echo "Deb: $DEB"

# --- 2) Download cloud image (once) ---
BASE_IMG="$VM_DIR/$IMG_NAME"
if [ ! -f "$BASE_IMG" ]; then
  echo ""
  echo "--- download cloud image ---"
  echo "URL: $IMG_URL"
  curl -fL --retry 3 -o "$BASE_IMG.partial" "$IMG_URL"
  mv "$BASE_IMG.partial" "$BASE_IMG"
fi
ls -lh "$BASE_IMG"

WORK_IMG="$VM_DIR/guest-work.qcow2"
SEED_ISO="$VM_DIR/seed.iso"
SEED_DIR="$VM_DIR/seed"
SSH_KEY="$VM_DIR/id_ed25519"
SERIAL_LOG="$VM_DIR/serial.log"
GUEST_LOG="$VM_DIR/guest-smoke.log"

rm -f "$WORK_IMG" "$SEED_ISO" "$SERIAL_LOG" "$GUEST_LOG"
qemu-img create -f qcow2 -F qcow2 -b "$BASE_IMG" "$WORK_IMG" 8G >/dev/null

# --- 3) Ephemeral SSH + cloud-init NoCloud seed ---
rm -rf "$SEED_DIR"
mkdir -p "$SEED_DIR"
if [ ! -f "$SSH_KEY" ]; then
  ssh-keygen -t ed25519 -N "" -f "$SSH_KEY" -q -C "janusboot-vm-smoke"
fi
PUB="$(cat "${SSH_KEY}.pub")"

cat >"$SEED_DIR/meta-data" <<EOF
instance-id: janusboot-vm-smoke
local-hostname: janusboot-guest
EOF

cat >"$SEED_DIR/user-data" <<EOF
#cloud-config
users:
  - name: debian
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - ${PUB}
ssh_pwauth: false
package_update: true
packages:
  - python3-tk
  - python3-pil
  - python3-jsonschema
  - xvfb
  - xauth
runcmd:
  - [ sh, -c, "echo cloud-init-ready > /var/lib/janusboot-cloud-ready" ]
EOF

(
  cd "$SEED_DIR"
  "$MKISO" -quiet -output "$SEED_ISO" -volid cidata -joliet -rock user-data meta-data
)

# --- 4) Boot guest ---
if [ -z "${OVMF_CODE:-}" ]; then
  for p in /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd /usr/share/qemu/OVMF.fd; do
    if [ -f "$p" ]; then OVMF_CODE="$p"; break; fi
  done
fi
if [ -z "${OVMF_VARS:-}" ]; then
  for p in /usr/share/OVMF/OVMF_VARS_4M.fd /usr/share/OVMF/OVMF_VARS.fd; do
    if [ -f "$p" ]; then OVMF_VARS="$p"; break; fi
  done
fi
OVMF_VARS_SRC="${OVMF_VARS:-}"
[ -n "${OVMF_CODE:-}" ] && [ -f "$OVMF_CODE" ] || fail "OVMF_CODE not found"
[ -n "$OVMF_VARS_SRC" ] && [ -f "$OVMF_VARS_SRC" ] || fail "OVMF_VARS not found"
OVMF_VARS_COPY="$VM_DIR/OVMF_VARS.fd"
cp -f "$OVMF_VARS_SRC" "$OVMF_VARS_COPY"

DISPLAY_ARGS=(-display none)
if [ "$INTERACTIVE" -eq 1 ]; then
  DISPLAY_ARGS=(-display gtk)
fi

echo ""
echo "--- boot guest (QEMU) ---"
if [ -e /dev/kvm ] && [ -r /dev/kvm ]; then
  QEMU_ACCEL=kvm
else
  QEMU_ACCEL=tcg
  echo "NOTE: /dev/kvm unavailable — using TCG (slower)"
fi
"$QEMU" \
  -name janusboot-guest \
  -machine q35,accel="$QEMU_ACCEL" \
  -cpu max \
  -m 2048 \
  -smp 2 \
  -drive if=pflash,format=raw,readonly=on,file="$OVMF_CODE" \
  -drive if=pflash,format=raw,file="$OVMF_VARS_COPY" \
  -drive if=virtio,format=qcow2,file="$WORK_IMG" \
  -drive file="$SEED_ISO",format=raw,media=cdrom,readonly=on,if=virtio \
  -netdev user,id=net0,hostfwd=tcp:127.0.0.1:${SSH_PORT}-:22 \
  -device virtio-net-pci,netdev=net0 \
  -serial file:"$SERIAL_LOG" \
  "${DISPLAY_ARGS[@]}" \
  -daemonize \
  -pidfile "$VM_DIR/qemu.pid"
sleep 1
[ -f "$VM_DIR/qemu.pid" ] || fail "QEMU did not write pidfile $VM_DIR/qemu.pid"
echo "QEMU pid $(cat "$VM_DIR/qemu.pid") (accel=$QEMU_ACCEL)"

cleanup() {
  if [ "$LEAVE_RUNNING" -eq 1 ]; then
    echo "Leaving QEMU running (pid $(cat "$VM_DIR/qemu.pid" 2>/dev/null || echo '?'))"
    echo "SSH: ssh -i $SSH_KEY -p $SSH_PORT debian@127.0.0.1"
    echo "GUI: ssh … 'janusboot-gui'  or  'xvfb-run -a janusboot-gui --smoke'"
    echo "Stop: kill \$(cat $VM_DIR/qemu.pid)"
    return 0
  fi
  if [ -f "$VM_DIR/qemu.pid" ]; then
    kill "$(cat "$VM_DIR/qemu.pid")" 2>/dev/null || true
    wait "$(cat "$VM_DIR/qemu.pid")" 2>/dev/null || true
    rm -f "$VM_DIR/qemu.pid"
  fi
}
trap cleanup EXIT

SSH_OPTS=(-i "$SSH_KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o ConnectTimeout=5 -o BatchMode=yes -p "$SSH_PORT")
SCP_OPTS=(-i "$SSH_KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o ConnectTimeout=5 -o BatchMode=yes -P "$SSH_PORT")
ssh_guest() { ssh "${SSH_OPTS[@]}" debian@127.0.0.1 "$@"; }
scp_guest() { scp "${SCP_OPTS[@]}" "$@"; }

echo "Waiting for SSH (timeout ${TIMEOUT_SEC}s)…"
deadline=$((SECONDS + TIMEOUT_SEC))
while (( SECONDS < deadline )); do
  if ssh_guest "test -f /var/lib/janusboot-cloud-ready && echo ready" 2>/dev/null | grep -q ready; then
    break
  fi
  # cloud-init may still be running; accept plain SSH login as progress
  if ssh_guest "true" 2>/dev/null; then
    if ssh_guest "cloud-init status --wait >/dev/null 2>&1 || true; test -f /var/lib/janusboot-cloud-ready || sudo touch /var/lib/janusboot-cloud-ready" 2>/dev/null; then
      :
    fi
    if ssh_guest "test -f /var/lib/janusboot-cloud-ready" 2>/dev/null; then
      break
    fi
  fi
  sleep 5
done
ssh_guest "true" 2>/dev/null || fail "guest SSH never became ready (see $SERIAL_LOG)"

# Wait for cloud-init packages if marker raced ahead
ssh_guest "sudo cloud-init status --wait || true" 2>/dev/null || true

echo ""
echo "--- install .deb inside guest ---"
scp_guest "$DEB" "debian@127.0.0.1:/tmp/janusbootctl.deb"
ssh_guest "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/janusbootctl.deb" \
  || ssh_guest "sudo dpkg -i /tmp/janusbootctl.deb && sudo apt-get install -fy"

echo ""
echo "--- guest GUI smoke (xvfb) ---"
ssh_guest "command -v janusboot-gui && command -v janusbootctl"
ssh_guest "janusbootctl --esp /usr/share/janusboot/fixtures/esp validate"
ssh_guest "xvfb-run -a janusboot-gui --smoke --smoke-ms 500" | tee "$GUEST_LOG"
grep -q "smoke ok" "$GUEST_LOG" || fail "guest GUI smoke missing 'smoke ok'"

pass "guest .deb install + janusboot-gui --smoke"

# --- 5) Optional Limine ESP smoke (host QEMU, no USB) ---
if [ "$SKIP_ESP" -eq 0 ]; then
  echo ""
  echo "--- Limine ESP qemu-smoke (host, no USB) ---"
  make qemu-smoke QEMU_SMOKE_TIMEOUT=30
  pass "Limine ESP qemu-smoke"
fi

# --- 6) Prove host packages unchanged ---
dpkg -l >"$HOST_DPKG_AFTER" 2>/dev/null || true
if ! diff -q "$HOST_DPKG_BEFORE" "$HOST_DPKG_AFTER" >/dev/null 2>&1; then
  echo "WARN: host dpkg -l changed during run:"
  diff -u "$HOST_DPKG_BEFORE" "$HOST_DPKG_AFTER" | head -40 || true
  fail "host dpkg database changed (must not install janusboot on host)"
fi
if dpkg -l 2>/dev/null | grep -qi janusboot; then
  fail "janusboot package present on host"
fi
pass "host dpkg unchanged (no janusboot host install)"

if [ "$KEEP" -eq 0 ]; then
  cleanup
  trap - EXIT
  rm -f "$WORK_IMG" "$SEED_ISO"
fi

echo ""
echo "Artifacts: $DEB"
echo "Guest log: $GUEST_LOG"
echo "Host dpkg proof: $HOST_DPKG_BEFORE (matches after)"
pass "vm-smoke complete"
