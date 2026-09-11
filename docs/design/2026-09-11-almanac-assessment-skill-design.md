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

The `audit` boundary is the one that takes work to hold, because the assessment does
read entry bodies and does count what is in them. **Measuring the unguarded surface
belongs here; judging it belongs to the audit.** How much of the directory rests on
assertions no `verify` line covers, and how many facts carry a line nothing could re-run
in this tree, are both structural properties of the mechanism — countable without
opening a question about any claim's truth, and nothing else measures them. Whether any
one of those assertions still holds is a verdict, needs evidence produced by running
something, and is exactly what the audit exists to produce. The seam is what keeps both
reports readable: a maintainer reading a coverage count knows it is a shape, and reading
an audit verdict knows something ran.

## Decisions

### A fourth skill, outside `skills/`

It lives at `.claude/skills/assess/SKILL.md`. The obvious home was `skills/`, beside
`init`, `record`, and `audit`, and that home is unsafe: **everything in `skills/`
reaches adopters**, and no bundler change prevents it.

`.claude-plugin/marketplace.json` declares `source: "./"`, so the documented Claude Code
install resolves the plugin at the repository root and discovers `skills/` from the
cloned tree. The Cursor marketplace file says the same. The codex manifest points at
`./skills/` and builds no archive at all. The release workflow creates a draft release
and attaches nothing. Only Antigravity installs from an archive, so an archive exclusion
would have guarded the one route almost nobody takes while leaving the documented ones
open.

`.claude/` is named by no manifest and no payload, so nothing distributes it. Claude
Code discovers it as a project skill when a session opens this checkout, which is the
best ergonomics available. Where another harness does not read that directory, the skill
is an ordinary markdown file and naming its path in the prompt works — which is the
fallback the design relies on rather than a workaround.

### What the move costs, and how it is paid

Leaving `skills/` gives up the structural suite. `tests/support/almanac.py` discovers
skills by globbing `skills/*/SKILL.md`, and two tests key off that glob to assert every
skill resolving the almanac names the same exclusion list. A skill outside it drops out
of that check with nothing failing, which is the silent exemption those tests were
written to prevent.

So discovery is extended to both locations, and `just validate` runs the spec validator
over the new directory too. The conventions the suite enforces — the frontmatter shape,
the description form, the exclusion-list agreement — are as worth holding for this skill
as for a shipped one.

### The walk, staged so the cold read stays cold

The skill's procedure follows the order an agent meets an almanac, and nothing explains
the design until the third stage. Ordering is the whole mechanism here: an agent told
what the listing is supposed to achieve cannot afterwards report what it actually
understood from the listing alone.

**Stage 0 — Resolve the almanac.** The same resolution block `record` and `audit` carry,
copied rather than reworded, because the drift test requires the exclusion list to match
across every skill that resolves.

**Stage 1 — First contact.** Which instruction files the harness surfaced without being
asked, each marked repository-level or operator-level, and whether the consult trigger
was in the repository's. Only the repository's counts: an operator's personal
configuration can supply a trigger and make an unwired almanac look wired. Then `ls` and
nothing else: from filenames alone, what does this agent believe the repository knows
and requires? Which titles it cannot decode without opening one. Then measurables about
the listing — how many entries, how long the longest slug, and how many of those entries
the agent actually named above. All three are countable from its own output.
Deliberately not what the agent would have done with a longer listing, and not how far
down it had read: the first is a behavioral claim this skill has no standing to make,
and the second is a number an agent cannot honestly produce and will therefore invent.

**Stage 2 — Retrieval probe, still without the contract.** The moments come from what
the repository **does** — its task runner, its CI jobs, its recently merged pull
requests — and never from the listing. A moment read off the listing is by construction
one the listing serves, so a probe built that way can never find a gap and returns a
clean result having tested nothing. There is deliberately **no quota** of unserved
moments: requiring some would make a fully-served list read as procedural error when the
honest explanation is that the almanac covers its repository, and an agent held to a
quota invents the gap. The sourcing discipline carries the stage instead. For each
moment, which entry fires from the title alone, and what a filename-only grep returned
when run. An entry that fires for no moment and a moment served by no entry are both
findings.

**Stage 3 — Read the contract and the skills.** Everything the staging withheld is
unbanned here: the almanac's contract, the repository's `README.md`, `CONTRIBUTING.md`,
and `docs/design/`. The explanation lands against notes already written, so the
reconciliation is honest rather than retrospective. Coherence checks belong here: the
fact and rule split as the live entries actually use it, precedence stated the same way
in the contract and in the skills, anything duplicated between `AGENTS.md` and an entry,
the `<!-- almanac-template: N -->` stamp against the canonical template, whether the
commands the contract prints are complete and correct as text, and whether the claims
the contract makes about the skills still match those skills. Running commands is Stage
4's, under one routing test: a finding that would disappear under a different harness is
harness fit, not coherence.

Stage 3 then closes with two **measurements** of what the mechanism does not cover: how
many entries carry concrete body assertions of the kind that rots — a named command, a
path, a flag, a count, a named implementation — and how many facts carry a `verify` line
that could not be re-run in this tree at all, because it describes a historical event or
a state that no longer exists. Both report a count and a list of filenames. Neither
reports whether any body detail is correct. This is the first point in the walk where
entry bodies are read, and it is safe there: the cold stages are over and their records
are already written.

**Stage 4 — Harness fit.** What this harness could not do. Whether the skills load and
under what name, whether subagents exist for the audit's fan-out, whether the
plugin-root variable resolves, whether the grep and ripgrep invocations the contract
hands you are available, and what the facts' `verify` lines require before they could
run — credentials, network, a live service, an absent tool — against what this harness
supplies. That last is the harness-comparable half of the fact-tier measurement above:
an entry that cannot be checked because a token is invalid is a statement about the
environment, not about the entry.

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
and parallel harnesses stay comparable: what ran, first contact, retrieval, coherence,
coverage, harness fit, findings, limits. **Coverage sits between coherence and harness
fit** because the two measurements are neither — they are not a contradiction between
texts and they do not vary with the tool — and giving them their own section keeps the
counts out of a findings list, where a number with no verdict attached would read as
one.

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

**A skill outside `skills/` is discovered differently on every harness.** Claude Code
finds it; the others may need the path named. That is the price of a location nothing
ships, and it is the right way round — a skill that is harder to invoke is recoverable,
and one that reaches adopters is not.

**The skill names a repository-local path.** `CONTRIBUTING.md` warns that writing a path
into a skill is the signal you have crossed the line into local convention, and a
shipped skill naming `docs/review/` would send an adopting repository's agent into a
directory it does not have. This one may, because it is development-only and reaches no
repository but this one. That reasoning belongs here rather than in the skill, where it
would be three lines addressed to a maintainer in a document an agent executes.

**Reports are not retained by default.** Session-first output keeps the instrument
light, but nothing accumulates unless the operator accepts the write offer, so a
cross-harness comparison is assembled by hand.

## Implementation

- `.claude/skills/assess/SKILL.md`, carrying the resolution block verbatim from the
  sibling skills.
- `tests/support/almanac.py` discovering skills from `.claude/skills/` as well, so the
  hygiene and exclusion-drift tests cover it, and `just validate` doing the same.
- An almanac entry recording that `skills/` ships to adopters through the marketplace
  route whatever the bundler does.
- A line in `CONTRIBUTING.md` recording why the development-only skill lives where it
  does. Not in `README.md`: that ships in every payload, and it would describe a skill
  the reader's install does not contain.
