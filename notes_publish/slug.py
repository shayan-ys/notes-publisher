"""Generate unguessable slugs for published pages."""
import secrets

from notes_publish.config import SLUG_BYTES


def generate_slug() -> str:
    """Return a 22-char base64url string with 128 bits of entropy.

    Regenerates if the first character is '-' or '_', which would cause
    argparse to misinterpret the slug as a flag when passed positionally.
    Rejection probability is ~12.5% per attempt; entropy loss is negligible
    (~0.18 bits — still effectively 128-bit security).
    """
    while True:
        slug = secrets.token_urlsafe(SLUG_BYTES)
        if slug[0].isalnum():
            return slug
