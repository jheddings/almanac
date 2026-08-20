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

### `verified` is set only by the audit, and only through the PR gate

Our entry format has an optional `verified:` date meaning exactly one thing: someone ran
the `verify` line on that date and the claim held. #1194's variant lacked the field. The
audit is the only process that actually re-runs those lines, so it is the only one
licensed to set it — otherwise the field is decorative.

But a bump is a write, and `almanac-audit` is specified read-only. Resolved as:
**`verified` bumps ride the same confirmation gate and the same PR as corrections.** No
fast path.

The reasoning that rules out a direct write: Step 3 of the audit requires the agent to
independently re-derive only _one_ finding. Every other verdict remains the workflow's
claim — a model's reading of command output. Bumping `verified` across all `holds`
results would set a freshness signal on the strength of unverified claims, which is
precisely the laundering of a stale fact as a current one that the field's rule forbids.
The audit would manufacture the condition it exists to detect.

Three consequences, written into the skill:

- Only `holds` bumps. `unverifiable` never touches the field — an entry nobody could
  check is not an entry that was checked.
- The command and its verbatim output are quoted per bumped entry in the PR body. The
  workflow already returns both, so this costs nothing and makes the bump reviewable
  rather than asserted.
- An audit where everything held still opens a PR — a diff of nothing but dates. That is
  the feature: it is the only durable record that an audit happened.

### Portability ceiling: stated, and lowered

`almanac-audit` invokes the Workflow tool, which is Claude Code only and gated. That
reintroduces one layer up the asymmetry the almanac was created to remove.

Rather than only documenting it, the skill now carries a **fallback**: if the Workflow
tool is unavailable, dispatch the same prompt and the same verdict schema to ordinary
subagents in batches of three, and continue from Step 3 unchanged. Every rule that makes
the verdicts trustworthy — `holds` requires positive evidence produced during the run,
no edits, no state-mutating commands, account for every input file — is prose in the
skill, not logic in the script. The workflow is an optimization, not a dependency.

The residual cost is still real and still stated in the plugin README: batch fan-out is
what makes an audit cheap enough to actually happen, and that is faster under the
Workflow tool.

### Almanac location: discovered, with a documented default

`docs/almanac/` was hardcoded throughout both skills. A plugin cannot assume it, and
there is no plugin config mechanism to make it a setting. Both skills now Glob
`**/almanac/README.md`, document `docs/almanac/` as conventional, and **stop** if there
is no match rather than creating a directory as a side effect of another job. One cheap
call; handles a root-level `almanac/`.

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
add the consult trigger to `AGENTS.md`. An `init` skill would do both, probe the repo
for real destinations to fill the local block, and make template drift detectable in
adopting repos rather than only here. Deferred to keep the first release to the two
proven skills. It is the top follow-up, and the reason `templates/` sits at the repo
root rather than inside a skill directory: it needs a home that does not presume `init`
exists.

## Repository layout

```
.claude-plugin/plugin.json          name: almanac, version 0.1.0
.claude-plugin/marketplace.json     self-hosted, one plugin at ./
skills/record/SKILL.md
skills/audit/SKILL.md
skills/audit/audit.workflow.js      batch fan-out; read-only by construction
templates/almanac/README.md         canonical contract text
docs/almanac/README.md              this repo's live almanac — an instance, no entries
docs/design/                        this document
scripts/check-template-drift.py
AGENTS.md                           consult trigger + conventions
README.md                           installer-facing; carries the design positions
CONTRIBUTING.md                     the three-halves rule, skill conventions
.justfile .prettierrc.json LICENSE
```

## Tooling

Follows `obsidian-steward`: `.justfile` (`tidy`, `check`, `style`, `validate`, `drift`,
`release-guard`, `release`), prettier at `printWidth: 88` with `proseWrap: always`,
`skills-ref validate` per skill, `renovate.json`, and a `release.yml` that drafts a
GitHub release from a `N.N.N` tag.

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

- `skills-ref validate` on both skills, `prettier --check .`, and the drift check — all
  runnable here.
- **The Workflow tool is not available in this session**, so `audit.workflow.js` cannot
  be executed end-to-end. It is ported with two changes from the version proven in #1194
  (the `scriptPath` becomes `${CLAUDE_PLUGIN_ROOT}`-relative, and the `holds`
  `proposedAction` mentions the `verified` bump); the fan-out logic is unchanged. First
  real exercise of the audit path is deferred to a repo with entries — this one has
  none.
- Behavioral checks worth running when entries exist: `record` handed a working
  preference should decline rather than file a hedged entry; `audit` given a
  deliberately broken `verify` line should return `unverifiable`, never `falsified`.

## Out of scope

- **`almanac:consult` and any session hook.** Consulting is a trigger; see the three
  halves.
- **Adapters for Codex, Cursor, or Gemini.** The skills are repo-agnostic and
  stack-neutral, but packaging waits until something needs it.
- **Scheduling the audit.** Whether it runs on a cadence is separate from it existing.
- **Seeding this repo's almanac.** Entries are recorded when something is discovered,
  never written to demonstrate the format.
