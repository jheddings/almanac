---
title:
    GitHub composes this repo's squash commit from the commit messages, not the PR body
kind: fact
recorded: 2026-08-24
source: "AGENTS.md, migrated 2026-08-24; confirmed against the repository settings"
verify:
    "`gh api repos/jheddings/almanac -q .squash_merge_commit_message` prints
    `COMMIT_MESSAGES`, and `-q .squash_merge_commit_title` prints `COMMIT_OR_PR_TITLE`"
verified: 2026-08-24
tags: [git, github, pull-requests, commits, squash]
---

The repository sets `squash_merge_commit_message: COMMIT_MESSAGES` and
`squash_merge_commit_title: COMMIT_OR_PR_TITLE`. A squash merge therefore takes its
**body** from the branch's commit messages rather than the PR description, and its
**title** from the sole commit when the PR has exactly one and from the PR title
otherwise.

**Why it matters:** the PR body is the thing everyone writes carefully, and it is
discarded at merge. Whatever was typed into the commit messages is what lands on `main`
permanently. Nothing warns you, and the PR page looks correct right up to the moment it
squashes.

**What to do:** write commit messages as the record that survives, wrapped for a
terminal that does not reflow. Put issue references in the PR body only when you do not
mind losing them.

Related:
[`commit-messages-use-conventional-commit-format`](commit-messages-use-conventional-commit-format.md)
is the rule this fact is the reason for.
