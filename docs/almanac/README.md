<!-- almanac-template: 3 -->

# Almanac

Discovered facts about working in this repository, recorded by agents for agents.

An almanac entry is something we **learned the hard way** and don't want to learn again:
a silent failure mode, a tool that lies, a constraint that isn't visible from the code.
The subject is as often the CI, the build tooling, or the agent harness as the code
itself — what matters is that the fact holds for anyone working here, not which layer
surfaced it. It is not documentation, and it is not a plan. Entries are terse, atomic,
and durable.

Humans are welcome here, but the audience is the next agent — likely one with no memory
of this session, possibly running under a different tool.

## What belongs here

An entry must pass all three tests:

1. **Durable** — will it still be true in six months? Facts about how the system
   _behaves_ qualify. Facts about what we're _currently doing_ do not.
2. **Discovered** — did someone find this out by running into it, rather than decide it?
   Provenance in _this_ session does not matter: a fact the operator hands you was
   discovered too, and counts once you have confirmed it. What does not count is
   anything true because someone chose it.
3. **Costly to rediscover** — is it non-obvious, expensive, or silent? If a competent
   agent would work it out in two minutes, leave it out. Failures that look like success
   are the highest-value entries we can write.

If you can't state the fact in one sentence, it's probably a design doc, not an entry.

**Subject.** The three tests ask whether a fact is durable, discovered, and costly —
never _who_ it is true for. That last question is scope, and it reads against this
almanac's **subject**: this repository, unless the local block below declares otherwise.
Ask _would this hold for everyone else working on this subject?_ — for a repository,
that means CI and everyone who clones it. Either way, a fact true only of one person's
machine goes to your agent's private memory, however well it passes the three tests.

## What doesn't belong here

<!-- almanac:local -->

| If it is...                              | It goes...                      |
| ---------------------------------------- | ------------------------------- |
| A rule you're required to follow         | `AGENTS.md` / `CONTRIBUTING.md` |
| Designed intent, a spec, or a plan       | `docs/design/`                  |
| The status of in-flight work             | A GitHub issue or PR            |
| Your own working preferences             | Your agent's private memory     |
| A fact about your machine, not this repo | Your agent's private memory     |

This repo is small enough that design intent, specs, and plans share one directory
rather than three.

Entries wrap at **88 columns** — `.prettierrc.json`, applied by the pre-commit hook, so
the convention is enforced rather than remembered. Prettier reflows frontmatter values
too, folding a long `verify` line onto indented continuation lines; that round-trips to
the same string, so leave it as prettier leaves it. Fenced blocks are untouched.

<!-- /almanac:local -->

The design-doc boundary is the one that blurs, so apply it as **design vs. discovery**:
an architecture note explains how a mechanism was _meant_ to work. An almanac entry
records what was observed when it ran — that a particular mock silently fails to
intercept, say. Same subject, different epistemics.

The general form of that boundary, and the fastest test when a row above is in doubt:
**can this be false without anyone changing their mind?** Reality can refute a fact.
Intent can only be diverged from, a rule only broken, a preference only dropped. It
follows that a fact which matters only as the rationale for a rule written down
elsewhere stays with the rule — the almanac is for facts you would act on even if no
rule existed.

## Entry format

One fact per file. Filename is a kebab-case slug stating the claim, not the topic —
`migrations-out-of-order-are-silently-skipped.md`, not `migrations.md`. This matters
more than it looks: the filenames are the index (see below), so a slug that states a
claim is readable knowledge on its own.

```text
---
title: Out-of-order migrations are silently skipped on deploy
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

`title`, `recorded`, and `source` are required. `source` is a PR, a commit, or — when
the fact was observed directly rather than uncovered by a change — a short description
of the circumstances.

`verify` is strongly encouraged: a command or check that re-tests the claim cheaply,
**plus the observation that would confirm it** — "returns nothing", "exits 1", "prints
`warn`". A bare command tells the next agent what to run and not what would count as a
refutation, and a check that merely locates the subject passes forever, including after
the behavior changes. This is the only real defense against an entry that quietly went
stale, because it lets a future agent re-check instead of trusting blindly.

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
rots. In particular there is no `confidence` and no `status` field: an entry you are not
confident about should not exist.

## Using the almanac

**Read the directory listing.** `ls <almanac-dir>/` is the table of contents: every
filename is a claim, so scanning them tells you what this repository already knows.
`<almanac-dir>` is wherever this file lives — conventionally `docs/almanac/`, but the
path is this repository's call, not the contract's. There is no index file to consult
and none to maintain. Do this when you start work in an unfamiliar area, not only once
you're stuck — the entries worth most are silent failures you would never think to
search for.

Grep it before assuming something is undocumented — filenames state claims, so
`grep -rl --exclude=README.md <keyword> <almanac-dir>/` (or `rg -l --glob '!README.md'`)
is usually enough. Exclude this file deliberately: it is the contract, not a claim, and
its worked example is keyword-dense enough to match almost any probe while the almanac
is young.

Read the entry, and if it carries a `verify` line and you're about to act on something
expensive, run it.

Entries are assertions of fact, not suggestions. If one contradicts what you're seeing,
the entry is a suspect, not an authority — see below.

## Method vs. local convention

This file is the **local** contract: the almanac's subject, the entry format, the
destinations table above, the wrap width, when a correction ships, how parallel sessions
avoid contention. Those are this repository's calls.

The **method** — the admission tests, how to decide whether a fact belongs, how to write
a `verify` line that fails when its claim fails, how to re-check entries that may have
gone stale — is carried by skills, so that it can be maintained in one place and travel
to other repositories. This file is not.

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

**Writing.** Record an entry when you've just finished being surprised: a debugging
session that ended in "oh, _that's_ why," a green build that hid a real failure, a tool
that behaved differently than its docs claim. Write it in the same PR as the work that
uncovered it, while the evidence is still in front of you.

Don't hedge. If you aren't confident it's true, don't write it — uncertainty belongs in
the PR discussion, not in a file that future agents will treat as settled.

**Finishing.** Noticing a fact and recording it are two different acts, and the second
one is the one that gets skipped: the session ends, the surprise is still in the
transcript, and nothing durable was written. So before opening a PR, ask explicitly —
_did this branch teach us anything an entry should carry?_ Answer it, out loud, even
when the answer is no. Most branches produce no entry. The ones that do are the reason
this directory exists.

**Correcting.** If you discover an entry is wrong, fix or delete it in your current PR.
Deleting a falsified entry is worth as much as adding a true one; a confidently-worded
stale fact is worse than no fact at all, because it gets acted on without re-derivation.
When a fix supersedes an entry rather than refuting it, update `recorded` and note what
changed.

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
- **One fact per file.** Two sessions recording two facts touch two files.
- **Duplicates are cheap, conflicts are not.** If you suspect an entry already exists
  but can't find it, write yours anyway. A reviewer merging two entries is a minor
  cleanup; a hand-resolved conflict in a shared index silently duplicates or drops
  content.
