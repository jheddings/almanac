---
name: record
description: >-
    Use when you have just finished being surprised by this repository — its code, its
    CI, its tooling, or the agent harness you are running under — a debugging session
    that ended in "oh, that's why," a green build or passing suite that concealed a real
    failure, a tool that behaved differently than its documentation claims, or the
    discovery that an existing almanac entry is wrong. Also use on an explicit request
    to "record this in the almanac", "add an almanac entry", "write down this gotcha",
    or "make sure we don't learn this again".
---

# Record an Almanac Entry

The almanac holds facts discovered the hard way, recorded by agents for agents. **An
entry is a claim a future agent will act on without re-deriving it**, so the bar is
truth, not usefulness — a plausible entry that is subtly wrong costs more than no entry
at all, because it gets trusted instead of checked.

## Locate the almanac

In order — stop at the first step that resolves:

1. **`docs/almanac/README.md`.** The conventional location. If it exists, that is the
   almanac; do not look further.
2. **Glob `**/almanac/README.md`**, then discard matches under `templates/`,
   `.worktrees/`, `node_modules/`, `vendor/`, or any other checkout nested inside this
   one. A bare directory-name match is not evidence of an almanac — **a template, an
   example, or a sibling worktree's copy is not this repo's almanac**, and treating one
   as the target means recording a fact where nobody will read it.
3. **Exactly one survivor → that is the almanac.** More than one, ask which. None, this
   repo has no almanac — say so and stop, rather than creating one as a side effect of
   recording.

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

**Deciding where a fact belongs is your call to make, not a caveat to pass along.** An
entry you are unsure belongs is not an entry with a disclaimer attached; it is a
decision you still owe. Writing "a reviewer may judge this closer to `CONTRIBUTING`
territory" into the entry, the PR body, or your final report does **not** discharge that
decision. The almanac has no gate but you: a reviewer reading a hedged entry inherits
your uncertainty without your evidence, and the default outcome of an unresolved
category question is that the entry stays.

**If you cannot decide it belongs, it does not go in.** Put it where it does belong, or
say plainly that you are not recording it and why.

### Does it belong somewhere else?

Ask each question. Any _yes_ disqualifies the entry:

1. Is it **designed intent** — how a subsystem is meant to work, rather than what
   happened when it ran?
2. Is it a **rule someone is required to follow**?
3. Is it the **status of in-flight work**?
4. Is it a **spec or an implementation plan**?
5. Is it **your own working preference or habit**?
6. Is it true **only of your machine or environment**, not of this repository?

The questions are the method, so they live here. **The answers are irreducibly
repo-local, so they live in the almanac's `README.md`** — read its destinations table
for where each category goes in _this_ repo. Do not guess a destination, and do not file
into a directory you have not confirmed exists.

Question 1 is **design vs. discovery**: how a thing was meant to work is architecture;
what turned out to be true when someone ran it is an almanac entry.

Question 5 is the one that traps. A preference is not disqualified by being _about_ a
real, verified, expensive-to-rediscover fact — most preferences are. Split them: the
behavior you observed may be a fine entry; "so I do X" is memory. Record the behavior
and its consequence, not your routine — then apply question 6 to what is left.

Question 6 is **scope**, and the three tests below cannot catch it: they ask whether a
fact is durable, discovered, and costly, never _who it is true for_. A proxy on your
laptop, a path in your shell, a credential CI does not have — all three pass and the
entry is still false for every other contributor. Ask: **would this hold for CI and for
everyone else who clones this repo?** If no, it goes to memory however well it passes
the rest.

Scope is about _who_, not which layer surfaced the fact: how a CI runner, a package
manager, or an agent harness behaves _here_ is true for everyone who meets it here, and
it belongs — those entries travel furthest, since the next agent likely runs a different
tool. Only your own machine's state is out; split it the way question 5 splits.

### Does it pass all three?

1. **Durable** — still true in six months. How the system _behaves_ qualifies; what we
   are _currently doing_ does not.
2. **Discovered** — learned empirically, by running it. Not read off a design doc.
3. **Costly to rediscover** — non-obvious, expensive, or silent. If a competent agent
   works it out in two minutes, leave it out. Failures that look like success are the
   highest-value entries there are.

All three, or it does not go in. If you cannot state the fact in one sentence, you have
a design doc, not an entry.

### Is it already there?

Grep first — filenames state claims, so one keyword pass is enough. If a matching entry
is **wrong**, fix or delete it in this same change; a confidently-worded stale fact is
worse than none. If you suspect a duplicate but cannot find it, follow the README's
local rule on duplicates rather than guessing.

## Verify, don't transcribe

Re-check every claim against the tree as it is **now**, even when the source is your own
notes from this session, a memory file, or something the user stated as fact. Notes
record what was true when written, under assumptions that may not have survived. Run the
command, read the file, reproduce the failure. Under time pressure this is the step to
keep, not the step to drop — an unverified entry is the artifact this skill exists to
prevent.

If verification contradicts the claim, say so and record nothing (or record the
corrected fact you actually established).

## Write a verify line that fails when the claim fails

`verify` is what stops an entry from quietly going stale. A verify line that merely
**locates the subject** does not clear the bar — it passes forever, including after the
behavior changes.

Say the claim is "the deploy skips migrations because `--include-all` is absent."

- **Bad:** `grep -n "db push" .github/workflows/deploy.yaml` — locates the subject. It
  finds that line whether or not the flag is on it, so it passes forever, including
  after someone adds the flag and the entry becomes false.
- **Good:** `grep -rn -- "--include-all" .github/workflows/` returns nothing. The
  observation _is_ the claim, so the day someone adds the flag, this stops holding.

Two habits make the difference. Test the load-bearing detail, not the neighbourhood it
lives in. And state the **expected observation** — "returns nothing", "exits 1", "prints
`warn`" — because a bare command tells the next agent what to run and not what would
count as a refutation.

## Write it

- **One fact per file.** Filename is a kebab-case slug **stating the claim, not the
  topic** — `migrations-out-of-order-are-silently-skipped.md`, not `migrations.md`.
- **Format, required fields, and wrap width: follow the almanac's `README.md`.** Read
  it; do not reconstruct the frontmatter from memory or from another repo's entries. Add
  no fields beyond the ones it names.
- Write the fact plainly, then its consequence — **what breaks, and whether it breaks
  loudly**. Silent failures are the point; say so explicitly when a failure reads as
  success.
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
  truth.** True for you is not true for the repository; it goes in memory.
- "I noted the caveat in the entry" — a caveat is not a category decision.
- "The user gave me this, so I don't need to check it" — check it.
- "No time to verify; I'll record it and confirm later" — later does not come.
- "A verify line would be nice but I can't think of one" — if the claim cannot be
  re-checked cheaply, reconsider whether it is a fact or an impression.
- "The README has no row for this, so the almanac is the closest fit" — a missing
  destination is a gap in the README, not a licence to record. Say so and stop.
