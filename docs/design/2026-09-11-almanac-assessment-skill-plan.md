# Almanac Assessment Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `almanac:assess`, a development-only fourth skill that critiques the
almanac mechanism from a fresh agent's cold read, and make it structurally impossible to
ship.

**Architecture:** The skill is an ordinary `skills/<name>/SKILL.md`, so the existing
structural suite covers it for free. The bundler gains a second exclusion list — one for
paths that were never in a payload, one for paths a payload copies and the stage must
strip — and a test asserts no archive carries the new skill. A stub under
`.claude/skills/` gives Claude Code a route to a file its plugin archive deliberately
omits.

**Tech Stack:** Markdown skills per the Agent Skills specification, Python 3 with pytest
for the structural suite, `just` as the verb layer, prettier at 88 columns for all
prose.

**Design:** `docs/design/2026-09-11-almanac-assessment-skill-design.md`

---

## Deviation from the design doc

The design doc's implementation list says a note goes in both `README.md` and
`CONTRIBUTING.md`. Only `CONTRIBUTING.md` gets one. `README.md` is named in every
harness payload and ships to adopters, so documenting an instrument they will never
receive would describe a skill that is absent from their install. `CONTRIBUTING.md` is
in no payload and is read by exactly the audience the note is for.

---

## File structure

| File                             | Responsibility                                                                             |
| -------------------------------- | ------------------------------------------------------------------------------------------ |
| `tools/bundle.py`                | Gains `LOCAL_ONLY` and `EXCLUDED`; `stage()` strips, `check_stage()` and `verify()` reject |
| `tests/test_bundle.py`           | Proves the stripping happens and that a leaked archive is rejected                         |
| `skills/assess/SKILL.md`         | The skill: boundaries, six stages, the honesty rules, the report shape                     |
| `.claude/skills/assess/SKILL.md` | A stub naming the real file, carrying no method                                            |
| `tests/test_repo_checks.py`      | Proves the stub stays a stub                                                               |
| `CONTRIBUTING.md`                | Records that the fourth skill is development-only; corrects the resolver count             |

---

## Task 1: The bundler strips the development-only skill

Write this first. Once it is in place, the skill cannot ship from the moment it exists.

**Files:**

- Modify: `tools/bundle.py:23` and the bodies of `stage`, `check_stage`, `verify`
- Test: `tests/test_bundle.py`

- [ ] **Step 1: Add the fixture path and write three failing tests**

In `tests/test_bundle.py`, add one line to the `fake_repo` fixture, immediately after
the line creating `skills/init/SKILL.md`:

```python
    (tmp_path / "skills" / "assess").mkdir(parents=True)
    (tmp_path / "skills" / "assess" / "SKILL.md").write_text("development only")
```

Then append these three tests to the end of the file:

```python
@pytest.mark.parametrize("name", BUNDLED)
def test_stage_never_carries_the_development_only_skill(name, fake_repo, tmp_path):
    """`skills/` ships wholesale, so a local-only skill leaves with it unless stripped."""
    harness = harnesses.get(name)
    into = tmp_path / "stage"
    bundle.stage(harness, fake_repo, into)
    assert (into / "skills" / "init").is_dir()
    assert not (into / "skills" / "assess").exists()


@pytest.mark.parametrize("name", BUNDLED)
def test_check_stage_rejects_a_stage_carrying_the_development_only_skill(
    name, fake_repo, tmp_path
):
    harness = harnesses.get(name)
    into = tmp_path / "stage"
    bundle.stage(harness, fake_repo, into)
    (into / "skills" / "assess").mkdir(parents=True)
    (into / "skills" / "assess" / "SKILL.md").write_text("leaked")
    assert bundle.check_stage(into, harness)


def test_verify_rejects_an_archive_carrying_the_development_only_skill(tmp_path):
    out = tmp_path / "leaky.zip"
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr(".claude-plugin/plugin.json", "{}")
        archive.writestr("skills/assess/SKILL.md", "leaked")
    assert bundle.verify(out, harnesses.get("claude"))
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
uv run pytest tests/test_bundle.py -k "development_only" -v
```

