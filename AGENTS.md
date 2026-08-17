# AGENTS.md

Always-applicable instructions for agents working in this repository. This is the
top-level instruction file; `CLAUDE.md` points here so both conventions resolve to the
same rules.

## The almanac

[`docs/almanac/`](docs/almanac/) records facts discovered the hard way — silent failure
modes, tools that behave differently than documented, constraints not visible from the
code. It is authoritative for this repo, and
[docs/almanac/README.md](docs/almanac/README.md) governs the details.

**Consult it when:**

- You start work in an area you don't already know. Run `ls docs/almanac/` once — the
  filenames state the claims, so the listing alone tells you what this codebase has
  already learned. Do this _before_ you have a symptom: the entries worth most are
  silent failures you would never think to search for.
- Something isn't behaving as expected. Grep it _before_ you start investigating, not
  after you're stuck — it's one command and it may end the investigation.
- You're about to do something whose failure would be silent or costly to undo:
  migrations, deploys, CI config, release tooling, anything touching production.

One keyword grep is enough (`grep -rl <keyword> docs/almanac/`, or `rg -l`). If nothing
hits, move on.

**Record an entry when** you finish being surprised — a debugging session that ended in
"oh, _that's_ why," or a green build that hid a real failure. Write it in the same PR as
the work that uncovered it, following
[docs/almanac/README.md](docs/almanac/README.md).

Before you finish a branch, ask explicitly: _did this teach us anything an entry should
carry?_ Answer it out loud, even when the answer is no.

## Commit conventions

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`

Scope is optional but encouraged — `fix(auth): ...`, `feat(events): ...`.

## Branch naming

Use the same type prefixes as commits, followed by a short description of the intended
change:

```
<type>/<change-slug>
```

Examples: `feat/email-notifications`, `fix/sidebar-delete-width`, `chore/update-deps`.
Optionally include the issue number: `feat/279-email-notifications`.

## Worktrees

Use a dedicated git worktree for development to keep the main working directory clean.
Worktrees live in `.worktrees/` and are specific to an **agent session**, not to the
feature or the changes — each session gets a fresh worktree with a unique name. Always
announce your worktree name when creating or switching to one; feel free to be
creative or silly with the name.

```bash
# Create a worktree based on origin/main
git worktree add .worktrees/<name> -b <branch-name> origin/main

# Clean up after merging
git worktree remove .worktrees/<name>
```

This repo has no remote yet, so `origin/main` will not resolve — branch from `main`
until one is added.
