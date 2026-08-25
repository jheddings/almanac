---
title: Development happens in a session-scoped git worktree, not the main checkout
kind: rule
recorded: 2026-08-24
source: "AGENTS.md, migrated 2026-08-24"
tags: [git, worktrees, workflow, conventions]
---

**Applies when:** you are starting work that will change files — before the first edit,
not after.

Use a dedicated git worktree so the main working directory stays clean. Worktrees live
in `.worktrees/` and are scoped to an **agent session**, not to the feature or the
changes: each session gets a fresh worktree with a unique name. Announce your worktree
name when you create or switch to one; feel free to be creative or silly with it.

```bash
# Create a worktree based on origin/main
git worktree add .worktrees/<name> -b <branch-name> origin/main

# Clean up after merging
git worktree remove .worktrees/<name>
```

**Why:** concurrent sessions otherwise contend for one checkout, and a half-finished
edit in the main tree is invisible to the session that inherits it. Session scope rather
than feature scope is what keeps two agents from landing in the same directory.

Note that a worktree is not fully isolated:
[`git-hooks-are-shared-by-every-worktree`](git-hooks-are-shared-by-every-worktree.md).
