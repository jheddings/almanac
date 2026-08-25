---
title: A PR with merge conflicts runs no workflows, and its checks read as passing
kind: fact
recorded: 2026-08-20
source:
    "PR #9 sat at zero runs for two pushes; `mergeable` was CONFLICTING, and the run
    appeared as soon as the rebase landed"
verify:
    "`gh api 'repos/<owner>/<repo>/actions/runs?head_sha=<sha>' -q .total_count` returns
    `0` for the head commit of a conflicted PR, while `gh pr checks <n>` still exits 0"
verified: 2026-08-20
tags: [github-actions, ci, pull-requests, silent-failure]
---

A `pull_request` workflow runs against the merge commit GitHub computes for the PR. When
the branch conflicts with its base, there is no such commit, so **no `pull_request`
workflow is queued at all** — not skipped, not failed, simply absent.

**Why it matters:** it fails as success. `gh pr checks <n>` lists only the checks that
did run, so a conflicted PR whose third-party checks are green prints an all-passing
table and exits 0. Nothing says "your CI did not run." The same PR shows
`mergeable: CONFLICTING` and `total_count: 0` from the runs API, but neither appears in
the place anyone looks.

Two things make it worse than a plain gap. Path-filtered workflows are legitimately
absent on many PRs, so "a workflow I expected isn't here" is a signal already trained to
be ignored. And the natural read of an intermittent-looking absence is flakiness — this
cost one session a wrong diagnosis, recorded in a PR comment as "I suspect I checked
before it registered," when the cause was a conflict introduced by main advancing five
commits.

**What to do:** treat `gh pr checks` as meaningful only once the PR is mergeable. Check
`gh pr view <n> --json mergeable` first, or confirm a run exists for the head SHA before
concluding anything from a green table. Absence of runs is absence of evidence, not a
pass.

Related:
[`piping-into-grep-q-under-pipefail-fails-on-sigpipe`](piping-into-grep-q-under-pipefail-fails-on-sigpipe.md)
and
[`a-plugin-archive-missing-its-manifest-loads-with-no-error`](a-plugin-archive-missing-its-manifest-loads-with-no-error.md)
are the same class — a check that examined nothing, reporting success.