Expected: all three fail. The stage test fails on the `assert not ... exists()`, because
`stage()` copies `skills/` wholesale. The other two fail because `check_stage` and
`verify` return an empty problem list.

- [ ] **Step 3: Add the exclusion lists to `tools/bundle.py`**

Replace the existing `FORBIDDEN` definition at `tools/bundle.py:23`:

```python
# Never named by any payload. docs/almanac/ holds this repo's own entries; an adopter
# gets the template and writes their own.
FORBIDDEN = ("docs",)

# Named by a payload, and stripped from the stage anyway. `skills/` ships wholesale, so
# a skill that is an instrument for maintaining this repo rather than part of the plugin
# stays out by name. Shipping one would hand an adopter a critique of a design they did
# not write.
LOCAL_ONLY = ("skills/assess",)

# What must not reach an archive, whatever put it there.
EXCLUDED = FORBIDDEN + LOCAL_ONLY
```

- [ ] **Step 4: Strip the local-only paths in `stage()`**

In `stage()`, immediately before the `# A payload that already names the manifest`
comment, add:

```python
    # A payload names `skills` as a directory, so anything local-only inside it arrives
    # with the rest and is removed here rather than filtered during the copy.
    for local in LOCAL_ONLY:
        shutil.rmtree(into / local, ignore_errors=True)
```

- [ ] **Step 5: Widen the two checks**

In `check_stage()`, change the second comprehension to read `EXCLUDED`:

```python
    problems += [
        f"{harness.name}: stage must not carry {forbidden}/"
        for forbidden in EXCLUDED
        if (staged / forbidden).exists()
    ]
```

In `verify()`, change the loop to read `EXCLUDED`:

```python
    for forbidden in EXCLUDED:
        if any(name.startswith(f"{forbidden}/") for name in names):
            problems.append(f"{harness.name}: archive must not contain {forbidden}/")
```

- [ ] **Step 6: Run the tests and confirm they pass**

```bash
uv run pytest tests/test_bundle.py -v
```

Expected: PASS, with no regression in the existing `docs` tests.

- [ ] **Step 7: Commit**

```bash
git add tools/bundle.py tests/test_bundle.py
git commit -m "feat(bundle): strip development-only skills from every payload"
```

---

## Task 2: The skill

**Files:**

- Create: `skills/assess/SKILL.md`

The structural suite already covers this file the moment it exists, so the failing test
comes for free.

- [ ] **Step 1: Confirm the suite is green before the file exists**

```bash
uv run pytest tests/test_skill_hygiene.py -q
```

Expected: PASS, and the parametrized ids name only `init`, `record`, `audit`.

- [ ] **Step 2: Write the frontmatter**

Create `skills/assess/SKILL.md` starting with exactly this.
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

- [ ] **Step 3: Write the body**

Write these sections in this order, in the repo's existing skill voice — second person,
load-bearing claims in bold, a stated reason after every instruction that could be
dropped.

**`# Assess the Almanac`** — Open with what the skill produces: a critique of the
mechanism from a first reading, not a verdict about any entry. State that a fresh
session under one harness is the intended condition, and that the report is comparable
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

**`## Before you start`** — The staging rule, and it is the mechanism, not a preference.
State it as a prohibition with its reason:

> Do not open `docs/almanac/README.md`, the repository's `README.md`, or anything under
> `docs/design/` until Stage 3. Stages 1 and 2 are worth having only because they happen
> before the design explains itself. An agent told what the listing is supposed to
> achieve cannot afterwards report what it actually understood from the listing alone.

Name the one exception: the instruction file the harness surfaced on its own is part of
first contact and is read in Stage 1.

**`## Stage 0 — Locate the almanac`** — Copy the three numbered resolution steps and the
"These steps search this tree, and never look up" paragraph **verbatim** from
`skills/record/SKILL.md`. Do not reword.
`test_every_skill_that_resolves_the_almanac_names_the_same_exclusions` compares the
backticked path list across every skill containing the glob `**/almanac/README.md`, and
a reworded copy either drifts or silently drops out of the check. Only the consequence
clause after the list is per-skill: here, assessing the wrong almanac produces a health
report about a directory nobody relies on.

