# skel Cursor Trial Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Declare `[cursor.trial]` and teach `tools/trial.py` to take `{session}` from
an optional `create` command, so `just skel trial cursor` can drive Cursor unattended
the same way Claude already is.

**Architecture:** Session naming stays a row in `harnesses.toml`. `Trial.create` is
optional; when set, the driver runs it in the run directory and uses stripped stdout as
`{session}` before `first`. Claude keeps generating the id itself. No Cursor branch in
Python.

**Tech Stack:** Python 3.12, the existing `tools/harnesses.py` table loader,
`tools/trial.py` driver, pytest. No live `agent` binary, no network.

Design:
[2026-08-26-skel-cursor-trial-design.md](2026-08-26-skel-cursor-trial-design.md).

---

## File structure

| Path                      | Responsibility                                                 |
| ------------------------- | -------------------------------------------------------------- |
| `tools/harnesses.py`      | `Trial.create`, loaded from optional `create` on `[*.trial]`   |
| `tools/trial.py`          | Resolve `{session}` from `create` stdout when the field is set |
| `harnesses.toml`          | `[cursor.trial]` row                                           |
| `tests/test_harnesses.py` | Loader: optional `create`, required fields, Cursor row parses  |
| `tests/test_trial.py`     | Driver: create-before-first, failure names the harness         |

---

### Task 1: Optional `create` on the trial schema

**Files:**

- Modify: `tools/harnesses.py`
- Test: `tests/test_harnesses.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_harnesses.py`:

```python
def test_trial_create_is_optional():
    """Claude names the session as a flag; a missing create must not be an error."""
    loaded = harnesses._harness(
        "paper",
        {
            "manifest": "harnesses.toml",
            "trial": {
                "first": ["echo", "{prompt}"],
                "resume": ["echo", "{prompt}"],
                "transcript": "{session}.jsonl",
            },
        },
    )
    assert loaded.trial is not None
    assert loaded.trial.create == ()


def test_trial_create_is_loaded_when_present():
    loaded = harnesses._harness(
        "paper",
        {
            "manifest": "harnesses.toml",
            "trial": {
                "create": ["agent", "create-chat"],
                "first": ["echo", "{session}"],
                "resume": ["echo", "{session}"],
                "transcript": "{session}.jsonl",
            },
        },
    )
    assert loaded.trial.create == ("agent", "create-chat")


def test_trial_required_fields_stay_required():
    """create is the new optional; first, resume, and transcript are not."""
    row = {
        "manifest": "harnesses.toml",
        "trial": {
            "resume": ["echo", "{prompt}"],
            "transcript": "{session}.jsonl",
        },
    }
    with pytest.raises(KeyError, match="first"):
        harnesses._harness("paper", row)
```

- [ ] **Step 2: Run them to verify they fail**

Run:
`uv run pytest tests/test_harnesses.py::test_trial_create_is_optional tests/test_harnesses.py::test_trial_create_is_loaded_when_present -v`

Expected: FAIL — `AttributeError: 'Trial' object has no attribute 'create'`

- [ ] **Step 3: Add `create` to `Trial` and load it**

In `tools/harnesses.py`, replace the `Trial` dataclass with:

```python
@dataclass(frozen=True)
class Trial:
    """How to drive this harness through the fixture, unattended.

    `first` opens the session and `resume` continues it, so the prompts arrive as one
    conversation rather than several — which is what makes a rule firing on the last
    prompt evidence that it survived the whole session.

    Some harnesses name the session themselves. `create`, when set, is run in the run
    directory first; stripped stdout becomes `{session}` for `first` and `resume`.
    """

    first: tuple[str, ...]
    resume: tuple[str, ...]
    transcript: str
    create: tuple[str, ...] = ()
    version: tuple[str, ...] = ()
```

In `_harness`, pass `create` next to the other trial fields:

```python
        Trial(
            first=tuple(raw_trial["first"]),
            resume=tuple(raw_trial["resume"]),
            transcript=raw_trial["transcript"],
            create=tuple(raw_trial.get("create", ())),
            version=tuple(raw_trial.get("version", ())),
        )
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_harnesses.py -v`

Expected: all PASS, including `test_trial_required_fields_stay_required`.

- [ ] **Step 5: Commit**

```bash
git add tools/harnesses.py tests/test_harnesses.py
git commit -m "$(cat <<'EOF'
feat(skel): accept an optional create on the trial schema

Cursor names a session by printing a UUID. The field is optional so
Claude keeps generating the id itself.

EOF
)"
```

---

### Task 2: Resolve `{session}` from `create` stdout

**Files:**

- Modify: `tools/trial.py`
- Test: `tests/test_trial.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_trial.py`:

```python
def test_create_stdout_is_the_session_the_prompts_attach_to(tmp_path, claude):
    """The harness names the session; the driver must not invent a second id."""
    recorder = tmp_path / "calls.txt"
    stub = harnesses.Harness(
        name="cursor",
        manifest=claude.manifest,
        trial=harnesses.Trial(
            create=("sh", "-c", f"echo create >> {recorder}; printf 'sess-1\\n'"),
            first=("sh", "-c", f"echo first {{session}} >> {recorder}"),
            resume=("sh", "-c", f"echo resume {{session}} >> {recorder}"),
            transcript=str(tmp_path / "{session}.jsonl"),
        ),
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
```

- [ ] **Step 2: Run them to verify they fail**

