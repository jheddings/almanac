# skel: a portable fixture for testing almanac behavior across harnesses

**Status:** design, approved 2026-08-24. Branch `feat/skel-harness`, stacked on
`feat/widened-almanac`.

## Why

The widened almanac bets that an agent will read a directory listing, carry the titles,
and load a body only when one applies. Two hand-run trials say the bet is unsettled:
Opus retrieved lazily as designed, Sonnet read every entry up front. Both passed the
rules; only one exercised the mechanism.

Two trials also exposed how fragile hand-running is. The scoring was six git commands
run from memory, and one run silently edited `AGENTS.md` — moving the instrument between
trials — which was caught only by diffing. A third trial run the same way would not get
the same scrutiny.

So: a fixture that is trivial to stand up on any agent platform, and a scorer that
measures the same things every time.

## Non-goals

Not a benchmark, and not a claim about model quality. It measures whether a given
harness, in a given configuration, retrieves and applies rules that live in an almanac.
Sample sizes are one. Results are evidence for a design decision, not a leaderboard.

No headless invocation, no matrix runner, no result aggregation. Those wait until the
prompts have earned their keep.

## Shape

The fixture is everything the agent sees. The rig lives outside it, because prompts
inside the fixture would tell the agent it is being tested.

```text
skel/                      the fixture, checked in complete
├── .devcontainer/
├── AGENTS.md              the trigger; restates no rule
├── README.md  pyproject.toml  .justfile  .gitignore
├── docs/almanac/          contract + three rule entries
└── src/skinner/  tests/

prompts/                   rig: never inside the fixture
├── 01-first-feature.md
├── 02-long-session.md
└── 03-urgent.md
tools/skel.py              rig
runs/                      gitignored output
```

`skel/` stays out of every shipped archive with no work: `harnesses.toml` payloads are
allowlists, and none of them names it.

A `skel/docs/almanac/` in this tree does not make almanac resolution ambiguous. The
documented rule prefers `docs/almanac/README.md` and stops there, so the glob step never
runs here. The skills' exclusion list needs no change.

## The fixture

A minimal Python project in a "coming soon" state: a package that imports, a task
runner, and an almanac holding three `kind: rule` entries — branch naming, commit
format, and session-scoped worktrees — with no facts. `AGENTS.md` carries the trigger to
read the listing and deliberately restates no rule, so an agent that skips the almanac
has nowhere else to learn them.

The devcontainer installs the **toolchain only**: python, uv, just, git. Not the harness
CLIs. A `devcontainer.json` installing `claude`, `codex`, and `gemini` side by side
tells the agent it is one of several being compared, which is the tell we are keeping
out of the fixture. Attach with whichever harness is under test.

## The rig

```text
just skel new <label>              a standalone git repo at runs/<date>-<label>/
just skel run <label> [prompt]     new + print the prompt to paste
just skel check <label>            score the rules against that run's git state
just skel clean                    remove runs/
```

`<label>` names the run and is conventionally the harness under test — `claude`,
`codex`, `cursor`. `[prompt]` selects a file from `prompts/` and defaults to
`01-first-feature`.

`new` produces a **standalone repository**, not a copy inside this one: `git init`, one
conventional initial commit, no remote. That is what makes the fixture portable to cloud
platforms, which clone a repo rather than opening a subfolder — push it anywhere and
point an agent at it.

## Scoring

`check` reproduces what was done by hand, so the tenth run gets the scrutiny the first
one got.

| Check                      | How                                                   |
| -------------------------- | ----------------------------------------------------- |
| Worktree fired             | a worktree under `.worktrees/`, live or in the reflog |
| Worktree is session-scoped | flag when the name is merely the branch slug          |
| Branch prefix              | matches a conventional type followed by `/`           |
| Commit subject             | conventional format; note whether a scope is present  |
| Commit body wrap           | no line over 72 columns                               |
| Contamination              | `AGENTS.md` or `docs/almanac/` differ from `skel/`    |

Two of these earn their place from observed failures rather than speculation. The
session-scope check is the exact miss one trial produced, where a loaded worktree skill
named the directory after the branch and quietly won over the entry that said otherwise.
The contamination check is the other: an agent rewrote `AGENTS.md` mid-run because a
sentence in it had become false, which is defensible behavior and still means the next
trial would have run against a different instrument.

Scoring reads git state, not the transcript. What an agent narrates about itself is not
evidence.

## Drift

`skel/docs/almanac/README.md` is a third instance of the canonical template, so
`tools/drift.py` extends from two hardcoded paths to a list and covers it. An uncovered
fixture goes stale against the contract it exists to test, which is the worst silent
failure available here.

The alternative was generating the fixture's almanac at `skel new` time, where drift is
impossible by construction. It was rejected because it breaks the property the fixture
is for: one folder, complete, that opens anywhere without running anything first.

## Costs

The devcontainer is fixture surface. An agent can read and edit it, so `check` compares
it like everything else.

Scoring is heuristic where it has to be. "Session-scoped" has no mechanical definition;
the check flags a suspicious name and a human decides. It is a prompt to look, not a
verdict.

The rig lives in this repository, so scoring a run requires this checkout. The fixture
does not — that asymmetry is deliberate, and it is why `new` emits a standalone repo.
