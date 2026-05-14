# notes-publisher

Publish HTML bodies to a static-site repo as unguessable 22-char URLs.
Pairs with [notes-dash](https://github.com/shayan-ys/notes-dash) for an index
and live search.

A small, opinionated Python CLI for the "share a writeup by private link"
workflow — the kind where you want to send one person a real URL without
making it public, indexable, or guessable, but you also don't want to set
up auth, accounts, or a database. URL-obscurity, honestly named.

- **Three commands.** `publish.py` writes a new page and pushes. `list.py`
  prints the ledger. `unpublish.py` removes a page and pushes.
- **22 chars of base64url entropy** per slug (~128 bits). Regenerates on the
  rare chance the slug starts with `-` or `_` so argparse never misreads it
  as a flag.
- **Cloudflare Pages / Workers friendly.** Push to your content repo; CF
  redeploys. An example `cloudflare-pages/` config is included.
- **A minimal wrapping `<head>`** with `noindex,nofollow` and
  `no-referrer`. No footer or disclaimer — the body fragment owns
  everything between `<body>` tags.
- **Python 3.12, stdlib + `pytest` only.** Zero runtime deps. ~400 LOC
  including tests.

## Privacy model — read this before pitching it as "private"

The privacy here is **URL-obscurity, not access control**.

- The slug is 22 chars of base64url (~128 bits of entropy) — not crawlable,
  not guessable.
- The wrapper sends `<meta name="robots" content="noindex,nofollow">` and
  `<meta name="referrer" content="no-referrer">`. The included `_headers`
  config adds `X-Frame-Options: DENY` and `Cache-Control: no-store`.
- `robots.txt: Disallow: /` keeps the whole site out of search engines.
- The page itself shows a footer warning that any messaging platform the
  link travels through can see the URL — i.e. **don't share anything you
  wouldn't put directly in that DM**.

What this does **not** defend against:

- Anyone with the link can read the page. There is no auth.
- If the recipient forwards the link, the new recipient can read it.
- If a messenger logs URLs (Slack, iMessage previews, email scanning),
  those systems hold the keys.

Don't oversell the privacy. It's "a private link," not "encryption."

## Install

```bash
git clone https://github.com/shayan-ys/notes-publisher
cd notes-publisher
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
```

## Setup

1. **Create a content repo** on GitHub (private is fine). This is where
   `publish.py` pushes the rendered pages. The repo only needs to contain a
   `.ledger.json` at the root, which the package manages.

2. **Clone it into `.pipeline/repo/`** inside the notes-publisher checkout:

   ```bash
   mkdir -p .pipeline
   git clone git@github.com:you/your-notes-content.git .pipeline/repo
   ```

3. **Copy `.env.example` to `.env`** and fill in:

   ```bash
   cp .env.example .env
   $EDITOR .env
   # NOTES_DOMAIN=notes.example.com
   # NOTES_CONTENT_REPO=git@github.com:you/your-notes-content.git
   ```

4. **Deploy your content repo.** See `cloudflare-pages/` for an example —
   the `_headers` / `robots.txt` combo keeps the site out of search engines
   and adds the security headers `publish.py` assumes are present.

## Usage

```bash
# Publish a body file with a title — prints the URL on the last line of stdout
set -a && source .env && set +a
python publish.py /tmp/body.html --title "Trip to Elora"
# → https://notes.example.com/<22-char-slug>/

# List
python list.py

# Unpublish (use --slug=<value> if the slug starts with '-' or '_')
python unpublish.py --slug=<slug>
```

### The body file is HTML body content, not a full document

The `<body-file>` argument is the inner HTML — what goes *inside* `<body>`.
The package's `wrap_body()` adds the doctype, `<html>`, `<head>` (with
title, viewport, robots noindex, no-referrer meta, baseline CSS), and
the `<body>` open/close.

The wrapper's baseline CSS is intentionally thin — any `<style>` block in
the body overrides it via source-order specificity.

Good:

```html
<h1>Trip to Elora</h1>
<p>We'll head out Saturday morning, stop in Guelph for coffee, then aim for the gorge by 11.</p>
```

Bad (produces nested `<html>` / double titles):

```html
<!doctype html>
<html><head><title>Trip</title></head><body><h1>...</h1></body></html>
```

### Optional: paired with notes-dash

[notes-dash](https://github.com/shayan-ys/notes-dash) is a tiny single-page
dashboard that reads the same `.ledger.json` and renders an index with live
search. Point its `NOTES_REPO_SLUG` env var at the same content repo and
you've got both halves of the pipeline. Either tool works without the
other.

## The `.ledger.json` schema (the contract between this tool and any reader)

The ledger is a flat dict, slug → entry, JSON-encoded with `indent=2` and
keys sorted. Each entry has exactly these fields:

```json
{
  "ABc12dEF34GHi56JKl78Mn": {
    "title": "Trip to Elora",
    "created": "2026-05-09T14:23:11.456Z",
    "updated": "2026-05-12T09:01:33.012Z"
  }
}
```

- `title`: plain string, used in `<title>` and (in notes-dash) the index row.
- `created`: ISO 8601 UTC, set on first publish, **preserved on re-publish**.
- `updated`: ISO 8601 UTC, set on every publish.

Slugs are 22 chars of `[A-Za-z0-9_-]`. The first character is always
alphanumeric (a regen-on-clash guarantee) so the slug is safe to pass to
argparse positionally.

If you build your own dashboard / RSS feed / search index against this, the
schema is stable and won't change without a major version bump.

## Tests

```bash
pip install -e '.[dev]'
pytest -v
```

33 tests, all stdlib + pytest. They cover slug entropy + flag-safety,
ledger read/write, git wrapper command shapes, template wrapping (doctype,
meta tags, title escaping), and end-to-end CLI flow
through publish/list/unpublish with a fake repo.

## Companion projects

- [notes-dash](https://github.com/shayan-ys/notes-dash) — dashboard / index
  / search for a notes-publisher content repo. Python stdlib + git +
  `http.server`. Pairs cleanly via the `.ledger.json` schema above.

## License

MIT — see [LICENSE](./LICENSE).
