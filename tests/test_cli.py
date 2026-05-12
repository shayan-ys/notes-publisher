"""Integration tests for publish.py / unpublish.py CLIs."""
import json
import re
import sys
from pathlib import Path

import pytest

import notes_publish.gitops as gitops_module
from notes_publish import config


@pytest.fixture
def fake_repo(tmp_path: Path, monkeypatch):
    """Point config.REPO_DIR/LEDGER_PATH at a temp fake repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".ledger.json").write_text("{}\n")
    (repo / ".git").mkdir()  # so ensure_repo thinks it's already cloned
    monkeypatch.setattr(config, "REPO_DIR", repo)
    monkeypatch.setattr(config, "LEDGER_PATH", repo / ".ledger.json")
    return repo


@pytest.fixture
def fake_gitops(monkeypatch):
    """Replace commit_and_push and ensure_repo with no-ops that record calls."""
    calls = []

    def fake_commit(repo_dir, *, message, runner=None):
        calls.append(("commit_and_push", repo_dir, message))

    def fake_ensure(repo_dir, *, remote_url, runner=None):
        calls.append(("ensure_repo", repo_dir, remote_url))

    monkeypatch.setattr(gitops_module, "commit_and_push", fake_commit)
    monkeypatch.setattr(gitops_module, "ensure_repo", fake_ensure)
    return calls


def test_publish_writes_index_html_at_slug(fake_repo, fake_gitops, tmp_path, capsys):
    body_file = tmp_path / "body.html"
    body_file.write_text("<h1>Trip</h1>")

    from publish import main
    rc = main(["--title", "Trip to Elora", str(body_file)])
    assert rc == 0

    # Find the slug folder
    slug_dirs = [p for p in fake_repo.iterdir() if p.is_dir() and p.name not in {".git"}]
    assert len(slug_dirs) == 1
    slug_dir = slug_dirs[0]
    assert re.match(r"^[A-Za-z0-9_-]{22}$", slug_dir.name)

    page = slug_dir / "index.html"
    assert page.exists()
    text = page.read_text()
    assert "<h1>Trip</h1>" in text
    assert "<title>Trip to Elora</title>" in text
    assert 'name="robots"' in text


def test_publish_updates_ledger(fake_repo, fake_gitops, tmp_path):
    body_file = tmp_path / "body.html"
    body_file.write_text("<p>x</p>")

    from publish import main
    main(["--title", "Hello", str(body_file)])

    ledger = json.loads((fake_repo / ".ledger.json").read_text())
    assert len(ledger) == 1
    slug, entry = next(iter(ledger.items()))
    assert entry["title"] == "Hello"
    assert entry["created"] == entry["updated"]
    assert re.match(r"^\d{4}-\d{2}-\d{2}T", entry["created"])  # ISO 8601


def test_publish_prints_full_url(fake_repo, fake_gitops, tmp_path, capsys):
    body_file = tmp_path / "body.html"
    body_file.write_text("<p>x</p>")

    from publish import main
    main(["--title", "Hello", str(body_file)])
    out = capsys.readouterr().out.strip()
    assert out.startswith(f"{config.NOTES_BASE_URL}/")
    assert out.endswith("/")


def test_publish_calls_git_commit_and_push(fake_repo, fake_gitops, tmp_path):
    body_file = tmp_path / "body.html"
    body_file.write_text("<p>x</p>")

    from publish import main
    main(["--title", "Hello", str(body_file)])

    op_names = [c[0] for c in fake_gitops]
    assert "commit_and_push" in op_names


def test_publish_with_existing_slug_overwrites(fake_repo, fake_gitops, tmp_path):
    body_file = tmp_path / "body.html"
    body_file.write_text("<p>v1</p>")

    from publish import main
    main(["--title", "Hello", "--slug", "fixed_slug_22_chars_aaa", str(body_file)])

    body_file.write_text("<p>v2</p>")
    main(["--title", "Hello v2", "--slug", "fixed_slug_22_chars_aaa", str(body_file)])

    page = fake_repo / "fixed_slug_22_chars_aaa" / "index.html"
    assert "<p>v2</p>" in page.read_text()
    assert "<title>Hello v2</title>" in page.read_text()

    ledger = json.loads((fake_repo / ".ledger.json").read_text())
    assert ledger["fixed_slug_22_chars_aaa"]["title"] == "Hello v2"
    # created should be preserved across overwrite
    assert ledger["fixed_slug_22_chars_aaa"]["created"] != ledger["fixed_slug_22_chars_aaa"]["updated"]


def test_list_prints_table(fake_repo, capsys):
    (fake_repo / ".ledger.json").write_text(json.dumps({
        "abc": {"title": "Trip", "created": "2026-05-01T10:00:00Z", "updated": "2026-05-01T10:00:00Z"},
        "def": {"title": "Recipe", "created": "2026-05-02T10:00:00Z", "updated": "2026-05-02T10:00:00Z"},
    }))

    from list import main as list_main
    rc = list_main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Trip" in out
    assert "Recipe" in out
    assert "abc" in out
    assert "def" in out
    # Most-recent first
    assert out.index("Recipe") < out.index("Trip")


def test_list_empty(fake_repo, capsys):
    from list import main as list_main
    rc = list_main([])
    assert rc == 0
    out = capsys.readouterr().out.lower()
    assert "no published pages" in out or "0 pages" in out or "(empty)" in out


def test_unpublish_removes_folder_and_ledger_entry(fake_repo, fake_gitops, monkeypatch):
    # Seed: one published page
    slug = "test_slug_22_chars_xyz"
    page_dir = fake_repo / slug
    page_dir.mkdir()
    (page_dir / "index.html").write_text("<html></html>")
    (fake_repo / ".ledger.json").write_text(json.dumps({
        slug: {"title": "Trip", "created": "2026-05-01T10:00:00Z", "updated": "2026-05-01T10:00:00Z"}
    }))

    # Ensure no HTTP call to api.cloudflare.com is made
    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: pytest.fail("urlopen called — CF purge must not happen"))

    from unpublish import main
    rc = main(["--slug", slug])
    assert rc == 0

    assert not page_dir.exists()
    ledger = json.loads((fake_repo / ".ledger.json").read_text())
    assert slug not in ledger


def test_unpublish_unknown_slug_returns_error(fake_repo, fake_gitops, monkeypatch, capsys):
    from unpublish import main
    rc = main(["--slug", "nonexistent_slug_22cha"])
    assert rc != 0
    assert "not found" in capsys.readouterr().err.lower()
