# Contributing

Thanks for helping improve **almanac**. This is a set of harness-neutral skills carrying
the procedural half of keeping an almanac — a directory holding a repository's operating
knowledge, one claim per file — packaged for Claude Code, Codex, Antigravity (`agy`),
and Cursor. The non-procedural half deliberately stays in each repo's own instructions;
see [Design positions](README.md#design-positions) before proposing that a skill absorb
it.

## Design philosophy: do one thing well

Each skill follows the Unix principle — **do one thing, and do it very well.** A skill
has a single, nameable job (`init` installs the repository pieces; `record` writes an
entry; `audit` re-checks the ones that exist) and resists growing a second one. When a
skill starts to need a second responsibility, that is the signal to write a _new_ skill,
not to widen an existing one.

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
| A **repo rule** — commit format, branch names       | a `kind: rule` almanac entry   | fires from the filename index, at the moment it applies               |

The last row is the widened contract, and it moved: rules used to be routed to
`AGENTS.md`, which is always loaded and therefore always paid for. They are entries now,
so `AGENTS.md` keeps the trigger and nothing an entry could carry.

The load-bearing case is the destinations table. The skill owns the _questions_ — is
this designed intent? in-flight status? a personal preference? — and the repo's README
owns the _answers_. A skill that hardcodes `docs/arch/` will send an agent in a repo
without that directory to file design intent into nowhere, and the usual outcome is that
the content lands in the almanac instead. If you find yourself writing a path into a
skill, that's the signal you've crossed the line.

The same split forbids Cursor `rules/` or hooks that inject consult: consult is a
trigger, so it stays in each repo's `AGENTS.md`.

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

The conventional location is `docs/almanac/`, and it is not guaranteed. Skills resolve
it in order: prefer `docs/almanac/README.md`, else glob `**/almanac/README.md` and
discard matches under `templates/`, `node_modules/`, `vendor/`, or any nested checkout;
then **stop** if nothing survives, rather than creating a directory as a side effect of
some other job.

The exclusions are not hypothetical — **this repo trips the naive glob.** From the
primary repo root, `**/almanac/README.md` matches four paths: the real almanac, the
shipped template, and one copy per active worktree. An earlier draft globbed in one step
and would have asked the operator to disambiguate on almost every invocation here, which
is the worst place for it to happen, since this is the repo that dogfoods the plugin. A
directory named `almanac` is not evidence of an almanac.

Copy the shared resolution steps verbatim from an existing skill rather than rewording
them. `init` changes only the no-match outcome: no survivor means it may propose a new
almanac, while `record` and `audit` stop.

Resolution is bounded **above** as well as below. The exclusions keep a skill out of
trees nested inside this one; the rule also stops at this tree's root, because a
workspace or parent repository may keep its own almanac with its own subject. Walking up
would let a skill record into a contract it never read, and leaves the same tree looking
uninitialized to one skill and adopted to another. `tests/test_discovery_rule.py` covers
both directions.

The **exclusion path list** is the part that must not drift, and
`test_every_skill_that_resolves_the_almanac_names_the_same_exclusions` enforces it
mechanically. The consequence clause that follows the list is legitimately per-skill —
recording into the wrong almanac and auditing the wrong one fail differently — so the
test compares paths, not prose. Three skills resolve the almanac, so this list has
already needed extending twice; a hand-edit that misses one is otherwise silent.
`tests/test_discovery_rule.py` also asserts the shipped prose names every path the
executable copy of the rule excludes, so the two cannot diverge.

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

### No skill may depend on a gated tool

Every rule that makes a skill's output trustworthy must be stated in the skill, not
enforced by something it bundles. `audit` shipped a Claude Code Workflow script for
batch fan-out in an early draft; it was removed before the first release, because a
guarantee that only holds on one harness is the asymmetry this plugin exists to remove.

The bar for new tooling: if a script is the only place a rule lives, the skill silently
degrades on every tool that can't run it, and nothing announces the degradation. Bundled
tooling may make a skill faster or cheaper. It may not be the reason the skill is
correct.

Where a rule was previously enforced mechanically and is now prose, **say so in the
skill.** An instruction and a validated schema are not the same guarantee, and
pretending otherwise is how a downgrade goes unnoticed.

## The template and this repo's instance

`templates/almanac/README.md` is the **canonical** contract text — what an adopting repo
copies. `docs/almanac/README.md` is this repo's own live almanac, and an _instance_ of
that template: byte-identical outside the block marked `<!-- almanac:local -->`, which
holds this repo's destinations table.

`init` reads the canonical template from `${CLAUDE_PLUGIN_ROOT}/templates/almanac/` if
that variable is set, otherwise `templates/almanac/` relative to the workspace,
otherwise the plugin install directory as the harness exposes it. It compares the
revision stamp with an existing repository copy and preserves the local block. It
reports drift but never upgrades the contract as a side effect of setup.

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

## Checks and packaging

Every harness this repo packages for is declared as a row in
[`harnesses.toml`](harnesses.toml): its manifests, its payload allowlist, its validator,
and what must and must not appear in the archive it produces. The recipes and the checks
read that table, so a harness is named there and nowhere else.

The checks live in [`tools/`](tools/) and run through `uv run` against the environment
`just venv` syncs. `uv` and `npx` are the only prerequisites.

```bash
just setup              # sync the venv and install the git hooks
just venv               # sync the venv alone

just check              # static checks: style + validate + manifests + drift
just test               # the structural suite
just preflight          # check + test
just tidy               # prettier --write .

just bundle claude      # stage -> validate -> dist/almanac-plugin-<version>.zip
just bundle cursor      # stage -> stage checks -> dist/almanac-cursor-plugin-<version>.zip
just bundle agy         # stage -> validate -> dist/almanac-agy-<version>.zip
just install agy        # bundle, then install through that harness's own CLI

just clean              # drop build output and caches
just clobber            # clean, and remove the virtual environment
```

`just` on its own runs `setup` then `preflight`, which is the full pass.

- `just style` — `prettier --check .` (also a pre-commit hook, so it runs on commit and
  in CI). Note `proseWrap: always` at 88 columns: prettier reflows Markdown prose.
- `just validate` — `skills-ref validate` per skill directory, matching the
  `validate-skill` workflow.
- `just manifests` — every harness at once: each manifest carries the shared `VERSION`
  and an MIT license, each marketplace lists exactly this plugin at `./` and says the
  same name and description as its plugin manifest, and every declared path exists. A
  mismatch breaks installation for whoever installs the release, and only for them.
  `just manifests cursor` narrows it to one harness.
- `just drift` — the template check described above.
- `just test` — the structural suite in `tests/`, via `uv run pytest`.
- `just preflight` — `check` and `test` together. This is what `just release` gates on.

Dependencies are declared in `pyproject.toml` under `[dependency-groups]` and pinned in
`uv.lock`, which is tracked. Recipes that touch Python depend on `venv`, so `uv` syncs
the environment before anything runs.

The manifest check, the drift check, and the suite are also pre-commit hooks. They
invoke `uv run` directly, because the CI image that runs pre-commit has no `just`. A
check that is not a pre-commit hook is not enforced in CI, which is why `style` and
`validate` have their own hook and workflow.

The checks are also a CLI in their own right: `uv run python -m tools --help` lists
them, and each command carries its own help.

### The structural suite

`tests/` holds deterministic checks — no model, no cost, safe to run on every push. It
exists because most of the defects this project has shipped and caught were structural:

| Check                       | Enforces                                                                                                                                             |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_entry_frontmatter.py` | required fields, and **only** the allowed fields — this is what makes "no frontmatter beyond those specified" a failing build rather than a sentence |
| `test_doc_examples.py`      | the docs' example entries satisfy the same contract, and no value silently loses characters to YAML                                                  |
| `test_verify_lines.py`      | every `verify` names a runnable check **and** an expected observation                                                                                |
| `test_discovery_rule.py`    | the resolution rule, executed against trees built to trip it, plus prose/code agreement                                                              |
| `test_skill_hygiene.py`     | naming, frontmatter shape, description form, exclusion-list agreement, prose ratchet                                                                 |
| `test_repo_checks.py`       | the revision stamp, and agreement _between_ harnesses rather than within one                                                                         |
| `test_manifests.py`         | every manifest rule, each against the broken manifest it exists to reject                                                                            |
| `test_bundle.py`            | staging, the payload allowlist, and what the finished archive does and does not contain                                                              |
| `test_harnesses.py`         | the table matches the harnesses actually present on disk                                                                                             |
| `test_drift.py`             | the template check, against a deliberately drifting pair                                                                                             |
| `test_release.py`           | the shared version reaches every manifest, and bump keywords resolve                                                                                 |
| `test_cli.py`               | `python3 -m tools` exits zero when the repo is clean and non-zero when it is not                                                                     |

Two conventions worth keeping:

**Every checker carries its own known-bad cases.** A validator that accepts everything
passes forever — the same defect `record` warns about in a `verify` line that merely
locates its subject. So `lint_verify` is tested against the exact anti-pattern the
template once shipped, and `check_entry_frontmatter` against a `confidence:` field. If
you add a check, add the input that must fail it.

**The prose ratchet is a scoreboard, not a gate.** `tests/baselines.json` freezes each
skill's word count. `record` and `audit` run well over CONTRIBUTING's "well under 500
words", and compressing them is deferred; the ratchet stops that debt growing without
pretending it is paid. Lowering a ceiling is routine. Raising one is a decision that
belongs in the PR description.

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
- `init` run twice should propose nothing on the second run, and must preserve an
  existing local destinations block rather than replacing it from the template.

## Releasing

```bash
just release patch   # or minor / major / an explicit version
```

Bumps `VERSION` and every harness manifest, commits, tags, and pushes. CI drafts the
GitHub release from the tag. Releases must come from `main` with a clean tree;
`release-guard` enforces it.

## Conventions

Every convention this repository requires is an almanac entry — `ls docs/almanac/`.
Conventional Commits, `<type>/<change-slug>` branches, pull requests, session worktrees,
Markdown wrapping, and comment style are all there.

They live there rather than here so every harness reads them, not only the ones that
look for a contributing guide, and so each one arrives at the moment it applies instead
of being paid for on every turn.
