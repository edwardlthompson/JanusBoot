# JanusBoot — LOCAL lane host/QEMU targets (Phase 0–2)
# Owns: Limine pin, FAT ESP image, QEMU+OVMF smoke.
# Cloud merge supplies schema/, fixtures/esp/, janusbootctl before esp-image/qemu succeed.
#
# Paths are repo-relative so workspaces with spaces (e.g. "Janus Boot") work with Make.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Pinned Limine binary release (UEFI x86_64). Bump deliberately; keep docs/qemu.md in sync.
LIMINE_VERSION ?= 12.9.0
LIMINE_TAG := v$(LIMINE_VERSION)
LIMINE_ARCHIVE := limine-binary.tar.xz
LIMINE_URL := https://github.com/Limine-Bootloader/Limine/releases/download/$(LIMINE_TAG)/$(LIMINE_ARCHIVE)

LIMINE_DIR := third_party/limine
LIMINE_EFI := $(LIMINE_DIR)/BOOTX64.EFI

BUILD := build
ESP_IMG := $(BUILD)/esp.img
ESP_SIZE_MIB ?= 64
OVMF_VARS_COPY := $(BUILD)/OVMF_VARS.fd
LIMINE_CONF := $(BUILD)/limine.conf
LIMINE_STAMP := $(BUILD)/limine-$(LIMINE_VERSION).stamp

FIXTURES_ESP := fixtures/esp
PYTHON_DIR := examples/python
UV ?= uv

# Debian/Ubuntu/Mint (noble+) defaults; override on other distros.
OVMF_CODE ?= $(firstword $(wildcard \
	/usr/share/OVMF/OVMF_CODE_4M.fd \
	/usr/share/OVMF/OVMF_CODE.fd \
	/usr/share/qemu/OVMF.fd \
	/usr/share/edk2/x64/OVMF_CODE.fd \
	/usr/share/edk2-ovmf/x64/OVMF_CODE.fd))
OVMF_VARS ?= $(firstword $(wildcard \
	/usr/share/OVMF/OVMF_VARS_4M.fd \
	/usr/share/OVMF/OVMF_VARS.fd \
	/usr/share/edk2/x64/OVMF_VARS.fd \
	/usr/share/edk2-ovmf/x64/OVMF_VARS.fd))

QEMU ?= qemu-system-x86_64
MKFS_FAT ?= $(firstword $(wildcard /usr/sbin/mkfs.fat /sbin/mkfs.fat /usr/bin/mkfs.fat))
MCOPY ?= mcopy
MMD ?= mmd

.PHONY: help deps check-host limine esp-image qemu validate test clean \
	_require-cloud _require-qemu _require-ovmf _require-fat-tools

help:
	@echo "JanusBoot LOCAL targets:"
	@echo "  make deps       Detect host tools; download pinned Limine $(LIMINE_TAG)"
	@echo "  make validate   janusbootctl validate (needs cloud merge)"
	@echo "  make test       pytest via uv in examples/python (needs cloud merge)"
	@echo "  make esp-image  Build FAT ESP image under build/ (needs cloud merge)"
	@echo "  make qemu       Boot ESP image with QEMU+OVMF (needs cloud merge + qemu/ovmf)"
	@echo "  make clean      Remove build/ and downloaded Limine tree"
	@echo ""
	@echo "Until cloud/phase-0-2 merges fixtures + janusbootctl, validate/esp-image/qemu fail by design."
	@echo "Never write ESP images to a real disk with dd. See docs/qemu.md."

deps: check-host limine
	@echo "deps: OK (Limine $(LIMINE_TAG) → $(LIMINE_EFI))"

