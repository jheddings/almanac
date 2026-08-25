"""Scaffold and score harness-test runs built from the `skel/` fixture.

A run is a standalone git repository, not a copy inside this one, because cloud
platforms clone a repo rather than opening a subfolder. Scoring reads git state and
never a transcript: one trial reported following the worktree rule while the directory
on disk was named after the feature.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tools.harnesses import REPO_ROOT

FIXTURE = REPO_ROOT / "skel"
RUNS = REPO_ROOT / "runs"
PROMPTS = REPO_ROOT / "prompts"

# Written under .git/, so it is outside the working tree and not something an agent
# lists, reads, or commits.
WORKTREE_LOG = "skel-worktrees.log"

INITIAL_COMMIT = "chore: initialize the project skeleton and almanac"

CONVENTIONAL_TYPES = (
    "feat",
    "fix",
    "chore",
    "docs",
    "refactor",
    "test",
    "style",
    "perf",
)
_TYPES = "|".join(CONVENTIONAL_TYPES)
BRANCH_RE = re.compile(rf"^({_TYPES})/.+")
SUBJECT_RE = re.compile(rf"^({_TYPES})(\(([a-z0-9._-]+)\))?: .+")

BANNER = "# skinner:module"
BODY_WIDTH = 72

# What the fixture sanctions an agent to add. Anything else is an invented destination:
# one trial created docs/superpowers/specs/ in a fixture whose almanac says not to.
SANCTIONED_PREFIXES = ("src/", "tests/")

# Hooks are shared by every worktree, so this fires in the session worktree too and the
# log tolerates repeated lines. A sandbox that denies writes under .git silences it
# entirely, which is why an empty log scores unrecoverable rather than failed.
HOOK = """#!/bin/sh
# Records each checkout's working tree so a worktree name survives its removal.
git rev-parse --show-toplevel >> "$(git rev-parse --git-common-dir)/{log}" 2>/dev/null || true
"""


class SkelError(Exception):
    pass


@dataclass(frozen=True)
class Finding:
    check: str
    status: str  # "pass" | "fail" | "unrecoverable"
    detail: str


def _git(run: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(run), *args], capture_output=True, text=True, check=True
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
    _git(run, "commit", "-q", "-m", INITIAL_COMMIT)
    return run


def _install_hook(run: Path) -> None:
    hooks = run / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "post-checkout"
    hook.write_text(HOOK.format(log=WORKTREE_LOG))
    hook.chmod(0o755)
