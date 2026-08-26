# Widening the almanac to carry rules

**Status:** merged as #28. See [Outcome](#outcome).

## The proposal

Treat the almanac as a filename-indexed store of everything an agent needs to work here,
not only the facts it learned the hard way. The retrieval flow is unchanged from what
the contract already described — read the listing cold, carry the titles, load a body
when one applies — but admission is widened so a required convention can be an entry.

The reasoning: an always-on instruction file pays for every rule on every turn, whether
or not it is relevant. A filename index pays one line per claim and loads the body only
when the title fires. If that works, `AGENTS.md` shrinks to a trigger and the listing
becomes the whole index of how to work here.

## What changed

- Admission tests are now **durable / actionable / costly to miss**. "Discovered" is
  gone; provenance no longer decides anything.
- A new gate replaces it: **would the title fire at the right moment?** In a lazily
  loaded store, retrievability is the admission criterion that matters.
- Entries declare `kind: fact` or `kind: rule`, and the schema enforces the split — a
  rule may not carry `verify` or `verified`.
- `record`'s category gate no longer routes rules elsewhere; `audit` gained an
  `unauditable` verdict and must name every rule it could not reach.
- Commits, branches, pull requests, and worktrees moved out of `AGENTS.md` into entries.
  Markdown conventions and comment style deliberately stayed, so the migration is
  partial and the two halves can be compared.

## What to watch

The three costs, in the order they are likely to bite:

1. **Rules cannot be audited.** This is structural, not an implementation gap. The
   schema and `audit` make the gap visible; nothing makes it smaller.
2. **Do lazily loaded rules actually get loaded?** A fact is consulted because reality
   resists you. A rule has no such moment — an agent about to commit has a prior, and
   priors do not generate lookups. The startup listing is the whole bet.
3. **Does a longer listing still read cold?** Five entries, all surprising, is a listing
   worth scanning. Ten, half of them conventions, may not be.

A fourth, already observed: every skill grew. The fact/rule decision, the title test,
and the `unauditable` verdict are method that did not exist before, and
`tests/baselines.json` records the raised ceilings and by how much.

## Outcome

Merged as #28 on 2026-08-24, and the partial migration completed on 2026-08-25: Markdown
wrapping, prose written outside the repo, and comment style are entries too, so
`AGENTS.md` now carries the trigger and the mechanical checks and nothing an entry could
hold. The two-halves comparison this doc set up was not run to a conclusion — the
argument that ended it was that the strongest case for migrating, prose written outside
the repository, was sitting in the half left behind: it fires at a nameable moment, and
getting it wrong is invisible until the text is already posted.

Cost 1 below is unchanged and permanent. Costs 2 and 3 are now live on the whole set
rather than half of it, and nothing here measures them.

## Reverting

Contained when this was written; no longer. Reverting now means reverting #28, #30, and
#31, restoring the ceilings named in `tests/baselines.json`, and moving seven entries
back into `AGENTS.md`. The entries migrated out of `AGENTS.md` are verbatim moves; their
content is recoverable from this branch's diff whichever way the experiment goes.