**`## Stage 1 — First contact`** — Four things, recorded before anything is explained:

- Which instruction file the harness surfaced without being asked, and whether the
  consult trigger was in it. If none was surfaced, that is the first finding.
- `ls` the almanac directory and nothing else. From the filenames alone, write down what
  this repository appears to know and what it appears to require.
- Which titles cannot be decoded without opening the file.
- Whether you would have read the listing to the end, given its length, and at what
  point attention would realistically have dropped.

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
2. **A cost the contract already admits is not a finding.** The repository's own
   `README.md` confesses its costs at length, so rediscovering one is not news. It
   becomes reportable only with evidence, seen during this walk, that it has actually
   materialized here.
3. **Every finding names three things:** the text you read, the moment the problem
   bites, and what a future agent does wrong as a result. A finding missing any of the
   three is an opinion about style, and it goes in no report.
4. **Harness-specific and universal findings stay separated.** Four reports are meant to
   be read against each other. Merging the two kinds makes that impossible.
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

**`## Common mistakes`** — Match the shape of the list at the end of
`skills/audit/SKILL.md`. At minimum: reading the contract before Stage 1 and reporting
the result as a cold read; restating the README's admitted costs as discoveries;
reporting a behavioral claim; merging harness-specific findings into universal ones;
producing findings because the skill was invoked; assessing whether an entry is true.

- [ ] **Step 4: Format, then run the whole suite**

```bash
npx prettier --write skills/assess/SKILL.md
just preflight
```

Expected: PASS. `just validate` now runs `skills-ref validate` over four directories,
and `test_skill_hygiene.py` now parametrizes over four skills including the
exclusion-list drift check.

- [ ] **Step 5: Confirm the bundler actually strips it**

This is the check that matters, and it reads the finished archive rather than the
staging directory.

```bash
just bundle claude
unzip -l dist/almanac-plugin-*.zip | grep -c assess
```

Expected: `0`. If `just bundle claude` cannot run because the Claude CLI validator is
unavailable, run this instead and expect no output:

```bash
uv run python -c "
from tools import bundle, harnesses
from pathlib import Path
import tempfile
with tempfile.TemporaryDirectory() as tmp:
    stage = bundle.stage(harnesses.get('claude'), Path('.'), Path(tmp) / 'stage')
    print([p for p in stage.rglob('assess')])
"
```

- [ ] **Step 6: Commit**

```bash
git add skills/assess/SKILL.md
git commit -m "feat(assess): add a development-only almanac assessment skill"
```

---

## Task 3: The Claude Code stub

Claude Code loads skills from an installed plugin archive, and Task 1 removed the skill
from every archive. Without this, the one harness the repo is developed under is the one
that cannot invoke the skill.

**Files:**

- Create: `.claude/skills/assess/SKILL.md`
- Modify: `tests/test_repo_checks.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_repo_checks.py`:

```python
STUB = almanac.REPO_ROOT / ".claude" / "skills" / "assess" / "SKILL.md"
REAL = "skills/assess/SKILL.md"


def test_the_assess_stub_exists_and_names_the_real_skill():
    """Claude Code installs from an archive that deliberately omits the skill."""
    assert STUB.is_file(), f"{STUB} is missing"
    assert REAL in STUB.read_text(), f"{STUB} must name {REAL}"


def test_the_assess_stub_carries_no_method():
    """Two copies of a procedure diverge, and the stale one wins whichever is read first."""
    _, body = almanac.split_frontmatter(STUB.read_text())
    assert len(body.split()) < 120, (
        "the stub has grown a procedure of its own — it may only point at "
        f"{REAL}"
    )
```

`tests/test_repo_checks.py` already imports `almanac` from `tests.support`, so no new
import is needed.

- [ ] **Step 2: Run the test and confirm it fails**

```bash
uv run pytest tests/test_repo_checks.py -k assess -v
```

Expected: FAIL on the missing file.

- [ ] **Step 3: Write the stub**

Create `.claude/skills/assess/SKILL.md`:

