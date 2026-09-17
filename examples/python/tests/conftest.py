"""Shared pytest helpers for janusbootctl."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from janusbootctl.paths import repo_root


@pytest.fixture
def repo() -> Path:
    return repo_root()


@pytest.fixture
def esp_copy(tmp_path: Path, repo: Path) -> Path:
    """Writable copy of fixtures/esp for mutating tests."""
    src = repo / "fixtures" / "esp"
    dest = tmp_path / "esp"
    shutil.copytree(src, dest)
    return dest
