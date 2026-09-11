# skel Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Status: executed, and partly superseded.** The rig was built from this plan, then
> two things in it were reversed. The mechanical scorer of Tasks 7 and 8 was removed —
> it was wrong on two of four known cases on first contact and encoded judgment a person
> makes faster from a diff. And the `skel-*` recipes of Task 10 became a `just` module,
> so `just skel new` replaces `just skel-new`. Read
> [the design](2026-08-24-skel-harness-design.md) for what the rig is now; this file
> records how it was built.

**Goal:** Build `skel/`, a portable fixture for testing whether an agent harness
retrieves and applies almanac rules, plus a scorer that measures the same things every
run.

**Architecture:** `skel/` is the fixture — everything the agent under test sees, checked
in complete so it opens anywhere. The rig lives outside it: `prompts/` holds the asks,
`tools/skel.py` scaffolds runs and scores them, and `runs/` is gitignored output.
`skel new` emits a standalone git repo so cloud platforms that clone can run it too.
Scoring reads git state, never transcripts.

**Tech Stack:** Python 3.12, click (already the CLI layer in `tools/cli.py`), pytest,
`just` recipes, git plumbing via `subprocess`.

Design: [2026-08-24-skel-harness-design.md](2026-08-24-skel-harness-design.md).

---

## File structure

| Path                                   | Responsibility                                       |
| -------------------------------------- | ---------------------------------------------------- |
| `skel/**`                              | The fixture. Everything the agent sees.              |
| `skel/docs/almanac/`                   | Contract + four rule entries (three git, one canary) |
| `skel/.devcontainer/devcontainer.json` | Toolchain only — no harness CLIs                     |
| `prompts/01-first-feature.md`          | The baseline ask                                     |
| `tools/skel.py`                        | Scaffold a run; score a run. Pure checks + git I/O   |
| `tools/cli.py`                         | Wires `skel` subcommands (existing file)             |
| `tools/drift.py`                       | Compares template against N instances (existing)     |
| `tests/test_skel.py`                   | Unit tests for every check                           |
| `tests/test_drift.py`                  | Extended for multiple instances (existing)           |

---

### Task 1: Land the fixture tree

**Files:**

- Create: `skel/` (whole tree)
- Modify: `.gitignore`

- [ ] **Step 1: Extract the pristine fixture from an existing run**

The four completed trials each hold the untouched fixture at their initial commit
`51b4124`. Any of them works; `sonnet` and `codex` left it unmodified.

```bash
mkdir -p skel
git -C ~/Projects/skinner/sonnet archive 51b4124 | tar -x -C skel/
ls skel/
```

Expected:
`AGENTS.md  LICENSE  README.md  docs  pyproject.toml  src  tests  .gitignore .justfile  uv.lock`

If `~/Projects/skinner` is gone, the same tree is reachable from this branch's history
once Task 1 is committed; recover with `git show <sha>:skel/<path>`.

- [ ] **Step 2: Verify the fixture's almanac arrived intact**

```bash
ls skel/docs/almanac/
```

Expected exactly four files:

```text
README.md
branch-names-carry-the-commit-type-as-a-prefix.md
commit-messages-use-conventional-commit-format.md
development-happens-in-a-session-scoped-worktree.md
```

- [ ] **Step 3: Ignore run output**

Append to `.gitignore`:

```text

# Harness-test runs produced by `just skel new`.
runs/
```

- [ ] **Step 4: Commit**

```bash
git add skel .gitignore
git commit -m "feat(skel): add the harness-test fixture tree"
```

---

### Task 2: Add the canary rule

A rule with no prior in any model, whose compliance lands in the committed diff. This is
what makes retrieval mechanically scoreable — every other rule can be reached by
imitation or prior, so a hit proves nothing about the almanac. `# skinner:module` proves
the entry was read.

The fixture deliberately contains **no example** of the banner.
`src/skinner/__init__.py` is exempt by the rule's own text, so an agent cannot copy the
convention from a neighbouring file; it can only get it from the entry.

**Files:**

- Create: `skel/docs/almanac/new-source-modules-open-with-the-provenance-banner.md`

