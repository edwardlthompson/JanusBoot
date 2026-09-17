#!/usr/bin/env bash
# Create / retarget a JanusBoot *product* GitHub remote.
# Refuses to treat agent-project-bootstrap as the product remote without --confirm-retarget.
# Never force-pushes. Never pushes to the bootstrap template as product origin.
#
# Usage:
#   scripts/janusboot-product-remote.sh                  # dry-run / detect
#   scripts/janusboot-product-remote.sh --apply          # create repo + retarget + push
#   scripts/janusboot-product-remote.sh --apply --confirm-retarget
#   scripts/janusboot-product-remote.sh --owner edwardlthompson --name JanusBoot
#
# Env: JANUSBOOT_OWNER, JANUSBOOT_REPO_NAME, JANUSBOOT_VISIBILITY (public|private)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APPLY=0
CONFIRM_RETARGET=0
OWNER="${JANUSBOOT_OWNER:-edwardlthompson}"
NAME="${JANUSBOOT_REPO_NAME:-JanusBoot}"
VISIBILITY="${JANUSBOOT_VISIBILITY:-public}"
BOOTSTRAP_SLUG="edwardlthompson/agent-project-bootstrap"

while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --confirm-retarget) CONFIRM_RETARGET=1; shift ;;
    --owner) OWNER="${2:?}"; shift 2 ;;
    --name) NAME="${2:?}"; shift 2 ;;
    --visibility) VISIBILITY="${2:?}"; shift 2 ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

PRODUCT_SLUG="${OWNER}/${NAME}"
PRODUCT_URL="https://github.com/${PRODUCT_SLUG}.git"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "$*"; }

current_origin() {
  git remote get-url origin 2>/dev/null || true
}

normalize_slug() {
  # Strip protocol/.git → owner/repo
  local u="$1"
  u="${u%.git}"
  u="${u#https://github.com/}"
  u="${u#http://github.com/}"
  u="${u#git@github.com:}"
  u="${u#ssh://git@github.com/}"
  printf '%s' "$u"
}

if ! command -v gh >/dev/null 2>&1; then
  die "gh CLI not found. Install: https://cli.github.com/
Then:
  gh auth login
  scripts/janusboot-product-remote.sh --apply --confirm-retarget"
fi

if ! gh auth status >/dev/null 2>&1; then
  die "gh is not authenticated.
  gh auth login
  scripts/janusboot-product-remote.sh --apply --confirm-retarget"
fi

ORIGIN="$(current_origin)"
ORIGIN_SLUG="$(normalize_slug "$ORIGIN")"

info "=== JanusBoot product remote ==="
info "Wanted:  ${PRODUCT_SLUG} (${VISIBILITY})"
info "Origin:  ${ORIGIN:-"(none)"} → slug=${ORIGIN_SLUG:-"(none)"}"
info "Branch:  $(git rev-parse --abbrev-ref HEAD)"

REPO_EXISTS=0
if gh repo view "$PRODUCT_SLUG" >/dev/null 2>&1; then
  REPO_EXISTS=1
  info "GitHub:  ${PRODUCT_SLUG} already exists"
else
  info "GitHub:  ${PRODUCT_SLUG} does not exist yet"
fi

if [ "$APPLY" -eq 0 ]; then
  info ""
  info "Dry-run. To create/retarget and push:"
  info "  scripts/janusboot-product-remote.sh --apply --confirm-retarget"
  if [ "$ORIGIN_SLUG" = "$BOOTSTRAP_SLUG" ]; then
    info ""
    info "NOTE: origin is still the bootstrap template (${BOOTSTRAP_SLUG})."
    info "      --confirm-retarget is required so we do not push product history there."
  fi
  exit 0
fi

# --- apply ---
if [ "$ORIGIN_SLUG" = "$BOOTSTRAP_SLUG" ] && [ "$CONFIRM_RETARGET" -ne 1 ]; then
  die "origin points at bootstrap template (${BOOTSTRAP_SLUG}).
Refuse to retarget without --confirm-retarget.
After confirm: bootstrap stays as remote 'bootstrap' (fetch-only recommended)."
fi

if [ "$ORIGIN_SLUG" = "$PRODUCT_SLUG" ]; then
  info "origin already points at product repo."
elif [ -n "$ORIGIN_SLUG" ] && [ "$ORIGIN_SLUG" != "$PRODUCT_SLUG" ]; then
  if git remote get-url bootstrap >/dev/null 2>&1; then
    info "Remote 'bootstrap' already set: $(git remote get-url bootstrap)"
  else
    info "Renaming origin → bootstrap (keep template remote)"
    git remote rename origin bootstrap
  fi
  if git remote get-url origin >/dev/null 2>&1; then
    info "Setting origin URL → ${PRODUCT_URL}"
    git remote set-url origin "$PRODUCT_URL"
  else
    info "Adding origin → ${PRODUCT_URL}"
    git remote add origin "$PRODUCT_URL"
  fi
elif [ -z "$ORIGIN_SLUG" ]; then
  git remote add origin "$PRODUCT_URL"
fi

if [ "$REPO_EXISTS" -eq 0 ]; then
  info "Creating GitHub repo ${PRODUCT_SLUG} (${VISIBILITY})…"
  # --source=. would push immediately; we create empty then push branches we choose.
  gh repo create "$PRODUCT_SLUG" --"$VISIBILITY" --description \
    "UEFI-first graphical boot manager (Limine + ESP settings + janusbootctl)" \
    --disable-wiki
else
  info "Using existing ${PRODUCT_SLUG}"
fi

# Ensure origin URL matches (gh create may leave remotes alone if we already set them)
git remote set-url origin "$PRODUCT_URL"

info "Fetching origin (may be empty)…"
git fetch origin 2>/dev/null || true

push_branch() {
  local b="$1"
  if git show-ref --verify --quiet "refs/heads/${b}"; then
    info "Pushing ${b} → origin (no force)…"
    git push -u origin "refs/heads/${b}:refs/heads/${b}"
  else
    info "Skip push: local branch ${b} missing"
  fi
}

# Prefer product branches; main last so default can be set after first push
push_branch "local/phase-0-2"
push_branch "cloud/phase-0-2"
push_branch "main"

# Default branch → main if we pushed it; else local/phase-0-2
if git show-ref --verify --quiet refs/heads/main; then
  gh repo edit "$PRODUCT_SLUG" --default-branch main 2>/dev/null || true
elif git show-ref --verify --quiet refs/heads/local/phase-0-2; then
  gh repo edit "$PRODUCT_SLUG" --default-branch local/phase-0-2 2>/dev/null || true
fi

info ""
info "PASS: product remote ready"
info "  URL: https://github.com/${PRODUCT_SLUG}"
info "  origin: $(git remote get-url origin)"
if git remote get-url bootstrap >/dev/null 2>&1; then
  info "  bootstrap: $(git remote get-url bootstrap)"
fi
info "Optional next: bash scripts/setup-github-repo.sh ${PRODUCT_SLUG}"
