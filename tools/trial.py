"""Drive a harness through the fixture unattended, and archive the evidence.

A trial runs in a throwaway directory, so nothing above the fixture contributes
instruction files of its own. It feeds the prompts to a single session in order, which
is what makes a rule firing on the last prompt evidence that the almanac survived the
whole session rather than only its opening.

The report the agent writes is a claim. The transcript archived beside it is what a
reader checks that claim against — one trial reported following a rule while the
directory on disk said otherwise, so the two are kept together deliberately.
"""

from __future__ import annotations

import glob
import json
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from pathlib import Path

from tools import skel
from tools.harnesses import Harness

REVIEW_DIR = "docs/review"
TRANSCRIPT_NAME = "session.jsonl"
MANIFEST_NAME = "manifest.json"

# Opening a session is a single round trip, so it gets far less rope than a prompt.
CREATE_TIMEOUT = 60

# A trial that has stopped making progress should fail rather than hold the terminal
# open indefinitely. Generous, because a real feature plus a report takes minutes.
PROMPT_TIMEOUT = 1800

# Numeric prefixes carry the order, and the review is 99 so it always lands last: it
# asks what the almanac changed about the work, which is only answerable once the work
# is done.
DEFAULT_PROMPTS = ("01-first-feature", "02-planned-feature", "99-almanac-review")

