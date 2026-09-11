---
title: "`git -C <dir>` does not override `GIT_DIR` inherited from the environment"
kind: fact
recorded: 2026-08-26
source:
    "Committing the skel harness branch — the pre-commit hook's own test suite staged
    the repository's entire contents as deleted, and the commit failed inside a
    scaffolded temp repo"
verify:
    "`GIT_DIR=$PWD/.git git -C /tmp rev-parse --git-dir` prints this repository's git
    directory, not an error about `/tmp`"
verified: 2026-08-26
tags: [git, hooks, subprocess, worktrees, silent-failure, testing]
---

Git resolves `GIT_DIR`, `GIT_WORK_TREE`, and `GIT_INDEX_FILE` from the environment
before it considers `-C`. A subprocess that runs `git -C <somewhere-else>` therefore
operates on whatever repository the environment names, with `<somewhere-else>` supplying
only the working directory. Git exports all three into every hook it runs — and in a
linked worktree it exports them as absolute paths — so any tool a hook invokes inherits
them.

**Why it matters:** code that creates its own repository under `/tmp` and populates it
with `git -C` looks correctly scoped and is not. Run from a hook, `git -C <run> add -A`
stages the run's files into the _outer_ repository's index and marks every tracked file
there as deleted; the following `git -C <run> commit` then fires the outer repo's
`pre-commit`, which fails with `No .pre-commit-config.yaml file was found` — naming the
run, pointing nowhere near the cause.

The green that hides it is the usual one. `pre-commit run --all-files`, which is what CI
runs, is an ordinary CLI invocation and exports none of these variables, so the suite
passes there and fails only on a developer's actual `git commit`.

`GIT_AUTHOR_NAME` and `GIT_AUTHOR_EMAIL` leak the same way, and they beat
`-c user.name=...` on the command line, so a scaffold that sets its own identity
silently gets the committer's instead.

A test suite that runs under the hook needs the same treatment, and needs it twice: the
assertions that read the result back are themselves `git -C` calls, so an unscrubbed one
reports the enclosing repository's last commit subject and author as if they were the
run's.

**What to do:** scrub the environment rather than trusting `-C`. Pass an explicit `env`
built as an allowlist, so a variable added by a later git cannot reintroduce it —
`tools/skel.py:clean_env` drops every `GIT_*` except the few that say how git runs
rather than where.

Related:
[`git-hooks-are-shared-by-every-worktree`](git-hooks-are-shared-by-every-worktree.md) —
the same hook fires from every worktree, which is how a session worktree's commit ends
up running it.
