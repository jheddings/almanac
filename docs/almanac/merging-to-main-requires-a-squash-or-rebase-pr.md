---
title: Merging to main requires a PR, squashed or rebased, with CI passing
kind: rule
recorded: 2026-08-24
source: "AGENTS.md, migrated 2026-08-24"
tags: [git, github, pull-requests, conventions]
---

**Applies when:** you are ready to land a branch.

PRs are required to merge to `main`. Squash or rebase only — merge commits are disabled
— and CI must pass. Put issue references in the PR **body**, not the title.

**Why:** the linear history is what makes the type prefixes in
[`commit-messages-use-conventional-commit-format`](commit-messages-use-conventional-commit-format.md)
worth having. Issue references go in the body because the title becomes the squash
commit subject in the multi-commit case, and a trailing `(#12)` there reads as a commit
reference rather than an issue one.

Before trusting a green PR, check that workflows actually ran:
[`a-pr-onto-a-non-main-base-runs-no-workflows`](a-pr-onto-a-non-main-base-runs-no-workflows.md)
and
[`a-conflicted-pr-runs-no-workflows-and-looks-green`](a-conflicted-pr-runs-no-workflows-and-looks-green.md)
both produce an all-passing table with no evidence behind it.
