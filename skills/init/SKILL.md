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

Find the repository root and read the applicable agent instructions. **There may not be
one.** A workspace holding several independent checkouts is a legitimate target and is
not itself a repository, so a failing `git rev-parse --show-toplevel` is a fact about
the target, not a reason to stop: take the directory the operator named as the root, and
carry the consequences into the proposal below. Resolve any existing almanac in order —
stop at the first step that resolves:

1. **`docs/almanac/README.md`.** The conventional location. If it exists, that is the
   almanac; do not look further.
2. **Glob `**/almanac/README.md`**, then discard matches under `templates/`,
   `node_modules/`, `vendor/`, or any other checkout nested inside this one. A bare
   directory-name match is not evidence of an almanac — **a template, an example, or a
   sibling worktree's copy is not this repo's almanac**.
3. **Exactly one survivor → that is the almanac.** More than one, ask which. None means
   the repository is not initialized; continue with the proposal below.

**These steps search this tree, and never look up.** A workspace or parent repository
enclosing this checkout may keep its own almanac; that is a separate almanac with a
separate subject, and this tree's is the one that resolves. So a checkout sitting under
a directory that already keeps an almanac is still uninitialized. Look for one anyway:
walk the parents once, checking each for `almanac/README.md`. That is a read, not a
resolution — name what you find and what its subject is in the proposal, so the operator
can decide whether this tree needs its own.

If a live almanac exists somewhere other than `docs/almanac/`, stop and ask whether the
operator wants to keep or migrate it. Never create a competing almanac.

Also check for:

- an almanac consult trigger in `AGENTS.md` or another always-read instruction file;
- tool-specific instruction files that already point to `AGENTS.md`;
- repository-local skills that duplicate this plugin's — a copy installed before the
  plugin is now superseded. Match on what a skill says, not what it is named: read the
  descriptions under the repository's skills directories and flag any that trigger on
  recording or auditing the almanac.

Report a superseded copy and leave it in place; removing it is a reviewed change, like
the README. Name it explicitly, because unlike the README it is invisible in normal use:
two skills triggering on the same moment is a coin flip, nothing breaks when the stale
one wins, and the operator keeps running the old method believing they upgraded.

Read the canonical contract template. Resolve it in order:

