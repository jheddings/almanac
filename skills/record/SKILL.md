---
name: record
description: >-
    Use when this repository has just taught you something a future agent must not
    re-derive. Either of two moments qualifies. You have finished being surprised by it
    — its code, its CI, its tooling, or the agent harness you are running under — a
    debugging session that ended in "oh, that's why," a green build or passing suite
    that concealed a real failure, a tool that behaved differently than its
    documentation claims, or the discovery that an existing almanac entry is wrong. Or a
    convention has become binding here — a decision about commits, branches, reviews,
    worktrees, or where work happens that everyone is now expected to follow, including
    one you find living where an agent will meet it too late to act on. Also use on an
    explicit request to "record this in the almanac", "add an almanac entry", "write
    down this gotcha", "we should write this rule down", or "make sure we don't learn
    this again".
---

# Record an Almanac Entry

The almanac holds a repository's operating knowledge, recorded by agents for agents and
retrieved by filename. **An entry is a claim a future agent will act on without
re-deriving it**, so a plausible entry that is subtly wrong costs more than no entry at
all: it gets trusted instead of checked.

Decide the **kind** before anything else. A **fact** is something reality can refute —
it carries a `verify` line, and an audit re-runs it. A **rule** is something this
repository requires — reality cannot refute it, only a decision can change it, and it
carries no `verify` line and no audit. One question settles it: **can this be false
without anyone changing their mind?** Yes, `fact`. No, `rule`. Wrong in the `rule`
direction and a real fact stops being checkable; wrong in the `fact` direction and an
audit reports compliance as if it were truth.

## Locate the almanac

In order — stop at the first step that resolves:

1. **`docs/almanac/README.md`.** The conventional location. If it exists, that is the
   almanac; do not look further.
2. **Glob `**/almanac/README.md`**, then discard matches under `templates/`,
   `node_modules/`, `vendor/`, or any other checkout nested inside this one. A bare
   directory-name match is not evidence of an almanac — **a template, an example, or a
   sibling worktree's copy is not this repo's almanac**, and treating one as the target
   means recording a fact where nobody will read it.
3. **Exactly one survivor → that is the almanac.** More than one, ask which. None, this
   repo has no almanac — say so and stop, rather than creating one as a side effect of
   recording.

**These steps search this tree, and never look up.** A workspace or parent repository
enclosing this checkout may keep its own almanac; that is a separate almanac with a
separate subject, and this tree's is the one that resolves. Read the outer one when it
is relevant to what you are doing, and record what this tree taught you here.

Hold the resolved **directory**, not just the README, and write into that directory.

**Read that README before writing anything.** It is the local contract, and it carries
things this skill deliberately does not: the required frontmatter fields, the wrap
width, where non-almanac content goes in this repo, and when a correction ships.

## Precedence

This skill owns the **method**: the admission tests, what disqualifies an entry, and the
procedure for writing one. The almanac's `README.md` owns what is genuinely **local to
this repository** — the file format, the wrap width, when an entry ships, and the
destinations for content that doesn't belong in the almanac.

- They disagree about method → **this skill wins.**
- They disagree about a convention the README claims as repo-local → **the README
  wins.**

The reason: the method is maintained centrally and travels across repos. If each repo's
README outranked it, one stale local copy would silently override a corrected rule.

## The category gate

This is the step agents skip. Not by ignoring it — by _noticing_ the problem, writing
the doubt down, and filing the entry anyway.

**Deciding where a claim belongs is your call to make, not a caveat to pass along.** An
entry you are unsure belongs is not an entry with a disclaimer attached; it is a
decision you still owe. Writing the doubt into the entry, the PR body, or your final
report does **not** discharge it. The almanac has no gate but you: a reviewer reading a
hedged entry inherits your uncertainty without your evidence, and the default outcome of
an unresolved category question is that the entry stays.

**If you cannot decide it belongs, it does not go in.** Put it where it does belong, or
say plainly that you are not recording it and why.

### Does it belong somewhere else?

Ask each question. Any _yes_ disqualifies the entry:

