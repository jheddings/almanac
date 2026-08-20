# Almanac as a Claude Code Plugin — Design

**Date:** 2026-08-20 **Status:** Approved **Supersedes:** the extraction contract in
`risefamily/red#1194`'s `2026-08-20-almanac-skills-design.md`

## Summary

Turn this repo into the distributable plugin for the almanac skills, porting
`almanac-record` and `almanac-audit` out of `risefamily/red#1194`. Claude Code is the
first publishing target; the structure follows `jheddings/obsidian-steward`, which the
same operator maintains.

Two skills ship: `almanac:record` and `almanac:audit`. Consulting the almanac does not
become a skill, and no session hook is added.

## Decisions

### The three halves

Every piece of content about the almanac belongs to exactly one of three homes, and the
whole design falls out of that split:

| Kind                                              | Home                           | Why                                                  |
| ------------------------------------------------- | ------------------------------ | ---------------------------------------------------- |
| **Trigger** — when to look at the almanac at all  | the repo's `AGENTS.md`         | must fire unloaded, and work on tools without skills |
| **Procedure** — how to record, how to verify      | a skill in this plugin         | maintained centrally, travels across repos           |
| **Local convention** — format, destinations, wrap | the repo's almanac `README.md` | irreducibly repo-specific                            |

Carried forward from #1194 unchanged: consulting is a trigger, so there is no
`almanac:consult`. A prior session's `SessionStart` hook that listed entries was removed
deliberately — it was Claude-only, which is the fragmentation the almanac exists to fix.

**Precedence within that split:** where a skill and the README disagree about method,
the skill wins; where they disagree about something the README claims as local, the
README wins. This is the reverse of the obvious anti-drift instinct. If each repo's
README outranked the shared method, one stale local copy would silently override a
corrected rule — drift resolving with the _worse_ copy winning, which is strictly worse
than no precedence rule.

### The disqualifier table was in the wrong half

#1194's `almanac-record` carried a table mapping content categories to **destinations**
— `docs/arch/`, `CONTRIBUTING.md`, "a plans/specs directory" — while simultaneously
claiming method-precedence over the repo README. Destinations are local convention, not
method, so the table was on the wrong side of the line the same skill drew. Shipped as a
plugin it would direct an agent in a repo without `docs/arch/` to file design intent
into a directory that does not exist; the reliable outcome of a missing destination is
that the content lands in the almanac instead.

**Fixed by splitting the table.** The skill owns the five _questions_ (designed intent?
a required rule? in-flight status? a spec or plan? a personal preference?) and instructs
the agent to read the answers from the repo's almanac README. The README owns the
answers. As a side effect the duplication that made a precedence rule necessary for this
table at all is gone, and `record` gains a red flag for the remaining gap: a category
with no row is a gap in the README, not a licence to record.

### `verified` is set only by having run the check, and the audit's bumps go through the PR gate

Our entry format has an optional `verified:` date meaning exactly one thing: someone ran
the `verify` line on that date and the claim held. #1194's variant lacked the field. The
audit is the only process that re-runs those lines _systematically_, so if it never sets
the field, nothing does and the field is decorative.

