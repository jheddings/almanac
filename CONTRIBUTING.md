# Contributing

The almanac is built around one distinction: repository instructions say **when** to consult it;
skills explain **how** to record and audit it.

## Skill structure

Each skill lives in `skills/<skill-name>/SKILL.md` and follows the Agent Skills specification.
Supporting files belong in `references/`, `scripts/`, or `assets/` only when the skill uses them.

Descriptions should state when the skill applies. Keep repository-local destinations out of shared
skills: the skill decides whether a fact is design intent, a required rule, in-flight status, or a
personal preference; the target repository's `docs/almanac/README.md` decides where those things go.

## Almanac invariants

- One factual claim per file.
- Filenames state claims and form the index; do not add a registry or generated contents file.
- Entries are durable, empirically discovered, and costly to rediscover.
- Do not write entries automatically or seed illustrative entries.
- Do not add speculative confidence or status fields.
- Verification must test the claim's load-bearing detail and state the expected observation.
- New entries, corrections, deletions, and `verified` freshness updates receive human review.

## Validation

Run:

```bash
just check
```

This checks formatting, validates every skill against the Agent Skills specification, and checks
the plugin manifests for internal consistency.

## Commits and branches

Use Conventional Commits and the matching branch prefixes documented in `AGENTS.md`.
