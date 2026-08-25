# skel: a portable fixture for testing almanac behavior across harnesses

**Status:** design, approved 2026-08-24. Branch `feat/skel-harness`, stacked on
`feat/widened-almanac`.

## Why

The widened almanac bets that an agent will read a directory listing, carry the titles,
and load a body only when one applies. Four hand-run trials — two local, two on cloud
platforms — say the retrieval half of that bet mostly holds and the precedence half does
not.

What the four established:

- **The commit and branch rules fired in every run**, across two vendors and two
  environments, each producing a scoped `feat(cli):` subject where the only commit in
  history was an unscoped `chore:`. Imitation cannot explain that.
- **Three of four opened with the directory listing** and loaded bodies on demand. The
  fourth read every entry up front, which reaches the same answer while paying the cost
  the design exists to avoid. With three entries that is free; the economy is unproven
  at forty.
- **The consult-on-surprise trigger fired, once, verbatim.** One run hit a sandbox that
  made `.git` read-only, said so, and grepped the almanac with the exact command the
  contract specifies before continuing. It is the only run where anything went wrong,
  and the recovery path worked.
- **Two of four had a loaded skill silently override an almanac rule.** One named a
  worktree after the branch because a worktree skill hardcodes that path shape. Another
  created `docs/superpowers/specs/` in a repository whose almanac says, in as many
  words, not to invent a destination. Neither announced the conflict; both otherwise
  followed the rules closely.

That last finding is the reason this fixture is worth building. A rule that loses to an
eagerly-loaded skill loses quietly, and quiet is the failure mode the almanac exists to
remove.

Four trials also exposed how fragile hand-running is. Scoring was a handful of git
commands run from memory; one run silently edited `AGENTS.md`, moving the instrument
between trials, and it was caught only by diffing. A fifth trial run the same way would
not get the same scrutiny.

So: a fixture that is trivial to stand up on any agent platform, and a scorer that
measures the same things every time.

## Non-goals

Not a benchmark, and not a claim about model quality. It measures whether a given
harness, in a given configuration, retrieves and applies rules that live in an almanac.
Sample sizes are one. Results are evidence for a design decision, not a leaderboard.

A run's result is a property of model, harness, loaded skills, and sandbox together. Two
of the first four ran on cloud platforms with sandboxes that the local runs did not
have, and one of those sandboxes made the worktree rule impossible to follow. Record
those four things per run or the numbers mean nothing.

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
runner, and an almanac holding four `kind: rule` entries and no facts. Three are real
conventions — branch naming, commit format, session-scoped worktrees. The fourth is a
**canary**: a banner line every new source module must open with.

`AGENTS.md` carries the trigger to read the listing and deliberately restates no rule,
so an agent that skips the almanac has nowhere else to learn them.

The canary is what makes retrieval mechanically scoreable. Every other rule can be
reached by prior or imitation — all four trials produced conventional commits, and a
model would do that unprompted — so a hit proves nothing about the almanac. No model has
a prior for this repository's banner text, and the fixture deliberately ships no example
of it: the one existing source file is exempt by the rule's own wording, so the
convention cannot be copied from a neighbour. It can only come from the entry.

Because the check runs per file, a run that creates several modules also measures
**decay**: a banner on the first and not the third is a rule fading mid-session, which
is the question a filename index most needs answered.

The devcontainer installs the **toolchain only**: python, uv, just, git. Not the harness
CLIs. A `devcontainer.json` installing `claude`, `codex`, and `gemini` side by side
tells the agent it is one of several being compared, which is the tell we are keeping
out of the fixture. Attach with whichever harness is under test.

## Naming and tone

The fixture is called `skinner`, and the rig around it is themed after the Bobiverse.
The split is deliberate and runs in one direction: **theme anything that does not say
"you are being observed."**

`skinner` is a good fixture name precisely because it is overdetermined — a surname, an
ordinary noun, a Simpsons character, an X-Files character. No single referent dominates,
so it reads as somebody's hobby project, which is what the fixture is pretending to be.
A name with one obvious referent would be a tell, and the more on-the-nose the rig's
theme becomes, the truer that gets: a fixture named `bob` inside a Bobiverse rig
announces itself.

The rig has no such constraint. **Replicative drift** — the in-universe term for how
each copy of an original diverges from it — is exactly what the scorer measures, and it
is the vocabulary to use. `moot`, where the copies convene to compare notes, is reserved
for the run-comparison command if one gets built.

