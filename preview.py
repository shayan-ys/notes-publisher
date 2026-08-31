"""Wrap a body fragment with the production templates and write it to a
local file so the page can be visually verified before publishing.

Prints the file:// URL on stdout — feed it to Playwright (MCP or otherwise)
to load the wrapped page exactly as the worker would render it. Catches
the failure mode where a missing </style> or a `<!doctype html>` outer
wrapper collapses the entire body into raw-text CSS.
"""
import argparse
import pathlib
import secrets
import sys

from notes_publish.templates import wrap_body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("body", type=pathlib.Path, help="Path to body fragment HTML.")
    ap.add_argument("--title", required=True, help="Page title (same one you'll pass to publish).")
    ap.add_argument(
        "--out",
        type=pathlib.Path,
        default=None,
        help="Output path. Default: /tmp/notes-preview-<rand>.html",
    )
    args = ap.parse_args()

    body = args.body.read_text(encoding="utf-8")
    wrapped = wrap_body(body, title=args.title)

    out = args.out or pathlib.Path(f"/tmp/notes-preview-{secrets.token_urlsafe(6)}.html")
    out.write_text(wrapped, encoding="utf-8")
    print(out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