- [ ] **Step 1: Write the entry**

````markdown
---
title: New source modules open with the provenance banner
kind: rule
recorded: 2026-08-24
source: "Project conventions, set when this repository was initialized"
tags: [python, source-layout, conventions]
---

**Applies when:** you are about to create a new `.py` file under `src/skinner/`.

Every source module opens with this exact line, before the module docstring:

```text
# skinner:module
```

Package `__init__.py` files are exempt and carry no banner.

**Why:** the banner marks a file as the package's own source rather than generated or
vendored code. Nothing enforces it, so a module missing the banner produces no error
anyone will see — it is simply wrong and silent.
````

- [ ] **Step 2: Verify it conforms to the entry contract**

```bash
uv run python -c "
from tests.support import almanac
from tests.test_entry_frontmatter import check_entry_frontmatter
from pathlib import Path
p = Path('skel/docs/almanac/new-source-modules-open-with-the-provenance-banner.md')
data = almanac.parse_frontmatter(p.read_text())
print(check_entry_frontmatter(data) or 'conforms')
"
```

Expected: `conforms`

- [ ] **Step 3: Commit**

```bash
git add skel/docs/almanac/new-source-modules-open-with-the-provenance-banner.md
git commit -m "feat(skel): add the canary rule that proves retrieval"
```

---

### Task 3: Add the devcontainer

Toolchain only. A `devcontainer.json` installing `claude`, `codex` and `gemini` side by
side tells the agent it is one of several being compared, which is the tell we keep out
of the fixture.

**Files:**

- Create: `skel/.devcontainer/devcontainer.json`

- [ ] **Step 1: Write it**

```json
{
    "name": "skinner",
    "image": "mcr.microsoft.com/devcontainers/python:3.12",
    "features": {
        "ghcr.io/devcontainers/features/git:1": {}
    },
    "postCreateCommand": "curl -LsSf https://astral.sh/uv/install.sh | sh && curl -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin",
    "customizations": {
        "vscode": {
            "extensions": ["charliermarsh.ruff"]
        }
    }
}
```

- [ ] **Step 2: Verify it parses**

```bash
uv run python -c "import json,pathlib; json.loads(pathlib.Path('skel/.devcontainer/devcontainer.json').read_text()); print('valid json')"
```

Expected: `valid json`

- [ ] **Step 3: Commit**

```bash
git add skel/.devcontainer
git commit -m "feat(skel): add a toolchain-only devcontainer"
```

---

### Task 4: Extend drift to cover the fixture's almanac

`skel/docs/almanac/README.md` is a third instance of the canonical template. An
uncovered fixture goes stale against the contract it exists to test.

**Files:**

- Modify: `tools/drift.py:20-21`, `tools/drift.py:58-60`
- Modify: `tools/cli.py` (the `drift_cmd` body)
- Test: `tests/test_drift.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_drift.py`:

```python
def test_every_declared_instance_is_compared(tmp_path, monkeypatch):
    """A second instance that drifts must fail the check, not be skipped."""
    template = tmp_path / "template.md"
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    template.write_text(document("Shared prose.", "t"))
    good.write_text(document("Shared prose.", "g"))
    bad.write_text(document("Shared prose, edited.", "b"))

    monkeypatch.setattr(drift, "TEMPLATE", template)
    monkeypatch.setattr(drift, "INSTANCES", (good, bad))
    assert drift.check()


def test_the_fixture_almanac_is_a_declared_instance():
    """Guard the guard: the fixture must actually be in the list."""
    names = [str(p) for p in drift.INSTANCES]
    assert any(p.endswith("skel/docs/almanac/README.md") for p in names), names
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_drift.py -v`

Expected: FAIL — `AttributeError: module 'tools.drift' has no attribute 'INSTANCES'`

- [ ] **Step 3: Replace the single instance with a list**

In `tools/drift.py`, replace:

```python
INSTANCE = REPO_ROOT / "docs" / "almanac" / "README.md"
```

with:

