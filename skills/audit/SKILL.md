---
name: audit
description: >-
    Use when checking whether the almanac's recorded facts are still true — "audit the
    almanac", "are these entries still valid", "is anything in here stale", "re-verify
    the almanac" — before relying heavily on almanac entries, or after a dependency,
    CLI, or tooling upgrade that could have quietly falsified one. Analysis is
    read-only; every edit goes through a confirmation gate and a PR.
---

# Audit the Almanac

The almanac holds facts discovered the hard way, recorded by agents for agents. Every
entry carries a `verify` line for exactly one reason: so a future agent can re-check the
claim cheaply instead of trusting it blindly. Nothing ever does. This skill is that
missing pass.

**An entry that quietly stopped being true is worse than no entry at all**, because it
is written to be acted on without re-derivation. Nobody re-checks a confidently-worded
fact; that is the whole point of writing one down. So the failure mode is silent by
construction — the entry keeps reading exactly as true as the day it was recorded.

Facts go stale from the outside: a dependency bumps, a CLI changes a default, a flag
gets added, a path moves. None of those touch the entry, and none of them announce
themselves.

## Precedence

This skill owns the **method**: what counts as verification, the verdicts and their
burden of proof, and the procedure for acting on the results. The almanac's `README.md`
owns what is genuinely **local to this repository** — the entry format, the wrap width,
how corrections ship.

- They disagree about method → **this skill wins.**
- They disagree about a convention the README claims as repo-local → **the README
  wins.**

The reason: the method is maintained centrally and travels across repos. If each repo's
README outranked it, one stale local copy would silently override a corrected rule.

## Step 1 — Enumerate the entries

Glob for `**/almanac/README.md` to find the almanac. The conventional location is
`docs/almanac/`. If there is no match, this repo has no almanac — say so and stop.

List every entry file in that directory, **excluding `README.md`** (it is the contract,
not a claim):

```bash
ls docs/almanac/*.md | grep -v 'README.md$'
```

If the operator scoped the request ("audit the migration entries"), filter here — but
say in your report which subset you audited, so an unaudited entry is never mistaken for
one that passed.

If the almanac is empty, say so and stop. An audit of zero entries is not a pass.

## Step 2 — Verify the entries

Fan the entries out to subagents in batches of about three, or run them sequentially in
the main thread if subagents are unavailable. Parallelism is an optimization; nothing
here depends on it, or on any tool a particular harness happens to provide.

Give each worker this task, verbatim in substance:

> For each file listed, read the entry. Its frontmatter carries a `title` (the claim)
> and usually a `verify` line (how to re-check it cheaply); the body states the
> consequence. Run the `verify` line, or the closest **faithful** read-only equivalent
> if the command has drifted — a renamed path, a moved file, a flag that changed
> spelling. "Faithful" means it tests the same load-bearing detail the claim rests on,
> not merely the neighbourhood that detail lives in. Then compare the actual output
> against what the claim predicts and assign one verdict:
>
> - **`holds`** — you ran a check and its output confirms the claim.
> - **`falsified`** — you ran a check and its output contradicts the claim.
> - **`unverifiable`** — you could not run a conclusive check: the command no longer
>   works, the path moved and no faithful equivalent exists, or verifying would need
>   credentials, network access, or production.

Four rules bind every worker. They are not style preferences — each one is a way the
audit manufactures a false result if it is dropped, so **restate them in the prompt**
rather than assuming they carry over:

1. **`holds` requires positive evidence produced during this run.** If nothing
   conclusive ran, the verdict is `unverifiable` — never `holds`. A confident reading of
   the entry's own prose is not evidence; the entry restating its claim proves nothing.
2. **Read-only.** Do not edit any file. Do not run anything that mutates state, writes
   to a database, installs, deploys, or reaches production. If verifying the claim would
   require that, return `unverifiable` and say so.
3. **A broken `verify` line is `unverifiable`**, not `falsified` — and the proposed
   action is to repair the line, so the entry becomes re-checkable. An entry with no
   `verify` line at all is `unverifiable` unless the worker devises and runs a
   conclusive read-only check itself.
4. **Quote output verbatim.** Not a summary, not a paraphrase, not an interpretation.
   Trim long output, but what comes back must be literal. If there was no output, say
   "no output" and name the exit status observed.

Require these fields back per entry, and reject a result that omits any of them:

| Field            | Must contain                                                    |
| ---------------- | --------------------------------------------------------------- |
| `file`           | the path exactly as given                                       |
| `title`          | the entry's `title` frontmatter value                           |
| `verdict`        | exactly one of `holds` / `falsified` / `unverifiable`           |
| `command`        | literally what ran — or "none", with the reason, if nothing did |
| `evidence`       | verbatim output                                                 |
| `proposedAction` | what a maintainer should do, concretely                         |