**A first draft overclaimed this as "the audit is the only process licensed to set
it."** A review of this branch flagged the resulting contradiction with the template,
which says anyone who ran the check may bump — and proposed resolving it by restricting
the template. That is the wrong direction. The contract already invites non-audit agents
to run verify lines ("if it carries a `verify` line and you're about to act on something
expensive, run it"), and evidence produced that way is exactly as real as the audit's.
Exclusivity would discard it while strengthening nothing: the rule that carries the
weight is _never set it without having run the check_, and that holds either way. An
ad-hoc bump also rides a PR diff, so it gets the same review. The skill and plugin
README were softened to match the template instead.

But a bump is a write, and `almanac-audit` is specified read-only. Resolved as:
**`verified` bumps ride the same confirmation gate and the same PR as corrections.** No
fast path.

The reasoning that rules out a direct write: Step 3 of the audit requires the agent to
independently re-derive only _one_ finding. Every other verdict remains a worker's claim
— a model's reading of command output. Bumping `verified` across all `holds` results
would set a freshness signal on the strength of unverified claims, which is precisely
the laundering of a stale fact as a current one that the field's rule forbids. The audit
would manufacture the condition it exists to detect.

Three consequences, written into the skill:

- Only `holds` bumps. `unverifiable` never touches the field — an entry nobody could
  check is not an entry that was checked.
- The command and its verbatim output are quoted per bumped entry in the PR body. Step 2
  already requires both back from every worker, so this costs nothing and makes the bump
  reviewable rather than asserted.
- An audit where everything held still opens a PR — a diff of nothing but dates. That is
  the feature: it is the only durable record that an audit happened.

### Portability ceiling: removed, not accepted

`almanac-audit` invoked the Workflow tool, which is Claude Code only and gated. That
reintroduces one layer up the asymmetry the almanac was created to remove.

This went through two positions, and the reversal is worth recording because the first
one looked reasonable. **Draft 1 accepted the cost and mitigated it:** keep
`audit.workflow.js` for batch fan-out, and add a fallback for harnesses without the
Workflow tool. That is defensible on its own terms — the workflow becomes an
optimization rather than a dependency, and auditing is rare enough that a fast path on
one tool is worth having.

**Draft 2 deleted the script.** A parallel session solving the same brief independently
reached the leaner design, and comparing the two made the flaw in draft 1 visible: a
fallback still leaves the _primary_ documented path unavailable to most tools, and a
skill whose main body describes a tool-specific mechanism will be read as requiring it.
Subagent fan-out is now the only path, with sequential execution in the main thread when
subagents are unavailable.

**What deleting it costs, stated plainly.** The script carried `VERDICT_SCHEMA`, hard-
validated at the subagent boundary — the mechanism that stopped a worker returning
`holds` without evidence, which #1194's testing identified as load-bearing. That
enforcement is now four prose rules the skill instructs the agent to restate in every
worker prompt, plus a required-fields table and an explicit instruction to diff
dispatched paths against returned ones. Prose that holds on every tool beats a schema
that holds on one, but it is a guarantee downgraded to an instruction, and both the
skill and the plugin README say so rather than implying the two are equivalent.

Done before the first tag deliberately. v0.1.0 would otherwise have published
`${CLAUDE_PLUGIN_ROOT}/skills/audit/audit.workflow.js` as a real path and a stated
design position, making the removal a breaking change and the published rationale wrong
in hindsight.

### Almanac location: discovered, with a documented default

`docs/almanac/` was hardcoded throughout both skills. A plugin cannot assume it, and
there is no plugin config mechanism to make it a setting.

The first draft globbed `**/almanac/README.md` in one step and asked the operator when
it found more than one match. **A review of this branch caught that as a bug,
correctly.** In this repo that glob returns four paths from the primary repo root — the
real almanac, the shipped template, and one copy per active worktree — so the ambiguity
prompt would have fired on nearly every invocation, in the one repo that dogfoods the
plugin. It was a collision between two decisions made separately: cheap discovery, and
putting the template at `templates/`. Neither was wrong; the interaction was untested.

Both skills now resolve in order: prefer `docs/almanac/README.md`; else glob and discard
matches under `templates/`, `.worktrees/`, `node_modules/`, `vendor/`, or any nested
checkout; then require exactly one survivor. The general rule the exclusions encode is
that **a directory named `almanac` is not evidence of an almanac** — a template or
another checkout's copy is not this repo's, and treating one as the target means
recording facts where nobody reads them, or auditing files nobody relies on. Skills hold
the resolved directory rather than re-globbing.

### Dogfood and template are two documents, and the template is canonical

The most consequential layout question: once the repo _is_ the plugin, is
`docs/almanac/` a live almanac or the shipped template?

**Both, template canonical.** They are genuinely different documents — a template has
placeholders and adoption instructions; a live contract has this repo's answers — so
collapsing them into one file would require lying in one direction.

- `templates/almanac/README.md` is canonical. Adopters copy it.
- `docs/almanac/README.md` is this repo's live almanac and an _instance_ of the
  template: byte-identical outside a block delimited by `<!-- almanac:local -->`, which
  holds the destinations table.
- `scripts/check-template-drift.py` strips that block from both and diffs the remainder,
  wired into `just drift` and a pre-commit hook. Duplication is the cost of this shape;
  the check is what keeps the cost from being silent.

Rejected: **dogfood only** (no template — every adopter hand-writes ~170 lines of
contract prose, which is the drift-with-the-worse-copy failure the precedence rule
exists to prevent); **template only** (kills dogfooding — the repo that preaches
recording facts records none, and the "starts empty" invariant stops meaning anything).

This repo's almanac starts empty and stays empty unless building the plugin surfaces a
genuine fact passing all three admission tests. Zero is the expected outcome.

### Skill names drop the `almanac-` prefix

`skills/record/` and `skills/audit/`, invoking as `almanac:record` and `almanac:audit`.
This matches `obsidian-steward` (plugin `tidy`, skill `check-links` →
`tidy:check-links`) and avoids the `almanac:almanac-record` stutter. #1194's extraction
contract had argued for keeping the prefix so the names self-identify outside a plugin
namespace; that cost is accepted, since the namespace is present on the only publishing
target this release has.

### `almanac:init` deferred to the next release

Bootstrapping is two manual steps today: copy `templates/almanac/` into `docs/`, then
add the consult trigger to `AGENTS.md`. An `init` skill would do both and probe the repo
for real destinations to fill the local block. Deferred to keep the first release to the
two proven skills; it is the top follow-up.

**`templates/` is its permanent home — `init` must not move it into
`skills/init/assets/`.** Two reasons, and they outlast the deferral. The path is
published in v0.1.0's setup instructions, so moving it breaks them. And a template
buried in a skill's assets is reachable only by agents that can load the skill, which
defeats the point: the contract text is what an adopter on a harness _without_ skills
needs most. `init` reads `${CLAUDE_PLUGIN_ROOT}/templates/almanac/README.md`.

### The canonical example modelled the anti-pattern

The template's example entry carried
`verify: check the deploy workflow for --include-all on the db push step` — a
description, not a command, stating no observation. `record` teaches in the same breath
that a verify line must test the load-bearing detail and state what would count as a
refutation, and offers almost this exact string as its **Bad** example. So the canonical
text that adopters copy contradicted the skill that governs it, in the one field where
the whole scheme's value sits. Caught in review of this branch. Now `verify: "`grep -rn
-- '--include-all' .github/workflows/` returns nothing"`, matching the skill's **Good**
example, with the observation rule stated in the template rather than only in the skill.

Validating that YAML surfaced a second defect in the same example: **`source: PR #1129`
parses as `PR`.** Unquoted, `#` opens a YAML comment, so every entry written from the
template would silently drop its provenance, with nothing warning about it. Both values
are now quoted, and the template says to quote anything containing `#` or `:`.

Neither is an almanac entry. The verify-line inconsistency was a defect in a file, fixed
rather than durable. The YAML comment rule is generic YAML knowledge and a two-minute
derivation — it fails the costly-to-rediscover test even though its effect here was
silent.

### Template revision stamp

`templates/almanac/README.md` opens with `<!-- almanac-template: 1 -->`. The drift check
already keeps this repo's instance honest, but an _adopting_ repo's copy has no such
link — nothing tells it the contract text moved on. The stamp is what makes a stale copy
diagnosable.

It is a **monotonic integer, deliberately not the plugin version.** Tying it to the
plugin version would invalidate every adopter's copy on each patch release, which trains
people to ignore it. Bump it only when the shared contract text changes; the local block
is excluded by definition. Adopters can then be told, in one sentence, which revision
they are on.

Added before the first tag because it is only cheap now: every repo initialized from an
unstamped v0.1.0 would be permanently unidentifiable.

## Repository layout

```
.claude-plugin/plugin.json          name: almanac, version 0.1.0
.claude-plugin/marketplace.json     self-hosted, one plugin at ./
skills/record/SKILL.md
skills/audit/SKILL.md
templates/almanac/README.md         canonical contract text, revision-stamped
docs/almanac/README.md              this repo's live almanac — an instance, no entries
docs/design/                        this document
scripts/check-template-drift.py
AGENTS.md                           consult trigger + conventions
README.md                           installer-facing; carries the design positions
CONTRIBUTING.md                     the three-halves rule, skill conventions
.justfile .prettierrc.json LICENSE
```

## Tooling

Follows `obsidian-steward`: `.justfile` (`tidy`, `check`, `style`, `validate`,
`manifests`, `drift`, `release-guard`, `release`), prettier at `printWidth: 88` with
`proseWrap: always`, `skills-ref validate` per skill, `renovate.json`, and a
`release.yml` that drafts a GitHub release from a `N.N.N` tag.

`manifests` is borrowed from the parallel session's branch and is not in
`obsidian-steward`. It asserts with `jq` that `plugin.json` and `marketplace.json` agree
on the plugin name and that the version is well-formed. `claude plugin validate` passed
both manifests without checking that they agree with each other, and a name mismatch
between them breaks installation — a failure that surfaces only for whoever installs the
release.

**One divergence.** This repo already had `.pre-commit-config.yaml` and a
`precommit.yaml` workflow, added after the almanac itself and so representing current
practice. `obsidian-steward`'s `preflight.yml` (prettier in CI) is therefore _not_
copied; prettier is added as a pre-commit hook instead, so formatting runs before a
local commit as well as in CI, through the workflow that already exists. The template
drift check joins it as a local hook. `validate-skill.yml` is copied as-is, since
per-skill matrix validation has no pre-commit equivalent.

Cost of adopting prettier: `proseWrap: always` reflows Markdown prose, so `AGENTS.md`
and the almanac README get rewrapped in this change.

## Verification

Skills are prose; verification is behavioral, plus the mechanical checks above. What
this change can and cannot establish:

- `skills-ref validate` on both skills, `prettier --check .`, the manifest checks, and
  the drift check — all runnable here. The drift check was itself tested against the
  failure it exists to catch, since a check that passes forever is the defect `record`
  warns about: prose edited outside the local block fails, the local block replaced
  wholesale passes, a removed marker fails.
- **The audit path is unexercised.** Deleting the workflow removed the only part of it
  that could be mechanically checked, and this almanac has no entries to run it against,
  so nothing here establishes that subagent fan-out produces correct verdicts. That is
  the main open risk in this change. First real exercise is deferred to a repo with
  entries.
- Behavioral checks worth running when entries exist: `record` handed a working
  preference should decline rather than file a hedged entry; `audit` given a
  deliberately broken `verify` line should return `unverifiable`, never `falsified`; and
  — new, because enforcement moved into prose — a worker that cannot run a conclusive
  check should return `unverifiable` rather than `holds`. That last one was guaranteed
  by the schema before and is now only instructed, so it is the regression to watch for.

## Out of scope

- **`almanac:consult` and any session hook.** Consulting is a trigger; see the three
  halves.
- **Adapters for Codex, Cursor, or Gemini.** The skills are repo-agnostic and
  stack-neutral, but packaging waits until something needs it.
- **Scheduling the audit.** Whether it runs on a cadence is separate from it existing.
- **Seeding this repo's almanac.** Entries are recorded when something is discovered,
  never written to demonstrate the format.