1. `${CLAUDE_PLUGIN_ROOT}/templates/almanac/README.md` if set;
2. `templates/almanac/README.md` relative to the workspace or repository root;
3. `templates/almanac/README.md` relative to the plugin's installed directory, however
   your harness exposes it (for example, inside your harness's plugins directory).

Extract its integer from `<!-- almanac-template: N -->`. The revision comment and the
`<!-- almanac:local -->` block are load-bearing; preserve both.

## Build the proposal

Show the operator the exact files that would change and what each change contains.

### Local contract

If `docs/almanac/README.md` is absent, propose creating it from the canonical template.
Replace only the contents of the `almanac:local` block with this repository's real
destinations for:

- designed intent;
- specifications or plans;
- in-flight status;
- personal preferences.

**Required rules are not on that list.** The contract admits them as `kind: rule`
entries, so there is no destination to establish. If the repository already keeps its
conventions in `CONTRIBUTING.md` or an instruction file, say so in the proposal and name
migrating them as separate follow-up work — never move someone's rules as a side effect
of setup.

Infer a destination only from files, directories, or services that actually exist, and
never invent one — no `docs/arch/`, no `CONTRIBUTING.md`, no issue tracker this
repository does not already use. Reuse is not invention: a destination established for
one row is available to another.

Ask the operator for any destination you cannot ground, and omit the row only if they
have no answer. Say what the omission costs when you propose it: `record` reads a
missing row as a hard stop, so an unanswered category becomes one a later agent can
neither record nor file anywhere.

Two further things go in that block. **The subject**, whenever the target is not a
single repository — say what it is, because the contract's scope test reads against it
and otherwise defaults to this repository. And **the wrap width** entries will use: the
contract claims that convention as local and supplies no value, so leaving it unset
hands every writer a different guess. Infer it from a formatter already configured here
— `.prettierrc*`, `.editorconfig` — and name the source; ask if nothing establishes it.

Where the target has no version control, the contract's review model has nothing to
attach to: "entries ride in the PR diff" is the safeguard, and there is no diff. Say so
in the proposal. The safeguard does not become optional — it becomes the writer's to
discharge in their report, while the operator can still check it.

A **section** of a file is a valid destination, and usually a better one than a bare
filename — `CLAUDE.md § Architecture` sends an agent somewhere specific. Two categories
resolving to the same destination is fine; that is a fact about the repository, not a
collision to resolve.

If the README already exists, preserve it. Compare its template revision with the
canonical revision and report one of these outcomes:

- equal — the shared contract is current;
- local lower — the plugin ships a newer contract. Name both revisions and stop.
  Upgrading means splicing this repository's `almanac:local` block into the newer
  template, which is a separate reviewed change and not one to make here;
- local higher — the installed plugin is older than the repository's contract;
- missing or malformed — the local contract is unversioned, which is the usual state of
  an almanac that predates this plugin. Adopting the template means copying the
  canonical text, moving the repository's existing destinations into the `almanac:local`
  block, and reviewing the rest of the diff. Same separate reviewed change; say so
  rather than leaving the verdict as a label.

Propose only clearly missing installation essentials. Do not replace its local block or
silently merge a newer template into it; repository-local conventions and template
upgrades require review.

### Consult trigger

First establish **which instruction file the agent that will use this almanac loads
automatically**, and say so in the proposal. This is the highest-consequence decision in
the whole initialization: a trigger in a file nothing reads is dormant, which leaves the
almanac inert and everything else here decorative.

If `AGENTS.md` exists, match its structure and propose the smallest addition that says:

- `docs/almanac/` holds this repository's operating knowledge — durable facts and the
  rules it requires — one claim per file, indexed by filename;
- that listing is the index and there is no other: a required convention is an entry
  rather than a section of the instruction file, and nothing restates one there once it
  is an entry;
- list it at the start of a session, carry the titles, and load a body when one bears on
  what you are about to do;
- grep it when behavior is unexpected, and consult it before silent or costly
  operations;
- follow `docs/almanac/README.md` when recording;
- before finishing a branch, state whether the work taught an almanac-worthy claim.

Do not paste a second almanac section when those concepts already exist. If `AGENTS.md`
is absent, propose creating it with a concise section containing those concepts. If a
tool-specific instruction file already points to `AGENTS.md`, leave it alone. Otherwise
identify the portability gap and ask before editing any additional instruction file.

You know which files your own runtime loads. For the tools you are not, look rather than
guess — `CLAUDE.md`, `.claude/CLAUDE.md`, `GEMINI.md`, `.cursor/rules/`, and
`.github/copilot-instructions.md` are current examples. Conventions change and the list
goes stale, so treat it as where to start, not as the whole search.

Do not create example entries. An empty almanac is the correct initial state.

## Confirm, apply, and verify

Check the repository's own contribution rules before writing — many forbid committing to
the default branch. Initialization changes shared instructions, so it ships the way any
other change to them does: a branch and a PR, unless the operator says otherwise.

Get explicit approval for the proposed files and local destinations before writing.
Apply only what was approved, then:

1. list the almanac and confirm it contains `README.md` without seeded entries;
2. name the instruction file the running agent auto-loads, and show the consult trigger
   either in that file or reachable by a pointer from it — a string that is present but
   never loaded is not a trigger;
3. confirm the template revision marker and both `almanac:local` delimiters remain
   intact;
4. run the repository's formatting or documentation checks when available. If they
   rewrite files rather than just failing — prettier, markdownlint, a
   trailing-whitespace hook — re-check step 3 afterwards;
5. report every created or modified file.

Finally, re-run the inspection steps against the resulting tree. A second invocation
should propose no changes. If it would duplicate instructions or replace local text, the
initialization was not idempotent; correct it before reporting success.
