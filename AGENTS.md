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

[`docs/almanac/`](docs/almanac/) is this repository's operating knowledge: the facts it
learned the hard way and the rules it holds you to, one claim per file. It is
authoritative, and [docs/almanac/README.md](docs/almanac/README.md) governs the details.

**Run `ls docs/almanac/` before anything else, every session.** The filenames state the
claims, so the listing alone tells you both what this repository knows and what it
requires of you — commit format, branch naming, where work happens, and the silent
failures you would never think to search for. Carry the titles; load a body only when
one bears on what you are about to do.

That listing is the index and there is no other. Conventions this repository requires
are entries, not sections in this file — so do not look for them here, and do not
restate one here when you find it there. Two copies of a rule diverge, and the stale one
wins whichever is read first.

Beyond the startup listing, consult it when:

- Something isn't behaving as expected. Grep it _before_ you start investigating, not
  after you're stuck — it's one command and it may end the investigation.
- You're about to do something whose failure would be silent or costly to undo:
  migrations, deploys, CI config, release tooling, anything touching production.

One keyword grep is enough — `grep -rl --exclude=README.md <keyword> docs/almanac/`, or
`rg -l --glob '!README.md'`. Skip `README.md`: it is the contract rather than a claim,
and its worked examples match almost any probe. If nothing hits, move on.

**Record an entry when** you finish being surprised — a debugging session that ended in
"oh, _that's_ why," or a green build that hid a real failure — or when a convention
becomes binding here and an agent would otherwise meet it too late. Write it in the same
PR as the work, following [docs/almanac/README.md](docs/almanac/README.md).

Before you finish a branch, ask explicitly: _did this teach us anything an entry should
carry?_ Answer it out loud, even when the answer is no. Most branches produce no entry —
zero is a normal outcome, and an invented one is worse than none.

The _procedures_ for recording and auditing are this plugin's own skills,
`almanac:record` and `almanac:audit`. Consulting stays here on purpose: it is a trigger,
and it has to work on tools that read this file but cannot load a skill.

## Checks

`just setup` syncs the virtual environment and installs the git hooks. `just check` runs
the static checks — `prettier --check .`, `skills-ref validate` per skill, and the
manifest and template-drift checks. `just test` runs the structural suite in
[`tests/`](tests/), and `just preflight` runs both. `just tidy` formats. Recipes that
touch Python sync the environment first.

The suite is deterministic and free, so run it before proposing a change to a skill, the
template, or the almanac. Note the prose ratchet in `tests/baselines.json`: editing a
skill so it grows past its recorded word count fails the build on purpose. See
[CONTRIBUTING.md](CONTRIBUTING.md#the-structural-suite).
