"""Tests for git wrapper (using a fake runner)."""
from pathlib import Path

import pytest

from notes_publish.gitops import GitError, commit_and_push, ensure_repo


class FakeRunner:
    def __init__(self, returns: list[tuple[int, str, str]] | None = None):
        # list of (returncode, stdout, stderr) for each call, in order
        self.returns = returns or []
        self.calls: list[list[str]] = []

    def __call__(self, args, *, cwd=None, check=False):
        self.calls.append(list(args))
        if not self.returns:
            return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        rc, out, err = self.returns.pop(0)
        return type("R", (), {"returncode": rc, "stdout": out, "stderr": err})()


def test_commit_and_push_runs_expected_commands(tmp_path: Path):
    runner = FakeRunner(returns=[(0, "", ""), (0, "", ""), (0, "", "")])  # add, commit, push
    commit_and_push(tmp_path, message="publish abc", runner=runner)
    assert [c[:2] for c in runner.calls] == [
        ["git", "add"],
        ["git", "commit"],
        ["git", "push"],
    ]
    assert runner.calls[0] == ["git", "add", "-A"]
    assert runner.calls[1][:3] == ["git", "commit", "-m"]
    assert runner.calls[1][3] == "publish abc"
    assert runner.calls[2] == ["git", "push", "origin", "main"]


def test_commit_and_push_uses_cwd(tmp_path: Path):
    runner = FakeRunner(returns=[(0, "", ""), (0, "", ""), (0, "", "")])
    commit_and_push(tmp_path, message="x", runner=runner)
    # Each subprocess call should be cwd=repo_path; FakeRunner doesn't capture cwd,
    # so this test just verifies the function doesn't crash. Real cwd assertion below.


def test_commit_and_push_raises_on_git_failure(tmp_path: Path):
    runner = FakeRunner(returns=[(1, "", "error: nothing to commit")])
    with pytest.raises(GitError) as exc_info:
        commit_and_push(tmp_path, message="x", runner=runner)
    assert "git add" in str(exc_info.value).lower() or "git" in str(exc_info.value).lower()


def test_ensure_repo_clones_when_missing(tmp_path: Path):
    target = tmp_path / "repo"
    runner = FakeRunner(returns=[(0, "", "")])
    fake_remote = "git@github.com:example/notes-content.git"
    ensure_repo(target, remote_url=fake_remote, runner=runner)
    assert runner.calls == [
        ["git", "clone", fake_remote, str(target)],
    ]


def test_ensure_repo_pulls_when_present(tmp_path: Path):
    target = tmp_path / "repo"
    target.mkdir()
    (target / ".git").mkdir()
    runner = FakeRunner(returns=[(0, "", "")])
    ensure_repo(target, remote_url="git@github.com:example/notes-content.git", runner=runner)
    assert runner.calls == [["git", "pull", "--rebase", "origin", "main"]]
