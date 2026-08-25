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

## Fixture revisions

Changing the fixture moves the instrument, so every revision starts a new cohort and
gets recorded here. Results either side of a line are not directly comparable.

**Cohort 1 — trials 1 to 5.** The original fixture. Its `AGENTS.md` described the
project as "a package that imports and nothing more", which the first feature is
guaranteed to falsify. Two of the five corrected that sentence and were flagged for
modifying the instrument — good behaviour, punished by a claim the fixture should never
have made. The Project section now describes the tooling and asserts no state the work
invalidates.

Cohort 1 still stands for what it established: the branch and commit rules held 5/5
across two vendors and two environments, and trial 5 produced the first canary hit. Only
the `fixture edited` row is contaminated, and only for the two runs that touched that
sentence.

**Cohort 2 — trial 6 onward.** Adds the license trap: two entries, a planted bait in the
README, and a second prompt. Also removes the mechanical scorer, which changes how runs
are read but not what the fixture presents to an agent. Cohort 1's canary and rule
results carry forward; nothing in cohort 1 met the trap, so it has no baseline.

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
just skel new <label> [out]        a standalone git repo at <out>/<date>-<label>/
just skel prompt [name]            print a prompt to paste
just skel run <label> [out] [name] new + prompt
just skel clean                    remove runs/
```

The recipes live in a `just` module declared with an explicit path —
`mod skel 'tools/skel.just'`. A bare `mod skel` would resolve against the `skel/`
fixture directory, and the rig must never live inside the tree an agent under test
reads. Module recipes run from the directory holding the module file, so the module sets
its working directory back to the repo root.

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

## No scoring

An earlier version of this rig scored runs mechanically — seven checks over git state,
producing pass / fail / unrecoverable per rule. It is gone, and the reason is worth
keeping.

Run against the four completed trials, where the answers were already known by hand, it
was **wrong on two of them on first contact**: half the runs had left work on an
unmerged branch and it read `HEAD` alone, reporting them as empty; and it flagged
`pyproject.toml` as tampering — a console script cannot be added without it — while the
run that actually rewrote `AGENTS.md` passed. It needed three rounds of correction
before it agreed with a reading anyone could do from `git diff` in under a minute.

That is the argument against it. Every check encoded a judgment call — is this worktree
name session-scoped, is this directory invented, is this edit contamination — and a
person makes those calls faster, more accurately, and with the context to say "yes, but
that one was reasonable." A scorer converts them into verdicts that read as measurement
and are not. The rig prepares runs; the operator reads diffs.

What survives is the part that is not judgment: the `post-checkout` hook, which captures
a worktree name at creation because git keeps nothing once the worktree is removed. That
is evidence collection, not evaluation, and without it the evidence is destroyed by an
agent following the rules.

## The trap

Rules that fire at obvious moments — about to commit, about to create a file — measure
whether an agent is generally careful. They do not measure the almanac's actual claim,
which is about facts that prevent failures nobody would think to look for.

The fixture therefore carries a **license policy**: permissive dependencies only, and a
commit trailer naming anything rejected for its license. Both are entries. Neither is
derivable from the repository — there is no amount of reading Python that reveals which
licenses an organization accepts — so an agent either consults the almanac or does not.

The failure is silent in the way that matters. A copyleft dependency installs, the tests
pass, the checks stay green, and the problem surfaces at legal review months later.

Two details make it a controlled test rather than a lottery. **The bait is planted:**
the fixture's README names `Unidecode` for the planned feature, and `Unidecode` is GPL,
so the obvious path leads into the trap and the almanac is the only thing that diverts
it. And **the disclosure carries the signal:** most packages are permissive, so an agent
could comply by luck, but a `Rejected-for-license:` trailer naming what it turned down
is an artifact that only exists if the entry was read and applied.

Transliteration was chosen over fuzzy matching deliberately. `difflib.get_close_matches`
would let an agent solve a fuzzy-matching task from the standard library, never add a
dependency, and never meet the trap — an honest null that wastes a run. The standard
library has no transliteration equivalent.

The residual gap, stated plainly: "about to add a dependency" is still a moment where a
careful agent might think about licensing unprompted. It is far less salient than "about
to commit", but it is not zero, and a fact with no salient moment at all remains
unmeasured.

## Drift

`skel/docs/almanac/README.md` is a third instance of the canonical template, so
`tools/drift.py` extends from two hardcoded paths to a list and covers it. An uncovered
fixture goes stale against the contract it exists to test, which is the worst silent
failure available here.

The alternative was generating the fixture's almanac at `skel new` time, where drift is
impossible by construction. It was rejected because it breaks the property the fixture
is for: one folder, complete, that opens anywhere without running anything first.

## Costs

The devcontainer is fixture surface. An agent can read and edit it like anything else in
the tree.

Reading a run is manual, and deliberately so. That caps how many trials are worth
running and means results depend on the reader's consistency — which is the price of not
pretending a heuristic is a measurement.

Nothing here reaches the question most in doubt. Whether an agent retrieved by title or
read the whole directory leaves no trace in git, so retrieval _strategy_ is only visible
in a transcript. The trap gets closer than the rest: it shows whether an entry changed a
decision, which is what the almanac is actually for.

The bait is a thumb on the scale. Naming `Unidecode` in the README makes the trap fire
reliably and also makes the fixture nudge an agent toward a specific package, so what is
measured is "did the almanac override a suggestion" rather than "did the almanac come to
mind unprompted". The weaker, more realistic version of this test drops the bait and
accepts that some runs produce nothing.

The fixture is portable and the rig is not — `just skel` needs this checkout, while a
run needs nothing but git. That asymmetry is deliberate, and it is why `new` emits a
standalone repository.
