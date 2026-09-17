#!/usr/bin/env bash
# Fill / refresh docs/INITIALIZATION_PROMPT.md from AGENT.md + branding/product.json.
# Idempotent. Does not re-run init-project.
#
# Usage:
#   scripts/janusboot-fill-init-prompt.sh           # apply
#   scripts/janusboot-fill-init-prompt.sh --check   # exit 1 if gaps remain
#   scripts/janusboot-fill-init-prompt.sh --dry-run
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CHECK=0
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help)
      sed -n '2,10p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

export JANUSBOOT_FILL_CHECK="$CHECK"
export JANUSBOOT_FILL_DRY="$DRY"

python3 - <<'PY'
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

root = Path(".").resolve()
init_path = root / "docs" / "INITIALIZATION_PROMPT.md"
agent_path = root / "AGENT.md"
brand_path = root / "branding" / "product.json"
stack_path = root / ".cursor" / "stack-selection.json"

check = os.environ.get("JANUSBOOT_FILL_CHECK") == "1"
dry = os.environ.get("JANUSBOOT_FILL_DRY") == "1"

if not init_path.is_file():
    print("ERROR: docs/INITIALIZATION_PROMPT.md missing", file=sys.stderr)
    sys.exit(1)

text = init_path.read_text(encoding="utf-8")
orig = text

one_liner = ""
if agent_path.is_file():
    am = agent_path.read_text(encoding="utf-8")
    m = re.search(
        r"<!-- agent-brief:one-liner -->\s*(.*?)\s*<!-- /agent-brief:one-liner -->",
        am,
        re.DOTALL,
    )
    if m:
        one_liner = " ".join(m.group(1).split())
    if not one_liner:
        m = re.search(r"^## One-sentence vision\n\n(.+?)$", am, re.MULTILINE)
        if m:
            one_liner = " ".join(m.group(1).split())

brand: dict = {}
if brand_path.is_file():
    brand = json.loads(brand_path.read_text(encoding="utf-8"))

stack = "python"
purpose = brand.get("tagline") or one_liner or (
    "UEFI-first graphical boot manager (Limine + ESP settings contract + janusbootctl)"
)
if stack_path.is_file():
    sel = json.loads(stack_path.read_text(encoding="utf-8"))
    stack = str(sel.get("stack") or stack)
    tier = sel.get("distribution_tier", "foss")
else:
    tier = "foss"

name = brand.get("name") or "JanusBoot"
repo = (brand.get("urls") or {}).get("github_repo") or "edwardlthompson/JanusBoot"

# Stamp stack / purpose lines (init already does placeholders; keep current shape).
text = re.sub(
    r"(\*\*Platform/Tech Stack:\*\*\s*).*",
    rf"\1{stack}",
    text,
    count=1,
)
text = re.sub(
    r"(\*\*Purpose & Goals:\*\*\s*).*",
    rf"\1{purpose}",
    text,
    count=1,
)

# Sacred brief pointer (replace generic Original brief paragraph if still template-ish).
brief_block = (
    f"**Original brief (sacred):** Read [`AGENT.md`](../AGENT.md) before any sprint row. "
    f"One-liner: {one_liner or purpose} "
    f"Product **{name}**; CLI **janusbootctl**; ESP **EFI/JanusBoot/**; "
    f"engine **Limine** (do not fork bootloaders / vendor BURG in v1). "
    f"Repo: https://github.com/{repo}. Distribution tier: **{tier}** (MIT)."
)
if "**Original brief:**" in text or "**Original brief (sacred):**" in text:
    text = re.sub(
        r"\*\*Original brief(?: \(sacred\))?:\*\*.*",
        brief_block,
        text,
        count=1,
    )

