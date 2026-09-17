# JanusBoot — janusbootctl

Python CLI for the ESP settings contract: validate, get/set, backup, and
generate Limine config. Schemas live in repo `schema/`; fixtures in
`fixtures/esp/`.

## Commands

```bash
uv sync --all-extras
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run janusbootctl validate
uv run janusbootctl get timeout
uv run janusbootctl set timeout 10
uv run janusbootctl backup
uv run janusbootctl generate-limine -o /tmp/limine.conf
uv run janusbootctl validate-theme ../../themes/high-contrast/theme.json
```

Default `--esp` is the repo fixture tree `fixtures/esp`.

## Layout

- `src/janusbootctl/` — CLI and pure logic (≤150 lines per module)
- Repo `schema/` — JSON Schema for settings, entries, themes
- Repo `fixtures/esp/EFI/JanusBoot/` — sample settings/entries + golden limine.conf

QEMU / Makefile / real ESP image builds are LOCAL lane only.
