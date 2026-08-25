---
title: A removed worktree's name is unrecoverable, while a merged branch's name survives
kind: fact
recorded: 2026-08-24
source:
    "Building the skel scorer — its session-scoped worktree check silently passed on a
    run where both the worktree and the branch had been cleaned up"
verify:
    "`uv run pytest tests/test_skel.py -k 'survive_their_own_deletion or
    cannot_conclude' -q` exits 0; both build a real repository, remove the worktree, and
    assert the name is gone while a merged branch's name persists"
verified: 2026-08-24
tags: [git, worktrees, reflog, silent-failure]
---

`git worktree remove` erases the worktree's administrative directory, and the name is
then gone from the repository entirely — no `.git/worktrees` entry, no reflog mention,
nothing left to grep. Branch names behave differently: one that was merged or checked
out in the main worktree survives in the reflog after `git branch -D`, but one created
inside a worktree with `git worktree add -b` and deleted unmerged leaves nothing either.

**Why it matters:** anything that inspects worktree usage after the fact reads absence
as evidence. A check comparing a worktree's name against its branch finds neither and
concludes everything was fine — the opposite of the answer it owes. Nothing errors,
because nothing is missing as far as git is concerned.

**What to do:** capture the name when the worktree is created rather than looking for it
later; a `post-checkout` hook writing under `.git/` outlives the worktree it describes.
Where no branch survives to compare against, report the result as unknown rather than as
a pass.

Related:
[`git-hooks-are-shared-by-every-worktree`](git-hooks-are-shared-by-every-worktree.md) —
such a hook fires in every worktree, so its log must tolerate repeated lines.
