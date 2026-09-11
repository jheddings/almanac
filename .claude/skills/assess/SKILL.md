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

This skill produces a **critique of the almanac mechanism from a first reading** — what
a fresh agent takes from it, what it retrieves, and where its pieces contradict each
other. It is not a verdict about any entry, and nothing here establishes whether a
recorded claim is still true.

The intended condition is a **fresh session under one harness**, with this skill invoked
before anything else in the repository has been read. That is what makes the walk worth
running: the findings are about what an agent understands before the design explains
itself, and an agent that has already read the design cannot produce them.

## What this is not

**Not `almanac:audit`.** The audit enumerates the entries, re-runs each fact's `verify`
line, and reaches a verdict — `holds`, `falsified`, `unverifiable` — about whether the
claim is still true. It owns that ground completely. **This skill never judges whether
an entry is true.** An entry may be badly stale and still assessed here as well-titled
and well-placed, because what is under assessment is retrieval and coherence, not truth.
If a claim looks wrong to you while you walk, say that the audit exists and move on; do
not verify it, and do not report a verdict.

**Not the trial harness.** That measures what an agent did, by driving a harness through
a fixture repository unattended and reading what came back. **This skill cannot measure
behavior, because invoking it primes the agent that would be the subject.** You were
told to go and look at the almanac, so nothing you do afterwards is evidence about
whether you would have looked. An assessment reporting a behavioral finding is reporting
a claim it has no standing to make, and it will be read as measurement by whoever
receives it.

**The priming goes three levels deep, and none of it is removable.** The invocation is
the first: you were told to go and look, so you cannot report whether you would have
looked unprompted. The second is the design — Stage 1 asks which titles you cannot
decode unopened, and Stage 2 cannot instruct a retrieval probe without naming retrieval,
so both hand you the contract's central claim before you reach it. **The walk therefore
tests how well the mechanism performs once you know what it is for, and never tests
discovery of the mechanism itself.** The third is the entries: Stage 1 necessarily loads
the whole listing, so by Stage 2 you have read every claim in the directory. Stage 2's
sourcing discipline governs **where a moment came from** and cannot make you blind to
what is already in there, which makes **a moment whose entry you recognised on sight
weaker evidence than one you did not.** No ordering of the stages fixes any of this —
Stage 1 has to come first. These three are what the report's Limits section carries.

## Before you start

> Do not open anything whose job is to explain this almanac's design until Stage 3 — the
> almanac's `README.md`, the repository's `README.md`, `CONTRIBUTING.md`, anything under
> `docs/design/`, and anything else that says why the mechanism is built the way it is.
> Stages 1 and 2 are worth having only because they happen before the design explains
> itself. An agent told what the listing is supposed to achieve cannot afterwards report
> what it actually understood from the listing alone.

The ban is on explanation, not on the repository. Build files, CI configuration, and the
project's own history stay open throughout, and Stage 2 needs them.

There is one exception: **the instruction files the harness surfaced on its own** —
`AGENTS.md`, `CLAUDE.md`, or whatever this tool loaded without being asked. Those are
first contact by definition, and Stage 1 reads them. Do not go looking for the ones it
did not surface; which ones it did is itself a Stage 1 observation.

If one of the banned documents was already open in this session before the skill was
invoked, say so in the report's Limits section and do not describe Stage 1 as cold.

## Stage 0 — Locate the almanac

Resolution needs to know which files exist, not what they say. **Check for
`docs/almanac/README.md` with a directory listing and leave it closed until Stage 3.**

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

Hold the resolved **directory**, and name it in the report. Step 2 can land on a
worktree's copy, and two reports that assessed different directories otherwise look
comparable.

## Stage 1 — First contact

Record four things, and record them now, while the design has not been explained. They
cannot be reconstructed at Stage 3.

- **Which instruction files the harness surfaced without being asked.** Name each one
  and mark it **repository-level** — checked into this tree, so every agent meets it —
  or **operator-level**, this user's own global instructions, which travel with them and
  are not part of this repository. Say whether the trigger to consult the almanac
  appeared in a repository-level file, and quote it. **Judge only the repository's.** An
  operator-level trigger makes the almanac look wired up when it is wired up for one
  person, and if no repository-level file was surfaced at all, that is the first finding
  of the run.
- **`ls` the almanac directory, and nothing else.** No grep, nothing opened. From the
  filenames alone, write down what this repository appears to know and what it appears
  to require of you.
- **Which titles you cannot decode without opening the file.** List them.
- **The shape of the listing, counted rather than estimated:** how many entries, how
  long the longest slug is, and how many of those entries you named in the two bullets
  above — **named meaning you paraphrased the claim**, not merely that the file was in
  the listing you read. Report those three numbers and stop there. The third is
  informative only once the listing is long enough that a reader stops before the end;
  where every title can be paraphrased in a single pass, report the count and draw
  nothing from it. Where your attention would have dropped, or what you would have done
  with a longer listing, is a claim about behavior, and this skill has no standing to
  make one.

