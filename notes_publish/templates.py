"""Wrap Claude-authored body HTML in standard <head> and footer.

The wrapper is intentionally thin: a tiny baseline reset + a "skin" of
fallback typography that matches the notes-dash favicon palette, plus
required meta tags and the disclaimer footer. Anything the body's own
inline <style> defines wins via the cascade, so a frontend-designed
body can fully take over the page without fighting the wrapper.
"""
from html import escape

DISCLAIMER = (
    "This page is shared by unguessable URL. Search engines won't index it, "
    "but the link travels through whatever messaging platform you share it on "
    "— don't share anything you wouldn't put directly in that DM."
)


def wrap_body(body: str, *, title: str) -> str:
    """Return a complete HTML document wrapping `body`.

    The body may include its own <style> block; those rules will
    override the baseline below thanks to source-order specificity.
    """
    safe_title = escape(title, quote=False)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta name="referrer" content="no-referrer">
<meta name="color-scheme" content="light dark">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<title>{safe_title}</title>
<style>
  /* Fallback baseline — any <style> in the body overrides this. */
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    margin: 0;
    padding: clamp(1rem, 4vw, 2rem) clamp(1rem, 4vw, 1.5rem);
    font-family: ui-serif, Georgia, "Iowan Old Style", Cambria, serif;
    font-size: clamp(1rem, 0.95rem + 0.2vw, 1.0625rem);
    line-height: 1.6;
    color: #1a1410;
    background: #f3ece0;
    max-width: 70ch;
    margin-inline: auto;
    overflow-wrap: break-word;
  }}
  img, svg, video {{ max-width: 100%; height: auto; }}
  pre {{ overflow-x: auto; }}
  footer.notes-disclaimer {{
    margin-top: 4rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(26, 20, 16, 0.18);
    font-size: 0.8rem;
    line-height: 1.5;
    color: rgba(26, 20, 16, 0.55);
    font-family: ui-sans-serif, system-ui, sans-serif;
  }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #f3ece0; background: #1a1410; }}
    footer.notes-disclaimer {{
      border-top-color: rgba(243, 236, 224, 0.18);
      color: rgba(243, 236, 224, 0.55);
    }}
  }}
</style>
</head>
<body>
{body}
<footer class="notes-disclaimer">{DISCLAIMER}</footer>
</body>
</html>
"""
