# Almanac Assessment Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `almanac:assess`, a development-only skill that critiques the almanac
mechanism from a fresh agent's cold read, in a location nothing distributes.

**Architecture:** The skill is an ordinary `SKILL.md` at `.claude/skills/assess/`, a
path no manifest and no payload names. The structural suite's skill discovery is widened
to reach it, so the hygiene conventions and the exclusion-list drift check apply to it
exactly as they do to the shipped three.

**Tech Stack:** Markdown skills per the Agent Skills specification, Python 3 with pytest
for the structural suite, `just` as the verb layer, prettier at 88 columns for all
prose.

**Design:** `docs/design/2026-09-11-almanac-assessment-skill-design.md`

---

## Why not `skills/`, and what was already reverted

An earlier revision of this plan put the skill in `skills/` and taught the bundler to
strip it from every archive. That was built, reviewed, and reverted in `cfdd565`,
because the premise was wrong: **the archive is not how this plugin reaches adopters.**

`.claude-plugin/marketplace.json` declares `source: "./"`, so the documented Claude Code
install resolves the plugin at the repository root and discovers `skills/` from the
cloned tree. The Cursor marketplace file says the same. The codex manifest points at
`./skills/` and builds no archive at all. The release workflow creates a draft release
and attaches nothing. Only Antigravity installs from an archive.

Do not reintroduce a bundler exclusion. A `LOCAL_ONLY` entry naming a path that does not
exist strips nothing while every check still reports success, and the path it would name
is no longer where the skill lives.

## Deviation from the design doc

`README.md` gets no note about this skill. It is named in every harness payload and
ships to adopters, so it would describe a skill the reader's install does not contain.
`CONTRIBUTING.md` is in no payload and is read by exactly the audience the note is for.

---

## File structure

| File                             | Responsibility                                                         |
| -------------------------------- | ---------------------------------------------------------------------- |
| `.claude/skills/assess/SKILL.md` | The skill: boundaries, six stages, the honesty rules, the report shape |
| `tests/support/almanac.py`       | Discovers skills from both roots, so nothing is silently exempt        |
| `tests/test_skill_hygiene.py`    | Proves the second root is actually reached                             |
| `.justfile`                      | `just validate` runs the spec validator over both roots                |
| `docs/almanac/<slug>.md`         | Records that `skills/` ships to adopters whatever the bundler does     |
| `CONTRIBUTING.md`                | Records why the development-only skill lives outside `skills/`         |

---

## Task 1: The skill, and the coverage that reaches it

These are one task because they are genuinely coupled. The skill is what makes the
discovery change testable, and the discovery change is what stops the skill being exempt
from every convention the suite enforces.

**Files:**

- Create: `.claude/skills/assess/SKILL.md`
- Modify: `tests/support/almanac.py` (the `skills()` function, near line 78)
- Modify: `tests/test_skill_hygiene.py`
- Modify: `.justfile` (the `validate` recipe)

- [ ] **Step 1: Write the skill**

Create `.claude/skills/assess/SKILL.md` starting with exactly this frontmatter.
`test_description_states_when_to_use_it` requires the string "use when", and
`test_frontmatter_carries_only_name_and_description` rejects any other key.

```yaml
---
name: assess
description: >-
    Use when you want a health review of this repository's almanac mechanism rather than
    its contents — "assess the almanac", "is the almanac framework working", "review the
    almanac mechanics", "how does this almanac read to a fresh agent" — and typically in
    a new session under a particular agent harness, so the reading is genuinely cold.
    This skill critiques the mechanism by walking it. It never judges whether an entry
    is true, which is almanac:audit, and it never claims to measure what an agent did,
    which the trial harness owns.
---
```

Then write the body, in the voice the shipped skills already use: second person,
load-bearing claims in bold, a stated reason after every instruction that could
otherwise be dropped. Use these sections, in this order.

**`# Assess the Almanac`** — Open with what the skill produces: a critique of the
mechanism from a first reading, not a verdict about any entry. State that a fresh
session under one harness is the intended condition, and that reports are comparable
across harnesses because the walk is identical and only the friction differs.

**`## What this is not`** — Two paragraphs, each naming the sibling that owns the
ground:

- Not `almanac:audit`. The audit re-runs a fact's `verify` line and reaches a verdict
  about whether the claim is still true. **This skill never judges whether an entry is
  true.**
- Not the trial harness. That measures what an agent did. **This skill cannot measure
  behavior, because invoking it primes the agent that would be the subject.** An
  assessment reporting a behavioral finding is reporting a claim it has no standing to
  make.

**`## Before you start`** — The staging rule. It is the mechanism, not a preference, so
state it as a prohibition with its reason:

