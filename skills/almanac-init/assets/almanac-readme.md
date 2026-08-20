<!-- almanac-template: 0.1.0 -->

# Almanac

Discovered facts about this codebase, recorded by agents for agents.

An entry records something learned the hard way: a silent failure mode, a tool that behaves
differently than documented, or a constraint not visible from the code. It is not general
documentation or a plan. Entries are terse, atomic, and durable.

## Admission test

An entry must be:

1. **Durable** — likely to remain true for at least six months.
2. **Discovered** — established empirically, rather than copied from design intent.
3. **Costly to rediscover** — non-obvious, expensive to establish, or silent when violated.

If a fact is instead a required rule, design intent, in-flight status, or a personal preference,
put it in the repository's appropriate location rather than here.

## Entry format

Use one fact per file. The kebab-case filename states the claim rather than naming only its topic.

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

**Why it matters:** what breaks, and whether it breaks loudly.

**What to do:** the corrective action, if there is one.
```

`title`, `recorded`, and `source` are required. `verify` is strongly encouraged and must state both
a read-only check and the observation that would confirm the claim. `verified` is optional and may
be changed only when someone ran the verification on that date and it held. `tags` aid discovery.

## Using the almanac

The directory listing is the index; do not create another one. Read claim-shaped filenames,
grep by keyword, then open only relevant entries. Before an expensive action, re-run the
entry's verification.

An entry is an assertion, not an authority. If current evidence contradicts it, correct or delete it
through the repository's normal review process.

## Maintaining the almanac

Write an entry in the same change that uncovered the fact while the evidence is available. Do not
hedge: if the claim cannot be verified, do not record it. Entries, corrections, deletions, and
freshness updates are reviewed like code because an agent cannot validate its own conclusion.

Do not maintain an index, automatically write entries, or add confidence and status fields. Before
finishing a branch, explicitly say whether the work taught an almanac-worthy fact.