1. Is it **designed intent** — how a subsystem is meant to work, rather than something
   you would act on at a nameable moment?
2. Is it the **status of in-flight work**?
3. Is it a **spec or an implementation plan**?
4. Is it **your own working preference or habit**?
5. Is it true **only of your own machine's state**, not of this almanac's subject?

**A rule someone is required to follow is not on this list.** Rules belong in the
almanac as `kind: rule` entries; that is what makes the directory listing the whole
index of how to work here rather than half of it.

The questions are the method, so they live here. **The answers are irreducibly
repo-local, so they live in the almanac's `README.md`** — read its destinations table
for where each category goes in _this_ repo. Do not guess a destination, and do not file
into a directory you have not confirmed exists.

If the category has no row at all, the table is incomplete — a gap in the README rather
than permission to record here. Ask the operator where that category goes, and hand them
the text you would have filed. Dropping the claim because the table came up short loses
it exactly as thoroughly as filing it wrong.

Question 1 is **intent vs. requirement**, and it is the one that blurs. An architecture
note explains how a mechanism was _meant_ to work, and reading it changes nothing you
are about to type; a rule tells you what to type.

Question 4 is the one that traps, and admitting rules sharpens it rather than softening
it: a rule is what this repository requires of _everyone_, while a preference is what
you happen to do. "Commits here use conventional format" is a rule; "I like to commit
early and often" is memory. **If nobody would be wrong for doing it differently, it is
not a rule.** Split a preference sitting on top of a real fact: the behavior you
observed may be a fine `fact`; "so I do X" is memory. Then apply question 5 to what is
left.

Question 5 is **scope**, and the three tests below cannot catch it: they ask whether an
entry is durable, actionable, and costly to miss, never _who it is true for_. A proxy on
your laptop, a path in your shell, a credential CI does not have — all three pass and
the entry is still false for everyone else. Ask: **would this hold for everyone else
working on this almanac's subject?** If no, it goes to memory however well it passes the
rest.

The subject is this repository, unless the almanac's `README.md` declares another one —
a workspace holding several checkouts, say. Read the README before you apply this
question; you already have to. For a repository it reads _would this hold for CI and for
everyone who clones it?_

Scope is about _who_, not which layer surfaced the claim: how a CI runner, a package
manager, or an agent harness behaves _here_ is true for everyone who meets it here, and
it belongs. Only your own machine's state is out.

### Does it pass all three?

1. **Durable** — still true in six months. How the system _behaves_ and what this
   repository _requires_ both qualify; what we are _currently doing_ does not.
2. **Actionable** — a future agent does something differently for knowing it, at a
   moment you can name. If nothing changes, it is background reading.
3. **Costly to miss** — non-obvious in the moment, or silent and expensive when missed.
   If a competent agent works it out in two minutes, or the mistake is caught loudly the
   first time, leave it out. Failures that look like success are the highest-value
   entries there are.

All three, or it does not go in. If you cannot state the claim in one sentence, you have
a design doc, not an entry.

### Would the title fire?

Bodies load lazily and the filenames are the whole index, so **an entry whose title does
not fire at the right moment does not exist.** Name the moment first — the command about
to run, the decision about to be made — then check that the slug would surface the entry
to an agent scanning the listing and nothing else. This test replaces provenance: what
matters is not whether the claim was discovered or decided, but whether it can be
retrieved by someone who does not yet know they need it.

### Is it already there?

Grep first — filenames state claims, so one keyword pass is enough. If a matching
**fact** is wrong, fix or delete it in this same change; a confidently-worded stale fact
is worse than none. A **rule** you believe is wrong is not yours to correct — only
whoever can change the decision behind it can, and nobody following it is evidence about
people. Raise it; do not resolve it. If you suspect a duplicate but cannot find it,
follow the README's local rule on duplicates rather than guessing.

## Verify, don't transcribe

Re-check every fact against the tree as it is **now**, even when the source is your own
notes from this session, a memory file, or something the user stated. Notes record what
was true when written, under assumptions that may not have survived. Run the command,
read the file, reproduce the failure. Under time pressure this is the step to keep — an
unverified entry is the artifact this skill exists to prevent. For a rule, the
equivalent is confirming the decision still stands and finding where it is written.