> Do not open the almanac's `README.md`, the repository's `README.md`, or anything under
> `docs/design/` until Stage 3. Stages 1 and 2 are worth having only because they happen
> before the design explains itself. An agent told what the listing is supposed to
> achieve cannot afterwards report what it actually understood from the listing alone.

Name the one exception: the instruction file the harness surfaced on its own is part of
first contact and is read in Stage 1.

**`## Stage 0 — Locate the almanac`** — Copy the three numbered resolution steps and the
"These steps search this tree, and never look up" paragraph **verbatim** from
`skills/record/SKILL.md`. Do not reword.
`test_every_skill_that_resolves_the_almanac_names_the_same_exclusions` compares the
backticked path list across every skill whose body contains the glob
`**/almanac/README.md`, and a reworded copy either drifts or silently drops out of the
check. Only the consequence clause after the list is per-skill: here, assessing the
wrong almanac produces a health report about a directory nobody relies on.

**`## Stage 1 — First contact`** — Four things, recorded before anything is explained:

- Which instruction file the harness surfaced without being asked, and whether the
  consult trigger was in it. If none was surfaced, that is the first finding.
- `ls` the almanac directory and nothing else. From the filenames alone, write down what
  this repository appears to know and what it appears to require.
- Which titles cannot be decoded without opening the file.
- Whether you would have read the listing to the end, given its length, and where
  attention would realistically have dropped.

**`## Stage 2 — Retrieval probe`** — Still no contract. Take the moments this repository
actually contains, derived from the listing rather than invented: about to commit, about
to open a pull request, prose that looks wrong, setting up a worktree, a build that came
back green. For each, name the entry that fires from its title alone, and whether a
single keyword grep would surface it. Then the two findings this stage exists for:

- **An entry that fires for no moment.** Its body may be excellent and it will never
  load.
- **A moment served by no entry.** Either nothing was recorded, or the title does not
  state the claim.

**`## Stage 3 — Read the contract and the skills`** — Now read the almanac's `README.md`
and the sibling skills. The reconciliation is the point: compare what the mechanism
intended against the notes already written, and say where they diverge. Then five
coherence checks:

- The fact and rule split as the live entries actually use it, not as the contract
  describes it.
- Whether precedence between the skill and the contract is stated the same way in both.
- Anything duplicated between the repository's instruction file and an entry, since two
  copies diverge and the stale one wins whichever is read first.
- The `<!-- almanac-template: N -->` stamp against the canonical template, resolved the
  way `almanac:audit` resolves it.
- Whether the commands the contract prints run as written under this harness.

**`## Stage 4 — Harness fit`** — What this harness could not do, each answered
concretely rather than assumed: whether the skills load and under what name, whether
subagents exist for the audit's fan-out, whether the plugin-root variable resolves,
whether the grep and ripgrep invocations the contract hands you are available as
written.

**`## Stage 5 — Report`** — A fixed section order, so two runs are comparable. Name the
sections explicitly:

1. **What ran** — harness, date, and what was read at each stage.
2. **First contact** — the Stage 1 record.
3. **Retrieval** — the Stage 2 record, including both failure shapes.
4. **Coherence** — the Stage 3 reconciliation.
5. **Harness fit** — the Stage 4 answers.
6. **Findings** — universal first, harness-specific second, each carrying its three
   parts.
7. **Limits** — what this run could not establish.

**`## What keeps this honest`** — The five rules, numbered, each with its reason. This
section is load-bearing and must not be compressed:

1. **Clean is an expected outcome.** Say so plainly and stop. A run that finds nothing
   is a result, in the same way a branch that teaches nothing recordable is a normal
   branch.
2. **A cost the contract already admits is not a finding.** This repository's
   `README.md` confesses its costs at length, so rediscovering one is not news. It
   becomes reportable only with evidence, seen during this walk, that it has actually
   materialized here.
3. **Every finding names three things:** the text you read, the moment the problem
   bites, and what a future agent does wrong as a result. A finding missing any of the
   three is an opinion about style, and it goes in no report.
4. **Harness-specific and universal findings stay separated.** Reports from four
   harnesses are meant to be read against each other, and merging the two kinds makes
   that impossible.
5. **The report states this skill's own limit.** Invoking it primed you, so you cannot
   report whether you would have consulted the almanac unprompted. Say that in the
   Limits section rather than letting the staging imply a rigor it does not have.

**`## Then offer`** — Two offers after the report, neither taken without approval,
matching what `init` and `audit` already do:

- Write the report to disk, proposing `docs/review/<date>-<harness>-assessment.md`
  rather than assuming it.
