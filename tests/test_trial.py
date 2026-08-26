"""Driving a harness through the fixture, without driving one.

Every test here stubs the harness command. A suite that shelled out to a real agent
would be slow, non-deterministic, and would need credentials — so what is checked is the
plumbing around the harness: prompt resolution, session continuity, and whether the
archive stays interpretable.
"""

from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

import pytest

from tools import harnesses, skel, trial


@pytest.fixture
def claude():
    return harnesses.get("claude")


@pytest.fixture
def codex():
    return harnesses.get("codex")


def test_the_declared_harness_can_be_driven(claude):
    """Guard the guard: without a trial block the rest of this suite is vacuous."""
    assert claude.trial is not None
    assert "{session}" in " ".join(claude.trial.first)
    assert "{session}" in " ".join(claude.trial.resume)
    assert "{session}" in claude.trial.transcript


def test_codex_can_be_driven_unattended_in_one_session(codex):
    """Codex cannot name a new session, so cwd-scoped `--last` continues it."""
    assert codex.trial is not None
    assert codex.trial.first[:2] == ("codex", "exec")
    assert codex.trial.resume[:3] == ("codex", "exec", "resume")
    assert "--last" in codex.trial.resume
    assert "--dangerously-bypass-approvals-and-sandbox" in codex.trial.first
    assert "--dangerously-bypass-approvals-and-sandbox" in codex.trial.resume
    assert codex.trial.version == ("codex", "--version")


def test_codex_transcript_glob_reaches_date_partitioned_rollouts(
    tmp_path, monkeypatch, codex
):
    """Codex stores rollouts below year/month/day, deeper than a `**` glob reaches."""
    rollout = (
        tmp_path
        / ".codex/sessions/2026/08/26"
        / "rollout-2026-08-26T10-00-00-session.jsonl"
    )
    rollout.parent.mkdir(parents=True)
    rollout.write_text("{}\n")
    monkeypatch.setenv("HOME", str(tmp_path))

    assert trial._find_transcript(codex, "unused") == rollout


def test_a_harness_without_a_trial_block_says_so(tmp_path, monkeypatch):
    """Only some harnesses can be driven; the rest must fail loudly, not silently."""
    bare = harnesses.Harness(name="paper", manifest=tmp_path / "m.json")
    with pytest.raises(trial.TrialError) as failure:
        trial.run(bare, tmp_path, "2026-08-26")
    assert "harnesses.toml" in str(failure.value)


def test_prompts_resolve_their_date(tmp_path):
    """The review prompt names the file it must write, so the date has to be real."""
    text = trial.prompt_text("99-almanac-review", "2026-08-26")
    assert "docs/review/2026-08-26-review.md" in text
    assert "{date}" not in text


def test_an_unknown_prompt_is_an_error():
    with pytest.raises(trial.TrialError):
        trial.prompt_text("99-does-not-exist", "2026-08-26")


def _stub_harness(base, recorder, *, names_session=True):
    """A harness whose commands are `true`, so the plumbing runs without an agent."""
    marker = " # {session}" if names_session else ""
    return harnesses.Harness(
        name=base.name,
        manifest=base.manifest,
        trial=harnesses.Trial(
            first=("sh", "-c", f"echo first >> {recorder}{marker}"),
            resume=("sh", "-c", f"echo resume >> {recorder}{marker}"),
            transcript=str(Path(recorder).parent / "{session}.jsonl"),
            version=("sh", "-c", "echo stub-version"),
        ),
    )


def test_the_first_prompt_opens_a_session_and_the_rest_continue_it(tmp_path, claude):
    """A rule firing on the last prompt only means something if it is one session."""
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder)

    trial.run(stub, tmp_path / "out", "2026-08-26")

    calls = recorder.read_text().split()
    assert calls == ["first", "resume", "resume"], calls


def test_the_archive_carries_the_run_and_its_manifest(tmp_path, claude):
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder)

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")

    assert archive.name == "2026-08-26-claude.zip"
    names = zipfile.ZipFile(archive).namelist()
    assert "2026-08-26-claude/AGENTS.md" in names
    assert "2026-08-26-claude/docs/almanac/README.md" in names
    assert any(n.endswith("docs/review/manifest.json") for n in names), names
    assert any(".git/" in n for n in names), "history is evidence too"


