#!/usr/bin/env python3
"""unpublish.py — remove a slug and push."""
import argparse
import shutil
import sys

from notes_publish import config, gitops
from notes_publish.ledger import load_ledger, remove_entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Unpublish a slug from {config.NOTES_BASE_URL}/")
    parser.add_argument("--slug", required=True,
                        help="Slug to remove (use --slug=<value> if the slug starts with '-' or '_')")
    args = parser.parse_args(argv)

    repo = config.REPO_DIR
    page_dir = repo / args.slug

    ledger = load_ledger(config.LEDGER_PATH)
    if args.slug not in ledger:
        print(f"error: slug {args.slug!r} not found in ledger", file=sys.stderr)
        return 2

    if page_dir.exists():
        shutil.rmtree(page_dir)
    remove_entry(config.LEDGER_PATH, slug=args.slug)
    gitops.commit_and_push(repo, message=f"unpublish {args.slug}")

    print(f"unpublished {args.slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
