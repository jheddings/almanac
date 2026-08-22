---
title: A PR onto a non-main base runs no workflows, and its checks read as passing
recorded: 2026-08-22
source: "PR #17, stacked on PR #16 — zero runs while `gh pr checks` exited 0"
verify:
    "`gh api repos/<owner>/<repo>/actions/runs?head_sha=<sha> -q .total_count` returns
    `0` for the head of a PR based on anything but `main`, while `gh pr checks <n>`
    still exits 0"
verified: 2026-08-22
tags: [github-actions, ci, pull-requests, stacked-prs, silent-failure]
---

Every workflow here filters `pull_request: branches: [main]`. A stacked PR — one whose
base is another feature branch — matches no trigger, so **no workflow is queued at
all**. Not skipped, not failed, simply absent.

**Why it matters:** it fails as success, and it does so on a PR that looks entirely
healthy. `gh pr checks <n>` lists only the checks that did run, so a stacked PR whose
third-party checks are green prints an all-passing table and exits 0. The branch filter
is plainly visible in the workflow YAML; what is not visible is that a green
`gh pr checks` means nothing on that PR.

**What to do:** confirm a run exists for the head SHA before concluding anything from a
green table. Note that checking `mergeable` first — the advice in the sibling entry
below — does **not** catch this one: a stacked PR is `MERGEABLE` and still runs nothing.
Run the checks locally, or open the PR against `main` once its base has landed.

Related:
[`a-conflicted-pr-runs-no-workflows-and-looks-green`](a-conflicted-pr-runs-no-workflows-and-looks-green.md)
is the same failure from a different cause. Absence of runs is absence of evidence, not
a pass.
