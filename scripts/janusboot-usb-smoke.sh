#!/usr/bin/env bash
# Removable-only USB smoke. Default: classifier + dry-run (no write).
# Real write: JANUSBOOT_USB_WRITE=1 JANUSBOOT_USB_DEVICE=/dev/sdX ISO=… (HUMAN disposable stick).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${ROOT}/examples/python"
cd "$PY"
UV="${UV:-uv}"

echo "usb-smoke: running classifier + dry-run tests"
$UV run pytest tests/test_usb_media.py -q -o addopts='-q' --cov-fail-under=0

MOCK="${ROOT}/build/usb-mock-devices.json"
ISO="${ROOT}/build/usb-rescue-stub.iso"
mkdir -p "${ROOT}/build"
printf '%s\n' '[{"path":"/dev/sdb","size_bytes":8000000000,"model":"MockStick","vendor":"Test","removable":true,"tran":"usb"},{"path":"/dev/nvme0n1","size_bytes":512000000000,"model":"SystemNVMe","tran":"nvme"}]' >"$MOCK"
printf 'JANUSBOOT-RESCUE-STUB' >"$ISO"

echo "usb-smoke: CLI list (must exclude nvme)"
out="$($UV run python -m janusbootctl usb list --mock-json "$MOCK")"
echo "$out" | grep -q '/dev/sdb'
if echo "$out" | grep -q 'nvme0n1'; then
  echo "FAIL: system disk leaked into removable list" >&2
  exit 1
fi

echo "usb-smoke: CLI preview dry-run"
$UV run python -m janusbootctl usb preview \
  --iso "$ISO" \
  --device /dev/sdb \
  --size-bytes 8000000000 \
  --model MockStick \
  --vendor Test \
  --removable \
  --tran usb | grep -q 'DRY-RUN'

if [[ "${JANUSBOOT_USB_WRITE:-}" == "1" ]]; then
  dev="${JANUSBOOT_USB_DEVICE:-}"
  iso_real="${JANUSBOOT_USB_ISO:-$ISO}"
  if [[ -z "$dev" ]]; then
    echo "FAIL: set JANUSBOOT_USB_DEVICE to a removable node" >&2
    exit 1
  fi
  echo "usb-smoke: refusing automatic destructive write without HUMAN confirm path"
  echo "  device=$dev iso=$iso_real — use janusbootctl usb write --confirm after verifying removable"
  echo "  Post-write verify: compare sha256 of ISO vs first/last blocks on device (docs/qemu.md)"
  exit 2
fi

echo "usb-smoke: OK (dry-run only; no physical stick write)"
