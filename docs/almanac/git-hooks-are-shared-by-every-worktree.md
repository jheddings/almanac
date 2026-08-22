---
title: Installing or removing git hooks from one worktree changes every worktree
recorded: 2026-08-22
source:
    "Verifying `just setup` while working in a session worktree — `pre-commit install`
    reported it had installed into the main checkout's `.git`, not the worktree's"
verify:
    "`git rev-parse --git-dir` inside a linked worktree prints
    `<main>/.git/worktrees/<name>` while `git rev-parse --git-common-dir` prints
    `<main>/.git`; running `pre-commit install` there prints that it installed at the
    **common** dir, and `pre-commit uninstall` from a second worktree leaves the main
    checkout with no `.git/hooks/pre-commit` and commits that run no hooks"
verified: 2026-08-22
tags: [git, worktrees, pre-commit, hooks, silent-failure, tooling]
---

A linked worktree has its own `$GIT_DIR` but shares `$GIT_COMMON_DIR` with the main
checkout. Hooks live in `$GIT_COMMON_DIR/hooks`, so there is exactly one hooks directory
for the repository and every worktree runs it. Tools that install hooks resolve the
common dir: `pre-commit install` from a worktree writes to the main checkout's
`.git/hooks/`, and `pre-commit uninstall` from any worktree removes it for all of them.

**Why it matters:** this repository gives each agent session its own worktree, and the
tooling has recipes on both ends — `just setup` installs hooks, `just clobber` removes
them. A session that tidies up after itself with `clobber` in a throwaway worktree
disarms pre-commit for the maintainer's main checkout, which never ran either command.

The removal is the quiet direction. `pre-commit uninstall` prints
`pre-commit uninstalled` and names no path; afterwards, commits in every checkout
succeed while running no hooks at all. A commit that skipped every hook looks exactly
like a commit that passed them, and the next signal is CI failing on something the hooks
existed to catch.

**What to do:** treat hook installation as repository-wide, not worktree-local. Before a
recipe installs or removes hooks, confirm it is running in the primary worktree:

```bash
test "$(git rev-parse --git-dir)" = "$(git rev-parse --git-common-dir)"
```

The two paths are equal only in the primary worktree. There is no per-worktree hooks
directory to fall back to — `core.hooksPath` sets one path for the whole repository, so
pointing it at a worktree makes every other worktree use that worktree's hooks.