# Reproducible from the tree and large enough to dominate an archive — one trial's
# virtualenv came to 85MB against a 4MB repository. The agent's commits live in .git, so
# nothing here is evidence.
ARCHIVE_EXCLUDE = frozenset(
    {".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}
)


class TrialError(Exception):
    pass


def prompt_text(name: str, stamp: str) -> str:
    """A prompt from `prompts/`, with `{date}` resolved."""
    path = skel.PROMPTS / f"{name}.md"
    if not path.is_file():
        raise TrialError(f"{path}: no such prompt")
    return path.read_text().strip().replace("{date}", stamp)


def _harness_version(harness: Harness) -> str | None:
    if not harness.trial.version:
        return None
    try:
        done = subprocess.run(
            list(harness.trial.version), capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.SubprocessError) as failure:
        return f"unavailable: {failure}"
    return done.stdout.strip() or done.stderr.strip() or None


def _names_session(harness: Harness) -> bool:
    """Whether the harness supplied the session id that the transcript glob can use.

    `create` prints the id; `{session}` in `first` passes it as a flag. Without either,
    collection matches the run's cwd instead.
    """
    trial = harness.trial
    return bool(trial.create) or any("{session}" in part for part in trial.first)


def _transcript_metadata(path: Path) -> dict:
    """The identifying metadata from a persisted Codex rollout, when present."""
    try:
        with path.open() as lines:
            first = json.loads(lines.readline())
    except (OSError, json.JSONDecodeError):
        return {}
    if first.get("type") != "session_meta":
        return {}
    payload = first.get("payload")
    return payload if isinstance(payload, dict) else {}


def _find_transcript(
    harness: Harness, session: str, run_dir: Path
) -> Path | None:
    pattern = harness.trial.transcript.format(session=session)
    matches = [Path(p) for p in glob.glob(str(Path(pattern).expanduser()))]
    if not _names_session(harness):
        run_cwd = run_dir.resolve()

        def belongs_to_run(path):
            cwd = _transcript_metadata(path).get("cwd")
            return bool(cwd) and Path(cwd).resolve() == run_cwd

        matches = [path for path in matches if belongs_to_run(path)]
    return max(matches, key=lambda p: p.stat().st_mtime) if matches else None


def _session(harness: Harness, run_dir: Path) -> str:
    """The id `first` and `resume` will attach to.

    When `create` is set, the harness names the session — Cursor's `create-chat`
    prints a UUID — and an empty or failed create is not a prompt failure: nothing
    has been asked yet, so there is nothing to archive.

    Every way this can fail names the harness. `create` is the first command a trial
    runs, so a CLI that is not installed surfaces here before anything else, and a bare
    `FileNotFoundError` says nothing about which harness the operator is missing.
    """
    if not harness.trial.create:
        return str(uuid.uuid4())
    try:
        done = subprocess.run(
            list(harness.trial.create),
            cwd=run_dir,
            capture_output=True,
            text=True,
            timeout=CREATE_TIMEOUT,
            env=skel.clean_env(),
        )
    except subprocess.TimeoutExpired:
        raise TrialError(
            f"{harness.name}: create did not return within {CREATE_TIMEOUT}s"
        ) from None
    except (OSError, subprocess.SubprocessError) as failure:
        raise TrialError(f"{harness.name}: create could not run: {failure}") from None
    if done.returncode != 0:
        raise TrialError(f"{harness.name}: create exited {done.returncode}")
    session = done.stdout.strip()
    if not session:
        raise TrialError(f"{harness.name}: create produced no session id")
    return session


def run(
    harness: Harness,
    out_dir: Path,
    stamp: str,
    prompts: tuple[str, ...] = DEFAULT_PROMPTS,
) -> Path:
    """Run every prompt through one session, then archive the run and its evidence.

    Prompts run in name order rather than the order given, so the numeric prefix is what
    decides the sequence and the review at 99 cannot be asked before the work it asks
    about has happened.
    """
    if harness.trial is None:
        raise TrialError(
            f"{harness.name} declares no [trial] in harnesses.toml, so it cannot be "
            "driven unattended"
        )

    prompts = tuple(sorted(prompts))
    texts = [prompt_text(name, stamp) for name in prompts]
    workspace = Path(tempfile.mkdtemp(prefix=f"skel-trial-{harness.name}-"))

    try:
        run_dir = skel.new_run(skel.FIXTURE, workspace, harness.name, stamp)
        initial_head = skel._git(run_dir, "rev-parse", "HEAD").strip()
        session = _session(harness, run_dir)
        results = _drive(harness, run_dir, session, prompts, texts)
        transcript, discovered_session = _collect(harness, run_dir, session)
        manifest_session = session if _names_session(harness) else discovered_session
        problems = _validation_problems(
            run_dir, initial_head, stamp, prompts, results, transcript
        )
        _write_manifest(
            harness,
            run_dir,
            manifest_session,
            stamp,
            prompts,
            results,
            transcript,
            problems,
        )
        archive = _archive(run_dir, out_dir, workspace)
        if problems:
            detail = "\n".join(f"- {problem}" for problem in problems)
            raise TrialError(
                f"trial evidence failed structural validation:\n{detail}\n"
                f"archived at {archive}"
            )
        return archive
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def _drive(harness, run_dir, session, prompts, texts) -> list[dict]:
    """Feed each prompt to the same session, stopping at the first that fails.

    Output is not captured: a trial takes minutes, and watching it is the only progress
    there is. What the harness did is recorded in the transcript, not in stdout.

    The harness inherits a scrubbed environment for the same reason the scaffold uses
    one: an agent that commits under a leaked `GIT_DIR` writes its work into whatever
    repository launched the trial, and the run it was asked to work in stays empty.
    """
    results = []
    for index, (name, text) in enumerate(zip(prompts, texts)):
        template = harness.trial.first if index == 0 else harness.trial.resume
        command = [part.format(session=session, prompt=text) for part in template]
        print(f"\n── prompt {index + 1}/{len(prompts)}: {name}\n", flush=True)
        try:
            done = subprocess.run(
                command, cwd=run_dir, timeout=PROMPT_TIMEOUT, env=skel.clean_env()
            )
            status = done.returncode
        except subprocess.TimeoutExpired:
            status = None
        results.append({"prompt": name, "exit": status})
        if status != 0:
            reason = "timed out" if status is None else f"exited {status}"
            print(f"\n!! {name} {reason} — archiving what exists", flush=True)
            break
    return results


def _collect(
    harness: Harness, run_dir: Path, session: str
) -> tuple[str | None, str | None]:
    """Copy the harness's own transcript in beside the agent's report."""
    review = run_dir / REVIEW_DIR
    review.mkdir(parents=True, exist_ok=True)

    found = _find_transcript(harness, session, run_dir)
    if found is None:
        return None, None
    shutil.copy2(found, review / TRANSCRIPT_NAME)
    metadata = _transcript_metadata(found)
    discovered_session = metadata.get("id") or metadata.get("session_id")
    return f"{REVIEW_DIR}/{TRANSCRIPT_NAME}", discovered_session


def _validation_problems(
    run_dir, initial_head, stamp, prompts, results, transcript
) -> list[str]:
    """Structural omissions that make a trial archive incomplete, not a score."""
    problems = []
    for result in results:
        if result["exit"] != 0:
            outcome = "timed out" if result["exit"] is None else f"exited {result['exit']}"
            problems.append(f"{result['prompt']} {outcome}")

    if skel._git(run_dir, "rev-parse", "main").strip() == initial_head:
        problems.append("main has no new commit beyond the scaffold")

    review_path = f"{REVIEW_DIR}/{stamp}-review.md"
    if "99-almanac-review" in prompts:
        committed = skel._git(
            run_dir, "ls-tree", "--name-only", "main", "--", review_path
        ).strip()
        if committed != review_path:
            problems.append(f"main does not contain the required {review_path}")

    if transcript is None:
        problems.append("no transcript matched the trial workspace")
    return problems


def _write_manifest(
    harness, run_dir, session, stamp, prompts, results, transcript, problems
):
    """What the archive needs to stay interpretable.

    A result is a property of the harness, its version, and what the agent was permitted
    to do, so the commands go in verbatim rather than as a summary.
    """
    review = run_dir / REVIEW_DIR
    review.mkdir(parents=True, exist_ok=True)
    (review / MANIFEST_NAME).write_text(
        json.dumps(
            {
                "harness": harness.name,
                "version": _harness_version(harness),
                "stamp": stamp,
                "session": session,
                "prompts": list(prompts),
                "results": results,
                "validation": {"passed": not problems, "problems": problems},
                "commands": {
                    "first": list(harness.trial.first),
                    "resume": list(harness.trial.resume),
                },
                "transcript": transcript,
                "fixture_entries": sorted(
                    p.name
                    for p in (skel.FIXTURE / "docs/almanac").glob("*.md")
                    if p.name != "README.md"
                ),
            },
            indent=4,
        )
        + "\n"
    )


def _archive(run_dir: Path, out_dir: Path, workspace: Path) -> Path:
    """Zip the run — working tree, git history, report, transcript, manifest."""
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{run_dir.name}.zip"

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(run_dir.rglob("*")):
            relative = path.relative_to(run_dir)
            if ARCHIVE_EXCLUDE & set(relative.parts):
                continue
            if path.is_file() and not path.is_symlink():
                bundle.write(path, path.relative_to(workspace))
    return target
