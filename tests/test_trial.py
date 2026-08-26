"""Driving a harness through the fixture, without driving one.

Every test here stubs the harness command. A suite that shelled out to a real agent
would be slow, non-deterministic, and would need credentials — so what is checked is the
plumbing around the harness: prompt resolution, session continuity, and whether the
archive stays interpretable.
"""

from __future__ import annotations

import json
import os
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
    assert codex.trial.first[:2] == ("codex", "--approve-for-me")
    assert codex.trial.resume[:2] == ("codex", "--approve-for-me")
    assert "--approve-for-me" in codex.trial.first
    assert "--approve-for-me" in codex.trial.resume
    assert "--sandbox" not in codex.trial.first
    assert "--sandbox" not in codex.trial.resume
    assert "exec" in codex.trial.first
    assert "resume" in codex.trial.resume
    assert "--last" in codex.trial.resume
    assert "--dangerously-bypass-approvals-and-sandbox" not in codex.trial.first
    assert "--dangerously-bypass-approvals-and-sandbox" not in codex.trial.resume
    assert codex.trial.version == ("codex", "--version")


def test_codex_transcript_glob_reaches_date_partitioned_rollouts(
    tmp_path, monkeypatch, codex
):
    """The newest rollout for another cwd must not win the global mtime race."""
    rollout = (
        tmp_path
        / ".codex/sessions/2026/08/26"
        / "rollout-2026-08-26T10-00-00-session.jsonl"
    )
    rollout.parent.mkdir(parents=True)
    rollout.write_text(
        json.dumps(
            {
                "type": "session_meta",
                "payload": {"cwd": str(tmp_path), "id": "matching-session"},
            }
        )
        + "\n"
    )
    foreign = rollout.with_name("rollout-2026-08-26T10-01-00-foreign.jsonl")
    foreign.write_text(
        json.dumps(
            {
                "type": "session_meta",
                "payload": {"cwd": str(tmp_path / "elsewhere"), "id": "foreign"},
            }
        )
        + "\n"
    )
    os.utime(foreign, (rollout.stat().st_mtime + 10,) * 2)
    monkeypatch.setenv("HOME", str(tmp_path))

    assert trial._find_transcript(codex, "unused", tmp_path) == rollout

    transcript, session = trial._collect(codex, tmp_path, "unused")
    assert transcript == "docs/review/session.jsonl"
    assert session == "matching-session"


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


def _stub_harness(
    base,
    recorder,
    *,
    names_session=True,
    makes_commit=True,
    makes_review=True,
    create=(),
):
    """A harness whose commands are `true`, so the plumbing runs without an agent."""
    marker = " # {session}" if names_session else ""
    echoed = " {session}" if create else ""
    transcript = Path(recorder).parent / "session.jsonl"
    metadata = (
        f"printf '{{\"type\":\"session_meta\",\"payload\":"
        f"{{\"cwd\":\"%s\",\"id\":\"stub-session\"}}}}\\n' "
        f'"$PWD" > {transcript}'
    )
    metadata = metadata.replace("{", "{{").replace("}", "}}")
    first = f"{metadata} && echo first{echoed} >> {recorder}"
    if makes_commit:
        first += (
            " && echo work > stub-work.txt"
            " && git add stub-work.txt"
            " && git -c user.name=stub -c user.email=stub@example.com"
            " commit -qm 'feat: add stub work'"
        )
    resume = f"echo resume{echoed} >> {recorder}"
    if makes_review:
        resume += (
            " && if test ! -f docs/review/2026-08-26-review.md; then"
            " mkdir -p docs/review"
            " && echo review > docs/review/2026-08-26-review.md"
            " && git add docs/review/2026-08-26-review.md"
            " && git -c user.name=stub -c user.email=stub@example.com"
            " commit -qm 'docs: add review'; fi"
        )
    return harnesses.Harness(
        name=base.name,
        manifest=base.manifest,
        trial=harnesses.Trial(
            first=("sh", "-c", first + marker),
            resume=("sh", "-c", resume + marker),
            transcript=str(transcript),
            create=tuple(create),
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
    assert manifest["validation"] == {"passed": True, "problems": []}


def test_the_manifest_records_the_discovered_codex_session_id(tmp_path, codex):
    """The manifest uses the rollout ID rather than the rig's unrelated UUID."""
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(codex, recorder, names_session=False)

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))

    assert manifest["session"] == "stub-session"