check-host:
	@missing=0; \
	if ! command -v $(QEMU) >/dev/null 2>&1; then \
	  echo "MISSING: $(QEMU)  (Mint/Ubuntu: sudo apt install qemu-system-x86)"; \
	  missing=1; \
	else \
	  echo "FOUND:   $(QEMU) ($$($(QEMU) --version | head -1))"; \
	fi; \
	if [ -z "$(OVMF_CODE)" ] || [ ! -f "$(OVMF_CODE)" ]; then \
	  echo "MISSING: OVMF_CODE  (Mint/Ubuntu: sudo apt install ovmf)"; \
	  echo "         expected e.g. /usr/share/OVMF/OVMF_CODE_4M.fd"; \
	  missing=1; \
	else \
	  echo "FOUND:   OVMF_CODE=$(OVMF_CODE)"; \
	fi; \
	if [ -z "$(OVMF_VARS)" ] || [ ! -f "$(OVMF_VARS)" ]; then \
	  echo "MISSING: OVMF_VARS  (same ovmf package; e.g. /usr/share/OVMF/OVMF_VARS_4M.fd)"; \
	  missing=1; \
	else \
	  echo "FOUND:   OVMF_VARS=$(OVMF_VARS)"; \
	fi; \
	if [ -z "$(MKFS_FAT)" ] || [ ! -x "$(MKFS_FAT)" ]; then \
	  echo "MISSING: mkfs.fat  (sudo apt install dosfstools)"; \
	  missing=1; \
	else \
	  echo "FOUND:   mkfs.fat=$(MKFS_FAT)"; \
	fi; \
	if ! command -v $(MCOPY) >/dev/null 2>&1; then \
	  echo "MISSING: mcopy  (sudo apt install mtools)"; \
	  missing=1; \
	else \
	  echo "FOUND:   mcopy"; \
	fi; \
	if ! command -v $(MMD) >/dev/null 2>&1; then \
	  echo "MISSING: mmd  (sudo apt install mtools)"; \
	  missing=1; \
	else \
	  echo "FOUND:   mmd"; \
	fi; \
	if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then \
	  echo "MISSING: curl or wget (needed to download Limine)"; \
	  missing=1; \
	fi; \
	if ! command -v $(UV) >/dev/null 2>&1; then \
	  echo "WARN:    uv not on PATH (validate/test wrappers need it after cloud merge)"; \
	else \
	  echo "FOUND:   uv"; \
	fi; \
	if [ ! -d "$(FIXTURES_ESP)/EFI/JanusBoot" ]; then \
	  echo "PENDING: fixtures/esp (cloud lane — merge cloud/phase-0-2 before esp-image)"; \
	fi; \
	if [ ! -d "$(PYTHON_DIR)/src/janusbootctl" ]; then \
	  echo "PENDING: janusbootctl under examples/python (cloud lane)"; \
	fi; \
	if [ "$$missing" -ne 0 ]; then \
	  echo ""; \
	  echo "Host packages incomplete. Install steps: docs/qemu.md"; \
	  echo "Limine download can still proceed (make limine)."; \
	  exit 0; \
	fi

limine: $(LIMINE_STAMP)

$(LIMINE_STAMP):
	@mkdir -p "$(LIMINE_DIR)" "$(BUILD)"
	@echo "Downloading Limine $(LIMINE_TAG) binary release…"
	@tmp="$(BUILD)/$(LIMINE_ARCHIVE)"; \
	if command -v curl >/dev/null 2>&1; then \
	  curl -fsSL -o "$$tmp" "$(LIMINE_URL)"; \
	else \
	  wget -q -O "$$tmp" "$(LIMINE_URL)"; \
	fi; \
	tar -xJf "$$tmp" -C "$(BUILD)"; \
	src="$(BUILD)/limine-binary/BOOTX64.EFI"; \
	if [ ! -f "$$src" ]; then \
	  echo "ERROR: BOOTX64.EFI missing from Limine archive"; \
	  exit 1; \
	fi; \
	cp -f "$$src" "$(LIMINE_EFI)"; \
	cp -f "$(BUILD)/limine-binary/LICENSE" "$(LIMINE_DIR)/LICENSE" 2>/dev/null || true; \
	touch "$(LIMINE_STAMP)"; \
	echo "Installed $(LIMINE_EFI)"

_require-cloud:
	@if [ ! -f "$(FIXTURES_ESP)/EFI/JanusBoot/settings.json" ] || \
	   [ ! -f "$(FIXTURES_ESP)/EFI/JanusBoot/entries.json" ]; then \
	  echo "BLOCKED: fixtures/esp/EFI/JanusBoot/{settings,entries}.json not on this branch."; \
	  echo "Merge cloud/phase-0-2 into local/phase-0-2 (integrate-pr), then re-run."; \
	  echo "Do not copy from cloud/* yourself in this lane."; \
	  exit 1; \
	fi
	@if [ ! -d "$(PYTHON_DIR)/src/janusbootctl" ]; then \
	  echo "BLOCKED: examples/python/src/janusbootctl missing."; \
	  echo "Merge cloud/phase-0-2 (CLI + uv.lock), then re-run."; \
	  exit 1; \
	fi
	@if ! (cd "$(PYTHON_DIR)" && $(UV) run janusbootctl --help >/dev/null 2>&1); then \
	  echo "BLOCKED: janusbootctl not runnable via 'uv run janusbootctl' in examples/python."; \
	  echo "Merge cloud/phase-0-2 (CLI + uv.lock), then re-run."; \
	  exit 1; \
	fi

