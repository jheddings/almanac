<!-- almanac-template: 4 -->

# Almanac

Operating knowledge for this repository, recorded by agents for agents and loaded on
demand.

An entry is something an agent working here needs to know and would not otherwise have:
a silent failure mode, a tool that lies, a constraint invisible from the code — or a
convention this repository requires that no amount of reading the code would reveal.
Entries are terse, atomic, and durable. One claim per file.

The **filenames are the index**, and they carry the whole retrieval mechanism. They are
meant to be read cold at the start of a session, without opening anything: a listing of
claim-shaped slugs tells an agent what this repository already knows and what it will be
held to. Bodies load only when a title looks like it applies.

Humans are welcome here, but the audience is the next agent — likely one with no memory
of this session, possibly running under a different tool.

## Two kinds of entry

Every entry declares a `kind`, and the two behave differently under maintenance.

**`fact`** — something true about the subject that reality can refute. The deploy skips
migrations; the mock does not intercept; the runner has no outbound network. A fact
carries a `verify` line, and an audit re-runs it.

**`rule`** — something you are required to do here. Branch naming, commit format, where
work happens. Reality cannot refute a rule; only a decision can change it. A rule
carries no `verify` line, and no audit can check it — see
[Maintaining the almanac](#maintaining-the-almanac).

The fastest test for which one you are holding: **can this be false without anyone
changing their mind?** Yes, `fact`. No, `rule`.

Facts and rules live in one directory on purpose. The index is only useful if it is the
_whole_ index — an agent that must consult two directories to find out how to work here
will reliably consult one. The cost is real and stated below.

## What belongs here

An entry must pass all three tests:

1. **Durable** — will it still be true in six months? How the system _behaves_ and what
   this repository _requires_ both qualify. What we are _currently doing_ does not.
2. **Actionable** — would a future agent do something differently for knowing it? An
   entry exists to change a decision at a specific moment. If nothing changes, it is
   background reading, and background reading belongs in the docs.
3. **Costly to miss** — is it non-obvious in the moment, or does missing it fail
   silently or expensively? If a competent agent works it out in two minutes, or the
   mistake is caught loudly the first time, leave it out. Failures that look like
   success are the highest-value entries we can write.

### The title is the gate

Bodies load lazily, so **an entry whose title does not fire at the right moment does not
exist.** Before writing, name the moment the entry applies — the command about to run,
the decision about to be made — and check that the filename would surface it to an agent
scanning the listing and nothing else.

This is the test that replaces provenance. It does not matter whether a claim was
discovered by running into it or decided in a meeting; what matters is whether it can be
retrieved by an agent who does not yet know it is needed. If you cannot state the claim
in one sentence, or the slug names a topic rather than a claim, it is a design doc, not
an entry.

**Subject.** The three tests ask whether an entry is durable, actionable, and costly to
miss — never _who_ it is true for. That last question is scope, and it reads against
this almanac's **subject**: this repository, unless the local block below declares
otherwise. Ask _would this hold for everyone else working on this subject?_ — for a
repository, that means CI and everyone who clones it. A claim true only of one person's
machine, or only of how one person likes to work, goes to your agent's private memory,
however well it passes the three tests.

## What doesn't belong here

<!-- almanac:local -->

| If it is...                              | It goes...                  |
| ---------------------------------------- | --------------------------- |
| Designed intent, a spec, or a plan       | `docs/design/`              |
| The status of in-flight work             | A GitHub issue or PR        |
| Your own working preferences             | Your agent's private memory |
| A fact about your machine, not this repo | Your agent's private memory |

This repo is small enough that design intent, specs, and plans share one directory
rather than three. Rules that used to live in `AGENTS.md` are entries here now; that
file keeps the trigger to read this listing, and nothing else that an entry could carry.

Entries wrap at **88 columns** — `.prettierrc.json`, applied by the pre-commit hook, so
the convention is enforced rather than remembered. Prettier reflows frontmatter values
too, folding a long `verify` line onto indented continuation lines; that round-trips to
the same string, so leave it as prettier leaves it. Fenced blocks are untouched.

<!-- /almanac:local -->

Notice which row is **absent**: a rule you are required to follow is no longer routed
elsewhere. Rules are entries, declared `kind: rule`. What remains excluded is everything
an agent cannot act on at a nameable moment — intent, plans, status — plus everything
that is true for you and not for the subject.

The design-doc boundary is the one that blurs, so apply it as **intent vs.
requirement**: an architecture note explains how a mechanism was _meant_ to work, and
reading it changes nothing you are about to type. A rule tells you what to type. Same
topic, different job.

## Entry format

One claim per file. Filename is a kebab-case slug stating that claim, not the topic —
`migrations-out-of-order-are-silently-skipped.md`, not `migrations.md`;
`branch-names-carry-the-commit-type-prefix.md`, not `branching.md`. This matters more
than it looks: the filenames are the index, so a slug that states a claim is readable
knowledge on its own.

A fact:

```text
---
title: Out-of-order migrations are silently skipped on deploy
kind: fact
recorded: 2026-08-15
source: "PR #1129"
verify: "`grep -rn -- '--include-all' .github/workflows/` returns nothing"
verified: 2026-08-16
tags: [migrations, deploy, ci, silent-failure]
---

One or two sentences stating the fact plainly.

**Why it matters:** the consequence — what breaks, and whether it breaks loudly.

**What to do:** the corrective action, if there is one.
```

A rule:

```text
---
title: Branch names carry the commit type as a prefix
kind: rule
recorded: 2026-08-15
source: "CONTRIBUTING.md, migrated 2026-08-15"
tags: [git, branches, conventions]
---

**Applies when:** you are about to create a branch.

One or two sentences stating what is required, with an example.

**Why:** the reason the rule exists, and what goes wrong without it.
```

`title`, `kind`, `recorded`, and `source` are required. `source` is a PR, a commit, a
short description of the circumstances a fact was observed in, or — for a rule — where
the decision is recorded and when it moved here.

**`verify` and `verified` belong to facts only.** A rule has nothing to re-run: a check
that a rule is being followed measures compliance, not truth, and a failure means
somebody broke the rule rather than that the entry is wrong. Putting a command there
would let an audit report a verdict about the wrong thing.

`verify` is strongly encouraged on every fact: a command or check that re-tests the
claim cheaply, **plus the observation that would confirm it** — "returns nothing",
"exits 1", "prints `warn`". A bare command tells the next agent what to run and not what
would count as a refutation, and a check that merely locates the thing it describes
passes forever, including after the behavior changes. This is the only real defense
against an entry that quietly went stale.

**Quote any value containing `#` or `:`.** Unquoted, `source: PR #1129` parses as `PR` —
YAML reads the rest as a comment, and nothing warns you. `verify` lines almost always
need quoting.

`verified` is optional and means exactly one thing: **someone ran the `verify` line on
that date and the claim held.** Never set it on the strength of having read the entry,
edited nearby code, or assumed it's still fine — a freshness signal that decouples from
an actual re-check is worse than no signal, because it launders a stale fact as a
current one. If you ran the check and it held, bump it. Otherwise leave it alone.

`tags` aid discovery; use them freely, since search is how entries get found.

**No other fields.** Git supplies history and modification times, and every extra field
rots. In particular there is no `confidence` and no `status`: an entry you are not
confident about should not exist.

## Using the almanac

**Read the directory listing first, before you need it.** `ls <almanac-dir>/` is the
table of contents: every filename is a claim, so scanning them tells you both what this
repository already knows and what it requires of you. Do this when a session starts and
when you enter an unfamiliar area — not once you're stuck. The entries worth most are
the ones you would never think to search for, because you do not yet know they apply.

`<almanac-dir>` is wherever this file lives — conventionally `docs/almanac/`, but the
path is this repository's call, not the contract's. There is no index file to consult
and none to maintain.

**Then carry the titles, not the bodies.** Having read the listing, load an entry when
its title bears on what you are about to do: before a commit, before a branch, before a
migration, or the moment something behaves unexpectedly. This is the whole economy of
the directory — an always-on index of one line per claim, and a body read only on
suspicion.

Grep it before assuming something is undocumented — filenames state claims, so
`grep -rl --exclude=README.md <keyword> <almanac-dir>/` (or `rg -l --glob '!README.md'`)
is usually enough. Exclude this file deliberately: it is the contract, not a claim, and
its worked examples are keyword-dense enough to match almost any probe.

Read the entry, and if it is a fact carrying a `verify` line and you're about to act on
something expensive, run it.

Entries are assertions, not suggestions. A `rule` is binding. If a `fact` contradicts
what you're seeing, the entry is a suspect, not an authority — see below.

## Method vs. local convention

This file is the **local** contract: the almanac's subject, the entry format, the
destinations table above, the wrap width, when a correction ships, how parallel sessions
avoid contention. Those are this repository's calls.

The **method** — the admission tests, how to decide whether a claim belongs, how to
write a `verify` line that fails when its claim fails, how to re-check entries that may
have gone stale — is carried by skills, so that it can be maintained in one place and
travel to other repositories. This file is not.

So: **where a skill and this file disagree about method, the skill wins. Where they
disagree about a convention this file claims as local, this file wins.** That is the
reverse of the obvious anti-drift instinct, and the reason matters: if each repository's
README outranked the shared method, one stale local copy would silently override a
corrected rule — drift with the _worse_ copy winning, which is strictly worse than
having no precedence rule at all.

The two barely overlap by design, so there is little to drift. Agents on tools that
cannot load skills should treat this file as the whole contract and apply the three
tests above with care.

## Maintaining the almanac

**Writing a fact.** Record one when you've just finished being surprised: a debugging
session that ended in "oh, _that's_ why," a green build that hid a real failure, a tool
that behaved differently than its docs claim. Write it in the same PR as the work that
uncovered it, while the evidence is still in front of you.

**Writing a rule.** Record one when a convention becomes binding here, or when you find
an existing convention living somewhere an agent won't read at the moment it applies. A
rule migrated out of another document is a move, not a copy — leave no second version
behind, because two copies of a rule diverge and the stale one wins whichever is read
first.

Don't hedge, in either kind. If you aren't confident it's true or that it's required,
don't write it — uncertainty belongs in the PR discussion, not in a file future agents
will treat as settled.

**Finishing.** Noticing and recording are two different acts, and the second is the one
that gets skipped: the session ends, the surprise is still in the transcript, and
nothing durable was written. So before opening a PR, ask explicitly — _did this branch
teach us anything an entry should carry?_ Answer it, out loud, even when the answer is
no. Most branches produce no entry.

**Correcting.** If you discover a fact is wrong, fix or delete it in your current PR.
Deleting a falsified entry is worth as much as adding a true one; a confidently-worded
stale fact is worse than no fact at all, because it gets acted on without re-derivation.
When a fix supersedes an entry rather than refuting it, update `recorded` and note what
changed.

**A rule is corrected only by whoever can change the decision.** An agent may not delete
or reword a `kind: rule` entry because it seems wrong, obsolete, or inconvenient —
observing that nobody follows a rule is evidence about people, not about the rule. Raise
it; do not resolve it.

**Rules cannot be audited, and this is the standing cost of keeping them here.** A fact
has a `verify` line, so an audit re-runs it and a stale fact gets caught. A rule has
nothing to re-run, so it decays in exactly the way this directory exists to prevent: it
stays confidently worded after the decision behind it has changed, and the only thing
that catches it is a human reading the listing. Review the `kind: rule` entries by hand
whenever the surrounding process changes.

**Reviewing.** Entries ride in the PR diff and get reviewed like code. This is
deliberate: an agent cannot validate its own entry, because whatever led it to write
something wrong would equally lead it to approve it. Nothing writes here unreviewed —
and nothing writes here automatically. There is no background summarizer and no
session-end capture, because an unreviewed entry is the artifact this directory exists
to prevent.

## Parallel sessions

Concurrent worktrees and sessions write to the almanac at once, so it is designed to
avoid write contention:

- **No index file.** Nothing to append to means nothing to conflict over. Discovery is
  by filename and grep, not a table of contents.
- **One claim per file.** Two sessions recording two claims touch two files.
- **Duplicates are cheap, conflicts are not.** If you suspect an entry already exists
  but can't find it, write yours anyway. A reviewer merging two entries is a minor
  cleanup; a hand-resolved conflict in a shared index silently duplicates or drops
  content.
