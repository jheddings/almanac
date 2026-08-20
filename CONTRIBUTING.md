# Contributing

Thanks for helping improve **almanac**. This is a Claude Code plugin carrying the
procedural half of keeping an almanac — a directory of facts discovered the hard way.
The non-procedural half deliberately stays in each repo's own instructions; see
[Design positions](README.md#design-positions) before proposing that a skill absorb it.

## Design philosophy: do one thing well

Each skill follows the Unix principle — **do one thing, and do it very well.** A skill
has a single, nameable job (`record` writes an entry; `audit` re-checks the ones that
exist) and resists growing a second one. When a skill starts to need a second
responsibility, that is the signal to write a _new_ skill, not to widen an existing one.

Concretely:

- **One purpose per skill.** If you can't state the job in one sentence, it's two
  skills.
- **Compose, don't conflate.** `audit` reports and proposes; it never rewrites an entry
  on its own authority. `record` decides and writes; it does not re-verify the whole
  directory.
- **Focused and efficient.** Keep `SKILL.md` short and scannable. Move heavy reference
  or reusable code into `references/` or `scripts/`.

### Trigger, procedure, or local convention?

Every addition to this plugin has to answer one question first: **which of the three
halves does this belong to?** Getting it wrong is the most expensive mistake available
here.

| Kind of content                                     | Where it lives                 | Why                                                                   |
| --------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------- |
| A **trigger** — when to look at the almanac at all  | the repo's `AGENTS.md`         | must fire without being loaded, and must work on tools without skills |
| A **procedure** — how to record, how to verify      | a skill in this plugin         | maintained centrally, travels across repos                            |
| A **local convention** — format, destinations, wrap | the repo's almanac `README.md` | irreducibly repo-specific; a shared answer would be wrong somewhere   |

The load-bearing case is the destinations table. The skill owns the _questions_ — is
this designed intent? a required rule? in-flight status? a personal preference? — and
the repo's README owns the _answers_. A skill that hardcodes `docs/arch/` will send an
agent in a repo without that directory to file design intent into nowhere, and the usual
outcome is that the content lands in the almanac instead. If you find yourself writing a
path into a skill, that's the signal you've crossed the line.

## Skill structure

Each skill lives in `skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`,
`description`) followed by the skill body, per the
[Agent Skills specification](https://agentskills.io/specification). Supporting material
goes in `references/`, `scripts/`, or `assets/` subdirectories.

### Naming

- Lowercase letters, numbers, and hyphens only.
- The directory name must match the `name` field in frontmatter.
- No leading/trailing hyphens, no consecutive hyphens.
- Names are **unprefixed** — the plugin namespace supplies `almanac:`, so a skill called
  `record` invokes as `almanac:record`. Don't write `almanac-record`.

### Descriptions

The `description` is what Claude reads to decide whether to load the skill, so it must
describe **when to use it**, not what it does. Pack in the trigger phrases a user would
actually type.

```yaml
# Good — triggering conditions
description: >-
    Use when checking whether the almanac's recorded facts are still true — "audit the
    almanac", "are these entries still valid", "is anything in here stale".

# Avoid — summarizes the workflow; Claude may follow the summary instead of the skill
description: Enumerate entries, run each verify line, then open a PR with corrections.
```

`record`'s description is the harder case and worth studying: its real trigger is a
_state_ (you have just finished being surprised), not a phrase anyone types. It names
both.

## Conventions

### Never hardcode the almanac's path

The conventional location is `docs/almanac/`, and it is not guaranteed. Skills Glob for
`**/almanac/README.md`, and **stop** if there is no match rather than creating a
directory as a side effect of some other job. One cheap call, and it handles a
root-level `almanac/`.

### Read the repo's README before writing

Both skills instruct the agent to read the almanac's own `README.md` before acting. That
is not politeness — it is where the frontmatter fields, the wrap width, and the
destinations live. A skill that reconstructs the entry format from memory will produce
entries that disagree with the ones already in the directory.

### Prefer built-in tools over Bash

Use the **Glob**, **Grep**, and **Read** tools rather than shelling out to `find`,
`grep`, `rg`, `cat`, `head`, or `tail`. Bash is acceptable when no built-in tool covers
the task. Skills that dispatch subagents must **repeat these constraints in the subagent
prompt**, since the subagent does not inherit them.

### Propose, don't rewrite

`audit` reads and proposes; the operator approves; the change ships as a PR. Preserve
that shape in anything new. An agent cannot validate its own conclusions, and a wrong
deletion is invisible afterwards because nothing remains to review.

### Don't let a bundled tool become a dependency

`audit` bundles `audit.workflow.js` for batch fan-out, and the Workflow tool is Claude
Code only. The skill therefore carries a fallback that reaches the same result with
ordinary subagents, and every rule that makes the verdicts trustworthy is stated in
prose rather than enforced in code. Hold new tooling to the same bar: if the script is
the only place a rule lives, the skill breaks on every tool that can't run it.

## The template and this repo's instance

`templates/almanac/README.md` is the **canonical** contract text — what an adopting repo
copies. `docs/almanac/README.md` is this repo's own live almanac, and an _instance_ of
that template: byte-identical outside the block marked `<!-- almanac:local -->`, which
holds this repo's destinations table.

`just drift` (also a pre-commit hook) enforces that. So when you improve the contract
text:

1. Edit `templates/almanac/README.md`.
2. Port the same edit into `docs/almanac/README.md`.
3. Run `just drift` — it prints a unified diff of whatever you missed.

If a change genuinely belongs to one repo and not to adopters, it goes _inside_ the
local block. If it doesn't fit there, it probably belongs in a skill instead.

Never seed `docs/almanac/` with illustrative or invented entries. It is a real almanac;
an entry that is not a fact somebody discovered here is exactly the artifact these
skills exist to prevent. Zero entries is a perfectly good state.

## Checks

```bash
just check   # style + validate + drift
just tidy    # prettier --write .
```

- `just style` — `prettier --check .` (also a pre-commit hook, so it runs on commit and
  in CI). Note `proseWrap: always` at 88 columns: prettier reflows Markdown prose.
- `just validate` — `skills-ref validate` per skill directory, matching the
  `validate-skill` workflow.
- `just drift` — the template check described above.

## Testing skills

Skills are prose, so there is nothing to unit-test; verification is behavioral. Run the
skill against a real repo and confirm it does the right thing — and the right _nothing_
when there is nothing to record. `superpowers:writing-skills` describes the test-first
method. Two paths are worth exercising explicitly, because both are failure modes seen
in practice:

- `record` handed something that is really a working preference should decline and say
  so, not file a hedged entry and leave the call to a reviewer.
- `audit` given a deliberately broken `verify` line should return `unverifiable`, never
  `falsified` — a command that no longer runs says nothing about the claim.

## Releasing

```bash
just release patch   # or minor / major / an explicit version
```

Bumps `.claude-plugin/plugin.json`, commits, tags, and pushes. CI drafts the GitHub
release from the tag. Releases must come from `main` with a clean tree; `release-guard`
enforces it.

## Commits and branches

See [AGENTS.md](AGENTS.md) — Conventional Commits, `<type>/<change-slug>` branches, and
session worktrees under `.worktrees/`.
