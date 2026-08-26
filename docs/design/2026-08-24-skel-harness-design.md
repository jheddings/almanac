# skel: a portable fixture for testing almanac behavior across harnesses

**Status:** design, approved 2026-08-24. Branch `feat/skel-harness`, stacked on
`feat/widened-almanac`.

## Why

The widened almanac bets that an agent will read a directory listing, carry the titles,
and load a body only when one applies. Six trials so far — four hand-run, one
interactive against the fixture, one unattended — say the compliance half of that bet
holds and the retrieval half does not.

What they established:

- **The commit and branch rules fired in every run**, across two vendors and two
  environments, each producing a scoped `feat(cli):` subject where the only commit in
  history was an unscoped `chore:`. Imitation cannot explain that.
- **Two of six read the whole directory up front** rather than by title, reaching the
  same answers while paying the cost the design exists to avoid. One said so against
  itself: "the opposite of the retrieval economy the directory is built on, and it would
  not scale." At seven entries that is free. The economy is unproven at forty, and this
  is the finding least likely to improve on its own.
- **The consult-on-surprise trigger fired, once, verbatim.** One run hit a sandbox that
  made `.git` read-only, said so, and grepped the almanac with the exact command the
  contract specifies before continuing. It is the only run where anything went wrong,
  and the recovery path worked.
- **The trap fired, and the record half fired unprompted.** The unattended trial
  rejected the GPL dependency its own README recommended, rejected a dual-licensed
  package nobody planted, and named both in a commit trailer. It then found that its
  trailer had not parsed — a blank line above it made git read it as body text — fixed
  the commit, and recorded the fact as an entry with a working verify line.
- **Two of the first four had a loaded skill silently override an almanac rule.** One
  named a worktree after the branch because a worktree skill hardcodes that path shape.
  Another created `docs/superpowers/specs/` in a repository whose almanac says, in as
  many words, not to invent a destination. Neither announced the conflict; both
  otherwise followed the rules closely.

That last finding is the reason this fixture is worth building. A rule that loses to an
eagerly-loaded skill loses quietly, and quiet is the failure mode the almanac exists to
remove.

Four trials also exposed how fragile hand-running is. Scoring was a handful of git
commands run from memory; one run silently edited `AGENTS.md`, moving the instrument
between trials, and it was caught only by diffing. A fifth trial run the same way would
not get the same scrutiny.