# Product / lanes block after Distribution (insert once).
marker = "<!-- janusboot-init-prompt:product -->"
if marker not in text:
    product_block = f"""
{marker}
### JanusBoot product (stamped)

- **Name:** {name} · **CLI:** janusbootctl · **ESP:** `EFI/JanusBoot/`
- **Lanes:** [`docs/JANUSBOOT_AGENT_LANES.md`](JANUSBOOT_AGENT_LANES.md) · lock [`.cursor/janusboot-lane-lock.json`](../.cursor/janusboot-lane-lock.json)
- **Local smoke:** `make smoke-all` · `scripts/janusboot-smoke-all.sh`
- **Product remote:** `scripts/janusboot-product-remote.sh` · GitHub settings: `scripts/setup-github-repo.sh`
- **HUMAN leftovers checklist:** `scripts/janusboot-human-checklist.sh`
<!-- /janusboot-init-prompt:product -->
"""
    # Insert after Distribution paragraph.
    text, n = re.subn(
        r"(\*\*Distribution:\*\*[^\n]*\n)",
        rf"\1{product_block}\n",
        text,
        count=1,
    )
    if n != 1:
        # Fallback: after ## 1. Project Dimensions heading block end / before ## 1a
        text = text.replace("## 1a. Explain the Why", product_block + "\n## 1a. Explain the Why", 1)

# Replace generic web init example with JanusBoot python non-interactive example.
old_example = re.search(
    r"```bash\nscripts/init-project\.sh \\\n.*?```",
    text,
    re.DOTALL,
)
new_example = f"""```bash
scripts/init-project.sh \\
  --non-interactive \\
  --stack {stack} \\
  --project-name "{name}" \\
  --purpose "{purpose}" \\
  --interval weekly \\
  --codeowner edwardlthompson \\
  --distribution-tier {tier} \\
  --prune --prune-optional
```"""
if old_example:
    text = text[: old_example.start()] + new_example + text[old_example.end() :]

# Align PowerShell one-liner with stamped stack/name (keep as single prose line).
text = re.sub(
    r"PowerShell: `pwsh scripts/init-project\.ps1[^`]+`",
    (
        f'PowerShell: `pwsh scripts/init-project.ps1 -NonInteractive -Stack {stack} '
        f'-ProjectName "{name}" -ProjectPurpose "{purpose}" -DistributionTier {tier}`'
    ),
    text,
    count=1,
)

# Gaps that still mean "not filled"
gaps: list[str] = []
if "[INSERT PLATFORM" in text or "[INSERT DETAILED APP" in text:
    gaps.append("placeholder tokens still present")
if f"**Platform/Tech Stack:** {stack}" not in text:
    gaps.append("stack line missing/wrong")
if "janusbootctl" not in text.lower() and "UEFI-first" not in text:
    gaps.append("purpose lacks JanusBoot signals")
if marker not in text and "JanusBoot product (stamped)" not in text:
    gaps.append("product stamp block missing")
bash_ex = re.search(r"```bash\nscripts/init-project\.sh.*?```", text, re.DOTALL)
if bash_ex and "--stack web" in bash_ex.group(0):
    gaps.append("bash init example still shows --stack web")
if check:
    if gaps or text != orig:
        for g in gaps:
            print(f"GAP: {g}")
        if text != orig and not gaps:
            print("GAP: file would change under --apply (run without --check)")
        sys.exit(1)
    print("PASS: docs/INITIALIZATION_PROMPT.md filled for JanusBoot")
    sys.exit(0)

if dry:
    if text == orig:
        print("Dry-run: no changes")
    else:
        print("Dry-run: would update docs/INITIALIZATION_PROMPT.md")
        for g in gaps:
            print(f"  would fix: {g}")
    sys.exit(0)

if text != orig:
    init_path.write_text(text, encoding="utf-8")
    print("Updated docs/INITIALIZATION_PROMPT.md from AGENT.md + branding")
else:
    print("OK: docs/INITIALIZATION_PROMPT.md already stamped")

if gaps:
    print("WARNING: residual gaps:", ", ".join(gaps), file=sys.stderr)
    sys.exit(1)
print("PASS: INITIALIZATION_PROMPT filled")
PY