## Stage 2 — Retrieval probe

Still no contract and still no skills. You have the listing and the notes from Stage 1.

**Derive the moments from what this repository does, not from what it has already
recorded.** A moment read off the listing tests nothing: it is served by construction,
so every probe hits and the stage reports clean retrieval without ever having looked for
a gap.

Build the list from the work instead:

- the recipes in `.justfile`, and what each one is for;
- the jobs in `.github/workflows/`, and what they gate;
- the last several merged pull requests — `gh pr list --state merged --limit 10` — and
  what they were touching. Skip the bot and dependency-update ones; they move a lockfile
  and stand in for no moment. Raise the limit until a few non-bot pull requests are in
  hand, because a window that returns nothing but bots leaves this source empty without
  saying so. Take **what changed** from the rest and nothing else: a pull request whose
  prose explains the almanac's design is banned like any other explanation, history or
  not.

From those, name at least six moments an agent working here actually reaches. Two or
three familiar ones are fine as illustrations — about to commit, setting up a worktree,
a build that came back green — but they cannot be the whole list.

**If every moment on your list turns out to be served, that is a legitimate result.** An
almanac that covers its repository is what a healthy one looks like. Before reporting
it, re-read your list against the three sources and confirm the moments came from there
rather than from the listing, then say plainly that they did. Never invent a moment
nobody here reaches in order to give the stage something to report.

For each moment, name **the entry that fires from its title alone** — not the entry you
could find by searching for it, but the one whose filename would stop you as you
scanned. **If two titles both fire, do not quietly pick the better one.** Either narrow
the moment until exactly one fires — which usually means you were holding two moments —
or record the collision, because two entries competing for a single moment is a
retrieval finding in its own right: whichever one an agent opens first may not be the
one that applies.

Then **run a single keyword grep, in the filename-only form** —
`grep -rl --exclude=README.md <keyword> <almanac-dir>/` — and record the command and its
output verbatim. `-l` returns paths instead of bodies, and the exclusion keeps the
almanac's own `README.md` out of the results; without both, a keyword that happens to
match that file prints it, and you have read at Stage 2 the document Stage 3 exists to
introduce. The grep you ran is the evidence; the one you imagine you would have typed is
not.

**A hit list covering most of the directory is a fact about your keyword, not about
retrieval.** `-l` suppresses the matched line but still matches file content, and every
entry carries structural text above its claim — `record` matches the `recorded:` field
in every entry there is. Check the hits against the slugs: if files whose titles have
nothing to do with the keyword came back, it matched structure rather than a claim.
Discard that keyword and pick another. Reporting its coverage as retrieval is worse than
running no probe at all, because it arrives looking like the strongest result available.

Then the two findings this stage exists for:

- **An entry that fires for no moment.** Its body may be excellent and it will never
  load. Name it.
- **A moment served by no entry.** Two causes, and they take different fixes: either
  nothing was ever recorded, or something was recorded under a title that does not state
  the claim. Say which you think it is.

Weigh how discriminating the probe was. **A probe in which every moment was served is
weak evidence about retrieval** — it barely exercises the sampling that would find a gap
— so say how many moments your enumeration produced and how many you carried forward.

## Stage 3 — Read the contract and the skills

The ban lifts here, on everything it covered. Read the almanac's `README.md`, the
repository's instruction files in full, the sibling skills, the repository's
`README.md`, `CONTRIBUTING.md`, and `docs/design/`.

**The reconciliation is the point.** You are holding notes written before the
explanation landed. Compare what the mechanism intended against what you actually took
from it, and say where the two diverge. That divergence is the finding, and it is
unavailable to anybody who read the contract first. **If the contract reads as
unsurprising, the likeliest reason is the priming rather than genuine agreement** — say
so alongside any "no divergence" you report about retrieval.

Then five coherence checks. They ask what the texts say; whether this harness can run
anything is Stage 4's, with the single exemption the fourth bullet names:

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
  installed directory as your harness exposes it. That chain is written for a repository
  that installed the plugin; **when the tree you are assessing is itself the plugin, the
  canonical copy is the one in this tree and the plugin-root variable is not the
  route.** Report a gap; upgrade nothing. **This is the exemption to the routing
  above**, because resolving the canonical copy is otherwise a harness question: if none
  of the fallbacks resolves here, the comparison is unavailable and that is a Stage 4
  finding, not a defect in the contract.