def test_a_zero_exit_trial_with_no_new_commit_fails_loudly(tmp_path, claude):
    """A graceful blocked response is process success, not a successful trial."""
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(
        claude, recorder, makes_commit=False, makes_review=False
    )
    out = tmp_path / "out"

    with pytest.raises(trial.TrialError) as failure:
        trial.run(stub, out, "2026-08-26")

    assert "main has no new commit" in str(failure.value)
    assert "review" in str(failure.value)
    archive = out / "2026-08-26-claude.zip"
    assert archive.is_file(), "failed evidence must still be archived"
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))
    assert manifest["validation"]["passed"] is False


def test_a_trial_without_a_committed_review_fails_loudly(tmp_path, claude):
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder, makes_review=False)

    with pytest.raises(trial.TrialError) as failure:
        trial.run(stub, tmp_path / "out", "2026-08-26")

    assert "review" in str(failure.value)
    assert "no new commit" not in str(failure.value)


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

    out = tmp_path / "out"
    with pytest.raises(trial.TrialError):
        trial.run(stub, out, "2026-08-26")
    archive = out / "2026-08-26-claude.zip"
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))

    assert [(r["prompt"], r["exit"]) for r in manifest["results"]] == [
        ("01-first-feature", 3)
    ]
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
    transcript = tmp_path / "session.jsonl"
    metadata = (
        f"printf '{{\"type\":\"session_meta\",\"payload\":"
        f"{{\"cwd\":\"%s\",\"id\":\"stub-session\"}}}}\\n' "
        f'"$PWD" > {transcript}'
    )
    metadata = metadata.replace("{", "{{").replace("}", "}}")
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
                "&& echo kept > src/skinner/real.py "
                "&& mkdir -p docs/review "
                "&& echo review > docs/review/2026-08-26-review.md "
                "&& git add src/skinner/real.py docs/review/2026-08-26-review.md "
                "&& git -c user.name=stub -c user.email=stub@example.com "
                "commit -qm 'feat: add real work' "
                f"&& {metadata}",
            ),
            resume=("sh", "-c", "true"),
            transcript=str(transcript),
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


def test_create_stdout_is_the_session_the_prompts_attach_to(tmp_path, claude):
    """The harness names the session; the driver must not invent a second id."""
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(
        claude,
        recorder,
        create=("sh", "-c", f"echo create >> {recorder}; printf 'sess-1\\n'"),
    )

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")

    assert recorder.read_text().split() == [
        "create",
        "first",
        "sess-1",
        "resume",
        "sess-1",
        "resume",
        "sess-1",
    ]
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))
    assert manifest["session"] == "sess-1"


def test_create_names_the_session_even_when_first_does_not_template_it(
    tmp_path, claude
):
    """Codex discovers the id from the rollout; create is the other way a harness names one."""
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(
        claude,
        recorder,
        names_session=False,
        create=("sh", "-c", f"printf 'sess-1\\n'"),
    )

    archive = trial.run(stub, tmp_path / "out", "2026-08-26")
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        manifest = json.loads(bundle.read(name))

    assert manifest["session"] == "sess-1"
    assert trial._names_session(stub)


def test_a_failing_create_names_the_harness_and_does_not_prompt(tmp_path, claude):
    """Nothing to archive: the session never opened, so no prompt has run."""
    recorder = tmp_path / "calls.txt"
    stub = harnesses.Harness(
        name="cursor",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            create=("sh", "-c", "exit 7"),
            first=("sh", "-c", f"echo first >> {recorder}"),
            resume=("sh", "-c", "true"),
            transcript=str(tmp_path / "{session}.jsonl"),
        ),
    )

    with pytest.raises(trial.TrialError) as failure:
        trial.run(stub, tmp_path / "out", "2026-08-26")

    assert "cursor" in str(failure.value)
    assert not recorder.exists()
    assert not list(tmp_path.rglob("*.zip"))