Run:
`uv run pytest tests/test_trial.py::test_create_stdout_is_the_session_the_prompts_attach_to tests/test_trial.py::test_a_failing_create_names_the_harness_and_does_not_prompt tests/test_trial.py::test_empty_create_stdout_is_a_failure -v`

Expected: FAIL — the first test sees a generated UUID in the recorder (or `create` never
runs); the failure tests never raise `TrialError`.

- [ ] **Step 3: Resolve the session after scaffolding**

In `tools/trial.py`, add `_session` above `run`, and call it after `new_run` instead of
generating the UUID up front.

```python
def _session(harness: Harness, run_dir: Path) -> str:
    """The id `first` and `resume` will attach to.

    When `create` is set, the harness names the session — Cursor's `create-chat`
    prints a UUID — and an empty or failed create is not a prompt failure: nothing
    has been asked yet, so there is nothing to archive.
    """
    if not harness.trial.create:
        return str(uuid.uuid4())
    done = subprocess.run(
        list(harness.trial.create),
        cwd=run_dir,
        capture_output=True,
        text=True,
        timeout=60,
        env=skel.clean_env(),
    )
    if done.returncode != 0:
        raise TrialError(f"{harness.name}: create exited {done.returncode}")
    session = done.stdout.strip()
    if not session:
        raise TrialError(f"{harness.name}: create produced no session id")
    return session
```

In `run`, replace `session = str(uuid.uuid4())` and the `new_run` / `_drive` pair with:

```python
    workspace = Path(tempfile.mkdtemp(prefix=f"skel-trial-{harness.name}-"))

    try:
        run_dir = skel.new_run(skel.FIXTURE, workspace, harness.name, stamp)
        session = _session(harness, run_dir)
        results = _drive(harness, run_dir, session, prompts, texts)
```

Do not `.format()` the create command: `{session}` does not exist yet.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_trial.py -v`

Expected: all PASS. Existing Claude stubs still generate a UUID and still call `first`
then `resume`.

- [ ] **Step 5: Commit**

```bash
git add tools/trial.py tests/test_trial.py
git commit -m "$(cat <<'EOF'
feat(skel): take the trial session id from create stdout

A harness that names its own session has to do so before the first
prompt, or the rest of the run attaches to a different conversation.

EOF
)"
```

---

### Task 3: Declare `[cursor.trial]`

**Files:**

- Modify: `harnesses.toml`
- Test: `tests/test_harnesses.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_harnesses.py`:

```python
def test_cursor_declares_a_trial():
    """Guard the guard: a row that does not parse leaves the recipe unwired."""
    cursor = harnesses.get("cursor")
    assert cursor.trial is not None
    assert cursor.trial.create == ("agent", "create-chat")
    assert "{session}" in " ".join(cursor.trial.first)
    assert "{session}" in " ".join(cursor.trial.resume)
    assert "{session}" in cursor.trial.transcript


def test_claude_trial_has_no_create():
    """Claude still names the session as a flag; the new field must not leak onto it."""
    claude = harnesses.get("claude")
    assert claude.trial is not None
    assert claude.trial.create == ()
    assert "{session}" in " ".join(claude.trial.first)
```

`harnesses.load` is cached. `get` calls `load()`, so these tests read the real table.

- [ ] **Step 2: Run them to verify they fail**

Run:
`uv run pytest tests/test_harnesses.py::test_cursor_declares_a_trial tests/test_harnesses.py::test_claude_trial_has_no_create -v`

Expected: FAIL — `cursor.trial is None`.

- [ ] **Step 3: Add the row**

Append to `harnesses.toml`, after the `[cursor.bundle]` `require` list and before
`[codex]`:

```toml

[cursor.trial]
# create-chat returns a UUID; first/resume both attach with --resume.
# --force is unattended file/shell approval; --trust skips the workspace prompt.
create = ["agent", "create-chat"]
first = [
    "agent", "-p", "--resume", "{session}",
    "--force", "--trust",
    "{prompt}",
]
resume = [
    "agent", "-p", "--resume", "{session}",
    "--force", "--trust",
    "{prompt}",
]
transcript = "~/.cursor/projects/*/agent-transcripts/{session}/{session}.jsonl"
version = ["agent", "--version"]
```

Do not add `--sandbox disabled`; that waits for a live run that stalls.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/test_harnesses.py tests/test_trial.py -v`

Expected: all PASS. `test_the_declared_harness_can_be_driven` still holds for Claude.

- [ ] **Step 5: Commit**

```bash
git add harnesses.toml tests/test_harnesses.py
git commit -m "$(cat <<'EOF'
feat(skel): declare a Cursor trial driven by agent create-chat

just skel trial cursor is now wired for a local agent CLI. CI does
not run it.

EOF
)"
```

---

### Task 4: Preflight

- [ ] **Step 1: Format**

Run: `just tidy`

Expected: prettier wraps the design and plan docs. No Python formatter in this repo
beyond what tidy already runs.

- [ ] **Step 2: Run the full preflight**

Run: `just preflight`

Expected: prettier clean, skills valid, manifests agree, drift matches, all tests pass.
`just skel trial cursor` is callable; do not invoke it — that would be a live `agent`
run.

- [ ] **Step 3: Commit formatting if tidy changed anything**

```bash
git add -u
git commit -m "$(cat <<'EOF'
style: apply prettier wrap to the Cursor trial docs

EOF
)"
```

Skip this commit if `git status` is clean.

---

## What this plan does not build

No live Cursor trial, no evidence archive, no Cursor-specific fixture changes, no
`--plugin-dir`, no `--sandbox disabled`. Those wait for an operator with a local `agent`
CLI, on purpose.
