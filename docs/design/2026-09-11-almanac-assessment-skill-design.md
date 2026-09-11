# Almanac Assessment Skill — Design

**Date:** 2026-09-11 **Status:** Approved

## Summary

The almanac's design rests on bets about agent behavior, and the repository already
admits that two of them go unmeasured.
`docs/design/2026-08-24-widened-almanac-experiment.md` names them: whether a lazily
loaded rule actually gets loaded, and whether a longer listing still reads cold. The
unmerged `skel` work answers those functionally, by driving a harness through a fixture
repository unattended and reading what it did.

This design covers the other half: a development-only skill, `almanac:assess`, invoked
in a fresh session under any supported harness. The agent walks the almanac the way an
agent meets it, records where it snags while still cold, and reports a health critique
of the mechanism. It is a reviewer, not an experiment. Its value is the judgment of a
differently-built agent reading the mechanism for the first time, which is comprehension
rather than conduct — the one thing a behavioral trial cannot collect.

The skill is not published. It is an instrument for maintaining this repository, and
shipping it to adopters would offer them a critique of a design they did not write.

## What this is not

Two boundaries, stated in the skill itself because an assessment that drifts across
either one produces confident output about something it never checked.

**It is not `almanac:audit`.** The audit re-runs every fact's `verify` line and reaches
a verdict about whether the claim is still true. The assessment never judges whether an
entry is true. It judges whether the mechanism around the entries works.

**It is not the trial harness.** The trial measures what an agent did. The assessment
cannot measure behavior, because invoking it primes the agent that would be the subject.
An assessment that reports behavioral findings is reporting a claim it has no standing
to make.

## Decisions

### A fourth skill, in `skills/`, excluded from every payload

It lives at `skills/assess/SKILL.md`, beside `init`, `record`, and `audit`. The reason
is coverage rather than tidiness: the structural suite already parses
`skills/*/SKILL.md`, so the hygiene tests, the frontmatter contract, and the
resolution-exclusion drift check apply to the new skill with nothing added.
`just validate` runs the spec validator over it for the same reason.

The cost is that `harnesses.toml` payloads name `skills` wholesale, so the bundler
copies the whole directory. That needs an explicit path exclusion, and a mistake there
ships a development instrument to every adopter. A test asserting that no archive
contains `skills/assess` is what makes the exclusion load-bearing rather than
remembered.

### Per-harness reach, and the stub that fills the gap

The four harnesses do not reach `skills/` the same way.

Codex consumes the repo tree directly and Cursor loads a plugin directory in place, so
both find the skill with nothing added. Claude Code and Antigravity install from an
archive that the exclusion above deliberately empties, so neither would see it.

A short stub at `.claude/skills/assess/SKILL.md` closes the Claude Code gap by naming
the real file. It carries no method of its own, which is what keeps the two from
drifting; this is the same shape as the Cursor command stubs that already name the
shipped skills. Under a harness with neither route, naming the path in the prompt works,
and the skill is an ordinary markdown file precisely so that fallback exists.

### The walk, staged so the cold read stays cold

The skill's procedure follows the order an agent meets an almanac, and nothing explains
the design until the third stage. Ordering is the whole mechanism here: an agent told
what the listing is supposed to achieve cannot afterwards report what it actually
understood from the listing alone.

**Stage 0 — Resolve the almanac.** The same resolution block `record` and `audit` carry,
copied rather than reworded, because the drift test requires the exclusion list to match
across every skill that resolves.

**Stage 1 — First contact.** Which instruction file the harness surfaced without being
asked, and whether the consult trigger was in it. Then `ls` and nothing else: from
filenames alone, what does this agent believe the repository knows and requires? Which
titles it cannot decode without opening one. Whether it would have read the listing to
the end.

**Stage 2 — Retrieval probe, still without the contract.** A handful of moments this
repository genuinely contains — about to commit, about to open a pull request, prose
looking wrong, setting up a worktree, a build that came back green. For each, which
entry fires from the title alone, and whether one keyword grep would surface it. An
entry that fires for no moment and a moment served by no entry are both findings, and
they are the two failures the filename index is most exposed to.

**Stage 3 — Read the contract and the skills.** The explanation now lands against notes
already written, so the reconciliation is honest rather than retrospective. Coherence
checks belong here: the fact and rule split as the live entries actually use it,
precedence stated the same way in the contract and in the skills, anything duplicated
between `AGENTS.md` and an entry, the `<!-- almanac-template: N -->` stamp against the
canonical template, and whether the commands the contract prints run as written under
this harness.

**Stage 4 — Harness fit.** What this harness could not do. Whether the skills load and
under what name, whether subagents exist for the audit's fan-out, whether the
plugin-root variable resolves, whether the grep and ripgrep invocations the contract
hands you are available.

**Stage 5 — Report, then offer.**

### What keeps the critique honest

An agent asked whether something looks healthy will produce findings whether or not any
exist, and this repository's README confesses its own costs at such length that a naive
critique will rediscover them and call them news. Five rules answer that, and they are
the load-bearing part of the skill.

1. **Clean is an expected outcome.** Say so plainly and stop. A run that finds nothing
   is a result, in the same way a branch that teaches nothing recordable is a normal
   branch.
2. **A cost the README already admits is not a finding.** It becomes reportable only
   with evidence that it has materialized here, and the evidence has to be something the
   agent saw during the walk.
3. **Every finding names three things:** the text it read, the moment the problem bites,
   and what a future agent does wrong as a result. A finding missing any of the three is
   an opinion about style.
4. **Harness-specific and universal findings are separated** in the report, so runs
   under four harnesses can be read against each other rather than merged into one blur.
5. **The report states the skill's own limit.** Invoking it primes the agent, so it
   cannot report whether it would have consulted the almanac unprompted.

### Output: session first, then two offers

The report is delivered in the session, in a fixed section order so that successive runs
and parallel harnesses stay comparable.

After the report, the skill offers to write it to disk and offers to file the obvious
defects as issues in the repository. The write offer proposes a dated, harness-named
path — `docs/review/<date>-<harness>-assessment.md` — rather than assuming one. Neither
happens without approval. That matches the posture the rest of the plugin already takes:
`init` proposes, `audit` proposes, and nothing writes unreviewed.

"Obvious" needs a bar or the issue offer becomes noise, so the skill states one: a
defect in the mechanism a maintainer would act on, not a matter of taste, and not a
restatement of an admitted cost.

## Costs

**A primed agent cannot be a cold reader, only a careful one.** Stage 1 is the closest
available approximation, and it is an approximation. The skill says so rather than
letting the staging imply a rigor it does not have.

**A fourth directory under `skills/` is a fourth thing that can ship by accident.** The
test makes that loud rather than silent, which is the most the design can do.

**Reports are not retained by default.** Session-first output keeps the instrument
light, but nothing accumulates unless the operator accepts the write offer, so a
cross-harness comparison is assembled by hand.

## Implementation

- `skills/assess/SKILL.md`, carrying the resolution block verbatim from the sibling
  skills.
- A path exclusion in `tools/bundle.py` covering `skills/assess`, with a test in
  `tests/test_bundle.py` asserting no archive contains it.
- `.claude/skills/assess/SKILL.md`, a stub naming the real file.
- A line in `README.md` and `CONTRIBUTING.md` recording that the fourth skill is
  development-only and never ships.