```markdown
---
name: assess
description: >-
    Use when you want a health review of this repository's almanac mechanism rather than
    its contents — "assess the almanac", "is the almanac framework working", "review the
    almanac mechanics". This is a pointer, not a procedure.
---

# Assess the Almanac

This skill is maintained at `skills/assess/SKILL.md` in this repository, alongside the
shipped skills, so the structural suite covers it. It is excluded from every harness
payload, which is why Claude Code cannot reach it through an installed plugin and needs
this pointer.

Read `skills/assess/SKILL.md` and follow it exactly. Nothing here restates it: two
copies of a procedure diverge, and the stale one wins whichever is read first.
```

- [ ] **Step 4: Run the test and confirm it passes**

```bash
npx prettier --write .claude/skills/assess/SKILL.md
uv run pytest tests/test_repo_checks.py -k assess -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/assess/SKILL.md tests/test_repo_checks.py
git commit -m "feat(assess): point Claude Code at a skill its archive omits"
```

---

## Task 4: Record the arrangement in CONTRIBUTING

**Files:**

- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Correct the resolver count**

`CONTRIBUTING.md` currently reads "Three skills resolve the almanac, so this list has
already needed extending twice". `assess` makes four. Change the count to four. Leave
the rest of the sentence alone.

- [ ] **Step 2: Add a short subsection on development-only skills**

Add it under the skill-conventions material, after the resolution discussion. It must
state three things and no more:

- `skills/assess/` is an instrument for maintaining this repository, not part of the
  plugin. Shipping it would hand an adopter a critique of a design they did not write.
- It stays out of every archive through `LOCAL_ONLY` in `tools/bundle.py`, and three
  tests in `tests/test_bundle.py` make the exclusion load-bearing rather than
  remembered.
- Claude Code and Antigravity install from an archive, so neither reaches it;
  `.claude/skills/assess/SKILL.md` is the pointer that closes the Claude Code gap. Codex
  and Cursor read the tree directly and need nothing.

Do not add a note to `README.md`. It ships in every payload, and it would describe a
skill the reader's install does not contain.

- [ ] **Step 3: Format and run the full suite**

```bash
npx prettier --write CONTRIBUTING.md
just preflight
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs(contributing): record how a development-only skill stays unshipped"
```

---

## Task 5: Use the skill on this repository, then finish

The plugin is expected to work on itself, and a skill nobody has run is a skill nobody
has tested.

- [ ] **Step 1: Run it**

In a fresh session, invoke `almanac:assess` against this repository and read the report
it produces. Judge it against the honesty rules rather than its conclusions: does it
stage the reading correctly, does every finding carry its three parts, does it separate
harness-specific from universal, and does it say plainly when it found nothing?

- [ ] **Step 2: Fix what the run exposes, in this branch**

Anything the run reveals about the skill itself is a defect in the skill. Findings about
the almanac are not part of this branch and go to the issue offer.

- [ ] **Step 3: Answer the almanac question out loud**

Before opening the pull request, answer explicitly: did this branch teach us anything an
entry should carry? Most branches produce none, and zero is a normal outcome. The
likeliest candidate here is the payload behaviour — `skills/` ships as a directory, so a
new skill ships by default. Weigh it honestly against the three admission tests, noting
that `tests/test_bundle.py` now makes that failure loud rather than silent, which is the
usual reason not to record something.

- [ ] **Step 4: Open the pull request**

```bash
git push -u origin feat/assess-skill
gh pr create --title "feat(assess): add a development-only almanac assessment skill" \
  --body "Adds almanac:assess, a development-only fourth skill that critiques the almanac mechanism from a fresh agent's cold read.

The trial harness answers the functional half of the same question, so this skill makes no behavioral claim: invoking it primes the agent that would be the subject, and the report says so.

skills/ ships as a directory, so the bundler now strips a local-only list from every stage and rejects any archive carrying one. Claude Code and Antigravity install from an archive, so .claude/skills/assess/SKILL.md is the pointer that closes that gap.

Design: docs/design/2026-09-11-almanac-assessment-skill-design.md"
```

Merging to `main` requires a squash or rebase pull request, and GitHub composes the
squash commit from the commit messages rather than the pull request body.
