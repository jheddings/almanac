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


def _find_transcript(harness: Harness, session: str) -> Path | None:
    pattern = harness.trial.transcript.format(session=session)
    matches = [Path(p) for p in glob.glob(str(Path(pattern).expanduser()))]
    return max(matches, key=lambda p: p.stat().st_mtime) if matches else None


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
    session = str(uuid.uuid4())
    workspace = Path(tempfile.mkdtemp(prefix=f"skel-trial-{harness.name}-"))

    try:
        run_dir = skel.new_run(skel.FIXTURE, workspace, harness.name, stamp)
        results = _drive(harness, run_dir, session, prompts, texts)
        transcript = _collect(harness, run_dir, session)
        _write_manifest(harness, run_dir, session, stamp, prompts, results, transcript)
        return _archive(run_dir, out_dir, workspace)
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


def _collect(harness: Harness, run_dir: Path, session: str) -> str | None:
    """Copy the harness's own transcript in beside the agent's report."""
    review = run_dir / REVIEW_DIR
    review.mkdir(parents=True, exist_ok=True)

    found = _find_transcript(harness, session)
    if found is None:
        return None
    shutil.copy2(found, review / TRANSCRIPT_NAME)
    return f"{REVIEW_DIR}/{TRANSCRIPT_NAME}"


def _write_manifest(harness, run_dir, session, stamp, prompts, results, transcript):
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
