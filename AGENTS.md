# notes-publisher — AGENTS.md

Publishes HTML to a **content repo** that Cloudflare serves as static assets
(Workers Static Assets — `wrangler.jsonc` with `assets.directory`). See the
README for the user-facing overview. This file is guidance for coding agents
working on the pipeline — especially the deploy/caching pitfalls that are easy
to get wrong and hard to debug.

## Deploy model

`publish.py` writes a page into the content repo and `git push`es. Deployment
is triggered by that push (Cloudflare git integration) — there is no
`wrangler deploy` in the tool's happy path. A manual `wrangler deploy` from a
content-repo clone works too, but see the leak warning below.

## `.assetsignore` is load-bearing — keep it committed

**Mental model:** `.gitignore` and `.assetsignore` are *orthogonal* controls.
`.gitignore` decides what lives in the git repo; `.assetsignore` decides what
wrangler uploads as public files. A file can (and often should) be **committed
to git yet excluded from the public deploy** — that combination is exactly what
the ledger needs (see below).

`wrangler`'s Static Assets uploader ships **the entire assets directory** as
public files, including dotfiles. With `assets.directory: "./"` (repo root),
a bare `wrangler deploy` from a working clone will upload `.git/` (the whole
history — every "unguessable" slug becomes trivially enumerable), plus any
tooling dirs (`.wrangler/`, editor configs) and tracked state files.

The guard is a committed **`.assetsignore`** at the assets-directory root
(gitignore syntax). It must list at least:

```
.git
.wrangler
node_modules
wrangler.jsonc
.gitignore
.assetsignore
# ...plus any local state files (see below)
```

Commit it so it protects **both** manual deploys and the CI/git-integration
build. Debugging tips:

- `✨ Read N files from the assets directory` is the **raw walk count
  (pre-filter)** — NOT the upload set. It does not change when `.assetsignore`
  works. Do not use it to judge whether ignores apply.
- To confirm what's actually excluded, run with `WRANGLER_LOG=debug` and grep
  for `Ignoring asset:` lines.
- Fallback if you must deploy without a working `.assetsignore`: deploy from a
  clean export, not the live clone — `git archive HEAD | tar -x -C <tmp>` gives
  tracked files only (no `.git/`), then strip any state files and
  `wrangler deploy` from there.

## The ledger is committed content (a reader indexes it)

The ledger (`.ledger.json`, slug → entry) is the index a companion dashboard
like [notes-dash](https://github.com/shayan-ys/notes-dash) reads to render the
archive. That reader clones the **content repo** and expects the ledger *in it*,
so the ledger must be committed there — `commit_and_push`'s `git add -A` picks it
up automatically as long as it is **not** `.gitignore`d. Do **not** gitignore it.

But keep it out of the **public deploy**: the ledger lists every "unguessable"
slug, so serving it publicly (`<site>/.ledger.json`) makes all slugs enumerable
and defeats the unguessable-URL privacy model. So the rule is two-sided:

- **Committed to git** (not `.gitignore`d) → the dashboard's clone can read it.
- **`.assetsignore`d** → the public site never serves it.

Keep the content repo private on top of that. (Only remove it from
`.assetsignore` if your slugs aren't meant to be private at all.)

(Historically this doc said "never commit the ledger." That broke the dashboard
on 2026-07-02 — see the incident note in `Tools/AGENTS.md`.)

## Edge caching is the #1 "my change isn't live" gotcha

Cloudflare edge-caches asset responses. Symptoms that are almost always cache,
not a failed deploy:

- A republished page still shows old content minutes after the push.
- A file removed from the deploy still returns `200` even though origin `404`s.

Key facts:

- **Verify origin vs edge** by appending a unique query string
  (`?cb=<random>`) — that bypasses the URL-keyed edge cache and shows what
  origin actually serves right now.
- Cloudflare **combines the header sets of every `_headers` rule that matches a
  path**, so a `Cache-Control` on a broad rule concatenates onto more specific
  ones and can produce contradictory values (`max-age=… , no-store`). Keep
  `Cache-Control` in **exactly one** rule. For a private, unindexed site the
  simplest correct setup is a single `/*` rule carrying the security headers
  **and** `Cache-Control: no-store` — nothing benefits from edge caching, and
  no-store gives instant republish and no stale/cached-leak window.
- A path that matches only `/*` (e.g. a slug page `/<slug>/` or a dotfile) with
  no `Cache-Control` gets Cloudflare's **default** edge caching. That is how a
  leaked file can keep being served from the edge after origin is fixed —
  purge the zone cache to close it.

## Two publish surfaces — don't cross them

- **Body-fragment notes** go through `publish.py`, which wraps the fragment in
  the editorial `<head>`/footer (`wrap_body`).
- **Full standalone HTML pages/apps** (their own `<!doctype html>`) are edited
  in place in the content repo and deployed as-is. Do **not** run these through
  `publish.py` — it would nest them inside the wrapper and break the page.
