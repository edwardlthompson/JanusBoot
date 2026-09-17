#!/usr/bin/env bash
# LOCAL: scan a mounted ESP (or synthetic tree) for bootmgfw + Linux EFI via janusbootctl.
# Never deletes foreign EFI files. Never dd's a real disk.
#
# Usage:
#   scripts/janusboot-scan-esp.sh                 # fixtures/esp
#   scripts/janusboot-scan-esp.sh /boot/efi       # live mount
#   scripts/janusboot-scan-esp.sh --write /path   # write entries.json under --esp
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WRITE=0
ESP_ROOT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --write) WRITE=1; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *)
      if [ -n "$ESP_ROOT" ]; then
        echo "Unexpected arg: $1" >&2
        exit 2
      fi
      ESP_ROOT=$1
      shift
      ;;
  esac
done

ESP_ROOT="${ESP_ROOT:-$ROOT/fixtures/esp}"
ESP_ROOT="$(cd "$ESP_ROOT" && pwd)"
if [ ! -d "$ESP_ROOT" ]; then
  echo "FAIL: ESP root not a directory: $ESP_ROOT" >&2
  exit 1
fi

# Heuristic: if caller passed a mount that looks like ESP parent without EFI/, try common path.
if [ ! -d "$ESP_ROOT/EFI" ] && [ -d "$ESP_ROOT/efi" ]; then
  :
elif [ ! -d "$ESP_ROOT/EFI" ] && [ -d "/boot/efi/EFI" ] && [ "$ESP_ROOT" = "/boot/efi" ]; then
  :
fi

ARGS=(--esp "$ESP_ROOT" scan --root "$ESP_ROOT")
if [ "$WRITE" -eq 1 ]; then
  ARGS+=(--write)
fi

echo "scan-esp: root=$ESP_ROOT write=$WRITE"
if [ -f "$ESP_ROOT/EFI/Microsoft/Boot/bootmgfw.efi" ] || \
   [ -f "$ESP_ROOT/efi/Microsoft/Boot/bootmgfw.efi" ]; then
  echo "FOUND: Windows bootmgfw.efi under ESP"
else
  echo "NOTE: bootmgfw.efi not present (OK for Linux-only / fixtures)"
fi

cd "$ROOT/examples/python"
uv run janusbootctl "${ARGS[@]}"
