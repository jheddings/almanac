---
name: almanac-audit
description: >-
  Use when asked to audit, validate, recheck, or find stale entries in a repository almanac,
  or after a dependency or tooling change that may have falsified recorded facts. The
  verification phase is read-only; corrections and verified-date updates require explicit
  confirmation and review.
---

# Almanac Audit

Re-check every in-scope almanac claim against the repository as it exists now. An entry that quietly
became false is worse than no entry because future agents are expected to trust it.

The method in this skill governs evidence and verdicts. The target repository's
`docs/almanac/README.md` governs its entry format and how approved changes ship.

## Establish scope and coverage

Enumerate `docs/almanac/*.md`, excluding `README.md`. If the operator requested a subset,
name that scope explicitly. If there are no entry files, report that the almanac is empty
and stop successfully.

Account for every selected path. A dropped or missing result is not a pass.

## Verify without changing state

For each entry:

1. Read its title, claim, consequence, and `verify` value.
2. Run the stated verification, or the closest faithful read-only equivalent when a path or command
   spelling drifted.
3. Preserve the literal command, exit status, and relevant verbatim output.
4. Assign exactly one verdict:

| Verdict        | Required evidence                                      |
| -------------- | ------------------------------------------------------ |
| `holds`        | A check ran during this audit and confirmed the claim  |
| `falsified`    | A check ran during this audit and contradicted it      |
| `unverifiable` | No safe, conclusive check could run                     |

A broken verify command is `unverifiable`, not evidence that the claim is false. Reading the entry's
own prose is never evidence that it holds. Do not run commands that mutate files or databases,
install dependencies, deploy, use production credentials, or otherwise create external effects.

When independent subagents are available, batches may run in parallel. Give each worker the same
read-only constraints and require structured results containing file, title, verdict, command,
evidence, and proposed action. Otherwise run the checks sequentially in the main agent. Parallelism
is an optimization, not a runtime dependency.

## Review the results critically

Return totals for selected, returned, missing, holds, falsified, and unverifiable. For every result,
show the command and evidence. Independently spot-check at least one `falsified` or `unverifiable`
finding before proposing a change; a worker's interpretation is itself only a claim.

Do not report “all clear” while any selected file is missing or unverifiable. An all-holds
result is valid only when every entry has positive evidence.

## Propose reviewed writes

The verification phase never edits entries. After presenting results, propose only changes supported
by the evidence:

- `holds`: set or bump `verified` to the audit date, but only if the exact verification ran
  and held;
- `falsified`: correct or delete the entry rather than weakening it with hedged prose;
- `unverifiable`: repair the verify value when a safe discriminating check can be supplied,
  otherwise flag it for human investigation without changing the claim.

Show the exact proposed files and actions, then get explicit operator confirmation. After approval,
apply the changes on a branch and deliver them through the repository's review process. A batch of
freshness-only updates still requires review. Do not fold unrelated prose cleanup into an audit.

Report the final per-entry action and evidence. If the operator declines changes, leave the audit as
a read-only report.