- File the obvious defects as issues. State the bar: **a defect in the mechanism a
  maintainer would act on** — not a matter of taste, and not a restatement of an
  admitted cost. If nothing clears the bar, say so and make no offer.

**`## Common mistakes`** — Match the shape of the list ending `skills/audit/SKILL.md`.
At minimum: reading the contract before Stage 1 and reporting the result as a cold read;
restating the README's admitted costs as discoveries; reporting a behavioral claim;
merging harness-specific findings into universal ones; producing findings because the
skill was invoked rather than because any exist; assessing whether an entry is true.

Format it before going further:

```bash
npx prettier --write .claude/skills/assess/SKILL.md
```

- [ ] **Step 2: Write the failing test**

Append to `tests/test_skill_hygiene.py`:

```python
def test_discovery_reaches_the_development_only_skill():
    """A skill outside `skills/` is exempt from every check above unless discovery finds it.

    That exemption is silent: the parametrized tests simply stop being generated for it,
    including the exclusion-list drift check, and nothing fails.
    """
    assert "assess" in {skill.name for skill in SKILLS}
```

- [ ] **Step 3: Run it and confirm it fails**

```bash
uv run pytest tests/test_skill_hygiene.py::test_discovery_reaches_the_development_only_skill -v
```

Expected: FAIL. `skills()` globs `skills/*/SKILL.md` only, so the new skill is not among
the discovered names. This failure is the point of the step: it proves the discovery
change in Step 4 is load-bearing rather than decorative.

- [ ] **Step 4: Widen discovery**

In `tests/support/almanac.py`, add a module constant beside the other path constants
near the top:

```python
# Both places a skill lives. `skills/` is what the plugin ships; `.claude/skills/` holds
# development-only skills, which reach no adopter because no manifest and no payload
# names that directory. Conventions below apply to both — a skill this helper does not
# find is silently exempt from every check that parametrizes over it.
SKILL_ROOTS = (REPO_ROOT / "skills", REPO_ROOT / ".claude" / "skills")
```

Then replace the body of `skills()`:

```python
def skills() -> list[Skill]:
    found = []
    for root in SKILL_ROOTS:
        for skill_md in sorted(root.glob("*/SKILL.md")):
            frontmatter, body = split_frontmatter(skill_md.read_text())
            found.append(
                Skill(
                    path=skill_md,
                    name=skill_md.parent.name,
                    frontmatter=frontmatter or {},
                    body=body,
                )
            )
    return found
```

- [ ] **Step 5: Run the full suite**

```bash
uv run pytest
```

Expected: PASS. The new skill is now parametrized into every hygiene test and into the
exclusion-list drift check. If the drift check fails, the resolution block in Step 1 was
reworded rather than copied — fix the skill, not the test.

- [ ] **Step 6: Validate the skill against the spec**

Update the `validate` recipe in `.justfile` so it covers both roots:

```make
# validate all skills against the vendor-neutral Agent Skills spec
validate:
    for dir in skills/*/ .claude/skills/*/; do npx skills-ref validate "$dir"; done
```

Then run it:

```bash
just validate
```

Expected: every directory validates, including `.claude/skills/assess/`.

- [ ] **Step 7: Confirm nothing ships the new skill**

```bash
just bundle claude && unzip -l dist/almanac-plugin-*.zip | grep -c assess
```

Expected: `0`. If the Claude CLI validator is unavailable and `just bundle claude`
cannot run, stage without archiving instead and expect an empty list:

```bash
uv run python -c "
from pathlib import Path
import tempfile
from tools import bundle, harnesses
with tempfile.TemporaryDirectory() as tmp:
    staged = bundle.stage(harnesses.get('claude'), Path('.'), Path(tmp) / 'stage')
    print(sorted(str(p) for p in staged.rglob('assess')))
"
```

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/assess/SKILL.md tests/support/almanac.py tests/test_skill_hygiene.py .justfile
git commit -m "feat(assess): add a development-only almanac assessment skill"
```

---

## Task 2: Record what the reverted work taught us

This is an almanac entry, and it must follow this repository's own contract. Read
`docs/almanac/README.md` before writing it, and follow `almanac:record` if you can load
it.

**Files:**

- Create: `docs/almanac/everything-in-skills-ships-to-adopters.md` (adjust the slug if a
  better claim-shaped one presents itself; the filename must state the claim)

- [ ] **Step 1: Confirm the claim independently**

Do not take this plan's word for it. Establish each of these yourself and keep the
output:

```bash
cat .claude-plugin/marketplace.json
grep -n "skills" .codex-plugin/plugin.json
grep -rn "payload" harnesses.toml
sed -n '1,40p' .github/workflows/release.yml
```

You are confirming that the marketplace manifest declares `source: "./"`, that the codex
manifest points at `./skills/`, and that the release workflow attaches no archive.

- [ ] **Step 2: Write the entry**

It is a `kind: fact` — reality can refute it, since changing the marketplace source or
the manifests would make it false. So it carries a `verify` line, and the line must fail
when the claim fails. A `verify` line asserting that `.claude-plugin/marketplace.json`
declares `source: "./"` is the load-bearing one.

Required frontmatter is `title`, `kind`, `recorded`, `source`, plus `verify` and
`verified` for a fact, and optionally `tags`. **No other fields.** Quote any value
containing `#` or `:` — an unquoted `verify` line parses as a comment and nothing warns
you. `recorded` and `verified` are `2026-09-11`. `source` is this branch and the review
that found it.

