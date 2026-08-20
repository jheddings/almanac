---
name: almanac-init
description: >-
  Use when asked to initialize, install, set up, or add an almanac to a repository so agents can
  share durable facts discovered the hard way. Also use when checking or repairing an existing
  almanac installation. Do not use merely to add or audit an individual entry.
---

# Almanac Init

Initialize the repository-level pieces that make the almanac available to every agent, including
agents that cannot load this skill.

The first release uses one conventional location: `docs/almanac/`. If the repository already uses
a different almanac path, stop and ask whether to migrate it; do not create a competing directory.

## Inspect

Find the repository root and read its applicable agent instruction files. Check for:

- `docs/almanac/README.md`
- an almanac consult trigger in `AGENTS.md`
- tool-specific instruction files such as `CLAUDE.md` that already point to `AGENTS.md`

Read the bundled assets before proposing changes:

- `${CLAUDE_PLUGIN_ROOT}/skills/almanac-init/assets/almanac-readme.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/almanac-init/assets/agents-snippet.md`

The README asset is a baseline, not an overwrite source. An existing local README owns local
destinations, formatting, and review conventions.

## Propose before writing

Show the operator a concise plan and the exact files that would change. Follow these rules:

1. If the README is absent, propose creating it from the asset. Adapt only repository-local
   destinations that can be established from existing files; omit destinations that do not exist.
2. If the README exists, preserve it. Propose only clearly missing installation essentials; never
   replace it wholesale or erase local conventions.
3. If `AGENTS.md` is absent, propose creating it with the bundled snippet. If present, insert only
   the missing concepts and match its structure rather than pasting a duplicate section.
4. If a tool-specific file already points to `AGENTS.md`, leave it alone. Otherwise mention the
   portability gap, but do not edit additional instruction files without operator approval.
5. Do not create example entries. An empty almanac is valid.

Get explicit confirmation before writing. Initialization writes repository instructions, so an
invocation is permission to inspect and propose, not permission to overwrite.

## Apply and verify

After confirmation, make only the approved changes. Then:

- list `docs/almanac/` and confirm it contains `README.md` without seeded entries;
- show the exact consult language now present in `AGENTS.md`;
- run the repository's formatting or documentation checks when available;
- report every created or modified file.

Running initialization again should propose no changes. If it would duplicate a section or replace
local text, the installation is not idempotent; fix the proposal before applying it.
