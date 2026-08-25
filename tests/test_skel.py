"""The harness-test rig: scaffolding a run, and scoring one.

Every check here is a pure function over git facts, so the suite never shells out to a
harness and never needs a network.
"""

from __future__ import annotations

import subprocess

from tools import skel


def test_new_run_is_a_standalone_repo(tmp_path):
    """Cloud platforms clone a repo; a subfolder copy cannot be pointed at."""
    fixture = tmp_path / "fixture"
    (fixture / "src").mkdir(parents=True)
    (fixture / "README.md").write_text("# fixture\n")
    (fixture / "src" / "__init__.py").write_text("")

    run = skel.new_run(fixture, tmp_path / "runs", "claude", stamp="2026-08-24")

    assert run.name == "2026-08-24-claude"
    assert (run / ".git").is_dir()
    assert (run / "README.md").read_text() == "# fixture\n"
    head = subprocess.run(
        ["git", "-C", str(run), "log", "--format=%s"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert head.startswith("chore: ")


def test_new_run_installs_the_worktree_hook(tmp_path):
    """The name is unrecoverable after cleanup, so it is captured at creation."""
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "README.md").write_text("x\n")

    run = skel.new_run(fixture, tmp_path / "runs", "codex", stamp="2026-08-24")

    hook = run / ".git" / "hooks" / "post-checkout"
    assert hook.is_file()
    assert hook.stat().st_mode & 0o111, "hook must be executable"
    assert skel.WORKTREE_LOG in hook.read_text()