- **Whether the commands the contract prints are complete and correct as written.** Read
  them; do not run them here. The retrieval commands under "Using the almanac" carry
  placeholders — `<almanac-dir>`, `<keyword>` — so they cannot be pasted literally, and
  what this check asks is whether the surrounding text makes the substitution obvious
  and the flags right. **Never run an entry's `verify` line.** That is the audit's, and
  a verdict reached here would be the truth claim this skill has just declared it does
  not make.

## Stage 4 — Harness fit

This stage owns tool availability, and no other stage does. One test routes a finding:
**would it disappear under a different harness?** Yes, and it is harness-specific and
belongs here and in the harness-specific half of the report. No, and it is universal,
whichever stage turned it up.

Answer each one concretely — run it, or try it — rather than assuming it from what you
know about harnesses in general:

- **Do the skills load, and under what name?** `almanac:record`, some other spelling, a
  file path you had to name yourself, or not at all.
- **Do subagents exist**, for the fan-out `almanac:audit` describes? If not, the audit
  degrades to a sequential run — which is fine, and the skill says so — but a report
  that leaves it unstated implies a capability this harness does not have.
- **Does the plugin-root variable resolve?** Print it. Every revision-stamp check in the
  plugin starts there, and an unset variable sends each of them down a different
  fallback.
- **Do the contract's retrieval commands run here?** Take the ones under "Using the
  almanac", substitute the placeholders for the resolved directory and a real keyword,
  and run them — the listing and the grep, flags included. An `--exclude` or `--glob`
  this harness's tooling will not accept turns the contract's one-command retrieval
  check into a dead end at the moment it is needed. Run nothing else the contract
  prints; an entry's `verify` line is the audit's.

## Common mistakes

Read these before writing the report, while there is still something to do about them.
The numbered rules they point at are in "What keeps this honest", below.

- **Reading an explanatory document before Stage 1**, then reporting the result as a
  cold read — see "Before you start".
- **Restating an admitted cost as a discovery** — rule 2.
- **Reporting a behavioral claim**, about an agent or about yourself — see "What this is
  not".
- **Merging harness-specific findings into universal ones** — rule 4, and the routing
  test in Stage 4.
- **Producing findings because the skill was invoked** rather than because any exist —
  rule 1.
- **Taking Stage 2's moments from the listing**, which guarantees every probe hits.
- **Grepping the almanac without `-l` and the `README.md` exclusion**, which prints the
  contract into a stage that has not read it.
- **Assessing whether an entry is true**, or running its `verify` line — that is
  `almanac:audit`.

## Stage 5 — Report

Deliver the report in the session, in this section order and no other. The order is
fixed so that two runs — successive runs under one harness, or parallel runs under four
— can be read against each other line by line.

1. **What ran** — the harness, the date, the almanac directory Stage 0 resolved, and
   what was read at each stage.
2. **First contact** — the Stage 1 record, as written at the time.
3. **Retrieval** — the Stage 2 record, including both failure shapes, and explicitly
   saying so when one of them is empty.
4. **Coherence** — the Stage 3 reconciliation and the five checks.
5. **Harness fit** — the Stage 4 answers.
6. **Findings** — universal first, harness-specific second, each carrying its three
   parts.
7. **Limits** — what this run could not establish, the three levels of priming under
   "What this is not" among them.

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
   `README.md` confesses its costs at length, and Stage 3 is where you meet them.
   Rediscovering one is not news, and reporting it as news buries whatever the run
   actually found. It becomes reportable only with evidence, seen during this walk, that
   the admitted cost has actually materialized here.
3. **Every finding names three things:** the text you read, the moment the problem
   bites, and what a future agent does wrong as a result. A finding missing any of the
   three is an opinion about style, and it goes in no report. The third part is the one
   that gets dropped, and it is the one that makes a finding actionable.
4. **Harness-specific and universal findings stay separated.** Reports from four
   harnesses are meant to be read against each other, and merging the two kinds makes
   that impossible — a defect in one tool reads as a defect in the mechanism, and the
   mechanism gets changed to fix a tool.
5. **The report states this skill's own limit.** The three levels of priming are set out
   under "What this is not", and the Limits section is where they go. Write them there
   rather than letting the staging imply a rigor it does not have.

## Then offer

Two offers, after the report is delivered, and neither is taken without approval.

- **Offer to write the report to disk.** Propose
  `docs/review/<date>-<harness>-assessment.md` rather than assuming it — the directory
  may not exist, and where reports live is the repository's call.
- **Offer to file the obvious defects as issues.** State the bar: **a defect in the
  mechanism a maintainer would act on** — not a matter of taste, and not a restatement
  of an admitted cost. If nothing clears the bar, say so and make no offer. An offer to
  file nothing in particular is how a clean run becomes a backlog anyway.
