---
title: A removed worktree's name is unrecoverable from git
kind: fact
recorded: 2026-08-24
source:
    "Building the skel rig — a worktree name needed after the fact turned out to be
    gone, with nothing reporting its absence"
verify:
    "`uv run pytest tests/test_skel.py -k survives_only_in_the_hook_log -q` exits 0; it
    builds a real repository, removes a worktree, and asserts git kept no record"
verified: 2026-08-25
tags: [git, worktrees, silent-failure]
---

`git worktree remove` erases the worktree's administrative directory, and the name is
then gone from the repository entirely — no `.git/worktrees` entry, no reflog mention,
nothing left to grep. Nothing warns you, because as far as git is concerned nothing is
missing.

**Why it matters:** anything that needs the name after the fact reads absence as
evidence and concludes nothing happened, which is the opposite of the truth. The rule
that tells an agent to clean up is the same rule that destroys the record of whether it
was followed.

**What to do:** capture the name when the worktree is created rather than looking for it
later. A `post-checkout` hook writing under `.git/` outlives the worktree it describes,
which is what `tools/skel.py` installs.

Related:
[`git-hooks-are-shared-by-every-worktree`](git-hooks-are-shared-by-every-worktree.md) —
such a hook fires in every worktree, so its log must tolerate repeated lines.
