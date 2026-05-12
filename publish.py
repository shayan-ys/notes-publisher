#!/usr/bin/env python3
"""publish.py — write a body file as a new (or existing) slug, commit, push."""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from notes_publish import config, gitops
from notes_publish.ledger import add_or_update_entry
from notes_publish.slug import generate_slug
from notes_publish.templates import wrap_body


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Publish an HTML body to {config.NOTES_BASE_URL}/")
    parser.add_argument("body", type=Path, help="Path to file containing the HTML <body> contents")
    parser.add_argument("--title", required=True, help="Page title")
    parser.add_argument("--slug", help="Use a specific slug (overwrites if exists). Default: random.")
    args = parser.parse_args(argv)

    body_html = args.body.read_text()
    slug = args.slug or generate_slug()

    repo = config.REPO_DIR
    if not repo.exists() or not (repo / ".git").is_dir():
        hint = config.NOTES_CONTENT_REPO or "<your content repo>"
        print(
            f"error: {repo} is not a git repo. Clone {hint} into that path first "
            f"(set NOTES_CONTENT_REPO in your .env to make this hint useful).",
            file=sys.stderr,
        )
        return 2

    page_dir = repo / slug
    page_dir.mkdir(exist_ok=True)
    (page_dir / "index.html").write_text(wrap_body(body_html, title=args.title))

    add_or_update_entry(config.LEDGER_PATH, slug=slug, title=args.title, now=_now_iso())

    gitops.commit_and_push(repo, message=f"publish {slug}: {args.title}")

    print(f"{config.NOTES_BASE_URL}/{slug}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
