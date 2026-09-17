#!/usr/bin/env bash
# Build janusbootctl_*.deb under dist/ without installing on the host.
# Layout mirrors the repo so janusbootctl.paths.repo_root() resolves schemas.
#
# Usage:
#   scripts/janusboot-build-deb.sh
#   scripts/janusboot-build-deb.sh --out dist
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OUT_DIR="$ROOT/dist"
VERSION=""
while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT_DIR="$(mkdir -p "${2:?}" && cd "$2" && pwd)"; shift 2 ;;
    --version) VERSION="${2:?}"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

CONTROL_IN="$ROOT/packaging/deb/debian/control"
SRC_PKG="$ROOT/examples/python/src/janusbootctl"
SCHEMA="$ROOT/schema"
FIXTURES="$ROOT/fixtures/esp"

[ -f "$CONTROL_IN" ] || { echo "FAIL: missing $CONTROL_IN" >&2; exit 1; }
[ -d "$SRC_PKG" ] || { echo "FAIL: missing $SRC_PKG (cloud merge?)" >&2; exit 1; }
[ -d "$SCHEMA" ] || { echo "FAIL: missing $SCHEMA" >&2; exit 1; }

if [ -z "$VERSION" ]; then
  VERSION="$(awk -F': ' '/^Version:/{print $2; exit}' "$CONTROL_IN")"
fi
PKG_NAME="janusbootctl_${VERSION}_all"
STAGE="$ROOT/build/deb-root"
DEB_PATH="$OUT_DIR/${PKG_NAME}.deb"

rm -rf "$STAGE"
mkdir -p \
  "$STAGE/DEBIAN" \
  "$STAGE/usr/bin" \
  "$STAGE/usr/share/janusboot/examples/python/src" \
  "$STAGE/usr/share/janusboot/schema" \
  "$STAGE/usr/share/janusboot/fixtures" \
  "$STAGE/usr/share/doc/janusbootctl"

# Control (pin version if overridden)
awk -v ver="$VERSION" '
  BEGIN { done=0 }
  /^Version:/ { print "Version: " ver; done=1; next }
  { print }
' "$CONTROL_IN" >"$STAGE/DEBIAN/control"

# Payload: preserve examples/python/src + schema + fixtures relative to share root
cp -a "$SRC_PKG" "$STAGE/usr/share/janusboot/examples/python/src/"
# Drop bytecode caches from the tree copy
find "$STAGE/usr/share/janusboot" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
cp -a "$SCHEMA"/. "$STAGE/usr/share/janusboot/schema/"
cp -a "$FIXTURES" "$STAGE/usr/share/janusboot/fixtures/esp"

install -m 0755 "$ROOT/packaging/deb/bin/janusbootctl" "$STAGE/usr/bin/janusbootctl"
install -m 0755 "$ROOT/packaging/deb/bin/janusboot-gui" "$STAGE/usr/bin/janusboot-gui"

cat >"$STAGE/usr/share/doc/janusbootctl/copyright" <<'EOF'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: JanusBoot
Source: https://github.com/edwardlthompson/JanusBoot

Files: *
Copyright: JanusBoot contributors
License: MIT
EOF

mkdir -p "$OUT_DIR"
if command -v dpkg-deb >/dev/null 2>&1; then
  dpkg-deb --root-owner-group --build "$STAGE" "$DEB_PATH"
else
  # Fallback: ar + tar (no host package install)
  echo "NOTE: dpkg-deb missing — building with ar/tar"
  DATA_TAR="$STAGE/../data.tar.gz"
  CTRL_TAR="$STAGE/../control.tar.gz"
  (
    cd "$STAGE"
    tar --owner=0 --group=0 -czf "$CTRL_TAR" -C DEBIAN .
    tar --owner=0 --group=0 -czf "$DATA_TAR" --exclude=./DEBIAN .
  )
  rm -f "$DEB_PATH"
  echo "2.0" >"$STAGE/../debian-binary"
  (
    cd "$(dirname "$STAGE")"
    ar r "$DEB_PATH" debian-binary control.tar.gz data.tar.gz
  )
fi

echo "PASS: built $DEB_PATH"
ls -lh "$DEB_PATH"