**Inside the fixture, keep the theme to the name and nothing else.** The tells to avoid
are specific: an almanac entry that references the experiment, a prompt that mentions
testing or comparison, a canary marker that reads as instrumentation rather than as a
convention a project might really hold. `# skinner:module` passes that bar; anything
that looks like measurement apparatus does not.

This is tone, not a rule, and it lives here rather than in an almanac. A mis-themed name
is caught loudly the first time anyone reads it, so it fails "costly to miss" — which is
the test that keeps preferences out of an almanac in the first place.

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
conventional initial commit, no remote, plus the `post-checkout` hook described under
Scoring. That is what makes the fixture portable to cloud platforms, which clone a repo
rather than opening a subfolder — push it anywhere and point an agent at it.

Pushing a run to a remote leaves the hook behind, since hooks do not travel with a
clone. A run executed on a cloud platform therefore reports its worktree name as
unrecoverable unless the transcript supplies it. Half the trials so far ran that way, so
this is the common case rather than the exception.

## Scoring

`check` reproduces what was done by hand, so the tenth run gets the scrutiny the first
one got.

| Check                      | How                                                       |
| -------------------------- | --------------------------------------------------------- |
| Worktree fired             | a name in the worktree log (see below), or one still live |
| Worktree is session-scoped | flag when the logged name is merely the branch slug       |
| Branch prefix              | matches a conventional type followed by `/`               |
| Commit subject             | conventional format; note whether a scope is present      |
| Commit body wrap           | no line over 72 columns                                   |
| Fixture edited             | tracked files differ from `skel/`                         |
| Fixture extended           | new paths outside `src/` and `tests/`                     |

Every row traces to an observed failure rather than speculation.

**Fixture edited** and **fixture extended** are two different violations and need two
rows. One trial rewrote `AGENTS.md` mid-run because a sentence in it had become false —
defensible, and it still means the next trial ran against a different instrument. A
different trial touched nothing existing and instead created `docs/superpowers/specs/`
and `docs/superpowers/plans/`, in a fixture whose almanac says not to invent a
destination. A check that compares only existing files reports that second run clean,
which is the one outcome that would make the scorer worse than useless.

**Rule broken is not rule impossible.** One trial's sandbox made the repository's `.git`
read-only, so `git worktree add` could not succeed no matter what the agent did; it
tried the documented command, said why it failed, and fell back to a clone. That is not
a worktree miss and must not be scored as one. Where a check fails, the scorer reports
whether the operation was attempted, so the two outcomes stay distinguishable.

**Skill-vs-rule collisions get their own line in the report.** Two of the first four
runs had a loaded skill's hardcoded convention beat an almanac rule with no
announcement. That cannot be detected from git state alone — the scorer flags the shapes
it can see (a worktree named for its branch, an invented directory under `docs/`) and
the operator reads the transcript for the rest.

Scoring reads git state, not the transcript. What an agent narrates about itself is not
evidence: one run reported following the session-scoped worktree rule while the
directory on disk was named after the feature.

### Capturing the worktree name

The session-scope check cannot read git state after the fact, and this was verified
rather than assumed. Once an agent runs `git worktree remove` and the branch is gone,
nothing retains the name: no `.git/worktrees` entry, no branch reflog, and the HEAD
reflog records only the merge. Two of the four trials cleaned up, and one of those names
survives solely in a transcript. The rule tells the agent to clean up, so following the
rule destroys the evidence for scoring it.

So `skel new` installs a `post-checkout` hook in `.git/hooks` that appends each new
worktree's path to `.git/skel-worktrees.log`. That path is outside the working tree and
hooks are untracked, so it is not a file an agent lists, reads, or commits, and the name
is captured at creation regardless of what happens later.

Two costs. Hooks are shared by every worktree of a repository, so the hook fires in the
session worktree as well and the log has to tolerate repeated lines. And a sandbox that
denies writes under `.git` — which one of the first four trials had — silences the hook
entirely. So an empty log is reported as **unrecoverable**, never as a failure: the one
environment that breaks the hook is the same one that breaks the rule it measures, and
conflating those would manufacture a result.

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
the check flags a name that merely repeats its branch and a human decides. It is a
prompt to look, not a verdict. The same applies to skill-vs-rule collisions, which the
scorer can only point at.

The scorer measures rule-following, which is not the thing most in doubt. Whether an
agent retrieved by title or read the whole directory leaves no trace in git at all, and
that — not the commit format — is the question the widened almanac turns on. It stays a
transcript read.

The rig lives in this repository, so scoring a run requires this checkout. The fixture
does not — that asymmetry is deliberate, and it is why `new` emits a standalone repo.
