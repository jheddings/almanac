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


def test_branch_check_wants_a_conventional_prefix():
    assert skel.check_branch(["feat/cli-entry-point"]).status == "pass"
    assert skel.check_branch(["add-cli"]).status == "fail"
    assert skel.check_branch([]).status == "unrecoverable"


def test_commit_subject_check_notes_the_scope():
    good = skel.check_commit_subjects(["feat(cli): add an entry point"])
    assert good.status == "pass"
    assert "scoped" in good.detail

    bare = skel.check_commit_subjects(["feat: add an entry point"])
    assert bare.status == "pass"
    assert "unscoped" in bare.detail

    assert skel.check_commit_subjects(["added a CLI"]).status == "fail"


def test_body_wrap_check_flags_long_lines():
    assert skel.check_commit_bodies(["short enough"]).status == "pass"
    assert skel.check_commit_bodies(["x" * 73]).status == "fail"


def test_worktree_check_flags_a_name_that_merely_repeats_its_branch():
    """The exact miss one trial produced when a skill's path shape won."""
    passing = skel.check_worktree_names(["food-pellet"], ["feat/cli-entry-point"])
    assert passing.status == "pass"
    failing = skel.check_worktree_names(["cli-version"], ["feat/cli-version"])
    assert failing.status == "fail"


def test_worktree_check_is_unrecoverable_when_the_log_is_empty():
    """A sandbox that denies .git writes silences the hook; that is not a failure."""
    assert skel.check_worktree_names([], ["feat/x"]).status == "unrecoverable"


def test_fixture_edited_and_extended_are_separate_checks():
    """One trial edited AGENTS.md; a different one invented a directory instead."""
    assert skel.check_fixture_edited(["AGENTS.md"]).status == "fail"
    assert skel.check_fixture_edited(["src/skinner/cli.py"]).status == "pass"

    invented = skel.check_fixture_extended(["docs/superpowers/specs/x.md"])
    assert invented.status == "fail"
    clean = skel.check_fixture_extended(["src/skinner/cli.py", "tests/test_cli.py"])
    assert clean.status == "pass"


def test_canary_check_reads_the_banner_per_file():
    """Per-file, so a rule that fades mid-session is visible as decay."""
    assert skel.check_canary({"src/skinner/cli.py": "# skinner:module"}).status == "pass"
    assert skel.check_canary({"src/skinner/cli.py": '"""CLI."""'}).status == "fail"

    mixed = skel.check_canary(
        {"src/skinner/cli.py": "# skinner:module", "src/skinner/config.py": "import os"}
    )
    assert mixed.status == "fail"
    assert "1/2" in mixed.detail

    assert skel.check_canary({}).status == "unrecoverable"