_require-fat-tools:
	@if [ -z "$(MKFS_FAT)" ] || [ ! -x "$(MKFS_FAT)" ]; then \
	  echo "ERROR: mkfs.fat required (apt install dosfstools)"; exit 1; \
	fi
	@command -v $(MCOPY) >/dev/null || { echo "ERROR: mcopy required (apt install mtools)"; exit 1; }
	@command -v $(MMD) >/dev/null || { echo "ERROR: mmd required (apt install mtools)"; exit 1; }

_require-qemu:
	@command -v $(QEMU) >/dev/null || { \
	  echo "ERROR: $(QEMU) not installed (apt install qemu-system-x86)"; exit 1; }

_require-ovmf:
	@if [ -z "$(OVMF_CODE)" ] || [ ! -f "$(OVMF_CODE)" ]; then \
	  echo "ERROR: OVMF_CODE not found (apt install ovmf)"; exit 1; \
	fi
	@if [ -z "$(OVMF_VARS)" ] || [ ! -f "$(OVMF_VARS)" ]; then \
	  echo "ERROR: OVMF_VARS not found (apt install ovmf)"; exit 1; \
	fi

# janusbootctl uses --esp (default: repo fixtures/esp) and subcommands without extra paths.
validate: _require-cloud
	@cd "$(PYTHON_DIR)" && $(UV) run janusbootctl --esp "../../$(FIXTURES_ESP)" validate

test:
	@if [ ! -f "$(PYTHON_DIR)/pyproject.toml" ]; then \
	  echo "ERROR: examples/python missing"; exit 1; \
	fi
	@if [ ! -d "$(PYTHON_DIR)/src/janusbootctl" ]; then \
	  echo "BLOCKED: janusbootctl tests need cloud merge (examples/python/src/janusbootctl)."; \
	  exit 1; \
	fi
	@cd "$(PYTHON_DIR)" && $(UV) run pytest

esp-image: limine _require-cloud _require-fat-tools
	@mkdir -p "$(BUILD)"
	@echo "Generating limine.conf from fixtures…"
	@cd "$(PYTHON_DIR)" && $(UV) run janusbootctl --esp "../../$(FIXTURES_ESP)" \
		generate-limine -o "../../$(LIMINE_CONF)"
	@echo "Creating FAT ESP image $(ESP_IMG) ($(ESP_SIZE_MIB) MiB)…"
	@rm -f "$(ESP_IMG)"
	@truncate -s "$(ESP_SIZE_MIB)M" "$(ESP_IMG)"
	@"$(MKFS_FAT)" -F 32 -n JANUSBOOT "$(ESP_IMG)" >/dev/null
	@export MTOOLS_SKIP_CHECK=1; \
	$(MMD) -i "$(ESP_IMG)" ::/EFI; \
	$(MMD) -i "$(ESP_IMG)" ::/EFI/BOOT; \
	$(MMD) -i "$(ESP_IMG)" ::/EFI/JanusBoot; \
	$(MCOPY) -i "$(ESP_IMG)" "$(LIMINE_EFI)" ::/EFI/BOOT/BOOTX64.EFI; \
	$(MCOPY) -i "$(ESP_IMG)" "$(LIMINE_CONF)" ::/limine.conf; \
	$(MCOPY) -i "$(ESP_IMG)" -s "$(FIXTURES_ESP)/EFI/JanusBoot/"* ::/EFI/JanusBoot/
	@echo "Wrote $(ESP_IMG)"
	@echo "NOTE: Never dd this image onto a real disk. QEMU only — see docs/qemu.md."

qemu: esp-image _require-qemu _require-ovmf
	@mkdir -p "$(BUILD)"
	@cp -f "$(OVMF_VARS)" "$(OVMF_VARS_COPY)"
	@echo "Starting QEMU (UEFI). Close the window or Ctrl-C to stop."
	@echo "OVMF_CODE=$(OVMF_CODE)"
	@$(QEMU) \
		-machine q35,accel=tcg \
		-m 512 \
		-drive if=pflash,format=raw,readonly=on,file="$(OVMF_CODE)" \
		-drive if=pflash,format=raw,file="$(OVMF_VARS_COPY)" \
		-drive if=virtio,format=raw,file="$(ESP_IMG)" \
		-net none \
		-display gtk \
		-serial stdio

clean:
	@rm -rf "$(BUILD)" "$(LIMINE_DIR)"
	@echo "Cleaned build/ and third_party/limine/"
