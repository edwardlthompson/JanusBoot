#!/usr/bin/env bash
# Fail if sacred JanusBoot product markers are missing or overwritten by template hello.
#
# Usage:
#   scripts/janusboot-protect-product.sh           # verify (exit 1 on failure)
#   scripts/janusboot-protect-product.sh --json    # machine-readable summary
#
# Wired for local/CI: call from validate-bootstrap --quick path or feature-gate python.
# Never copies parent template examples/python — verify-only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

JSON=0
while [ $# -gt 0 ]; do
  case "$1" in
    --json) JSON=1; shift ;;
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

ERRORS=0
msgs=()

fail() {
  msgs+=("$*")
  ERRORS=$((ERRORS + 1))
}

need_file() {
  if [ ! -f "$1" ]; then
    fail "MISSING file: $1"
  fi
}

need_dir() {
  if [ ! -d "$1" ]; then
    fail "MISSING dir: $1"
  fi
}

need_grep() {
  local path="$1" pattern="$2" label="$3"
  if [ ! -f "$path" ]; then
    fail "MISSING file: $path ($label)"
    return
  fi
  if ! grep -qE "$pattern" "$path"; then
    fail "MISSING marker in $path: $label ($pattern)"
  fi
}

# --- Sacred product identity ---
need_file "AGENT.md"
need_grep "AGENT.md" "JanusBoot" "product name"
need_grep "AGENT.md" "janusbootctl" "CLI name"
need_file "AGENTS.md"
need_grep "AGENTS.md" "\\*\\*Product:\\*\\* JanusBoot" "project card"
need_file "branding/product.json"
need_grep "branding/product.json" '"name": "JanusBoot"' "branding identity"

# --- janusbootctl package (must not be template hello-only) ---
need_dir "examples/python/src/janusbootctl"
need_file "examples/python/src/janusbootctl/cli.py"
need_file "examples/python/src/janusbootctl/about.py"
need_file "examples/python/src/janusbootctl/crash.py"
need_file "examples/python/pyproject.toml"
need_grep "examples/python/pyproject.toml" 'name = "janusbootctl"' "package name"
need_grep "examples/python/pyproject.toml" 'janusbootctl = "janusbootctl.cli:main"' "console script"
need_file "examples/python/uv.lock"

# Template hello must not be the primary package
if grep -qE 'name = "golden-path-python"' examples/python/pyproject.toml 2>/dev/null; then
  fail "pyproject.toml must not be renamed to golden-path-python (product retained)"
fi
if grep -qE '^hello = "hello.cli:main"' examples/python/pyproject.toml 2>/dev/null; then
  if ! grep -qE 'janusbootctl = "janusbootctl.cli:main"' examples/python/pyproject.toml; then
    fail "hello console script without janusbootctl primary script"
  fi
fi

# Golden Path catalog shims may exist, but must re-export product modules
if [ -f examples/python/src/hello/about.py ]; then
  need_grep "examples/python/src/hello/about.py" "janusbootctl.about" "hello.about re-exports product"
fi
if [ -f examples/python/src/hello/crash.py ]; then
  need_grep "examples/python/src/hello/crash.py" "janusbootctl.crash" "hello.crash re-exports product"
fi

# --- Lane / ESP contract ---
need_file ".cursor/janusboot-lane-lock.json"
need_file ".cursor/rules/janusboot.mdc"
need_file ".cursorrules"
need_file "docs/JANUSBOOT_AGENT_LANES.md"
need_file "docs/VISION.md"
need_file "docs/spec.md"
need_file "docs/qemu.md"
need_file "docs/limine-gen.md"
need_file "Makefile"
need_dir "schema"
need_dir "fixtures/esp"
need_dir "themes"
need_dir "esp"

# --- Sacred upgrade policy: AGENTS product card must stay JanusBoot ---
if grep -qE '\\*\\*Product:\\*\\* agent-project-bootstrap' AGENTS.md 2>/dev/null; then
  fail "AGENTS.md product card drifted to template name"
fi

if [ "$JSON" -eq 1 ]; then
  if [ "$ERRORS" -eq 0 ]; then
    printf '{"ok":true,"errors":0}\n'
  else
    python3 - "$ERRORS" "${msgs[@]}" <<'PY'
import json, sys
n = int(sys.argv[1])
print(json.dumps({"ok": False, "errors": n, "messages": sys.argv[2:]}))
PY
  fi
else
  if [ "$ERRORS" -eq 0 ]; then
    echo "OK   janusboot-protect-product: sacred JanusBoot markers present"
  else
    echo "FAIL janusboot-protect-product ($ERRORS):" >&2
    for m in "${msgs[@]}"; do
      echo "  - $m" >&2
    done
  fi
fi

exit "$ERRORS"
