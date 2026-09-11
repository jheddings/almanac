---
name: assess
description: >-
    Use when you want a health review of this repository's almanac mechanism rather than
    its contents — "assess the almanac", "is the almanac framework working", "review the
    almanac mechanics", "how does this almanac read to a fresh agent" — and typically in
    a new session under a particular agent harness, so the reading is genuinely cold.
    This skill critiques the mechanism by walking it. It never judges whether an entry
    is true, which is almanac:audit, and it never claims to measure what an agent did,
    which the trial harness owns.
---

# Assess the Almanac

This skill produces a **critique of the almanac mechanism as it reads on first contact**
— whether the listing is legible, whether the right entry fires at the right moment,
whether the contract and the skills say the same thing. It is not a verdict about any
entry, and nothing here establishes whether a recorded claim is still true.

The intended condition is a **fresh session under one harness**, with this skill invoked
before anything else in the repository has been read. That is what makes the walk worth
running: the findings are about what an agent understands before the design explains
itself, and an agent that has already read the design cannot produce them.

Reports are comparable across harnesses because the walk is identical — the same stages,
the same probes, in the same order. What differs between runs is the friction each
harness adds: what it surfaces unasked, what it can load, what it can run. Two reports
read side by side therefore separate a problem in the mechanism from a problem in the
tool.

## What this is not

**Not `almanac:audit`.** The audit enumerates the entries, re-runs each fact's `verify`
line, and reaches a verdict — `holds`, `falsified`, `unverifiable` — about whether the
claim is still true. It owns that ground completely. **This skill never judges whether
an entry is true.** An entry may be badly stale and still assessed here as well-titled
and well-placed, because what is under assessment is retrieval and coherence, not truth.
If a claim looks wrong to you while you walk, say that the audit exists and move on; do
not verify it, and do not report a verdict.

**Not the trial harness.** That measures what an agent did — whether a lazily loaded
rule actually got loaded, whether a longer listing still got read to the end — by
driving a harness through a fixture repository unattended and reading what came out.
**This skill cannot measure behavior, because invoking it primes the agent that would be
the subject.** You were told to go and look at the almanac, so nothing you do afterwards
is evidence about whether you would have looked. An assessment reporting a behavioral
finding is reporting a claim it has no standing to make, and it will be read as
measurement by whoever receives it.

## Before you start

The staging below is the mechanism, not a preference.

> Do not open the almanac's `README.md`, the repository's `README.md`, or anything under
> `docs/design/` until Stage 3. Stages 1 and 2 are worth having only because they happen
> before the design explains itself. An agent told what the listing is supposed to
> achieve cannot afterwards report what it actually understood from the listing alone.

There is one exception: **the instruction file the harness surfaced on its own** —
`AGENTS.md`, `CLAUDE.md`, or whatever this tool loads without being asked. That file is
part of first contact by definition, and Stage 1 reads it. Do not go looking for the
instruction files the harness did not surface; which ones it did is itself a Stage 1
observation.

If one of the staged documents was already open in this session before the skill was
invoked, say so in the report's Limits section and do not describe Stage 1 as cold.

## Stage 0 — Locate the almanac

In order — stop at the first step that resolves:

1. **`docs/almanac/README.md`.** The conventional location. If it exists, that is the
   almanac; do not look further.
2. **Glob `**/almanac/README.md`**, then discard matches under `templates/`,
   `node_modules/`, `vendor/`, or any other checkout nested inside this one. A bare
   directory-name match is not evidence of an almanac — **a template, an example, or a
   sibling worktree's copy is not this repo's almanac**, and assessing the wrong almanac
   produces a health report about a directory nobody relies on.
3. **Exactly one survivor → that is the almanac.** More than one, ask which. None, this
   repo has no almanac — say so and stop.

**These steps search this tree, and never look up.** A workspace or parent repository
enclosing this checkout may keep its own almanac; that is a separate almanac with a
separate subject, and this tree's is the one that resolves. An enclosing almanac is
outside this assessment: it is a different mechanism serving a different tree, and its
health says nothing about this one's.

Hold the resolved **directory**. Every stage below reads from it.

## Stage 1 — First contact

