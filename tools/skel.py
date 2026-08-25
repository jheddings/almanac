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

REFLOG_BRANCH_RES = (
    re.compile(r"^merge (\S+):"),
    re.compile(r"^checkout: moving from \S+ to (\S+)$"),
)

BANNER = "# skinner:module"
BODY_WIDTH = 72

# Where new files may legitimately go. Anything else is an invented destination: one
# trial created docs/superpowers/specs/ in a fixture whose almanac says not to.
SANCTIONED_PREFIXES = ("src/", "tests/")

# The instrument: the rules a run is measured against. Editing these changes what the
# run was tested on. Build config is not on this list — a console script cannot be
# added without touching pyproject.toml, and flagging that reports required work as
# contamination while a run that rewrote AGENTS.md passes.
PROTECTED_PATHS = ("AGENTS.md", "CLAUDE.md", "docs/almanac/")

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


def check_branch(branches: list[str]) -> Finding:
    if not branches:
        return Finding("branch prefix", "unrecoverable", "no branch beyond main")
    bad = [b for b in branches if not BRANCH_RE.match(b)]
    if bad:
        return Finding("branch prefix", "fail", f"no conventional type: {bad}")
    return Finding("branch prefix", "pass", ", ".join(branches))


def check_commit_subjects(subjects: list[str]) -> Finding:
    if not subjects:
        return Finding("commit subject", "unrecoverable", "no commits beyond the first")
    bad = [s for s in subjects if not SUBJECT_RE.match(s)]
    if bad:
        return Finding("commit subject", "fail", f"not conventional: {bad}")
    scoped = sum(1 for s in subjects if SUBJECT_RE.match(s).group(2))
    shape = (
        "scoped"
        if scoped == len(subjects)
        else f"unscoped ({scoped}/{len(subjects)} scoped)"
    )
    return Finding("commit subject", "pass", shape)


def check_commit_bodies(bodies: list[str]) -> Finding:
    lines = [line for body in bodies for line in body.splitlines()]
    if not lines:
        return Finding("commit body wrap", "unrecoverable", "no commit bodies")
    over = [line for line in lines if len(line) > BODY_WIDTH]
    if over:
        return Finding(
            "commit body wrap", "fail", f"{len(over)} line(s) over {BODY_WIDTH}"
        )
    return Finding("commit body wrap", "pass", f"max {max(len(l) for l in lines)}")


def check_worktree_names(logged: list[str], branches: list[str]) -> Finding:
    if not logged:
        return Finding(
            "worktree session-scoped",
            "unrecoverable",
            "hook log empty — cleaned up, cloned, or .git not writable",
        )
    if not branches:
        return Finding(
            "worktree session-scoped",
            "unrecoverable",
            f"{', '.join(logged)} — no branch survives to compare the name against",
        )
    slugs = {b.split("/", 1)[-1] for b in branches}
    echoes = [name for name in logged if name in slugs]
    if echoes:
        return Finding(
            "worktree session-scoped", "fail", f"named for its branch: {echoes}"
        )
    return Finding("worktree session-scoped", "pass", ", ".join(logged))


def check_fixture_edited(changed: list[str]) -> Finding:
    touched = [p for p in changed if p.startswith(PROTECTED_PATHS)]
    if touched:
        return Finding("fixture edited", "fail", f"instrument modified: {touched}")
    return Finding("fixture edited", "pass", "instrument untouched")


def check_fixture_extended(added: list[str]) -> Finding:
    invented = [p for p in added if not p.startswith(SANCTIONED_PREFIXES)]
    if invented:
        return Finding("fixture extended", "fail", f"invented: {invented}")
    return Finding("fixture extended", "pass", "no invented destinations")


