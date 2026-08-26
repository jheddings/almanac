"""The harness-test rig: scaffolding a run.

The rig reaches no verdicts, so there is nothing here about scoring. What it must get
right is producing a run that behaves the same wherever it is created.
"""

from __future__ import annotations

import subprocess

import pytest

from tools import skel


def _git(*args: str) -> str:
    """Run git with the scaffold's own scrubbed environment.

    The suite runs under `pre-commit`, and git exports `GIT_DIR` and `GIT_INDEX_FILE`
    into every hook. A bare `git -C <run>` here would read and write the repository
    being committed to instead of the run, which is the failure `clean_env` exists to
    prevent — so the assertions must not be making it themselves.
    """
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        env=skel.clean_env(),
        check=True,
    ).stdout.strip()


def _fixture(tmp_path):
    fixture = tmp_path / "fixture"
    (fixture / "src" / "skinner").mkdir(parents=True)
    (fixture / "src" / "skinner" / "__init__.py").write_text("")
    (fixture / "README.md").write_text("# fixture\n")
    return fixture


def test_new_run_is_a_standalone_repo(tmp_path):
    """Cloud platforms clone a repo; a subfolder copy cannot be pointed at."""
    run = skel.new_run(_fixture(tmp_path), tmp_path / "runs", "claude", "2026-08-24")

    assert run.name == "2026-08-24-claude"
    assert (run / ".git").is_dir()
    assert (run / "README.md").read_text() == "# fixture\n"
    subject = _git("-C", str(run), "log", "-1", "--format=%s")
    assert subject.startswith("chore: ")


def test_a_run_may_be_placed_outside_the_repository(tmp_path):
    """A run nested under this repo inherits its instruction files.

    A session started inside `runs/` reads every CLAUDE.md and AGENTS.md above it,
    including this repository's own — which names a different almanac. The trial would
    then meet two rule sets at once, so the destination has to be movable.
    """
    elsewhere = tmp_path / "somewhere-else"
    run = skel.new_run(_fixture(tmp_path), elsewhere, "claude", "2026-08-24")

    assert run.parent == elsewhere
    assert (run / ".git").is_dir()


def test_the_scaffold_commit_carries_its_own_identity(tmp_path):
    """A CI runner has no user.name, and neither does a fresh container.

    Asserting the author directly is what makes this hold everywhere. Emptying git's
    config files instead would not: on a host where git can derive an identity from the
    account and hostname the simulation passes while proving nothing, which is how this
    reached CI. See docs/almanac/.
    """
    run = skel.new_run(_fixture(tmp_path), tmp_path / "runs", "claude", "2026-08-24")
    author = _git("-C", str(run), "log", "-1", "--format=%an <%ae>")
    assert author == "skel <skel@example.com>"


def test_a_removed_worktrees_name_survives_only_in_the_hook_log(tmp_path):
    """The hook exists because git keeps nothing once a worktree is removed.

    This is the fact the corresponding almanac entry records, asserted against a real
    repository rather than assumed.
    """
    run = skel.new_run(_fixture(tmp_path), tmp_path / "runs", "claude", "2026-08-24")
    _git("-C", str(run), "worktree", "add", "-q", ".worktrees/bender", "-b",
         "feat/probe", "main")
    _git("-C", str(run), "worktree", "remove", ".worktrees/bender")

    assert not (run / ".git" / "worktrees").exists(), "git kept no record of its own"
    log = (run / ".git" / skel.WORKTREE_LOG).read_text()
    assert "bender" in log, "the hook is the only thing that remembers the name"


def test_a_run_ignores_the_git_environment_it_was_launched_in(tmp_path, monkeypatch):
    """A scaffold run from inside a git hook must not touch the enclosing repository.

    Git exports `GIT_DIR` and `GIT_INDEX_FILE` into every hook it runs, and `git -C`
    does not override them — the environment wins. Without scrubbing, `git add -A` here
    stages the run's files into the *outer* repository's index and marks everything
    else deleted, and the outer repo's `pre-commit` then runs against the run.
    """
    outer = tmp_path / "outer"
    outer.mkdir()
    identity = ("-c", "user.name=o", "-c", "user.email=o@e.com")
    _git("-C", str(outer), "init", "-q", "-b", "main")
    (outer / "kept.txt").write_text("outer\n")
    _git("-C", str(outer), *identity, "add", "-A")
    _git("-C", str(outer), *identity, "commit", "-q", "-m", "chore: outer")

    monkeypatch.setenv("GIT_DIR", str(outer / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(outer / ".git" / "index"))
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Somebody Else")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "else@example.com")

    run = skel.new_run(_fixture(tmp_path), tmp_path / "runs", "claude", "2026-08-24")

    dirty = _git("-C", str(outer), "status", "--porcelain")
    assert dirty == "", f"the scaffold reached into the enclosing repository: {dirty!r}"

    author = _git("-C", str(run), "log", "-1", "--format=%an <%ae>")
    assert author == "skel <skel@example.com>", author


def test_a_git_failure_says_what_git_said(tmp_path):
    """`check=True` alone raises with the exit status and discards the diagnosis."""
    not_a_repo = tmp_path / "bare"
    not_a_repo.mkdir()
    with pytest.raises(skel.SkelError) as failure:
        skel._git(not_a_repo, "log", "-1")
    assert "not a git repository" in str(failure.value).lower()
