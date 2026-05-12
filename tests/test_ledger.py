"""Tests for the .ledger.json read/write helpers."""
import json
from pathlib import Path

import pytest

from notes_publish.ledger import (
    add_or_update_entry,
    list_entries,
    load_ledger,
    remove_entry,
    save_ledger,
)


def test_load_empty_ledger(tmp_path: Path):
    p = tmp_path / ".ledger.json"
    p.write_text("{}\n")
    assert load_ledger(p) == {}


def test_load_missing_ledger_returns_empty(tmp_path: Path):
    p = tmp_path / "missing.json"
    assert load_ledger(p) == {}


def test_save_then_load_roundtrip(tmp_path: Path):
    p = tmp_path / ".ledger.json"
    save_ledger(p, {"abc": {"title": "x", "created": "2026-05-09T10:00:00Z", "updated": "2026-05-09T10:00:00Z"}})
    assert load_ledger(p) == {"abc": {"title": "x", "created": "2026-05-09T10:00:00Z", "updated": "2026-05-09T10:00:00Z"}}


def test_save_is_pretty_printed(tmp_path: Path):
    p = tmp_path / ".ledger.json"
    save_ledger(p, {"abc": {"title": "x", "created": "t", "updated": "t"}})
    text = p.read_text()
    assert "\n" in text  # not a single line
    assert text.endswith("\n")


def test_add_new_entry_sets_created_and_updated(tmp_path: Path):
    p = tmp_path / ".ledger.json"
    p.write_text("{}\n")
    add_or_update_entry(p, slug="abc", title="Trip", now="2026-05-09T10:00:00Z")
    data = load_ledger(p)
    assert data["abc"] == {
        "title": "Trip",
        "created": "2026-05-09T10:00:00Z",
        "updated": "2026-05-09T10:00:00Z",
    }


def test_update_existing_entry_preserves_created(tmp_path: Path):
    p = tmp_path / ".ledger.json"
    p.write_text(json.dumps({"abc": {"title": "old", "created": "2026-01-01T00:00:00Z", "updated": "2026-01-01T00:00:00Z"}}))
    add_or_update_entry(p, slug="abc", title="new", now="2026-05-09T10:00:00Z")
    data = load_ledger(p)
    assert data["abc"]["created"] == "2026-01-01T00:00:00Z"
    assert data["abc"]["updated"] == "2026-05-09T10:00:00Z"
    assert data["abc"]["title"] == "new"


def test_remove_entry(tmp_path: Path):
    p = tmp_path / ".ledger.json"
    p.write_text(json.dumps({"abc": {"title": "x", "created": "t", "updated": "t"}, "def": {"title": "y", "created": "t", "updated": "t"}}))
    remove_entry(p, slug="abc")
    assert load_ledger(p) == {"def": {"title": "y", "created": "t", "updated": "t"}}


def test_remove_missing_slug_raises(tmp_path: Path):
    p = tmp_path / ".ledger.json"
    p.write_text("{}\n")
    with pytest.raises(KeyError):
        remove_entry(p, slug="abc")


def test_list_entries_sorted_by_updated_desc(tmp_path: Path):
    p = tmp_path / ".ledger.json"
    p.write_text(json.dumps({
        "old": {"title": "Old", "created": "2026-01-01T00:00:00Z", "updated": "2026-01-01T00:00:00Z"},
        "new": {"title": "New", "created": "2026-05-01T00:00:00Z", "updated": "2026-05-01T00:00:00Z"},
        "mid": {"title": "Mid", "created": "2026-03-01T00:00:00Z", "updated": "2026-03-01T00:00:00Z"},
    }))
    entries = list_entries(p)
    assert [e["slug"] for e in entries] == ["new", "mid", "old"]