Record four things, and record them now, while nothing has been explained. They cannot
be reconstructed at Stage 3, because by then you will know what the listing was trying
to achieve.

- **Which instruction file the harness surfaced without being asked**, and whether the
  trigger to consult the almanac was in it. Quote the trigger if it was there. If the
  harness surfaced nothing at all, that is the first finding of the run: an almanac
  nobody is told to read is an almanac nobody reads.
- **`ls` the almanac directory, and nothing else.** No grep, nothing opened. From the
  filenames alone, write down what this repository appears to know and what it appears
  to require of you. The filename index is the artifact the whole design rests on, and
  this paragraph is the only measurement of it you will get.
- **Which titles you cannot decode without opening the file.** A title that needs its
  body to be understood has already failed at the one job the index gives it.
- **Whether you would have read the listing to the end**, given its length, and where
  your attention would realistically have dropped. Answer that honestly rather than
  charitably. The length at which the index stops working is exactly what this question
  exists to find, and a polite answer destroys the measurement.

## Stage 2 — Retrieval probe

Still no contract and still no skills. You have the listing and the notes from Stage 1.

Take the moments this repository actually contains, derived from the listing rather than
invented — a moment nobody here ever meets tests nothing. About to commit. About to open
a pull request. Prose that looks wrong. Setting up a worktree. A build that came back
green.

For each moment, name **the entry that fires from its title alone** — not the entry you
could find by searching for it, but the one whose filename would stop you as you scanned
the listing. Then say whether **a single keyword grep** would surface it, using the
keyword you would actually have typed in that moment rather than one read back off the
filename.

Then the two findings this stage exists for. Both are failures of the filename index,
and neither is visible to anyone reading entry bodies:

- **An entry that fires for no moment.** Its body may be excellent and it will never
  load. Name it.
- **A moment served by no entry.** Two causes, and they take different fixes: either
  nothing was ever recorded, or something was recorded under a title that does not state
  the claim. Say which you think it is.

## Stage 3 — Read the contract and the skills

Now read the almanac's `README.md`, the repository's instruction file in full, and the
sibling skills.

**The reconciliation is the point.** You are holding notes written before the
explanation landed. Compare what the mechanism intended against what you actually took
from it, and say where the two diverge. That divergence is the finding, and it is
unavailable to anybody who read the contract first.

Then five coherence checks:

- **The fact and rule split as the live entries actually use it**, not as the contract
  describes it. Read each entry's `kind` against its title and decide whether the
  directory is using the distinction the contract defines, or a looser one that has
  grown in its place.
- **Whether precedence between the skill and the contract is stated the same way in
  both.** Each names a winner when they disagree about method and a winner when they
  disagree about local convention. If they name different winners, or one states it and
  the other is silent, an agent holding both has no rule at all.
- **Anything duplicated between the repository's instruction file and an entry.** Two
  copies diverge, and the stale one wins whichever is read first.
- **The `<!-- almanac-template: N -->` stamp against the canonical template**, resolved
  the way `almanac:audit` resolves it —
  `${CLAUDE_PLUGIN_ROOT}/templates/almanac/README.md` if that variable is set, otherwise
  `templates/almanac/README.md` relative to the workspace root, otherwise the plugin's
  installed directory as your harness exposes it. Report a gap; upgrade nothing.
- **Whether the commands the contract prints run as written under this harness.** Run
  them. A command quoted in a contract that fails when pasted is a defect nobody
  catches, because everyone assumes somebody ran it once.

## Stage 4 — Harness fit

What this harness could not do. Answer each one concretely — run it, or try it — rather
than assuming it from what you know about harnesses in general:

- **Do the skills load, and under what name?** `almanac:record`, some other spelling, a
  file path you had to name yourself, or not at all.
- **Do subagents exist**, for the fan-out `almanac:audit` describes? If not, the audit
  degrades to a sequential run — which is fine, and the skill says so — but a report
  that leaves it unstated implies a capability this harness does not have.
- **Does the plugin-root variable resolve?** Print it. Every revision-stamp check in the
  plugin starts there, and an unset variable sends each of them down a different
  fallback.