```python
# Every copy of the canonical contract in this tree. The live almanac is this repo's
# own; the fixture's is what a harness-test run adopts, and an uncovered fixture goes
# stale against the contract it exists to test.
INSTANCES = (
    REPO_ROOT / "docs" / "almanac" / "README.md",
    REPO_ROOT / "skel" / "docs" / "almanac" / "README.md",
)
```

and replace:

```python
def check() -> list[str]:
    return compare(TEMPLATE, INSTANCE)
```

with:

```python
def check() -> list[str]:
    problems = []
    for instance in INSTANCES:
        problems += compare(TEMPLATE, instance)
    return problems
```

- [ ] **Step 4: Update the CLI, which names `drift.INSTANCE`**

In `tools/cli.py`, replace the body of `drift_cmd` with:

```python
@click.command("drift")
def drift_cmd():
    """Check every almanac README against the shipped template."""
    diff = drift.check()
    if diff:
        click.echo("".join(diff), nl=False)
        raise click.ClickException(
            f"an almanac README differs from {drift.TEMPLATE} outside the local "
            f"block. The template is canonical: port the change to it, or move the "
            f"text inside the {drift.OPEN} block when it is genuinely repo-local."
        )
    for instance in drift.INSTANCES:
        click.echo(f"{instance} matches {drift.TEMPLATE} outside the local block")
```

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/test_drift.py -v && uv run python -m tools drift`

Expected: all pass; `drift` prints two `matches` lines.

- [ ] **Step 6: Commit**

```bash
git add tools/drift.py tools/cli.py tests/test_drift.py
git commit -m "feat(drift): compare the template against every instance"
```

---

### Task 5: Cover the fixture's entries with the contract tests

**Files:**

- Modify: `tests/support/almanac.py`
- Modify: `tests/test_entry_frontmatter.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_entry_frontmatter.py`:

```python
@pytest.mark.parametrize(
    "path", almanac.fixture_entry_paths(), ids=lambda p: p.name if p else "none"
)
def test_fixture_entry_frontmatter_conforms(path):
    """The fixture ships a contract; its own entries must satisfy it."""
    data = almanac.parse_frontmatter(path.read_text())
    assert data is not None, f"{path.name}: no frontmatter"
    assert check_entry_frontmatter(data) == [], f"{path.name}"


