"""Scaffold harness-test runs from the `skel/` fixture.

A run is a standalone git repository, not a copy inside this one, because cloud
platforms clone a repo rather than opening a subfolder — and because a run nested under
this tree inherits its instruction files, including an `AGENTS.md` naming a different
almanac.

The rig prepares a run and gets out of the way. It reaches no verdicts: what an agent
did is read from the diff, by a person, who is both faster and more reliable at it than
any heuristic worth maintaining.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from tools.harnesses import REPO_ROOT

FIXTURE = REPO_ROOT / "skel"
RUNS = REPO_ROOT / "runs"
PROMPTS = REPO_ROOT / "prompts"

# Written under .git/, so it is outside the working tree and not something an agent
# lists, reads, or commits. It exists because a removed worktree's name is otherwise
# unrecoverable — see docs/almanac/.
WORKTREE_LOG = "skel-worktrees.log"

INITIAL_COMMIT = "chore: initialize the project skeleton and almanac"

# The scaffold's own commit, made wherever the rig runs. A CI runner or a fresh
# container has no git identity, and git refuses to commit without one.
SCAFFOLD_IDENTITY = ("-c", "user.name=skel", "-c", "user.email=skel@example.com")

# Hooks are shared by every worktree, so this fires in the session worktree too and the
# log tolerates repeated lines. A sandbox that denies writes under .git silences it
# entirely, and then the log is simply empty.
HOOK = """#!/bin/sh
# Records each checkout's working tree so a worktree name survives its removal.
git rev-parse --show-toplevel >> "$(git rev-parse --git-common-dir)/{log}" 2>/dev/null || true
"""


# Git variables that say *which* repository to act on, or who is acting. `git -C` does
# not override them — the environment wins — so a run scaffolded from inside a git hook
# would be staged and committed into the enclosing repository instead. Anything git
# needs to run at all (where its helpers live, how it reaches a remote) is kept.
GIT_ENV_KEEP = frozenset(
    {
        "GIT_EXEC_PATH",
        "GIT_SSH",
        "GIT_SSH_COMMAND",
        "GIT_ASKPASS",
        "GIT_TERMINAL_PROMPT",
    }
)


class SkelError(Exception):
    pass


def clean_env() -> dict[str, str]:
    """The ambient environment with git's repository and identity variables removed.

    An allowlist rather than a list of the known offenders: `GIT_DIR`, `GIT_INDEX_FILE`,
    and `GIT_AUTHOR_NAME` are the ones that bite today, and a variable added by a later
    git could reintroduce exactly this bug without anyone editing this file.
    """
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_") or key in GIT_ENV_KEEP
    }


def _git(run: Path, *args: str) -> str:
    """Run git, and surface what it said when it fails.

    `check=True` alone raises with the exit status and nothing else, so a failure
    arrives as "exit 128" with the diagnosis discarded — which is the whole of what git
    wrote to stderr.
    """
    result = subprocess.run(
        ["git", "-C", str(run), *args],
        capture_output=True,
        text=True,
        env=clean_env(),
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        raise SkelError(
            f"git {' '.join(args)} in {run} exited {result.returncode}: {detail}"
        )
    return result.stdout


def new_run(fixture: Path, runs: Path, label: str, stamp: str) -> Path:
    """Copy the fixture to `runs/<stamp>-<label>/` as a standalone repository."""
    if not fixture.is_dir():
        raise SkelError(f"{fixture}: no fixture to copy")

    run = runs / f"{stamp}-{label}"
    if run.exists():
        raise SkelError(f"{run}: already exists")

    run.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(fixture, run)

    _git(run, "init", "-q", "-b", "main")
    _install_hook(run)
    _git(run, "add", "-A")
    _git(run, *SCAFFOLD_IDENTITY, "commit", "-q", "-m", INITIAL_COMMIT)
    return run


def _install_hook(run: Path) -> None:
    hooks = run / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "post-checkout"
    hook.write_text(HOOK.format(log=WORKTREE_LOG))
    hook.chmod(0o755)