If verification contradicts the claim, say so and record nothing (or record the
corrected fact you actually established).

## Write a verify line that fails when the claim fails

**Facts only.** A rule has nothing to re-run: a check that a rule is being followed
measures compliance, not truth, and a failure would mean somebody broke the rule rather
than that the entry is wrong. Putting a command on a rule lets an audit return a verdict
about the wrong thing. Leave the field off.

`verify` is what stops an entry from quietly going stale. A verify line that merely
**locates the thing it describes** does not clear the bar — it passes forever, including
after the behavior changes.

Say the claim is "the deploy skips migrations because `--include-all` is absent."

- **Bad:** `grep -n "db push" .github/workflows/deploy.yaml` — locates the thing it
  describes. It finds that line whether or not the flag is on it, so it passes forever,
  including after someone adds the flag and the entry becomes false.
- **Good:** `grep -rn -- "--include-all" .github/workflows/` returns nothing. The
  observation _is_ the claim, so the day someone adds the flag, this stops holding.

Two habits make the difference. Test the load-bearing detail, not the neighbourhood it
lives in. And state the **expected observation** — "returns nothing", "exits 1", "prints
`warn`" — because a bare command tells the next agent what to run, not what would count
as a refutation.

## Write it

- **One claim per file.** Filename is a kebab-case slug **stating the claim, not the
  topic** — `migrations-out-of-order-are-silently-skipped.md`, not `migrations.md`;
  `branch-names-carry-the-commit-type-prefix.md`, not `branching.md`.
- **Declare the `kind`.** A rule opens its body with **Applies when:** and the moment it
  fires, then the requirement, then why it exists. A fact states the fact, then its
  consequence.
- **Format, required fields, and wrap width: follow the almanac's `README.md`.** Read
  it; do not reconstruct the frontmatter from memory or from another repo's entries. Add
  no fields beyond the ones it names.
- Write a fact plainly, then its consequence — **what breaks, and whether it breaks
  loudly**. Silent failures are the point; say so explicitly when a failure reads as
  success.
- A rule **moved** from another document is a move, not a copy: delete the original in
  the same change, or the two copies diverge and the stale one wins.
- Give the corrective action if there is one, and cross-link entries in the same class.
- Don't hedge about **truth** either: no "seems to", no "I think". Uncertainty belongs
  in the PR discussion, not in a file future agents treat as settled.
- **When it ships** — same PR as the work, or otherwise — is the README's call.

An agent cannot review its own entry: whatever produced a wrong claim would equally
approve it. Say clearly in your report what you recorded and on what evidence, so a
human can.

## Red flags — STOP

- "A reviewer may judge this closer to X territory, but I kept it" — **you have not made
  the decision.** Decide, or don't record it.
- "It's arguably a preference, but the underlying fact is real" — record the fact, drop
  the routine, or file it in memory.
- "It's only true on my setup, but the fact itself is real" — **that is scope, not
  truth.** True for you is not true for the subject; it goes in memory.
- "I noted the caveat in the entry" — a caveat is not a category decision.
- "The user gave me this, so I don't need to check it" — check it.
- "The operator told me, so it isn't discovered" — provenance is not a test. Confirm it,
  decide its `kind`, and record it.
- "Everyone here does it this way, so it's a rule" — if nobody would be wrong for doing
  it differently, it is a preference. That goes to memory.
- "I'll give the rule a verify line so the audit covers it too" — that reports
  compliance as truth. Rules carry no verify line and no audit; that is the cost.
- "No time to verify; I'll record it and confirm later" — later does not come.
- "A verify line would be nice but I can't think of one" — if the claim cannot be
  re-checked cheaply, reconsider whether it is a fact, an impression, or a rule.
- "The README has no row for this, so the almanac is the closest fit" — a missing
  destination is a gap in the README, not a licence to record. Say so, then ask where it
  goes; stopping without asking abandons the claim.