def test_empty_create_stdout_is_a_failure(tmp_path, claude):
    stub = harnesses.Harness(
        name="cursor",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            create=("sh", "-c", "true"),
            first=("sh", "-c", "true"),
            resume=("sh", "-c", "true"),
            transcript=str(tmp_path / "{session}.jsonl"),
        ),
    )

    with pytest.raises(trial.TrialError) as failure:
        trial.run(stub, tmp_path / "out", "2026-08-26")

    assert "cursor" in str(failure.value)
    assert "session" in str(failure.value).lower()


def _create_only(claude, tmp_path, create):
    return harnesses.Harness(
        name="cursor",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            create=create,
            first=("sh", "-c", "true"),
            resume=("sh", "-c", "true"),
            transcript=str(tmp_path / "{session}.jsonl"),
        ),
    )


def test_a_create_command_that_does_not_exist_names_the_harness(tmp_path, claude):
    """`create` runs before anything else, so a missing CLI is the first thing hit.

    Without a handler it arrives as a bare FileNotFoundError, which says nothing about
    which harness the operator failed to install.
    """
    stub = _create_only(claude, tmp_path, ("definitely-not-a-real-binary",))

    with pytest.raises(trial.TrialError) as failure:
        trial.run(stub, tmp_path / "out", "2026-08-26")

    assert "cursor" in str(failure.value)


def test_a_create_command_that_hangs_names_the_harness(tmp_path, claude, monkeypatch):
    """A create that never returns is a failed trial, not a traceback."""
    monkeypatch.setattr(trial, "CREATE_TIMEOUT", 1)
    stub = _create_only(claude, tmp_path, ("sh", "-c", "sleep 30"))

    with pytest.raises(trial.TrialError) as failure:
        trial.run(stub, tmp_path / "out", "2026-08-26")

    assert "cursor" in str(failure.value)


def _manifest_of(archive):
    with zipfile.ZipFile(archive) as bundle:
        name = next(n for n in bundle.namelist() if n.endswith("manifest.json"))
        return json.loads(bundle.read(name))


def _failed_archive(stub, out):
    """The archive from a run that failed validation but still produced evidence."""
    with pytest.raises(trial.TrialError):
        trial.run(stub, out, "2026-08-26")
    return out / "2026-08-26-claude.zip"


def _manifest_of_failed(stub, out):
    return _manifest_of(_failed_archive(stub, out))


def test_a_passing_trial_still_says_which_prompt_did_the_work(tmp_path, claude):
    """Validation asks whether there is something to read, not whether each prompt ran.

    A session where the feature prompts produced nothing and only the review committed
    satisfies every structural prerequisite — `main` moved, the review is in it, a
    transcript matched — and passes. That is a real run: one harness spent two of its
    three prompts waiting on a question nobody could answer. The counts are what make
    the difference visible without opening the archive.
    """
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder, makes_commit=False)

    manifest = _manifest_of(trial.run(stub, tmp_path / "out", "2026-08-26"))

    assert manifest["validation"]["passed"] is True
    assert [r["commits"] for r in manifest["results"]] == [1, 2, 2]


def test_work_left_on_an_unmerged_branch_still_counts(tmp_path, claude):
    """A count taken from HEAD alone reports an unmerged branch as an empty run.

    That is not hypothetical: it is the reading an earlier mechanical scorer got wrong
    on half the trials it was given.
    """
    stub = harnesses.Harness(
        name="claude",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            first=(
                "sh",
                "-c",
                "git checkout -q -b feat/stranded"
                " && echo work > src/skinner/cli.py"
                " && git add -A"
                " && git -c user.name=t -c user.email=t@e commit -qm 'feat: cli'"
                " && git checkout -q main",
            ),
            resume=("sh", "-c", "true"),
            transcript=str(tmp_path / "{session}.jsonl"),
        ),
    )

    manifest = _manifest_of_failed(stub, tmp_path / "out")

    assert manifest["results"][0]["commits"] == 2, manifest["results"]


def test_uncommitted_work_is_visible_as_well(tmp_path, claude):
    """An earlier trial left its report uncommitted, where a commit count misses it."""
    stub = harnesses.Harness(
        name="claude",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            first=("sh", "-c", "echo draft > src/skinner/cli.py"),
            resume=("sh", "-c", "true"),
            transcript=str(tmp_path / "{session}.jsonl"),
        ),
    )

    manifest = _manifest_of_failed(stub, tmp_path / "out")

    assert manifest["results"][0]["commits"] == 1
    assert manifest["results"][0]["dirty"] == 1


