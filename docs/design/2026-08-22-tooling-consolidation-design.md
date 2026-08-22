# Repo Tooling Consolidation — Design

**Date:** 2026-08-22 **Status:** Approved

## Summary

Repository tooling is currently split three ways: `just` recipes, four `bash` check
scripts, and a Python test suite. The split is not the real cost. The real cost is that
the same invariants are implemented twice in two languages with opposite designs, and
that the bundle algorithm is copied three times into embedded shell.

Consolidate on **Python**. Express each harness as a row in a table, implement the
manifest checks and the bundle once against that table, and let `just` stay the verb
layer it already is. Nothing in the shipped payload changes, and no skill is edited.

## Decisions

### Nothing executable ships, so this is a contributor-and-CI choice

Every harness payload is inert — `plugin.json`, `skills/`, `templates/`, Cursor's
markdown command stubs, `README.md`, `LICENSE`. `templates/almanac/README.md` is
load-bearing at runtime because `init` reads the contract from it, but it is still
markdown. No script, no binary, and no interpreter reaches an adopter.

The language chosen here is therefore a build-time dependency for contributors and for
CI, and nothing more. It carries no distribution weight, which removes the usual
argument for a statically linked tool.

### Python, not Go

Python wins on every axis that applies to this repo:

- **The suite already exists.** `tests/` is ~970 lines across six modules and a support
  library, and it is the mature part of the tooling. Rewriting it buys nothing.
- **CI already runs Python.** `pre-commit` is itself Python and the workflow already
  calls `setup-python`. Go would add a toolchain the CI image does not have.
- **The work is text-shaped.** YAML frontmatter, markdown fence scanning, JSON manifest
  assertions, unified diffs, glob tree-walks. That is stdlib plus PyYAML.
- **Speed is already a non-issue.** The suite runs 81 tests in 0.14s. Go's startup and
  throughput advantages have nothing to bite on.

Go's genuine strengths — a single static binary, fast cold start, concurrency — are all
irrelevant when no artifact is distributed, the suite is already sub-second, and nothing
runs in parallel. The honest argument for Go is a maintainer's preference for writing
Go, which is legitimate but is not a finding about this codebase.

One point in Go's favor deserves naming and dismissing: static typing for the entry
schema. It does not apply. The binding invariant is "the required fields **and only**
the allowed fields," which `ENTRY_REQUIRED` / `ENTRY_ALLOWED` already express as set
arithmetic. A Go struct models the open-world case well and the closed-world case badly.

### A harness is a table row, not a script

Adding a harness today means touching seven places:

| #   | Location                                                       |
| --- | -------------------------------------------------------------- |
| 1   | `mod` line in the root `.justfile`                             |
| 2   | plugin-path variable in the root `.justfile`                   |
| 3   | the `check` recipe's list of `<harness>::manifests`            |
| 4   | the `release` recipe's loop over manifest paths                |
| 5   | a new `scripts/check-<harness>-manifest.sh`                    |
| 6   | a new hook in `.pre-commit-config.yaml`                        |
| 7   | a new `.<harness>-plugin/.justfile` with its payload allowlist |

Five of those are the same list of harnesses written out five times. Meanwhile
`tests/test_repo_checks.py` already does the opposite and says so out loud — it globs
`.*-plugin/plugin.json` and comments that "a new harness is data, not a new test."

That instinct is the right one and should govern the tooling too. A single
`harnesses.toml` declares, per harness: the manifest path, an optional marketplace path,
the payload allowlist, the validator command, and the paths required or forbidden in the
resulting archive. Adding a harness becomes one row plus whatever genuinely differs.

### One bundle implementation, and `zipfile` instead of shelling out

`.claude-plugin/`, `.cursor-plugin/`, and `.agy-plugin/` each carry the same seven steps
in embedded bash: clear the stage, make it, copy the payload allowlist, validate, remove
any prior archive, `zip -rXq`, then confirm the manifest survived. They differ only in
the payload list, the stage name, and which validator runs. That is roughly 180 lines of
triplicated shell across 220 lines of harness justfiles, in seven `#!/usr/bin/env bash`
heredocs that no linter and no test can reach.

It is also where the intermittent failure in
[`piping-into-grep-q-under-pipefail-fails-on-sigpipe.md`](../almanac/piping-into-grep-q-under-pipefail-fails-on-sigpipe.md)
came from — a bug an agent had already dismissed as flaky before somebody chased it
down.

Python's `zipfile` replaces `zip -rXq`, and `ZipFile.namelist()` replaces
`unzip -l | grep -q`. The almanac entry stays true about bash; this repo simply stops
standing in front of that particular gun.

### Checks become importable functions, not exit codes

`tests/test_repo_checks.py` currently runs `scripts/*` as subprocesses and asserts on
the return code. Pytest is already the wrapper around the shell scripts, which makes the
shell an intermediate layer rather than a boundary.

Once the checks are Python functions, tests call them directly and assert on structured
results. That matters most for a convention CONTRIBUTING already commits to — "every
checker carries its own known-bad cases." Feeding a deliberately broken manifest to
`check_manifest(...)` is a fixture; doing it to a bash script means building a fake tree
and parsing stderr.

