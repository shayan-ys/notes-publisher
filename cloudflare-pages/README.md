# cloudflare-pages/

Example config files for serving a notes-publisher content repo via
Cloudflare Pages. **These files live in your CONTENT repo, not in this
notes-publisher checkout** — they're shipped here as a reference.

## Setup

1. In Cloudflare → Pages, create a new project connected to your content
   repo (the one notes-publisher pushes to).
   - **Build command:** none (the repo IS the static site).
   - **Build output directory:** `/` (repo root).
2. Copy `_headers` and `robots.txt` from this directory into the root of
   your content repo.
3. Commit + push. Cloudflare auto-deploys.
4. Add your custom domain in **Pages → Settings → Custom domains**. Match
   the value you set for `NOTES_DOMAIN` in notes-publisher's `.env`.

## What these files do

- **`_headers`** — Cloudflare Pages headers config. Sends
  `X-Frame-Options: DENY` (no iframe embedding), `Referrer-Policy: no-referrer`
  (no Referer header leaking the URL to outbound links), and
  `Cache-Control: no-store` (no edge caching of the URL contents). Together
  with `<meta name="robots">` in the page itself this is the full
  "URL-obscurity" stack notes-publisher's privacy model assumes.

- **`robots.txt`** — `User-agent: * / Disallow: /`. Belt-and-braces with the
  `<meta name="robots">` already in the page. Well-behaved crawlers (Google,
  Bing, Common Crawl) honour both; misbehaving ones honour neither — that's
  why slug entropy is the real defense, not these headers.

## What's NOT in this directory

- **Cache-purge integration.** notes-publisher's `unpublish.py` removes the
  page and pushes; Cloudflare's edge cache may serve the old page for up to
  the configured TTL (no `purge_cache` call is made). If you need
  immediate-eviction, wire a Cloudflare API call into your own post-publish
  hook — the package keeps this concern out of the core flow.

- **Auth.** There is none, by design. See the parent README's "Privacy
  model" section.