**Account for every file you dispatched.** Diff the paths that came back against the
paths you sent, and treat any gap as an explicit result of the audit — see Step 3.
Nothing does this accounting for you.

Verification never edits an entry, never deletes one, and never opens a PR. Those stay
in the main thread, behind the gate in Step 4.

## Step 3 — Read the result critically

| Verdict        | What it means                | What you owe it                        |
| -------------- | ---------------------------- | -------------------------------------- |
| `holds`        | Ran a check; output confirms | Bump `verified` — see Step 4.          |
| `falsified`    | Ran a check; output refutes  | Spot-check it, then correct or delete. |
| `unverifiable` | No conclusive check ran      | Repair the `verify` line, or flag it.  |

Two warnings, both of which are how this step goes wrong:

**Everything in `falsified` and `unverifiable` is a worker's _claim_, not fact.** It is
a model's reading of command output, and it can misread one — the entry may still be
true, or false for a different reason. Before acting on anything, **independently
re-derive at least one finding yourself**: run the command, read the output, and confirm
it says what the report says it says. Checking the report against itself is circular.

**A missing result is not a pass.** An entry that produced no verdict — a batch that
dropped, a worker that failed — has been checked by nobody. Silence is absence of
evidence, and it must never be reported as "all clear." Re-run those files before
concluding anything about them, and if they still come back empty, name them in your
report as unaudited.

Weigh how discriminating the run was, too. An audit where everything held is weak
evidence: it barely exercises the parts that catch staleness.

## Step 4 — Confirmation gate

Before editing anything, show the operator what you propose to change: the entry, why
the audit says it is stale, the evidence you independently confirmed, and the specific
edit — reword, repair the verify line, delete, or bump `verified`. Get explicit
approval.

### Bumping `verified`

If the almanac's README defines a `verified` field, **this audit is the only process
licensed to set it**, because it is the only one that actually re-runs the `verify`
line. Leaving it untouched after a `holds` verdict makes the field decorative.

The rules, and they are narrow:

- **Only a `holds` verdict bumps it**, to the date the check ran. `unverifiable` never
  touches the field — an entry nobody could check is not an entry that was checked.
- **A bump is a write, so it goes through this same gate and the same PR** as a
  correction. It does not get a fast path. Step 3 only requires you to independently
  re-derive _one_ finding; the rest remain the workers' claims, and setting a freshness
  signal on the strength of an unverified claim is exactly the laundering the README
  forbids.
- **Quote the command and its verbatim output, per bumped entry, in the PR body.** That
  is what makes the bump reviewable rather than asserted. Step 2 already required both
  back from every worker.

An audit where every entry held still produces a PR — a diff of nothing but dates. That
is the feature: it is the only durable record that an audit ran at all.

**Deleting a falsified entry is legitimate and often the right answer.** Removing a
stale fact is worth as much as adding a true one. Do not soften a falsified entry into a
hedged one that survives — a hedged entry is a claim nobody can act on and nobody will
delete.

Do not fold unrelated fixes in. An audit that quietly rewrites prose it merely dislikes
is no longer an audit.

## Step 5 — Deliver as a PR

Never rewrite entries in place on a shared branch. Work on a branch, commit the changes,
and open a PR so they get reviewed like any other — an agent cannot validate its own
conclusions, and that applies to deletions and date bumps as much as to new entries.

In the PR body, give one line per entry: what the audit found, the command and output
that established it, and what changed. Where a fix **supersedes** an entry rather than
refuting it — the behavior changed, so the old fact is now history — update `recorded`
and note what changed, per the almanac's `README.md`.

## Common mistakes

- **Marking an entry true from its own prose.** The entry restating its claim is not
  evidence. No command ran, so the verdict is `unverifiable`, not `holds`.
- **Bumping `verified` on an `unverifiable` verdict**, or bumping it outside the PR
  gate. Both convert "nobody checked" into "someone checked", which is the one failure
  the field is supposed to rule out.
- **Silently editing instead of proposing.** The gate in Step 4 exists because a wrong
  deletion is invisible afterwards — nothing remains to review.
- **Treating a broken `verify` line as a falsified claim.** A command that no longer
  runs says nothing about the fact. That is `unverifiable`, and the fix is repairing the
  verify line, not deleting the entry.
- **Trusting a worker's findings without re-deriving one.** Its verdicts are claims.
- **Reporting a run as clean when some entry produced no verdict.** Nobody checked it.
- **Dropping a rule from Step 2 when prompting a worker** because it seemed implied.
  Every one of the four is a way to manufacture a false result; none of them is enforced
  for you.
- **Auditing a subset and reporting it as "the almanac."** Name what you covered.