The four `scripts/*.sh` files retire. `scripts/check-template-drift.py` moves into the
package essentially unchanged; its logic is already correct.

### One synced environment, reached through `uv run`

CONTRIBUTING stated the ephemeral-dependency posture as deliberate:
`uv run --with pytest --with pyyaml`, "nothing to install, no lockfile," in the same
spirit as `npx --yes`. That posture was right when `tests/` was self-contained. It stops
fitting once `tools/` must be importable by `tests/`.

Adopt a `pyproject.toml` with a dev dependency group and a committed `uv.lock`, and run
everything Python through `uv run` against the environment `just venv` syncs. This is a
`venv` recipe that runs `uv sync`, a `setup` recipe that adds `pre-commit install`, and
every recipe that touches Python depending on `venv`, so the environment is current
before anything runs.

The alternative — keeping `tools/` stdlib-only so `python3 -m tools` runs anywhere — was
tried first and rejected. It works, but it leaves two invocation paths (bare `python3`
for the checks, `uv` for the suite) and two dependency declarations (`pyproject.toml`
and pre-commit's `additional_dependencies`). Consistency is worth more here than the
ability to run one of the checks without `uv`. `tools/` remains stdlib-only as a
property; nothing depends on it any more.

Pre-commit hooks call `uv run` for the same reason they do not call `just`: the CI image
has neither by default, so CI installs `uv` explicitly and the hooks resolve the same
environment the recipes do.

This trades away a stated design position, so it is recorded here as a decision rather
than absorbed as a side effect. The CONTRIBUTING passage describing the old posture is
updated in the same change.

### `just` stays the verb layer, and the npx validators stay external

`just` is not the problem and is not replaced. It remains the set of verbs a contributor
types, with recipes shrinking to one-line delegations. The four harness modules can
collapse into a parameterized `just bundle <harness>`, or stay as thin aliases if the
current ergonomics are worth keeping — that is a taste call, not a design one.

`npx prettier` and `npx skills-ref validate` stay exactly as they are. They are external
validators this repo does not own, and wrapping them would add a layer without adding a
check.

A side effect worth having: the pre-commit hooks currently call `scripts/*` rather than
`just`, because the CI image that runs pre-commit has no `just`. Once hooks call
`python3 -m tools ...` under `language: python` with declared dependencies, hooks and
`just` stop being two separate invocation paths with two separate failure modes.

## Repository layout

```
harnesses.toml              # one row per harness
pyproject.toml              # dev dependency group; makes tools/ importable
uv.lock                     # tracked, pinning the dev environment
tools/
  __main__.py               # check-manifests [harness] | bundle <harness> | drift
  harnesses.py              # load and validate the table
  manifests.py              # the invariants, generic over harnesses
  bundle.py                 # stage -> validate -> zipfile -> verify namelist()
  drift.py                  # today's scripts/check-template-drift.py
tests/                      # imports tools/* instead of running scripts/*
```

Removed: `scripts/check-manifests.sh`, `scripts/check-cursor-manifest.sh`,
`scripts/check-codex-manifest.sh`, `scripts/check-agy-manifest.sh`,
`scripts/check-template-drift.py`.

Rough size: ~360 lines of bash and embedded shell become ~200 lines of Python plus a
~40-line table, and the duplicated manifest logic inside `test_repo_checks.py` becomes
imports.

## Tooling

- `just setup` / `just venv` — sync the environment, install the hooks.
- `just check` — unchanged as a verb; its harness fan-out comes from the table.
- `just bundle <harness>` — one recipe over the table, replacing three near-identical
  module recipes.
- `just test` — `uv run pytest`.
- `just release` — keeps its version-bump logic, but loops the table rather than a
  hardcoded list of four manifest paths.
- Pre-commit hooks call `uv run ...` under `language: system`.

## Verification

The refactor is behavior-preserving, so the bar is that the existing checks still pass
and still fail on the same inputs:

- All 81 existing tests pass unchanged in intent; tests that shelled out are rewritten
  to import.
- Each retired bash script's invariants have a corresponding known-bad fixture, per the
  CONTRIBUTING convention. A version that disagrees with `VERSION`, a name that
  disagrees between plugin and marketplace, a `skills` path that does not begin with
  `./`, a missing payload entry, and an archive missing its manifest must each fail.
- `just claude bundle`, `just cursor bundle`, and `just agy bundle` produce archives
  with the same listings as the current recipes.
- The `docs/` exclusion — enforced today only for Cursor — becomes a table field and is
  asserted for every harness.

## Out of scope

- The skills themselves, `templates/`, and everything in the shipped payload.
- The prose ratchet in `tests/baselines.json` and the word-count discipline.
- The `npx` validators, and any attempt to reimplement `skills-ref` or `prettier`.
- The GitHub workflows, beyond whatever the dependency change requires.
- Adding a new harness. The table is built to make that cheap; filling it in is later
  work.

## Docs

`CONTRIBUTING.md` gains the table as the place a harness is declared, and its
`uv run --with` passage is corrected to match the `pyproject.toml` decision. `AGENTS.md`
keeps its `just check` / `just test` / `just tidy` summary, which stays accurate.