- **Are the grep and ripgrep invocations the contract hands you available as written?**
  Including their flags. An `--exclude` or `--glob` this harness's tooling will not
  accept turns the contract's one-command retrieval check into a dead end at the moment
  it is needed.

## Stage 5 — Report

Deliver the report in the session, in this section order and no other. The order is
fixed so that two runs — successive runs under one harness, or parallel runs under four
— can be read against each other line by line.

1. **What ran** — the harness, the date, and what was read at each stage.
2. **First contact** — the Stage 1 record, as written at the time.
3. **Retrieval** — the Stage 2 record, including both failure shapes, and explicitly
   saying so when one of them is empty.
4. **Coherence** — the Stage 3 reconciliation and the five checks.
5. **Harness fit** — the Stage 4 answers.
6. **Findings** — universal first, harness-specific second, each carrying its three
   parts.
7. **Limits** — what this run could not establish.

## What keeps this honest

An agent asked whether something looks healthy will produce findings whether or not any
exist. These five rules are what stop that, and each is a way this assessment
manufactures a false result when it is dropped. Do not compress them, and do not skip
one because a run felt too clean to need it.

1. **Clean is an expected outcome.** Say so plainly and stop. A run that finds nothing
   is a result, in the same way a branch that teaches nothing recordable is a normal
   branch. Padding a clean run with observations you would not have volunteered is how a
   healthy mechanism acquires a maintenance backlog.
2. **A cost the contract already admits is not a finding.** This repository's
   `README.md` confesses its costs at length — lazily loaded rules, a listing that
   grows, rules that no audit can reach. Rediscovering one is not news, and reporting it
   as news buries whatever the run actually found. It becomes reportable only with
   evidence, seen during this walk, that the admitted cost has actually materialized
   here.
3. **Every finding names three things:** the text you read, the moment the problem
   bites, and what a future agent does wrong as a result. A finding missing any of the
   three is an opinion about style, and it goes in no report. The third part is the one
   that gets dropped, and it is the one that makes a finding actionable.
4. **Harness-specific and universal findings stay separated.** Reports from four
   harnesses are meant to be read against each other, and merging the two kinds makes
   that impossible — a defect in one tool reads as a defect in the mechanism, and the
   mechanism gets changed to fix a tool.
5. **The report states this skill's own limit.** Invoking it primed you, so you cannot
   report whether you would have consulted the almanac unprompted. Say that in the
   Limits section rather than letting the staging imply a rigor it does not have.

## Then offer

Two offers, after the report is delivered, and neither is taken without approval.
`almanac:init` proposes and `almanac:audit` proposes; nothing in this plugin writes
unreviewed, and an assessment is the last thing that should.

- **Offer to write the report to disk.** Propose
  `docs/review/<date>-<harness>-assessment.md` rather than assuming it — the directory
  may not exist, and where reports live is the repository's call, not this skill's.
- **Offer to file the obvious defects as issues.** State the bar: **a defect in the
  mechanism a maintainer would act on** — not a matter of taste, and not a restatement
  of an admitted cost. If nothing clears the bar, say so and make no offer. An offer to
  file nothing in particular is how a clean run becomes a backlog anyway.

## Common mistakes

- **Reading the contract before Stage 1 and reporting the result as a cold read.** The
  staging is the only instrument this skill has. Once you know what the listing was
  designed to do, your account of what you understood from it is a reconstruction, and
  it will read as a measurement.
- **Restating the README's admitted costs as discoveries.** The contract names them
  itself. Reporting one without evidence that it has materialized here is not a finding,
  and it displaces the ones that are.
- **Reporting a behavioral claim.** "An agent would skip this entry" is a measurement,
  and invoking this skill destroyed your standing to make it. Say what the text does;
  leave what agents do to the trial.
- **Merging harness-specific findings into universal ones.** The merge is invisible in a
  single report and only surfaces when four are compared — by which point the mechanism
  has been changed to fix one tool.
- **Producing findings because the skill was invoked** rather than because any exist. An
  assessment that never comes back clean is an assessment that measures nothing.
- **Assessing whether an entry is true.** That is `almanac:audit`, it needs commands
  this walk never runs, and a truth verdict reached here carries the authority of one
  that was actually checked.
