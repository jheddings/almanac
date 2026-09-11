---
title: An out-of-policy Codex permission flag is clamped, not refused
kind: fact
recorded: 2026-08-26
source:
    "The 2026-08-26 Codex trial: three prompts, three zero exits, and a run directory
    holding nothing but the scaffold commit"
verify:
    "`codex exec --help` still offers `--dangerously-bypass-approvals-and-sandbox` while
    `~/.codex/cloud-config-bundle-cache.json` lists `allowed_approval_policies` without
    `never` — and a session started with that flag records `approval_policy: untrusted`
    in every `turn_context` of its rollout"
verified: 2026-08-26
tags: [codex, sandbox, permissions, trials, silent-failure]
---

A ChatGPT account under enterprise management receives a requirements bundle naming the
approval policies and sandbox modes its sessions may use.
`--dangerously-bypass-approvals-and-sandbox` asks for `never` and `danger-full-access`.
When the bundle allows neither, Codex lowers the session to what is permitted and starts
anyway: the flag is still offered by `--help`, nothing on the command line is rejected,
and no message says it did not take.

**Why it matters:** it fails as success. Under the clamped policy a headless
`codex exec` has no one to approve anything, so every command outside the built-in
trusted set dies with `Rejected("approval request failed")` — including `ls`,
`git ls-files`, and `apply_patch`. The session narrates the problem to itself, writes
nothing, and exits 0. A trial driven this way reported a clean run for all three prompts
while the run directory held only the commit the scaffold made.

**What to do:** read the effective policy from the transcript rather than from the
command that asked for it — `turn_context` carries `approval_policy` and
`sandbox_policy` per turn. Where the bundle forbids the bypass, no invocation of that
flag will ever work, and `workspace-write` is the strongest sandbox such an account can
reach. This is why `[codex.trial]` in `harnesses.toml` drives `--approve-for-me` rather
than the flag that reads as the obvious choice; switching it back costs a whole trial
and says nothing while it does.

Related:
[`a-conflicted-pr-runs-no-workflows-and-looks-green`](a-conflicted-pr-runs-no-workflows-and-looks-green.md)
and
[`a-plugin-archive-missing-its-manifest-loads-with-no-error`](a-plugin-archive-missing-its-manifest-loads-with-no-error.md)
are the same class — a check that examined nothing, reporting success.