So: a fixture that is trivial to stand up on any agent platform, and a runner that
presents it the same way every time — leaving what the agent did to be read from the
diff, by a person. See [No scoring](#no-scoring) for why the reading stays manual.

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
├── docs/almanac/          contract + seven rule entries
└── src/skinner/  tests/

prompts/                   rig: never inside the fixture
├── 01-first-feature.md
├── 02-planned-feature.md
└── 99-almanac-review.md
tools/skel.py              rig: scaffold a run
tools/trial.py             rig: drive a harness through it, and archive
tools/skel.just            rig: the `just skel` recipes
runs/                      gitignored output
```

`skel/` stays out of every shipped archive with no work: `harnesses.toml` payloads are
allowlists, and none of them names it.

A `skel/docs/almanac/` in this tree does not make almanac resolution ambiguous. The
documented rule prefers `docs/almanac/README.md` and stops there, so the glob step never
runs here. The skills' exclusion list needs no change.

## The fixture

A minimal Python project in a "coming soon" state: a package that imports, a task
runner, and an almanac holding seven `kind: rule` entries and no facts. Four are
ordinary conventions — branch naming, commit format, session-scoped worktrees, and what
a merge commit to `main` explains. One is a **canary**: a banner line every new source
module must open with. The remaining two carry the license policy, described under
[The trap](#the-trap).

`AGENTS.md` carries the trigger to read the listing and deliberately restates no rule,
so an agent that skips the almanac has nowhere else to learn them.

The canary is what makes retrieval legible in the diff. Every other rule can be reached
by prior or imitation — every trial so far produced conventional commits, and a model
would do that unprompted — so a hit proves nothing about the almanac. No model has a
prior for this repository's banner text, and the fixture deliberately ships no example
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

**Cohort 3 — trial 7 onward.** Each prompt now squashes its work onto `main`, and the
review is committed like everything else, so git history is the record rather than a
working tree. Adds `merges-to-main-explain-why-not-what`. The worktree entry's cleanup
line moved from "after merging" to session end — under per-prompt merges the old wording
would have had an agent remove its worktree after the first feature and build a second
for the next, which reads as feature-scoped and is the failure that entry exists to
catch. The rule was about to manufacture its own violation.

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
each copy of an original diverges from it — is exactly what a trial is looking for, and
it is the vocabulary to use. `moot`, where the copies convene to compare notes, is
reserved for the run-comparison command if one gets built.

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
just skel trial <harness> [out]    drive a harness through it unattended
just skel clean                    remove runs/
```

The recipes live in a `just` module declared with an explicit path —
`mod skel 'tools/skel.just'`. A bare `mod skel` would resolve against the `skel/`
fixture directory, and the rig must never live inside the tree an agent under test
reads. Module recipes run from the directory holding the module file, so the module sets
its working directory back to the repo root.

`<label>` names the run and is conventionally the harness under test — `claude`,
`codex`, `cursor`. `[name]` selects a file from `prompts/` and defaults to
`01-first-feature`.

`new` produces a **standalone repository**, not a copy inside this one: `git init`, one
conventional initial commit, no remote, plus the `post-checkout` hook that records each
worktree's name at creation, because `git worktree remove` erases it. That is what makes
the fixture portable to cloud platforms, which clone a repo rather than opening a
subfolder — push it anywhere and point an agent at it.

Pushing a run to a remote leaves the hook behind, since hooks do not travel with a
clone. A run executed on a cloud platform therefore reports its worktree name as
unrecoverable unless the transcript supplies it. Half the trials so far ran that way, so
this is the common case rather than the exception.

## Running a trial

`just skel trial <harness>` scaffolds the fixture into a throwaway directory, feeds
every prompt to one session in order, captures the harness's own transcript, writes a
manifest, and zips the result.

The temp directory is load-bearing: nothing above the fixture in the tree contributes
instruction files, which a run inside this repository cannot avoid. It reaches only that
far. A harness also loads skills, plugins, and instructions from the user's
configuration directory, which no working directory excludes — one Cursor trial read
three skills out of the host's plugin cache, and a design gate in one of them stalled
two prompts of the three on a clarifying question no one was there to answer. The
harness row therefore names the variable that moves that directory, and the rig points
it at a throwaway home beside the run, for `create` as well as for the prompts. A
variable a harness ignores is a silent no-op, so the manifest records whether anything
was written there. One session is the other half — a rule firing on the last prompt is
evidence the almanac survived the whole session, which separate invocations cannot show.
That `--resume` genuinely carries context was verified rather than assumed: a resumed
turn correctly answered a question about what the previous turn had done.

How to drive a harness is a row in `harnesses.toml`, so a harness stays named in one
place. Claude can **name** its own session as a flag, so its transcript path is known
rather than discovered. Cursor names it the other way: `agent create-chat` prints a
UUID, which `first` and `resume` attach with `--resume`. Codex assigns the ID:
`codex exec resume --last` continues the newest session for the run's working directory,
while transcript collection takes the newest date-partitioned rollout whose
`session_meta.cwd` matches the run. That content check makes a concurrent Codex session
in another workspace ineligible even when its file is newer. The manifest records the ID
from the matching rollout rather than the rig's unrelated internal UUID. The commands go
into the table verbatim — including Codex's automatic approval reviewer, which requests
workspace-write without asking a managed account for a prohibited full-access mode — and
are copied into every archive's manifest, so a reader knows what the agent was permitted
to do.

Before returning success, the rig checks three structural prerequisites: `main` moved
beyond the scaffold commit, the requested review exists in `main`, and a transcript
matched the trial workspace. It still archives the run before reporting a failure, so
the evidence survives. These checks establish that there is something to read; they do
not judge whether the agent followed a rule correctly.

They also do not ask which prompt left it there, and a session can satisfy all three on
the strength of its last prompt alone. One did: two of its three prompts stalled, and
the review prompt still committed its report, so every prerequisite held. Each result
therefore carries a commit and dirty-file count taken after that prompt. Commits are
counted across every ref, since work left on an unmerged branch is exactly what a
`HEAD`-only count reported as an empty run.

**Prompts run in name order, not the order given.** The review is numbered 99 because it
asks what the almanac changed about the work, which is only answerable once the work has
happened.

Because every prompt squashes onto `main` and the review is committed, an archive needs
only two things to be readable: the git history and the transcript.

How much the second of those carries is the harness's choice, not ours. A Codex rollout
records each command and its output, so a report's claim about what a command returned
can be checked. A Cursor transcript records the tool calls and nothing they returned, so
it shows what was attempted and the git history has to supply the rest. Neither is a
defect to fix; it is a reason to keep both halves of the evidence, and a reason not to
write a check that assumes the transcript can refute an outcome. Working trees and
worktrees are carried along, but nothing depends on them — an earlier trial left its
report uncommitted inside a session worktree, where it survived only because the archive
happened to capture untracked files.

Archives exclude `.venv` and cache directories. One trial produced 85MB of virtualenv
against a 4MB repository, and the agent's commits are in `.git` regardless.

## The review prompt

The last prompt asks the agent to report on its own almanac use. That report is a
**claim, not a finding**. One trial reported following the worktree rule while the
directory on disk was named after the feature, so the report is written as statements
the transcript can refute — which entries, loaded when, changing what — and the
transcript is archived beside it.

Reflection stays confined to this prompt on purpose. A rule requiring an agent to
justify every merge would have it consulting more deliberately all session than one
working naturally, which inflates every measurement here rather than only the
almanac-specific ones. `merges-to-main-explain-why-not-what` is therefore worded as an
ordinary engineering convention, with no invitation to introspect on process or sources.

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

The structural validation and the per-prompt counts belong to the same half. They answer
whether the agent was able to act, which is a property of the rig, and stop short of
what it did, which is the operator's reading. The distinction is not academic: two
harnesses have returned three clean exit statuses each for sessions that produced almost
nothing — one denied every command it tried, one stalled on a question nobody could
answer — and the archives said `exit: 0` three times in both cases. A count of zero new
commits does not say the almanac failed. It says the trial did, and that the run is not
evidence about the almanac at all.

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
