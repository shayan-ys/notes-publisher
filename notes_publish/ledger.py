"""Read/write helpers for .ledger.json."""
import json
from pathlib import Path
from typing import Any


def load_ledger(path: Path) -> dict[str, dict[str, str]]:
    """Return the ledger dict, or {} if the file doesn't exist."""
    if not path.exists():
        return {}
    return json.loads(path.read_text() or "{}")


def save_ledger(path: Path, data: dict[str, dict[str, str]]) -> None:
    """Write ledger dict pretty-printed with trailing newline."""
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def add_or_update_entry(path: Path, *, slug: str, title: str, now: str) -> None:
    """Insert or update slug. Preserves `created` if already present."""
    data = load_ledger(path)
    existing = data.get(slug)
    created = existing["created"] if existing else now
    data[slug] = {"title": title, "created": created, "updated": now}
    save_ledger(path, data)


def remove_entry(path: Path, *, slug: str) -> None:
    """Remove slug from ledger. Raises KeyError if absent."""
    data = load_ledger(path)
    del data[slug]  # raises KeyError if missing — caller handles
    save_ledger(path, data)


def list_entries(path: Path) -> list[dict[str, Any]]:
    """Return entries sorted by `updated` descending, with slug attached."""
    data = load_ledger(path)
    entries = [{"slug": slug, **fields} for slug, fields in data.items()]
    entries.sort(key=lambda e: e["updated"], reverse=True)
    return entries
