"""Shared fixtures for notes-publisher tests."""
import json
from pathlib import Path

import pytest


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """A temp dir that mimics the layout of the notes-publisher repo."""
    (tmp_path / ".ledger.json").write_text("{}\n")
    return tmp_path


@pytest.fixture
def sample_body() -> str:
    return "<h1>Hello</h1>\n<p>World.</p>\n"
