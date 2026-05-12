"""Constants for the notes-publisher pipeline.

`NOTES_DOMAIN` and `NOTES_CONTENT_REPO` are read from the environment so the
package can be reused for different sites without forking. Set them in a
`.env` / `.env.tpl` file (consumed by `op run` or a shell `set -a`) before
invoking the CLIs.
"""
import os
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_STATE = PIPELINE_ROOT / ".pipeline"
REPO_DIR = PIPELINE_STATE / "repo"
LEDGER_PATH = REPO_DIR / ".ledger.json"

NOTES_DOMAIN = os.environ.get("NOTES_DOMAIN", "notes.example.com")
NOTES_BASE_URL = f"https://{NOTES_DOMAIN}"

NOTES_CONTENT_REPO = os.environ.get("NOTES_CONTENT_REPO", "")

SLUG_BYTES = 16
