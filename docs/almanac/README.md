# Almanac

Discovered facts about this codebase, recorded by agents for agents.

An almanac entry is something we **learned the hard way** and don't want to learn again:
a silent failure mode, a tool that lies, a constraint that isn't visible from the code.
It is not documentation, and it is not a plan. Entries are terse, atomic, and durable.

Humans are welcome here, but the audience is the next agent — likely one with no memory
of this session, possibly running under a different tool.

## What belongs here

An entry must pass all three tests:

1. **Durable** — will it still be true in six months? Facts about how the system
   _behaves_ qualify. Facts about what we're _currently doing_ do not.
2. **Discovered** — was it learned empirically? Design intent is written down elsewhere;
   the almanac records what turned out to be true when someone ran it.
3. **Costly to rediscover** — is it non-obvious, expensive, or silent? If a competent
   agent would work it out in two minutes, leave it out. Failures that look like success
   are the highest-value entries we can write.

If you can't state the fact in one sentence, it's probably a design doc, not an entry.

## What doesn't belong here

| If it is...                      | It goes...                  |
| -------------------------------- | --------------------------- |
| A rule you're required to follow | `AGENTS.md`                 |
| Your own working preferences     | Your agent's private memory |

This repo has no architecture-doc directory, plans directory, or issue tracker yet. When
one appears, add its row here — design intent, specs, and in-flight status all belong in
those places rather than in the almanac.

The design-doc boundary is the one that blurs, so apply it as **design vs. discovery**: an
architecture note explains how a mechanism was _meant_ to work. An almanac entry records
what was observed when it ran — that a particular mock silently fails to intercept, say.
Same subject, different epistemics.

## Entry format

One fact per file. Filename is a kebab-case slug stating the claim, not the topic —
`migrations-out-of-order-are-silently-skipped.md`, not `migrations.md`. This matters more
than it looks: the filenames are the index (see below), so a slug that states a claim is
readable knowledge on its own.

```markdown
---
title: Out-of-order migrations are silently skipped on deploy
recorded: 2026-08-15
source: PR #1129
verify: "`rg -- '--include-all' .github/workflows/deploy.yml` returns no matches"
verified: 2026-08-16
tags: [migrations, deploy, ci, silent-failure]
---

One or two sentences stating the fact plainly.

**Why it matters:** the consequence — what breaks, and whether it breaks loudly.

**What to do:** the corrective action, if there is one.
```

`title`, `recorded`, and `source` are required. `source` is a PR, a commit, or — when the
fact was observed directly rather than uncovered by a change — a short description of the
circumstances.

`verify` is strongly encouraged: a cheap, read-only command or check plus the observation
that confirms the claim. It must test the load-bearing detail rather than merely locating
the subject. This is the only real defense against an entry that quietly went stale,
because it lets a future agent re-check instead of trusting blindly.

`verified` is optional and means exactly one thing: **someone ran the `verify` line on that
date and the claim held.** Never set it on the strength of having read the entry, edited
nearby code, or assumed it's still fine — a freshness signal that decouples from an actual
re-check is worse than no signal, because it launders a stale fact as a current one. If you
ran the check and it held, bump it. Otherwise leave it alone.

`tags` aid discovery; use them freely, since search is how entries get found.

## Method vs. local convention

This file is the local contract: entry format, repository-specific destinations, wrapping,
and review conventions. The shared recording and auditing method is carried by the
`almanac-record` and `almanac-audit` skills. Where they disagree about method, the skill
wins; where they disagree about a convention this file identifies as local, this file
wins. Agents that cannot load the skills should apply this README as the complete contract.

## Using the almanac

**Read the directory listing.** `ls docs/almanac/` is the table of contents: every
filename is a claim, so scanning them tells you what this codebase already knows. There
is no index file to consult and none to maintain. Do this when you start work in an
unfamiliar area, not only once you're stuck — the entries worth most are silent failures
you would never think to search for.

Grep it before assuming something is undocumented — filenames state claims, so
`grep -rl <keyword> docs/almanac/` (or `rg -l`) is usually enough.

Read the entry, and if it carries a `verify` line and you're about to act on something
expensive, run it.

Entries are assertions of fact, not suggestions. If one contradicts what you're seeing,
the entry is a suspect, not an authority — see below.

## Maintaining the almanac

**Writing.** Record an entry when you've just finished being surprised: a debugging
session that ended in "oh, _that's_ why," a green build that hid a real failure, a tool
that behaved differently than its docs claim. Write it in the same PR as the work that
uncovered it, while the evidence is still in front of you.

Don't hedge. If you aren't confident it's true, don't write it — uncertainty belongs in
the PR discussion, not in a file that future agents will treat as settled.

**Finishing.** Noticing a fact and recording it are two different acts, and the second one
is the one that gets skipped: the session ends, the surprise is still in the transcript,
and nothing durable was written. So before opening a PR, ask explicitly — _did this branch
teach us anything an entry should carry?_ Answer it, out loud, even when the answer is no.
Most branches produce no entry. The ones that do are the reason this directory exists.

**Correcting.** If you discover an entry is wrong, fix or delete it in your current PR.
Deleting a falsified entry is worth as much as adding a true one; a confidently-worded
stale fact is worse than no fact at all, because it gets acted on without re-derivation.
When a fix supersedes an entry rather than refuting it, update `recorded` and note what
changed.

**Reviewing.** Entries ride in the PR diff and get reviewed like code. This is
deliberate: an agent cannot validate its own entry, because whatever led it to write
something wrong would equally lead it to approve it. Nothing writes here unreviewed.
