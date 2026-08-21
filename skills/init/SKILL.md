---
name: init
description: >-
    Use when asked to initialize, install, set up, or add an almanac to a repository, or
    to repair an incomplete almanac setup. Do not use merely to record or audit an
    individual entry.
---

# Initialize an Almanac

Install the repository-level pieces that let every agent consult the almanac, including
agents that cannot load this skill. Initialization writes shared instructions, so
inspect and propose first; an invocation is not permission to overwrite existing
content.

## Inspect the repository

Find the repository root and read the applicable agent instructions. Resolve any
existing almanac in order — stop at the first step that resolves:

1. **`docs/almanac/README.md`.** The conventional location. If it exists, that is the
   almanac; do not look further.
2. **Glob `**/almanac/README.md`**, then discard matches under `templates/`,
   `.worktrees/`, `node_modules/`, `vendor/`, or any other checkout nested inside this
   one. A bare directory-name match is not evidence of an almanac — **a template, an
   example, or a sibling worktree's copy is not this repo's almanac**.
3. **Exactly one survivor → that is the almanac.** More than one, ask which. None means
   the repository is not initialized; continue with the proposal below.

If a live almanac exists somewhere other than `docs/almanac/`, stop and ask whether the
operator wants to keep or migrate it. Never create a competing almanac.

Also check for:

- an almanac consult trigger in `AGENTS.md` or another always-read instruction file;
- tool-specific instruction files that already point to `AGENTS.md`.

Read the canonical contract at `${CLAUDE_PLUGIN_ROOT}/templates/almanac/README.md` and
extract its integer from `<!-- almanac-template: N -->`. The revision comment and the
`<!-- almanac:local -->` block are load-bearing; preserve both.

## Build the proposal

Show the operator the exact files that would change and what each change contains.

### Local contract

If `docs/almanac/README.md` is absent, propose creating it from the canonical template.
Replace only the contents of the `almanac:local` block with this repository's real
destinations for:

- designed intent;
- required rules;
- specifications or plans;
- in-flight status;
- personal preferences.

Infer a destination only from files, directories, or services that actually exist. Omit
a category whose destination cannot be established; never invent `docs/arch/`,
`CONTRIBUTING.md`, or an issue tracker. Explain any omitted category so the operator can
supply an answer before approving the file.

If the README already exists, preserve it. Compare its template revision with the
canonical revision and report one of these outcomes:

- equal — the shared contract is current;
- local lower — a newer contract exists and needs a separately reviewed upgrade;
- local higher — the installed plugin is older than the repository's contract;
- missing or malformed — the local contract is unversioned.

Propose only clearly missing installation essentials. Do not replace its local block or
silently merge a newer template into it; repository-local conventions and template
upgrades require review.

### Consult trigger

If `AGENTS.md` exists, match its structure and propose the smallest addition that says:

- `docs/almanac/` records durable facts discovered the hard way;
- list it when starting unfamiliar work, grep it when behavior is unexpected, and
  consult it before silent or costly operations;
- follow `docs/almanac/README.md` when recording a genuine surprise;
- before finishing a branch, state whether the work taught an almanac-worthy fact.

Do not paste a second almanac section when those concepts already exist. If `AGENTS.md`
is absent, propose creating it with a concise section containing those concepts. If a
tool-specific instruction file already points to `AGENTS.md`, leave it alone. Otherwise
identify the portability gap and ask before editing any additional instruction file.

Do not create example entries. An empty almanac is the correct initial state.

## Confirm, apply, and verify

Get explicit approval for the proposed files and local destinations before writing.
Apply only what was approved, then:

1. list the almanac and confirm it contains `README.md` without seeded entries;
2. show the consult trigger now present in the shared instructions;
3. confirm the template revision marker remains intact;
4. run the repository's formatting or documentation checks when available;
5. report every created or modified file.

Finally, re-run the inspection steps against the resulting tree. A second invocation
should propose no changes. If it would duplicate instructions or replace local text, the
initialization was not idempotent; correct it before reporting success.