def test_the_fixture_carries_entries():
    """Guard the guard: an empty glob would make the check above vacuous."""
    assert almanac.fixture_entry_paths()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_entry_frontmatter.py -v`

Expected: FAIL — `AttributeError: module has no attribute 'fixture_entry_paths'`

- [ ] **Step 3: Add the helper**

In `tests/support/almanac.py`, below `LIVE_ALMANAC`, add:

```python
FIXTURE_ALMANAC = REPO_ROOT / "skel" / "docs" / "almanac"
```

and below `entry_paths()`, add:

```python
def fixture_entry_paths() -> list[Path]:
    """Every entry in the harness-test fixture's almanac."""
    if not FIXTURE_ALMANAC.is_dir():
        return []
    return sorted(p for p in FIXTURE_ALMANAC.glob("*.md") if p.name != ALMANAC_README)
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_entry_frontmatter.py -v`

Expected: PASS, with four `test_fixture_entry_frontmatter_conforms` cases.

- [ ] **Step 5: Commit**

```bash
git add tests/support/almanac.py tests/test_entry_frontmatter.py
git commit -m "test(skel): hold the fixture's entries to the entry contract"
```

---

### Task 6: `skel new` — scaffold a standalone run

**Files:**

- Create: `tools/skel.py`
- Test: `tests/test_skel.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_skel.py`:

```python
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
        capture_output=True, text=True, check=True,
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_skel.py -v`

Expected: FAIL — `ModuleNotFoundError: No module named 'tools.skel'`

- [ ] **Step 3: Write the implementation**

Create `tools/skel.py`:

```python
"""Scaffold and score harness-test runs built from the `skel/` fixture.

A run is a standalone git repository, not a copy inside this one, because cloud
platforms clone a repo rather than opening a subfolder. Scoring reads git state and
never a transcript: one trial reported following the worktree rule while the directory
on disk was named after the feature.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from tools.harnesses import REPO_ROOT

FIXTURE = REPO_ROOT / "skel"
RUNS = REPO_ROOT / "runs"
PROMPTS = REPO_ROOT / "prompts"

# Written under .git/, so it is outside the working tree and not something an agent
# lists, reads, or commits.
WORKTREE_LOG = "skel-worktrees.log"

INITIAL_COMMIT = "chore: initialize the project skeleton and almanac"

# Hooks are shared by every worktree, so this fires in the session worktree too and the
# log tolerates repeated lines. A sandbox that denies writes under .git silences it
# entirely, which is why an empty log scores unrecoverable rather than failed.
HOOK = """#!/bin/sh
# Records each checkout's working tree so a worktree name survives its removal.
git rev-parse --show-toplevel >> "$(git rev-parse --git-common-dir)/{log}" 2>/dev/null || true
"""


class SkelError(Exception):
    pass


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
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_skel.py -v`

Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/skel.py tests/test_skel.py
git commit -m "feat(skel): scaffold a run as a standalone repository"
```

---

### Task 7: The checks

Every check is a pure function over git facts so it can be tested without a harness.
Each returns a `Finding` whose status is `pass`, `fail`, or `unrecoverable` — the third
exists because a sandbox that denies `.git` writes breaks the hook and the worktree rule
in the same stroke, and scoring those as failures would manufacture a result.

**Files:**

- Modify: `tools/skel.py`
- Test: `tests/test_skel.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_skel.py`:

```python
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
    assert skel.check_worktree_names(["food-pellet"], ["feat/cli-entry-point"]).status == "pass"
    assert skel.check_worktree_names(["cli-version"], ["feat/cli-version"]).status == "fail"


def test_worktree_check_is_unrecoverable_when_the_log_is_empty():
    """A sandbox that denies .git writes silences the hook; that is not a failure."""
    assert skel.check_worktree_names([], ["feat/x"]).status == "unrecoverable"


def test_fixture_edited_and_extended_are_separate_checks():
    """One trial edited AGENTS.md; a different one invented a directory instead."""
    assert skel.check_fixture_edited(["AGENTS.md"]).status == "fail"
    assert skel.check_fixture_edited(["src/skinner/cli.py"]).status == "pass"

    assert skel.check_fixture_extended(["docs/superpowers/specs/x.md"]).status == "fail"
    assert skel.check_fixture_extended(["src/skinner/cli.py", "tests/test_cli.py"]).status == "pass"


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
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/test_skel.py -v`

Expected: FAIL — `AttributeError: module 'tools.skel' has no attribute 'check_branch'`

- [ ] **Step 3: Write the implementation**

In `tools/skel.py`, add `import re` and `from dataclasses import dataclass` to the
existing import block at the top of the module. Add the constants below the existing
constants, and the functions at the end of the file.

```python
CONVENTIONAL_TYPES = (
    "feat", "fix", "chore", "docs", "refactor", "test", "style", "perf",
)
_TYPES = "|".join(CONVENTIONAL_TYPES)
BRANCH_RE = re.compile(rf"^({_TYPES})/.+")
SUBJECT_RE = re.compile(rf"^({_TYPES})(\(([a-z0-9._-]+)\))?: .+")

BANNER = "# skinner:module"
BODY_WIDTH = 72

# What the fixture sanctions an agent to add. Anything else is an invented destination:
# one trial created docs/superpowers/specs/ in a fixture whose almanac says not to.
SANCTIONED_PREFIXES = ("src/", "tests/")


@dataclass(frozen=True)
class Finding:
    check: str
    status: str  # "pass" | "fail" | "unrecoverable"
    detail: str


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
    shape = "scoped" if scoped == len(subjects) else f"unscoped ({scoped}/{len(subjects)} scoped)"
    return Finding("commit subject", "pass", shape)


def check_commit_bodies(bodies: list[str]) -> Finding:
    lines = [line for body in bodies for line in body.splitlines()]
    if not lines:
        return Finding("commit body wrap", "unrecoverable", "no commit bodies")
    over = [line for line in lines if len(line) > BODY_WIDTH]
    if over:
        return Finding("commit body wrap", "fail", f"{len(over)} line(s) over {BODY_WIDTH}")
    return Finding("commit body wrap", "pass", f"max {max(len(l) for l in lines)}")


def check_worktree_names(logged: list[str], branches: list[str]) -> Finding:
    if not logged:
        return Finding(
            "worktree session-scoped",
            "unrecoverable",
            "hook log empty — cleaned up, cloned, or .git not writable",
        )
    slugs = {b.split("/", 1)[-1] for b in branches}
    echoes = [name for name in logged if name in slugs]
    if echoes:
        return Finding(
            "worktree session-scoped", "fail", f"named for its branch: {echoes}"
        )
    return Finding("worktree session-scoped", "pass", ", ".join(logged))


def check_fixture_edited(changed: list[str]) -> Finding:
    touched = [p for p in changed if not p.startswith(SANCTIONED_PREFIXES)]
    if touched:
        return Finding("fixture edited", "fail", f"modified: {touched}")
    return Finding("fixture edited", "pass", "fixture files untouched")


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
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_skel.py -v`

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/skel.py tests/test_skel.py
git commit -m "feat(skel): add the rule checks"
```

---

### Task 8: `skel check` — gather git facts and report

**Files:**

- Modify: `tools/skel.py`
- Test: `tests/test_skel.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_skel.py`:

```python
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
    subprocess.run(["git", "-C", str(run), "checkout", "-q", "-b", "feat/cli"], check=True)
    _commit(run, "feat(cli): add an entry point", "src/skinner/cli.py", "# skinner:module\n")

    findings = {f.check: f for f in skel.score(run)}
    assert findings["branch prefix"].status == "pass"
    assert findings["commit subject"].status == "pass"
    assert findings["canary banner"].status == "pass"
    assert findings["fixture edited"].status == "pass"
    assert findings["fixture extended"].status == "pass"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_skel.py::test_score_reads_a_real_run -v`

Expected: FAIL — `AttributeError: module 'tools.skel' has no attribute 'score'`

- [ ] **Step 3: Write the implementation**

Append to `tools/skel.py`:

```python
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


def score(run: Path) -> list[Finding]:
    """Every check, run against one completed harness-test run."""
    base = _base_commit(run)
    revs = f"{base}..HEAD"

    branches = [
        b.strip().lstrip("* ")
        for b in _git(run, "branch", "--format=%(refname:short)").splitlines()
        if b.strip() and b.strip().lstrip("* ") != "main"
    ]
    subjects = [s for s in _git(run, "log", "--format=%s", revs).splitlines() if s]
    bodies = _git(run, "log", "--format=%b%x00", revs).split("\x00")

    status = _git(run, "diff", "--name-status", base, "HEAD").splitlines()
    changed = [line.split("\t", 1)[1] for line in status if line.startswith("M")]
    added = [line.split("\t", 1)[1] for line in status if line.startswith("A")]

    first_lines = {}
    for path in added:
        if path.startswith("src/") and path.endswith(".py"):
            if Path(path).name == "__init__.py":
                continue
            body = _git(run, "show", f"HEAD:{path}")
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
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_skel.py -v`

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/skel.py tests/test_skel.py
git commit -m "feat(skel): score a completed run from its git state"
```

---

### Task 9: The prompt

**Files:**

- Create: `prompts/01-first-feature.md`

- [ ] **Step 1: Write it**

The ask names no convention, no branch format, no worktree, and never says "almanac".
"On its own branch" stays for now: it gives the branch rule an independent shot rather
than letting one worktree miss cascade. Drop it once the worktree rule is settled.

```markdown
This project is brand new — it doesn't do anything yet. Add a command-line entry point
so `skinner` can be run from the terminal, starting with a `--version` flag that prints
the package version. Include a test. Commit the work on its own branch when it's done.
```

- [ ] **Step 2: Commit**

```bash
git add prompts/01-first-feature.md
git commit -m "feat(skel): add the baseline prompt"
```

---

### Task 10: Wire up the CLI and the recipe

**Files:**

- Modify: `tools/cli.py`
- Modify: `.justfile`

- [ ] **Step 1: Add the commands**

In `tools/cli.py`, add `skel` to the imports:

```python
from tools import bundle, drift, harnesses, manifests, release, skel
```

Add `skel.SkelError` to `ToolsGroup.LIBRARY_ERRORS`:

```python
    LIBRARY_ERRORS = (
        bundle.BundleError,
        drift.DriftError,
        release.ReleaseError,
        harnesses.UnknownHarness,
        skel.SkelError,
    )
```

Add the commands before the `cli.add_command` block:

```python
@click.command("skel-new")
@click.argument("label")
@click.option("--stamp", default=None, help="Date stamp; defaults to today.")
def skel_new_cmd(label, stamp):
    """Scaffold a harness-test run as a standalone repository."""
    import datetime

    stamp = stamp or datetime.date.today().isoformat()
    run = skel.new_run(skel.FIXTURE, skel.RUNS, label, stamp)
    click.echo(f"run ready: {run}")


@click.command("skel-prompt")
@click.argument("name", default="01-first-feature")
def skel_prompt_cmd(name):
    """Print a prompt for pasting into the harness under test."""
    path = skel.PROMPTS / f"{name}.md"
    if not path.is_file():
        raise click.ClickException(f"{path}: no such prompt")
    click.echo(path.read_text().strip())


@click.command("skel-check")
@click.argument("label")
def skel_check_cmd(label):
    """Score a completed run against the almanac's rules."""
    matches = sorted(skel.RUNS.glob(f"*{label}*"))
    if not matches:
        raise click.ClickException(f"no run matching {label!r} under {skel.RUNS}")
    run = matches[-1]

    click.echo(f"{run.name}")
    for finding in skel.score(run):
        mark = {"pass": "PASS", "fail": "FAIL", "unrecoverable": "----"}[finding.status]
        click.echo(f"  {mark}  {finding.check}: {finding.detail}")
