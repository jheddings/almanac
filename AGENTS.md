# AGENTS.md

Always-applicable instructions for agents working in this repository. This is the
top-level instruction file; `CLAUDE.md` points here so both conventions resolve to the
same rules.

## Project

This repo ships the almanac skills — `almanac:init`, `almanac:record`, and
`almanac:audit`, in [`skills/`](skills/) — **packaged for Claude Code, Codex,
Antigravity (`agy`), and Cursor**. The packaging is harness-specific; the skills
deliberately are not, and an almanac exists to be readable by whatever agent shows up
next. [README.md](README.md) states the design positions and
[CONTRIBUTING.md](CONTRIBUTING.md) the conventions; read both before changing a skill.

Two files are easy to confuse.
[`templates/almanac/README.md`](templates/almanac/README.md) is the **canonical**
contract text that adopting repos copy.
[`docs/almanac/README.md`](docs/almanac/README.md) is _this_ repo's live almanac and an
instance of that template — identical outside the `<!-- almanac:local -->` block. Edit
the template first, port the change, then run `just drift`.

## The almanac

[`docs/almanac/`](docs/almanac/) records facts discovered the hard way — silent failure
modes, tools that behave differently than documented, constraints not visible from the
code. It is authoritative for this repo, and
[docs/almanac/README.md](docs/almanac/README.md) governs the details.

**Consult it when:**

- You start work in an area you don't already know. Run `ls docs/almanac/` once — the
  filenames state the claims, so the listing alone tells you what this repository has
  already learned. Do this _before_ you have a symptom: the entries worth most are
  silent failures you would never think to search for.
- Something isn't behaving as expected. Grep it _before_ you start investigating, not
  after you're stuck — it's one command and it may end the investigation.
- You're about to do something whose failure would be silent or costly to undo:
  migrations, deploys, CI config, release tooling, anything touching production.

One keyword grep is enough — `grep -rl --exclude=README.md <keyword> docs/almanac/`, or
`rg -l --glob '!README.md'`. Skip `README.md`: it is the contract rather than a claim,
and its worked example matches almost any probe. If nothing hits, move on.

**Record an entry when** you finish being surprised — a debugging session that ended in
"oh, _that's_ why," or a green build that hid a real failure. Write it in the same PR as
the work that uncovered it, following [docs/almanac/README.md](docs/almanac/README.md).

Before you finish a branch, ask explicitly: _did this teach us anything an entry should
carry?_ Answer it out loud, even when the answer is no. Most branches produce no entry —
zero is a normal outcome, and an invented one is worse than none.

The _procedures_ for recording and auditing are this plugin's own skills,
`almanac:record` and `almanac:audit`. Consulting stays here on purpose: it is a trigger,
and it has to work on tools that read this file but cannot load a skill.

## Conventions

### Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`

Scope is optional but encouraged — `fix(audit): ...`, `feat(init): ...`. Include the
issue number where one applies — `feat: add the init skill (#3)`.

### Branches

Use the same type prefixes as commits, followed by a short description of the intended
change:

```
<type>/<change-slug>
```

Examples: `feat/email-notifications`, `fix/sidebar-delete-width`, `chore/update-deps`.
Optionally include the issue number: `feat/279-email-notifications`.

### Pull requests

- PRs are required to merge to `main`; squash or rebase only, and CI must pass.
- GitHub composes the squash commit from the **commit messages**, and takes its title
  from the sole commit when a PR has exactly one and from the PR title otherwise. Both
  follow the commit convention above.
- Put issue references in the PR **body**, not the title.

### Markdown

Repository `.md` files are wrapped by tooling: `.prettierrc.json` sets
`proseWrap: always` at `printWidth: 88`, enforced by `just check` and the prettier
pre-commit hook. Do not hand-wrap or hand-align prose in them — run `just tidy` and let
prettier own the line breaks.

Prose written _outside_ the repo — PR descriptions, issue bodies, review comments —
never passes through prettier, and GitHub renders its line breaks literally rather than
reflowing them. Hard-wrapping there produces visibly ragged text. Write those paragraphs
as one continuous line per paragraph and let the browser wrap.

Commit messages are the exception: wrap those at about 72 columns, since they are read
in terminals that do not reflow — and since squashing puts the commit messages, not the
PR body, on `main`.

### Comments and docstrings

Write comments that describe how the code works now. State the mechanism, the constraint
it satisfies, or the failure it prevents, as a present-tense fact about the code in
front of the reader.

Leave out comparisons to an earlier implementation, justifications framed as history,
and references to other repositories. A reader six months from now has only this code; a
comment about what the code is not, or about how some other project does it, is
something they have to decode before they can use it. Rationale that is genuinely about
a tradeoff belongs in the pull request or a design doc under
[`docs/design/`](docs/design/), where it is dated and can be cleared out once it stops
mattering.

### Worktrees

Use a dedicated git worktree for development to keep the main working directory clean.
Worktrees live in `.worktrees/` and are specific to an **agent session**, not to the
feature or the changes — each session gets a fresh worktree with a unique name. Always
announce your worktree name when creating or switching to one; feel free to be creative
or silly with the name.

```bash
# Create a worktree based on origin/main
git worktree add .worktrees/<name> -b <branch-name> origin/main

# Clean up after merging
git worktree remove .worktrees/<name>
```

## Checks

`just setup` syncs the virtual environment and installs the git hooks. `just check` runs
the static checks — `prettier --check .`, `skills-ref validate` per skill, and the
manifest and template-drift checks. `just test` runs the structural suite in
[`tests/`](tests/), and `just preflight` runs both. `just tidy` formats. Recipes that
touch Python sync the environment first.

Prettier uses `proseWrap: always` at 88 columns, so it reflows Markdown prose — expect
it to rewrap paragraphs you edit.

The suite is deterministic and free, so run it before proposing a change to a skill, the
template, or the almanac. Note the prose ratchet in `tests/baselines.json`: editing a
skill so it grows past its recorded word count fails the build on purpose. See
[CONTRIBUTING.md](CONTRIBUTING.md#the-structural-suite).
