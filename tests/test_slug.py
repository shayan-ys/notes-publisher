"""Tests for slug generation."""
import re

from notes_publish.slug import generate_slug


def test_slug_is_22_chars():
    assert len(generate_slug()) == 22


def test_slug_is_base64url_safe():
    # base64url alphabet: A-Z a-z 0-9 - _
    pattern = re.compile(r"^[A-Za-z0-9_-]{22}$")
    for _ in range(50):
        assert pattern.match(generate_slug())


def test_slug_never_starts_with_dash_or_underscore():
    # Leading '-' or '_' causes argparse to treat the slug as a flag.
    for _ in range(200):
        slug = generate_slug()
        assert slug[0] not in ("-", "_"), f"slug {slug!r} starts with a flag-like character"


def test_slugs_are_unique():
    slugs = {generate_slug() for _ in range(1000)}
    assert len(slugs) == 1000
