"""The harness-test rig: scaffolding a run, and scoring one.

Every check here is a pure function over git facts, so the suite never shells out to a
harness and never needs a network.
"""

from __future__ import annotations

import subprocess

import pytest

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


def _commit(run, message, path, text):
    (run / path).parent.mkdir(parents=True, exist_ok=True)
    (run / path).write_text(text)
    subprocess.run(["git", "-C", str(run), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(run), "commit", "-q", "-m", message], check=True)


def test_score_reads_a_real_run(tmp_path):
    fixture = tmp_path / "fixture"
    (fixture / "src" / "skinner").mkdir(parents=True)
    (fixture / "src" / "skinner" / "__init__.py").write_text("")
    (fixture / "AGENTS.md").write_text("trigger\n")

    run = skel.new_run(fixture, tmp_path / "runs", "claude", stamp="2026-08-24")
    subprocess.run(
        ["git", "-C", str(run), "checkout", "-q", "-b", "feat/cli"], check=True
    )
    _commit(
        run,
        "feat(cli): add an entry point",
        "src/skinner/cli.py",
        "# skinner:module\n",
    )

    findings = {f.check: f for f in skel.score(run)}
    assert findings["branch prefix"].status == "pass"
    assert findings["commit subject"].status == "pass"
    assert findings["canary banner"].status == "pass"
    assert findings["fixture edited"].status == "pass"
    assert findings["fixture extended"].status == "pass"


def test_branch_names_survive_their_own_deletion(tmp_path):
    """Two of four trials merged and deleted the branch; live refs are not enough.

    Without the reflog, `check_worktree_names` compares against an empty branch list
    and a worktree named for its branch passes — the one case the check exists for.
    """
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "README.md").write_text("x\n")
    run = skel.new_run(fixture, tmp_path / "runs", "cursor", stamp="2026-08-24")

    subprocess.run(
        ["git", "-C", str(run), "checkout", "-q", "-b", "feat/cli-version"], check=True
    )
    _commit(run, "feat(cli): add it", "src/skinner/cli.py", "# skinner:module\n")
    subprocess.run(["git", "-C", str(run), "checkout", "-q", "main"], check=True)
    subprocess.run(
        ["git", "-C", str(run), "merge", "-q", "--ff-only", "feat/cli-version"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(run), "branch", "-q", "-D", "feat/cli-version"], check=True
    )

    assert skel.branch_names(run) == ["feat/cli-version"]
    findings = {f.check: f for f in skel.score(run)}
    assert findings["branch prefix"].status == "pass"


def test_worktree_check_cannot_conclude_without_a_branch_to_compare():
    """A name with nothing to compare it against is not a pass.

    A branch created inside a worktree and deleted unmerged leaves no ref and no entry
    in the main reflog. The worktree name survives in the hook log, but whether it
    merely echoed that branch is no longer knowable, and saying "pass" would invent a
    result.
    """
    finding = skel.check_worktree_names(["bender"], [])
    assert finding.status == "unrecoverable"
    assert "bender" in finding.detail


def test_a_run_may_be_placed_outside_the_repository(tmp_path):
    """A run nested under this repo inherits its instruction files.

    A session started inside `runs/` reads every CLAUDE.md and AGENTS.md above it,
    including this repository's own — which names a different almanac. The trial would
    then measure two rule sets at once, so the destination has to be movable.
    """
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "README.md").write_text("x\n")

    elsewhere = tmp_path / "somewhere-else"
    run = skel.new_run(fixture, elsewhere, "claude", stamp="2026-08-24")

    assert run.parent == elsewhere
    assert (run / ".git").is_dir()


def test_runs_are_found_by_label_in_a_given_directory(tmp_path):
    """Scoring has to reach runs wherever they were placed, not only the default."""
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "README.md").write_text("x\n")
    elsewhere = tmp_path / "elsewhere"

    skel.new_run(fixture, elsewhere, "opus", stamp="2026-08-24")
    skel.new_run(fixture, elsewhere, "codex", stamp="2026-08-24")

    found = skel.find_run(elsewhere, "codex")
    assert found.name == "2026-08-24-codex"

    with pytest.raises(skel.SkelError):
        skel.find_run(elsewhere, "cursor")


def test_work_left_on_an_unmerged_branch_is_still_scored(tmp_path):
    """Two of the first four trials never merged; reading HEAD alone saw nothing."""
    fixture = tmp_path / "fixture"
    (fixture / "src" / "skinner").mkdir(parents=True)
    (fixture / "src" / "skinner" / "__init__.py").write_text("")
    run = skel.new_run(fixture, tmp_path / "runs", "opus", stamp="2026-08-24")

    subprocess.run(
        ["git", "-C", str(run), "checkout", "-q", "-b", "feat/cli"], check=True
    )
    _commit(run, "feat(cli): add it", "src/skinner/cli.py", "# skinner:module\n")
    subprocess.run(["git", "-C", str(run), "checkout", "-q", "main"], check=True)

    findings = {f.check: f for f in skel.score(run)}
    assert findings["commit subject"].status == "pass", findings["commit subject"]
    assert findings["canary banner"].status == "pass", findings["canary banner"]


def test_only_the_instrument_counts_as_fixture_tampering():
    """Build config is not the instrument; the rules the run is measured against are.

    A console script cannot be added without editing pyproject.toml, so flagging it
    reports required work as contamination while the run that actually rewrote
    AGENTS.md passes.
    """
    assert skel.check_fixture_edited(["pyproject.toml"]).status == "pass"
    assert skel.check_fixture_edited(["README.md"]).status == "pass"
    assert skel.check_fixture_edited(["AGENTS.md"]).status == "fail"
    edited_rule = skel.check_fixture_edited(
        ["docs/almanac/commit-messages-use-conventional-commit-format.md"]
    )
    assert edited_rule.status == "fail"