```

Register them at the bottom, alongside the existing `cli.add_command` calls:

```python
cli.add_command(skel_new_cmd)
cli.add_command(skel_prompt_cmd)
cli.add_command(skel_check_cmd)
```

- [ ] **Step 2: Add the recipes**

Append to `.justfile`:

```make
# scaffold a harness-test run from the skel fixture
skel-new label: venv
    uv run python -m tools skel-new {{ label }}

# print a prompt to paste into the harness under test
skel-prompt name="01-first-feature": venv
    uv run python -m tools skel-prompt {{ name }}

# scaffold a run and print the prompt to paste
skel-run label name="01-first-feature": (skel-new label) (skel-prompt name)

# score a completed harness-test run
skel-check label: venv
    uv run python -m tools skel-check {{ label }}

# remove harness-test runs
skel-clean:
    rm -rf "{{ basedir }}/runs"
```

- [ ] **Step 3: Verify end to end**

```bash
just skel-run smoke
just skel-check smoke
just skel-clean
```

Expected: `skel-run` prints `run ready: .../runs/<today>-smoke` followed by the prompt.
`skel-check` prints one line per check — `branch prefix` and `commit subject`
`unrecoverable` (no work done yet), `fixture edited` and `fixture extended` `PASS`.

- [ ] **Step 4: Run the full preflight**

Run: `just preflight`

Expected: prettier clean, three skills valid, manifests agree, drift prints two matches,
all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tools/cli.py .justfile
git commit -m "feat(skel): wire the rig into the CLI and recipes"
```

---

## What this plan does not build

No headless invocation, no matrix runner, no result aggregation — the design defers all
three until the prompts have earned their keep.

The scorer measures rule-following, not retrieval strategy. Whether an agent read the
listing or the whole directory leaves no trace in git; that stays a transcript read. The
canary is the one exception, and it only proves the entry was reached, not how.

Decay across a session needs a prompt that induces several new modules.
`01-first-feature` produces one or two, so `check_canary` reports `1/1` and measures
nothing about fade. A multi-module prompt is the obvious `02`.
