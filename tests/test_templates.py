"""Tests for HTML wrapping."""
from notes_publish.templates import wrap_body


def test_wrap_includes_doctype_and_lang():
    out = wrap_body("<p>hi</p>", title="Trip")
    assert out.startswith("<!doctype html>")
    assert "<html lang=\"en\">" in out


def test_wrap_includes_required_meta_tags():
    out = wrap_body("<p>hi</p>", title="Trip")
    assert '<meta name="viewport"' in out
    assert '<meta name="robots" content="noindex,nofollow">' in out
    assert '<meta name="referrer" content="no-referrer">' in out
    assert '<meta charset="utf-8">' in out


def test_wrap_uses_title():
    out = wrap_body("<p>hi</p>", title="Trip to Elora")
    assert "<title>Trip to Elora</title>" in out


def test_wrap_escapes_title():
    out = wrap_body("<p>hi</p>", title="A & B <script>alert(1)</script>")
    assert "<title>A &amp; B &lt;script&gt;alert(1)&lt;/script&gt;</title>" in out


def test_wrap_inlines_body_unchanged():
    body = "<h1>Hello</h1>\n<p>World</p>"
    out = wrap_body(body, title="x")
    assert body in out


def test_wrap_omits_disclaimer_footer():
    out = wrap_body("<p>hi</p>", title="x")
    assert "<footer" not in out
    assert "messaging platform" not in out.lower()
