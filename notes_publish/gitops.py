"""Thin wrappers around git, with an injectable runner for tests."""
import subprocess
from pathlib import Path
from typing import Callable, Protocol


class _Result(Protocol):
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[..., _Result]


class GitError(RuntimeError):
    """A git invocation returned a non-zero exit code."""


def _default_runner(args: list[str], *, cwd: Path | None = None, check: bool = False):
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


def _run(runner: Runner, args: list[str], cwd: Path | None) -> None:
    res = runner(args, cwd=cwd, check=False)
    if res.returncode != 0:
        raise GitError(f"{' '.join(args)} failed (rc={res.returncode}): {res.stderr.strip()}")


def ensure_repo(repo_dir: Path, *, remote_url: str, runner: Runner | None = None) -> None:
    """Clone if missing, otherwise pull latest from main."""
    runner = runner or _default_runner
    if (repo_dir / ".git").is_dir():
        _run(runner, ["git", "pull", "--rebase", "origin", "main"], cwd=repo_dir)
    else:
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        _run(runner, ["git", "clone", remote_url, str(repo_dir)], cwd=None)


def commit_and_push(repo_dir: Path, *, message: str, runner: Runner | None = None) -> None:
    """Stage everything, commit with message, push to origin/main."""
    runner = runner or _default_runner
    _run(runner, ["git", "add", "-A"], cwd=repo_dir)
    _run(runner, ["git", "commit", "-m", message], cwd=repo_dir)
    _run(runner, ["git", "push", "origin", "main"], cwd=repo_dir)