def _homed_harness(claude, tmp_path, script, env, create=()):
    return harnesses.Harness(
        name="claude",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            create=create,
            first=("sh", "-c", script),
            resume=("sh", "-c", "true"),
            transcript=str(tmp_path / "{session}.jsonl"),
            env=env,
        ),
    )


def _read_from_failed(claude, tmp_path, script, env, name, create=()):
    stub = _homed_harness(claude, tmp_path, script, env, create)
    archive = _failed_archive(stub, tmp_path / "out")
    with zipfile.ZipFile(archive) as bundle:
        found = next(n for n in bundle.namelist() if n.endswith(name))
        return bundle.read(found).decode().strip()


def test_a_declared_home_reaches_the_harness_and_exists(tmp_path, claude):
    """A harness cannot write its configuration into a directory that is not there."""
    seen = _read_from_failed(
        claude,
        tmp_path,
        'test -d "$AGENT_HOME" && echo "$AGENT_HOME" > home.txt',
        env=(("AGENT_HOME", "{home}"),),
        name="home.txt",
    )
    assert seen, "the harness saw no home"


def test_the_hosts_own_configuration_does_not_reach_the_run(
    tmp_path, claude, monkeypatch
):
    """One trial loaded three skills from the host's plugin cache and stalled on one.

    The ambient value is what a trial inherits today, so overriding it is the whole
    point: a variable that merely got set when absent would change nothing here.
    """
    monkeypatch.setenv("AGENT_HOME", "/Users/someone/.agent")

    seen = _read_from_failed(
        claude,
        tmp_path,
        'echo "$AGENT_HOME" > home.txt',
        env=(("AGENT_HOME", "{home}"),),
        name="home.txt",
    )
    assert seen != "/Users/someone/.agent", "the host's configuration reached the run"


def test_create_runs_under_the_same_home_as_the_prompts(tmp_path, claude):
    """`create` opens the session, so it reads the same skills and plugins as the rest.

    Isolating only the prompts would leave the one command that establishes the
    conversation reading the host's configuration.
    """
    seen = _read_from_failed(
        claude,
        tmp_path,
        "true",
        env=(("AGENT_HOME", "{home}"),),
        name="create-home.txt",
        create=("sh", "-c", 'echo "$AGENT_HOME" > create-home.txt; echo sess-1'),
    )
    assert seen.endswith(trial.AGENT_HOME), seen


def test_the_manifest_records_the_redirect_without_the_temp_path(tmp_path, claude):
    """The template says what was isolated; the expansion says only where it ran."""
    stub = _homed_harness(claude, tmp_path, "true", env=(("AGENT_HOME", "{home}"),))

    manifest = _manifest_of_failed(stub, tmp_path / "out")

    assert manifest["env"] == {"AGENT_HOME": "{home}"}


def test_a_redirect_the_harness_ignored_is_visible(tmp_path, claude):
    """A variable a harness does not read is a silent no-op, and reads as isolation.

    Nothing under the throwaway home means the harness kept its configuration
    somewhere else, which is the failure this record exists to make loud.
    """
    ignored = _homed_harness(
        claude, tmp_path, "true", env=(("NOT_A_REAL_HOME", "{home}"),)
    )
    honoured = _homed_harness(
        claude,
        tmp_path,
        'mkdir -p "$AGENT_HOME/skills" && echo x > "$AGENT_HOME/skills/s.md"',
        env=(("AGENT_HOME", "{home}"),),
    )

    blind = _manifest_of_failed(ignored, tmp_path / "out")
    seeing = _manifest_of_failed(honoured, tmp_path / "out2")

    assert blind["config_home_used"] is False
    assert seeing["config_home_used"] is True


def test_a_harness_declaring_no_env_records_none(tmp_path, claude):
    recorder = tmp_path / "calls.txt"
    stub = _stub_harness(claude, recorder)

    manifest = _manifest_of(trial.run(stub, tmp_path / "out", "2026-08-26"))

    assert manifest["env"] == {}
    assert manifest["config_home_used"] is None
