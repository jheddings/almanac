---
name: almanac-record
description: >-
  Use after resolving a surprising repository behavior, silent failure, misleading green check, or
  undocumented constraint that future agents should not rediscover. Also use when explicitly asked
  to add, correct, or delete an almanac entry. Do not use for design intent, required rules, plans,
  current status, or personal preferences.
---

# Almanac Record

Record a fact only when a future agent can safely act on it without re-deriving it. Truth matters
more than apparent usefulness; a plausible but wrong entry costs more than no entry.

The method in this skill governs admission and verification. The target repository's
`docs/almanac/README.md` governs local destinations, entry format, wrapping, and review conventions.

## Decide whether it belongs

Make the category decision yourself. Do not write an entry with a caveat that a reviewer may prefer
somewhere else. Ask:

- Is this designed intent rather than observed behavior?
- Is it a rule people are required to follow?
- Is it a plan, specification, or current work status?
- Is it a personal preference or routine?

If yes, consult the local README and repository structure for the correct destination.
Shared skills must not invent paths such as `docs/arch/` or `CONTRIBUTING.md`; those
destinations are repository-local. If the proper destination is unclear, do not put the
item in the almanac.

The remaining fact must pass all three tests:

1. **Durable** — likely still true in six months.
2. **Discovered** — established empirically rather than read from design documentation.
3. **Costly to rediscover** — non-obvious, expensive, or silent when violated.

If a competent agent could establish it in a couple of minutes, leave it out. If the claim cannot be
stated in one sentence, it is probably documentation rather than an atomic entry.

## Establish the fact

List `docs/almanac/`, then search filenames, tags, and text for the subject. Correct or extend an
existing entry rather than duplicating it. A falsified entry should be fixed or deleted in the same
change.

Re-run the evidence against the current tree. Do not transcribe the user's statement, session notes,
or memory without checking it. If verification contradicts the proposed claim, record nothing—or
record the corrected fact actually established.

## Make verification discriminating

The `verify` value should be a cheap, read-only check plus the observation that confirms the claim.
It must test the load-bearing detail, not merely locate the surrounding file.

For the claim “deploy omits `--include-all`”:

- Weak: `rg 'db push' .github/workflows/` — this still succeeds after the flag is added.
- Strong: `` `rg -- '--include-all' .github/workflows/deploy.yml` returns no matches ``.

Never use a verification that mutates data, installs, deploys, or reaches production. When no safe,
conclusive check exists, reconsider whether the claim is established strongly enough to record.

## Write and report

Read `docs/almanac/README.md` rather than reconstructing its frontmatter from memory. Use
one file per fact and a kebab-case filename that states the claim. Write the fact plainly,
explain the consequence and whether failure is silent, and give a corrective action when
one exists. Do not hedge.

Do not set `verified` unless the verification was actually run during this work and held.
Report what was recorded, changed, or deleted and the evidence used. The entry must travel
through the repository's normal review path; an agent cannot approve its own conclusion.