The body states the fact, then **Why it matters**, then **What to do**. What to do: a
skill that must not reach adopters does not go in `skills/`, whatever the bundler is
taught.

- [ ] **Step 3: Format and run the suite**

```bash
npx prettier --write docs/almanac/
uv run pytest
```

Expected: PASS. `tests/test_entry_frontmatter.py` enforces the field contract, and
`tests/test_verify_lines.py` checks the verify line's shape.

- [ ] **Step 4: Run your own verify line**

Run exactly what you wrote in the `verify` field and confirm the output matches what the
claim predicts. An entry whose verify line was never run is not a verified entry, and
`verified` may only carry a date on which someone actually ran it.

- [ ] **Step 5: Commit**

```bash
git add docs/almanac/
git commit -m "docs(almanac): record that skills/ ships to adopters whatever the bundler does"
```

---

## Task 3: Record the arrangement in CONTRIBUTING

**Files:**

- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Correct the resolver count**

`CONTRIBUTING.md` currently reads "Three skills resolve the almanac, so this list has
already needed extending twice". `assess` makes four. Change the count to four and leave
the rest of the sentence alone.

- [ ] **Step 2: Add a short subsection on development-only skills**

Place it with the other skill conventions, after the resolution discussion. It states
three things and no more:

- A development-only skill lives in `.claude/skills/`, not `skills/`. Everything in
  `skills/` reaches adopters through the marketplace route, which resolves the plugin at
  the repository root; see the almanac entry from Task 2.
- `tests/support/almanac.py` discovers both roots, so the hygiene conventions and the
  exclusion-list drift check apply to it exactly as to a shipped skill, and
  `just validate` covers both.
- Claude Code discovers `.claude/skills/` on its own. Another harness that does not can
  be handed the path, which is the fallback the arrangement relies on.

Do not add a note to `README.md`. It ships in every payload, and it would describe a
skill the reader's install does not contain.

- [ ] **Step 3: Format and run the full checks**

```bash
npx prettier --write CONTRIBUTING.md
just preflight
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs(contributing): record where a development-only skill lives, and why"
```

---

## Task 4: Use the skill, then finish the branch

The plugin is expected to work on itself, and a skill nobody has run is a skill nobody
has tested.

- [ ] **Step 1: Run it**

In a fresh session, invoke the skill against this repository and read the report. Judge
it against the honesty rules rather than its conclusions: does it stage the reading
correctly, does every finding carry its three parts, does it separate harness-specific
from universal, and does it say plainly when it found nothing?

- [ ] **Step 2: Fix what the run exposes, in this branch**

Anything the run reveals about the skill itself is a defect in the skill. Findings about
the almanac are not part of this branch and go to the issue offer.

- [ ] **Step 3: Answer the almanac question out loud**

Before opening the pull request, answer explicitly: did this branch teach us anything
else an entry should carry? Task 2 already recorded the one clear candidate. Most
branches produce none, and zero is a normal outcome for whatever remains.

- [ ] **Step 4: Open the pull request**

```bash
git push -u origin feat/assess-skill
gh pr create --title "feat(assess): add a development-only almanac assessment skill" \
  --body "Adds a development-only skill that critiques the almanac mechanism from a fresh agent's cold read, staged so the cold read happens before the design explains itself.

The trial harness answers the functional half of the same question, so this skill makes no behavioral claim: invoking it primes the agent that would be the subject, and the report says so.

It lives in .claude/skills/ rather than skills/. An earlier revision put it in skills/ and taught the bundler to strip it from every archive; that was reverted, because the marketplace manifest declares source ./ and the documented install discovers skills/ from the cloned tree. An almanac entry records that.

Design: docs/design/2026-09-11-almanac-assessment-skill-design.md"
```

Merging to `main` requires a squash or rebase pull request, and GitHub composes the
squash commit from the commit messages rather than the pull request body.