def test_the_manifest_records_what_makes_a_result_interpretable(tmp_path, claude):
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder)

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))

    assert manifest["harness"] == "claude"
    assert manifest["version"] == "stub-version"
    assert manifest["session"]
    assert manifest["prompts"] == list(trial.DEFAULT_PROMPTS)
    assert [r["exit"] for r in manifest["results"]] == [0, 0, 0]
    # The permission the agent ran under lives in the command, so it is copied verbatim
    # rather than summarised.
    assert manifest["commands"]["first"] == list(stub.trial.first)
    assert manifest["fixture_entries"], "the entry set is part of the result"


def test_the_manifest_does_not_invent_a_codex_session_id(tmp_path, codex):
    """The rig's UUID is not the ID Codex assigns when it opens the session."""
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(codex, recorder, names_session=False)

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))

    assert manifest["session"] is None


def test_a_failing_prompt_stops_the_run_but_still_archives(tmp_path, claude):
    """Evidence from a partial run is worth more than no evidence."""
    stub = harnesses.Harness(
        name="claude",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            first=("sh", "-c", "exit 3"),
            resume=("sh", "-c", "true"),
            transcript=str(tmp_path / "{session}.jsonl"),
        ),
    )

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))

    assert manifest["results"] == [{"prompt": "01-first-feature", "exit": 3}]
    assert manifest["transcript"] is None


def test_the_workspace_is_cleaned_up(tmp_path, claude, monkeypatch):
    """The run is a throwaway; only the archive survives it.

    The workspace this run made is captured as it is created, rather than globbing the
    temp directory for a name-shaped match: that would pass vacuously wherever `TMPDIR`
    is not `/tmp`, and fail whenever a real trial happened to be running alongside the
    suite.
    """
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder)

    made = []
    real_mkdtemp = tempfile.mkdtemp
    monkeypatch.setattr(
        tempfile, "mkdtemp", lambda **kw: made.append(real_mkdtemp(**kw)) or made[-1]
    )

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")

    assert archive.is_file()
    assert made, "the run did not go through a temporary workspace"
    assert not [w for w in made if Path(w).exists()], made


def test_the_archive_leaves_out_what_is_reproducible(tmp_path, claude):
    """One trial's virtualenv came to 85MB against a 4MB repository.

    The stub plants both excluded directories, because the fixture ships neither: an
    assertion that they are absent from an archive that could never have held them
    holds no matter what `ARCHIVE_EXCLUDE` says.
    """
    stub = harnesses.Harness(
        name="claude",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            first=(
                "sh",
                "-c",
                "mkdir -p .venv/lib src/skinner/__pycache__ "
                "&& echo big > .venv/lib/payload "
                "&& echo cached > src/skinner/__pycache__/mod.pyc "
                "&& echo kept > src/skinner/real.py",
            ),
            resume=("sh", "-c", "true"),
            transcript=str(tmp_path / "{session}.jsonl"),
        ),
    )

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")
    names = zipfile.ZipFile(archive).namelist()

    assert not [n for n in names if "/.venv/" in n or "__pycache__" in n], names
    assert any(n.endswith("src/skinner/real.py") for n in names), (
        "the stub planted nothing, so the exclusion was never exercised"
    )


def test_the_manifest_counts_entries_not_the_contract(tmp_path, claude):
    """README.md is the local contract, not a claim, and is excluded everywhere else."""
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder)

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))

    assert "README.md" not in manifest["fixture_entries"]
    assert manifest["fixture_entries"]


def test_the_review_runs_last_however_it_is_asked_for(tmp_path, claude):
    """The review asks what the almanac changed, which needs the work to exist first."""
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder)

    archive = trial.run(
        stub,
        tmp_path / "out",
        "2026-08-26",
        prompts=("99-almanac-review", "01-first-feature"),
    )
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))

    assert manifest["prompts"] == ["01-first-feature", "99-almanac-review"]
