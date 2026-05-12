#!/usr/bin/env python3
"""list.py — print the ledger as a table."""
import argparse
import sys

from notes_publish import config
from notes_publish.ledger import list_entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"List published pages on {config.NOTES_BASE_URL}/")
    parser.parse_args(argv)

    entries = list_entries(config.LEDGER_PATH)
    if not entries:
        print("(empty) no published pages")
        return 0

    # Compute column widths
    title_w = max(len(e["title"]) for e in entries)
    title_w = min(title_w, 50)
    print(f"{'updated':<20}  {'slug':<22}  title")
    print(f"{'-' * 20}  {'-' * 22}  {'-' * title_w}")
    for e in entries:
        title = e["title"][:title_w]
        print(f"{e['updated']:<20}  {e['slug']:<22}  {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