def check_canary(first_lines: dict[str, str]) -> Finding:
    if not first_lines:
        return Finding("canary banner", "unrecoverable", "no new source modules")
    carried = [p for p, line in first_lines.items() if line.strip() == BANNER]
    total = len(first_lines)
    if len(carried) == total:
        return Finding("canary banner", "pass", f"{total}/{total} modules")
    missing = sorted(set(first_lines) - set(carried))
    return Finding(
        "canary banner", "fail", f"{len(carried)}/{total} modules; missing {missing}"
    )


def _base_commit(run: Path) -> str:
    """The fixture's own initial commit — everything after it is the run's work."""
    return _git(run, "rev-list", "--max-parents=0", "HEAD").strip().splitlines()[0]


def _worktree_names(run: Path) -> list[str]:
    log = Path(_git(run, "rev-parse", "--git-common-dir").strip())
    if not log.is_absolute():
        log = run / log
    log = log / WORKTREE_LOG
    if not log.is_file():
        return []
    seen = []
    for line in log.read_text().splitlines():
        name = Path(line.strip()).name
        if name and name != run.name and name not in seen:
            seen.append(name)
    return seen


def branch_names(run: Path) -> list[str]:
    """Every branch the run worked on, including ones it deleted.

    Live refs are not enough: an agent that merges and deletes its branch leaves none,
    and then a worktree named for that branch has nothing to be compared against. The
    reflog outlives the ref, so it is what makes the check survive a tidy agent.
    """
    found = []
    for line in _git(run, "branch", "--format=%(refname:short)").splitlines():
        name = line.strip().lstrip("* ")
        if name and name != "main" and name not in found:
            found.append(name)

    for entry in _git(run, "reflog", "--format=%gs").splitlines():
        for pattern in REFLOG_BRANCH_RES:
            match = pattern.match(entry.strip())
            if match and match.group(1) != "main" and match.group(1) not in found:
                found.append(match.group(1))
    return found


def find_run(runs: Path, label: str) -> Path:
    """The most recent run directory under `runs` whose name contains `label`."""
    matches = sorted(p for p in runs.glob(f"*{label}*") if p.is_dir())
    if not matches:
        raise SkelError(f"no run matching {label!r} under {runs}")
    return matches[-1]


def _work_tip(run: Path, base: str) -> str:
    """The ref carrying this run's work.

    Half the first four trials left their work on a branch they never merged, so
    reading HEAD alone reported those runs as empty.
    """
    tip, ahead = "HEAD", 0
    refs = ["HEAD"] + [
        line.strip()
        for line in _git(run, "branch", "--format=%(refname:short)").splitlines()
        if line.strip()
    ]
    for ref in refs:
        try:
            count = int(_git(run, "rev-list", "--count", f"{base}..{ref}").strip())
        except (subprocess.CalledProcessError, ValueError):
            continue
        if count > ahead:
            tip, ahead = ref, count
    return tip


def score(run: Path) -> list[Finding]:
    """Every check, run against one completed harness-test run."""
    base = _base_commit(run)
    tip = _work_tip(run, base)
    revs = f"{base}..{tip}"

    branches = branch_names(run)
    subjects = [s for s in _git(run, "log", "--format=%s", revs).splitlines() if s]
    bodies = _git(run, "log", "--format=%b%x00", revs).split("\x00")

    status = _git(run, "diff", "--name-status", base, tip).splitlines()
    changed = [line.split("\t", 1)[1] for line in status if line.startswith("M")]
    added = [line.split("\t", 1)[1] for line in status if line.startswith("A")]

    first_lines = {}
    for path in added:
        if path.startswith("src/") and path.endswith(".py"):
            if Path(path).name == "__init__.py":
                continue
            body = _git(run, "show", f"{tip}:{path}")
            first_lines[path] = body.splitlines()[0] if body.splitlines() else ""

    return [
        check_worktree_names(_worktree_names(run), branches),
        check_branch(branches),
        check_commit_subjects(subjects),
        check_commit_bodies([b for b in bodies if b.strip()]),
        check_canary(first_lines),
        check_fixture_edited(changed),
        check_fixture_extended(added),
    ]
